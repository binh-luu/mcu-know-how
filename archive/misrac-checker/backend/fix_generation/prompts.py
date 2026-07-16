"""
LLM Prompt Templates

Defines prompt templates for MISRA C:2012 fix generation and self-review.
"""


# System prompt for the MISRA fix assistant
FIX_GENERATION_SYSTEM_PROMPT = """You are an expert MISRA C:2012 compliance assistant. Your task is to generate code fixes for MISRA C:2012 violations.

You must:
1. Understand the violation and its context
2. Generate a minimal, correct fix that resolves the violation
3. Ensure the fix does not introduce new MISRA violations
4. Preserve the original code's functionality
5. Follow MISRA C:2012 best practices

Respond with a JSON object containing:
- "description": A brief explanation of the fix
- "original_code": The original code snippet being modified
- "fixed_code": The corrected code snippet
"""

# User prompt template for fix generation
FIX_GENERATION_USER_PROMPT_TEMPLATE = """Fix the following MISRA C:2012 violation:

Rule: {rule_id}
Category: {category}
Description: {violation_description}

File: {file}
Line: {line}

--- Code Context ---
{code_context}

--- Static Analysis Context ---
{static_analysis_context}

--- Relevant MISRA Rule Context ---
{rag_context}

Generate a fix that resolves this violation while maintaining the code's functionality.
"""

# System prompt for self-review
SELF_REVIEW_SYSTEM_PROMPT = """You are a MISRA C:2012 compliance reviewer. Your task is to review a proposed code fix for correctness and MISRA compliance.

Evaluate the fix on:
1. Does it correctly resolve the stated violation?
2. Does it introduce any new MISRA C:2012 violations?
3. Does it preserve the original functionality?
4. Is the fix minimal and focused?

Respond with a JSON object containing:
- "approved": true/false - whether the fix is acceptable
- "issues": list of any issues found (empty if none)
- "summary": brief assessment of the fix
"""

# User prompt template for self-review
SELF_REVIEW_USER_PROMPT_TEMPLATE = """Review the following fix for a MISRA C:2012 violation:

Rule: {rule_id}
Violation: {violation_description}

--- Original Code ---
{original_code}

--- Proposed Fix ---
{fixed_code}

--- Fix Description ---
{fix_description}

Review this fix and provide your assessment.
"""


def build_fix_generation_prompt(
    rule_id: str,
    category: str,
    violation_description: str,
    file: str,
    line: int,
    code_context: str,
    static_analysis_context: str,
    rag_context: str
) -> str:
    """
    Build the user prompt for fix generation.
    
    Args:
        rule_id: MISRA rule ID.
        category: Rule category.
        violation_description: Description of the violation.
        file: Source file name.
        line: Line number.
        code_context: Surrounding code context.
        static_analysis_context: Context from cppcheck .dump and .ctu-info files.
        rag_context: Retrieved context from vector store.
        
    Returns:
        Formatted prompt string.
    """
    return FIX_GENERATION_USER_PROMPT_TEMPLATE.format(
        rule_id=rule_id,
        category=category,
        violation_description=violation_description,
        file=file,
        line=line,
        code_context=code_context,
        static_analysis_context=static_analysis_context or "(none)",
        rag_context=rag_context or "(none)"
    )
    return FIX_GENERATION_USER_PROMPT_TEMPLATE.format(
        rule_id=rule_id,
        category=category,
        violation_description=violation_description,
        file=file,
        line=line,
        code_context=code_context or "No code context available.",
        rag_context=rag_context or "No additional context available."
    )


def build_self_review_prompt(
    rule_id: str,
    violation_description: str,
    original_code: str,
    fixed_code: str,
    fix_description: str
) -> str:
    """
    Build the user prompt for self-review.
    
    Args:
        rule_id: MISRA rule ID.
        violation_description: Description of the violation.
        original_code: Original code snippet.
        fixed_code: Fixed code snippet.
        fix_description: Description of the fix.
        
    Returns:
        Formatted prompt string.
    """
    return SELF_REVIEW_USER_PROMPT_TEMPLATE.format(
        rule_id=rule_id,
        violation_description=violation_description,
        original_code=original_code,
        fixed_code=fixed_code,
        fix_description=fix_description
    )