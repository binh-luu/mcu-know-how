"""
Data models for the MISRA-C:2012 AI Fixing Assistant.

Defines core data structures for violations, rules, code context,
and fix generation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class RuleCategory(Enum):
    """MISRA C:2012 rule categories."""
    REQUIRED = "Required"
    ADVISORY = "Advisory"
    MANDATORY = "Mandatory"


class RuleType(Enum):
    """Type of MISRA guideline."""
    RULE = "Rule"
    DIRECTIVE = "Directive"


@dataclass
class Violation:
    """
    Represents a single MISRA C:2012 violation detected in source code.
    
    Attributes:
        file: Source file name (as referenced in CSV report, maps to src/<file>).
        line: Line number where the violation occurred.
        column: Column number where the violation occurred (may be empty).
        rule_id: The MISRA rule identifier (e.g., "8.4", "10.4").
        category: The rule category (Required, Advisory, Mandatory).
        description: Brief description of the violation.
        code_context: Surrounding source code lines (populated during analysis).
    """
    file: str
    line: int
    column: Optional[int]
    rule_id: str
    category: str
    description: str
    code_context: Optional[str] = None


@dataclass
class Rule:
    """
    Represents a MISRA C:2012 rule or directive with example context.
    
    Attributes:
        rule_id: The rule identifier (e.g., "8.4").
        rule_type: Whether this is a Rule or Directive.
        category: The rule category (Required, Advisory, Mandatory).
        description: The rule's description/guideline text.
        example_files: List of related Example Suite file paths.
        example_content: Full text content of example files.
    """
    rule_id: str
    rule_type: RuleType
    category: str
    description: str
    example_files: list[str] = field(default_factory=list)
    example_content: str = ""


@dataclass
class CodeContext:
    """
    Represents the code context surrounding a violation.
    
    Attributes:
        file_path: Full path to the source file.
        line_number: Line number of the violation.
        surrounding_lines: Lines of code around the violation.
        function_scope: The enclosing function's code (if applicable).
        full_file_content: Complete file content for reference.
        dump_context: Relevant data extracted from cppcheck .dump file
            (types, symbols, preprocessed code, etc.).
        ctu_context: Cross-translation-unit info from .ctu-info file
            (exported symbols visible from other files).
    """
    file_path: str
    line_number: int
    surrounding_lines: str = ""
    function_scope: str = ""
    full_file_content: str = ""
    dump_context: str = ""
    ctu_context: str = ""


@dataclass
class Fix:
    """
    Represents a generated fix for a MISRA violation.
    
    Attributes:
        violation: The violation this fix addresses.
        description: Human-readable explanation of the fix.
        original_code: The original code snippet being modified.
        fixed_code: The corrected code snippet.
        git_patch: Full git unified diff patch for the fix.
        self_review: LLM self-review assessment of the fix.
        full_file_content: Complete source file content (for patch generation).
    """
    violation: Violation
    description: str
    original_code: str
    fixed_code: str
    git_patch: str = ""
    self_review: str = ""
    full_file_content: str = ""


@dataclass
class RuleGroupFix:
    """
    Represents a collection of fixes for violations of the same rule.
    
    Attributes:
        rule_id: The MISRA rule identifier.
        fixes: List of Fix objects for this rule.
        combined_patch: Combined git patch for all fixes in this group.
    """
    rule_id: str
    fixes: list[Fix] = field(default_factory=list)
    combined_patch: str = ""