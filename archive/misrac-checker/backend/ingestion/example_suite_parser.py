"""
Example Suite Parser

Parses the MISRA C:2012 Example Suite to extract rule examples,
including all related files (.c, .h, system/support files).
"""

import os
import re
from typing import Dict, List, Tuple, Optional

from backend.utils.models import Rule, RuleType


# Common headers shared across example files
COMMON_HEADERS = ['mc3_header.h', 'mc3_types.h']


def parse_example_suite(suite_dir: str) -> Dict[str, Rule]:
    """
    Parse the entire Example Suite and return a dictionary of rules.
    
    Args:
        suite_dir: Path to the Example-Suite-master directory.
        
    Returns:
        Dictionary mapping rule_id to Rule objects.
    """
    rules = {}
    
    if not os.path.exists(suite_dir):
        print(f"Example Suite directory '{suite_dir}' not found.")
        return rules
    
    # Get all files in the suite directory
    all_files = os.listdir(suite_dir)
    
    # Parse rule files (R_xx_yy.c)
    rules.update(_parse_rule_files(suite_dir, all_files, RuleType.RULE))
    
    # Parse directive files (D_xx_yy.c)
    rules.update(_parse_rule_files(suite_dir, all_files, RuleType.DIRECTIVE))
    
    # Attach related files to each rule
    _attach_related_files(suite_dir, all_files, rules)
    
    return rules


def _parse_rule_files(
    suite_dir: str,
    all_files: List[str],
    rule_type: RuleType
) -> Dict[str, Rule]:
    """
    Parse rule or directive files and extract metadata.
    
    Args:
        suite_dir: Path to the Example Suite directory.
        all_files: List of all files in the directory.
        rule_type: Whether parsing Rules or Directives.
        
    Returns:
        Dictionary of parsed Rule objects.
    """
    rules = {}
    prefix = 'R' if rule_type == RuleType.RULE else 'D'
    pattern = re.compile(rf'^{prefix}_\d+_\d+\.c$')
    
    for filename in all_files:
        match = pattern.match(filename)
        if not match:
            continue
        
        filepath = os.path.join(suite_dir, filename)
        rule = _parse_single_file(filepath, rule_type)
        if rule:
            rules[rule.rule_id] = rule
    
    return rules


def _parse_single_file(filepath: str, rule_type: RuleType) -> Rule:
    """
    Parse a single example file and extract rule metadata.
    
    Args:
        filepath: Path to the example file.
        rule_type: Whether this is a Rule or Directive.
        
    Returns:
        Rule object with extracted metadata.
    """
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Extract rule ID from filename (e.g., R_08_04.c -> 8.4)
    filename = os.path.basename(filepath)
    match = re.search(r'[RD]_(\d+)_(\d+)\.c', filename)
    if not match:
        return None
    
    chapter = int(match.group(1))
    subrule = int(match.group(2))
    rule_id = f"{chapter}.{subrule}"
    
    # Extract description from comments
    description = _extract_description(content)
    
    # Extract category (Mandatory/Advisory/Required) from comments
    category = _extract_category(content)
    
    return Rule(
        rule_id=rule_id,
        rule_type=rule_type,
        category=category,
        description=description,
        example_files=[filename],
        example_content=content
    )


def _extract_description(content: str) -> str:
    """
    Extract the rule description from file comments.
    
    Args:
        content: Full file content.
        
    Returns:
        Extracted description string.
    """
    # Look for the rule description in comments
    # Pattern: "A compatible declaration shall be visible..."
    lines = content.split('\n')
    description_lines = []
    in_description = False
    
    for line in lines:
        stripped = line.strip()
        
        # Start collecting after the rule number comment
        if re.match(r'/(?:\*|/)\s*[RD]\.\d+\.\d+', stripped):
            in_description = True
            continue
        
        if in_description:
            # Remove comment markers
            clean = re.sub(r'^\s*(?:/\*|\*|//)\s*', '', stripped)
            clean = re.sub(r'\*/\s*$', '', clean)
            clean = clean.strip()
            
            if clean and not clean.startswith('Note:'):
                description_lines.append(clean)
            elif stripped in ('*/', ''):
                break
    
    return ' '.join(description_lines)


def _extract_category(content: str) -> str:
    """
    Extract the rule category from file comments.
    
    Args:
        content: Full file content.
        
    Returns:
        Category string (Required/Advisory/Mandatory).
    """
    # Check for category keywords in comments
    if 'Mandatory' in content:
        return 'Mandatory'
    elif 'Advisory' in content:
        return 'Advisory'
    elif 'Required' in content:
        return 'Required'
    return 'Mandatory'  # Default fallback


def _attach_related_files(
    suite_dir: str,
    all_files: List[str],
    rules: Dict[str, Rule]
) -> None:
    """
    Attach related files (headers, system/support files) to each rule.
    
    Args:
        suite_dir: Path to the Example Suite directory.
        all_files: List of all files in the directory.
        rules: Dictionary of Rule objects to update.
    """
    for rule_id, rule in rules.items():
        chapter, subrule = _parse_rule_id(rule_id)
        if chapter is None or subrule is None:
            continue
        
        prefix = 'R' if rule.rule_type == RuleType.RULE else 'D'
        
        # Find associated header files
        header_patterns = [
            f"{prefix}_{chapter:02d}_{subrule:02d}.h",
            f"{prefix}_{chapter:02d}_{subrule:02d}_1.h",
            f"{prefix}_{chapter:02d}_{subrule:02d}_2.h",
        ]
        
        for header in header_patterns:
            if header in all_files:
                if header not in rule.example_files:
                    rule.example_files.append(header)
                    _append_file_content(suite_dir, header, rule)
        
        # Find system/support files for this chapter
        system_file = f"{prefix}_{chapter:02d}_system.c"
        support_file = f"{prefix}_{chapter:02d}_support.c"
        
        for sys_file in [system_file, support_file]:
            if sys_file in all_files:
                if sys_file not in rule.example_files:
                    rule.example_files.append(sys_file)
                    _append_file_content(suite_dir, sys_file, rule)
        
        # Add common headers
        for common_header in COMMON_HEADERS:
            if common_header in all_files:
                if common_header not in rule.example_files:
                    rule.example_files.append(common_header)
                    _append_file_content(suite_dir, common_header, rule)


def _append_file_content(suite_dir: str, filename: str, rule: Rule) -> None:
    """
    Append a file's content to the rule's example_content.
    
    Args:
        suite_dir: Path to the Example Suite directory.
        filename: Name of the file to read.
        rule: Rule object to update.
    """
    filepath = os.path.join(suite_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        rule.example_content += f"\n\n--- {filename} ---\n{content}"
    except Exception as e:
        print(f"Warning: Could not read {filename}: {e}")


def _parse_rule_id(rule_id: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Parse a rule ID string into chapter and subrule numbers.
    
    Args:
        rule_id: Rule ID string (e.g., "8.4").
        
    Returns:
        Tuple of (chapter, subrule) integers, or (None, None) if invalid.
    """
    match = re.match(r'(\d+)\.(\d+)', rule_id)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None