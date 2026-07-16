#!/usr/bin/env python3
"""
MISRA-C:2012 AI Fixing Assistant CLI

Command-line interface for the MISRA-C:2012 fixing intelligent AI assistant.
"""

import argparse
import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.config import config
from backend.ingestion.csv_loader import load_all_reports
from backend.ingestion.example_suite_parser import parse_example_suite
from backend.rag.embedding_pipeline import EmbeddingPipeline
from backend.rag.vector_store import VectorStore
from backend.rag.retriever import RAGRetriever
from backend.analysis.context_extractor import CodeContextExtractor
from backend.analysis.categorizer import ViolationCategorizer
from backend.analysis.workflow import MISRAWorkflow
from backend.fix_generation.fix_generator import FixGenerator


def cmd_init(args):
    """Initialize the RAG vector store with Example Suite data."""
    print("=== Initializing RAG Vector Store ===")
    
    # Parse Example Suite
    print(f"Parsing Example Suite from {config.EXAMPLE_SUITE_DIR}...")
    rules = parse_example_suite(config.EXAMPLE_SUITE_DIR)
    print(f"  Found {len(rules)} rules/directives")
    
    # Create embeddings
    print("Creating embeddings...")
    vector_store = VectorStore()
    embedding_pipeline = EmbeddingPipeline(vector_store=vector_store)
    embedding_pipeline.create_embeddings(rules)
    
    count = vector_store.get_collection_count()
    print(f"=== Initialization Complete ===")
    print(f"  {count} rules embedded in vector store")


def cmd_analyze(args):
    """Analyze violations and generate fixes."""
    print("=== MISRA-C:2012 AI Analysis ===")
    
    # Validate config
    config.validate()
    
    # Load violations from reports
    print(f"Loading violations from {config.REPORT_DIR}...")
    violations = load_all_reports(config.REPORT_DIR)
    
    if not violations:
        print("No violations found in reports.")
        return
    
    print(f"  Found {len(violations)} violations")
    
    # Parse Example Suite for rule context
    print(f"Parsing Example Suite from {config.EXAMPLE_SUITE_DIR}...")
    rules = parse_example_suite(config.EXAMPLE_SUITE_DIR)
    print(f"  Loaded {len(rules)} rules")
    
    # Initialize components
    vector_store = VectorStore()
    rag_retriever = RAGRetriever(vector_store=vector_store)
    context_extractor = CodeContextExtractor()
    categorizer = ViolationCategorizer()
    fix_generator = FixGenerator()
    
    # Run workflow
    workflow = MISRAWorkflow(
        context_extractor=context_extractor,
        categorizer=categorizer,
        rag_retriever=rag_retriever,
        fix_generator=fix_generator
    )
    
    state = workflow.execute(violations, rules)
    
    # Output results
    if args.output:
        _save_results(state, args.output)
    
    # Print summary
    summary = categorizer.get_summary(violations)
    print("\n=== Violation Summary ===")
    print(f"Total violations: {summary['total']}")
    print(f"\nBy Category:")
    for cat, count in summary['by_category'].items():
        print(f"  {cat}: {count}")
    print(f"\nBy Rule:")
    for rule, count in sorted(summary['by_rule'].items()):
        print(f"  Rule {rule}: {count}")
    
    # Save patches
    if state.fixes:
        patch_dir = args.patch_dir or './patches'
        os.makedirs(patch_dir, exist_ok=True)
        _save_patches(state.fixes, patch_dir)
        print(f"\nPatches saved to {patch_dir}/")


def cmd_list(args):
    """List violations from reports."""
    violations = load_all_reports(config.REPORT_DIR)
    
    if not violations:
        print("No violations found.")
        return
    
    categorizer = ViolationCategorizer()
    summary = categorizer.get_summary(violations)
    
    print(f"Found {summary['total']} violations:\n")
    print(f"{'File':<25} {'Line':<6} {'Rule':<8} {'Category':<12} Description")
    print("-" * 80)
    
    for v in violations:
        print(f"{v.file:<25} {v.line:<6} {v.rule_id:<8} {v.category:<12} {v.description[:40]}...")


def _save_results(state, output_path: str):
    """Save analysis results to a JSON file."""
    results = {
        'violations': [
            {
                'file': v.file,
                'line': v.line,
                'rule_id': v.rule_id,
                'category': v.category,
                'description': v.description
            }
            for v in state.violations
        ],
        'fixes': [
            {
                'file': f.violation.file,
                'line': f.violation.line,
                'rule_id': f.violation.rule_id,
                'description': f.description,
                'original_code': f.original_code,
                'fixed_code': f.fixed_code,
                'self_review': f.self_review
            }
            for f in state.fixes
        ],
        'errors': state.errors
    }
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {output_path}")


def _save_patches(fixes, patch_dir: str):
    """Save git patches organized by rule (valid unified diff format)."""
    os.makedirs(patch_dir, exist_ok=True)

    # Group fixes by rule
    by_rule = {}
    for fix in fixes:
        rule_id = fix.violation.rule_id
        if rule_id not in by_rule:
            by_rule[rule_id] = []
        by_rule[rule_id].append(fix)

    for rule_id, rule_fixes in by_rule.items():
        patch_path = os.path.join(patch_dir, f"rule_{rule_id}.patch")

        # Collect all diffs for this rule (only valid unified diff content)
        all_diffs = []
        for fix in rule_fixes:
            if fix.git_patch:
                all_diffs.append(fix.git_patch)

        if all_diffs:
            with open(patch_path, 'w') as f:
                for diff in all_diffs:
                    f.write(diff + "\n")
            print(f"  Saved patch for Rule {rule_id}: {patch_path}")
        else:
            print(f"  No valid patches for Rule {rule_id}")

    # Save metadata (descriptions, self-review) to a separate JSON file
    metadata_path = os.path.join(patch_dir, "fix_metadata.json")
    metadata = []
    for fix in fixes:
        metadata.append({
            "file": fix.violation.file,
            "line": fix.violation.line,
            "rule_id": fix.violation.rule_id,
            "description": fix.description,
            "original_code": fix.original_code,
            "fixed_code": fix.fixed_code,
            "self_review": fix.self_review
        })
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  Fix metadata saved to {metadata_path}")


def main():
    parser = argparse.ArgumentParser(
        description='MISRA-C:2012 AI Fixing Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize vector store with Example Suite
  %(prog)s init

  # Analyze violations and generate fixes
  %(prog)s analyze

  # List violations from reports
  %(prog)s list
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize RAG vector store')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze violations and generate fixes')
    analyze_parser.add_argument('--output', '-o', help='Output path for results JSON')
    analyze_parser.add_argument('--patch-dir', '-p', help='Directory to save patches', default='./patches')
    
    # List command
    subparsers.add_parser('list', help='List violations from reports')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    commands = {
        'init': cmd_init,
        'analyze': cmd_analyze,
        'list': cmd_list,
    }
    
    commands[args.command](args)


if __name__ == '__main__':
    main()