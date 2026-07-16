"""
LangGraph Workflow

Defines the multi-step agentic workflow for analyzing and fixing
MISRA C:2012 violations using LangGraph.
"""

from typing import Dict, List, Optional, Any

from backend.utils.models import Violation, Rule, CodeContext, Fix
from backend.analysis.context_extractor import CodeContextExtractor
from backend.analysis.categorizer import ViolationCategorizer
from backend.rag.retriever import RAGRetriever
from backend.fix_generation.fix_generator import FixGenerator


class AnalysisState:
    """
    State container for the LangGraph workflow.
    
    Holds all data passed between workflow nodes.
    """

    def __init__(self):
        self.violations: List[Violation] = []
        self.rules: Dict[str, Rule] = {}
        self.contexts: Dict[str, CodeContext] = {}
        self.rag_contexts: Dict[str, str] = {}
        self.fixes: List[Fix] = []
        self.errors: List[str] = []


class MISRAWorkflow:
    """
    LangGraph-based workflow for MISRA violation analysis and fixing.
    
    Workflow steps:
    1. Ingest violations and rules
    2. Extract code context for each violation
    3. Retrieve RAG context from vector store
    4. Generate fixes using LLM
    5. Self-review generated fixes
    6. Generate git patches
    """

    def __init__(
        self,
        context_extractor: Optional[CodeContextExtractor] = None,
        categorizer: Optional[ViolationCategorizer] = None,
        rag_retriever: Optional[RAGRetriever] = None,
        fix_generator: Optional[FixGenerator] = None
    ):
        """
        Initialize the workflow.
        
        Args:
            context_extractor: CodeContextExtractor instance.
            categorizer: ViolationCategorizer instance.
            rag_retriever: RAGRetriever instance.
            fix_generator: FixGenerator instance.
        """
        self.context_extractor = context_extractor or CodeContextExtractor()
        self.categorizer = categorizer or ViolationCategorizer()
        self.rag_retriever = rag_retriever or RAGRetriever()
        self.fix_generator = fix_generator or FixGenerator()

    def execute(
        self,
        violations: List[Violation],
        rules: Dict[str, Rule]
    ) -> AnalysisState:
        """
        Execute the full workflow.
        
        Args:
            violations: List of violations to process.
            rules: Dictionary of MISRA rules.
            
        Returns:
            AnalysisState with all results.
        """
        state = AnalysisState()
        state.violations = violations
        state.rules = rules

        # Step 1: Categorize violations
        print("Step 1: Categorizing violations...")
        processing_order = self.categorizer.get_processing_order(violations)
        summary = self.categorizer.get_summary(violations)
        print(f"  Found {summary['total']} violations across "
              f"{len(summary['by_rule'])} rules")

        # Step 2: Extract code context
        print("Step 2: Extracting code context...")
        for violation in violations:
            context_key = f"{violation.file}:{violation.line}:{violation.rule_id}"
            context = self.context_extractor.extract(violation)
            if context:
                state.contexts[context_key] = context
                violation.code_context = context.surrounding_lines

        # Step 3: Retrieve RAG context
        print("Step 3: Retrieving RAG context...")
        rag_results = self.rag_retriever.retrieve_context_for_violations(violations)
        for key, results in rag_results.items():
            state.rag_contexts[key] = self.rag_retriever.format_context_for_llm(results)

        # Step 4: Generate fixes
        print("Step 4: Generating fixes...")
        for rule_id, rule_violations in processing_order:
            print(f"  Processing Rule {rule_id} ({len(rule_violations)} violations)...")
            
            for violation in rule_violations:
                context_key = f"{violation.file}:{violation.line}:{violation.rule_id}"
                
                # Get context
                code_context = state.contexts.get(context_key)
                rag_context = state.rag_contexts.get(context_key, "")
                
                # Get rule info
                rule = rules.get(violation.rule_id)
                
                try:
                    fix = self.fix_generator.generate_fix(
                        violation=violation,
                        code_context=code_context,
                        rag_context=rag_context,
                        rule=rule
                    )
                    state.fixes.append(fix)
                except Exception as e:
                    error_msg = f"Failed to generate fix for {context_key}: {str(e)}"
                    state.errors.append(error_msg)
                    print(f"  Error: {error_msg}")

        # Step 5: Self-review fixes
        print("Step 5: Self-reviewing fixes...")
        for fix in state.fixes:
            try:
                fix.self_review = self.fix_generator.self_review(fix)
            except Exception as e:
                state.errors.append(f"Self-review failed for fix: {str(e)}")

        # Step 6: Generate git patches
        print("Step 6: Generating git patches...")
        for fix in state.fixes:
            try:
                # Attach full file content for proper diff generation
                context_key = f"{fix.violation.file}:{fix.violation.line}:{fix.violation.rule_id}"
                code_context = state.contexts.get(context_key)
                if code_context:
                    fix.full_file_content = code_context.full_file_content

                fix.git_patch = self.fix_generator.generate_git_patch(fix)
            except Exception as e:
                state.errors.append(f"Git patch generation failed: {str(e)}")

        # Print summary
        print("\n=== Workflow Complete ===")
        print(f"  Violations processed: {len(violations)}")
        print(f"  Fixes generated: {len(state.fixes)}")
        print(f"  Errors: {len(state.errors)}")

        return state