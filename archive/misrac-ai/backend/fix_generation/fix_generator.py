"""
Fix Generator

Generates code fixes for MISRA C:2012 violations using OpenAI's LLM API.
Includes self-review capability and git patch generation.
"""

import json
import os
import difflib
from typing import Optional

import openai

from backend.utils.models import Violation, Rule, CodeContext, Fix
from backend.utils.config import config
from backend.fix_generation.prompts import (
    FIX_GENERATION_SYSTEM_PROMPT,
    build_fix_generation_prompt,
    SELF_REVIEW_SYSTEM_PROMPT,
    build_self_review_prompt,
)


class FixGenerator:
    """
    Generates and validates fixes for MISRA C:2012 violations.
    
    Uses OpenAI's LLM to generate context-aware fixes and performs
    self-review to ensure fix quality.
    """

    def __init__(self, openai_client: openai.OpenAI = None):
        """
        Initialize the fix generator.
        
        Args:
            openai_client: OpenAI client instance.
        """
        self.client = openai_client or openai.OpenAI(
            api_key=config.OPENAI_LLM_API_KEY,
            base_url=config.OPENAI_LLM_API_ENDPOINT or None
        )

    def generate_fix(
        self,
        violation: Violation,
        code_context: Optional[CodeContext] = None,
        rag_context: str = "",
        rule: Optional[Rule] = None
    ) -> Fix:
        """
        Generate a fix for a MISRA violation.
        
        Args:
            violation: The violation to fix.
            code_context: Code context around the violation.
            rag_context: Retrieved context from vector store.
            rule: The MISRA rule details.
            
        Returns:
            Fix object with the generated fix.
        """
        # Build the prompt
        context_text = ""
        static_analysis_text = ""
        if code_context:
            context_text = code_context.surrounding_lines
            # Combine dump and CTU context for static analysis
            sa_parts = []
            if code_context.dump_context:
                sa_parts.append(code_context.dump_context)
            if code_context.ctu_context:
                sa_parts.append(code_context.ctu_context)
            static_analysis_text = "\n\n".join(sa_parts)

        user_prompt = build_fix_generation_prompt(
            rule_id=violation.rule_id,
            category=violation.category,
            violation_description=violation.description,
            file=violation.file,
            line=violation.line,
            code_context=context_text,
            static_analysis_context=static_analysis_text,
            rag_context=rag_context
        )
        
        # Call LLM
        response = self.client.chat.completions.create(
            model=config.OPENAI_LLM_MODEL,
            messages=[
                {"role": "system", "content": FIX_GENERATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Low temperature for deterministic fixes
            response_format={"type": "json_object"}
        )
        
        # Parse response
        result = json.loads(response.choices[0].message.content)
        
        return Fix(
            violation=violation,
            description=result.get("description", ""),
            original_code=result.get("original_code", ""),
            fixed_code=result.get("fixed_code", ""),
            git_patch="",
            self_review=""
        )

    def self_review(self, fix: Fix) -> str:
        """
        Perform LLM self-review on a generated fix.
        
        Args:
            fix: The fix to review.
            
        Returns:
            Review assessment string.
        """
        user_prompt = build_self_review_prompt(
            rule_id=fix.violation.rule_id,
            violation_description=fix.violation.description,
            original_code=fix.original_code,
            fixed_code=fix.fixed_code,
            fix_description=fix.description
        )
        
        # Call LLM for review
        response = self.client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SELF_REVIEW_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Format review result
        approved = result.get("approved", False)
        issues = result.get("issues", [])
        summary = result.get("summary", "")
        
        review_text = f"Review: {'APPROVED' if approved else 'NEEDS REVISION'}\n"
        review_text += f"Summary: {summary}\n"
        if issues:
            review_text += "Issues:\n"
            for issue in issues:
                review_text += f"  - {issue}\n"
        
        return review_text

    def generate_git_patch(self, fix: Fix) -> str:
        """
        Generate a git unified diff patch for a fix.

        Uses the full file content and the violation's line number to replace
        the exact line(s) in the source file, producing a proper unified diff
        with context lines.  The indentation of the original line is preserved
        so the LLM's (often unindented) fixed_code still produces a valid diff.

        Args:
            fix: The fix to generate a patch for.

        Returns:
            Git unified diff string.
        """
        file_path = fix.violation.file

        if fix.full_file_content:
            lines = fix.full_file_content.split('\n')
            violation_line = fix.violation.line  # 1-indexed
            line_idx = violation_line - 1

            if 0 <= line_idx < len(lines):
                original_line = lines[line_idx]
                leading_ws = len(original_line) - len(original_line.lstrip())
                prefix = original_line[:leading_ws] if leading_ws > 0 else ""

                original_snippet = (fix.original_code or "").strip('\n').strip()
                fixed_snippet = (fix.fixed_code or "").strip('\n').strip()

                # Only emit a patch when the change is a simple one-line replacement
                # for the exact line in the file.
                if not fixed_snippet or '\n' in fixed_snippet or '\n' in original_snippet:
                    return ""

                normalized_current = original_line.strip()
                normalized_original = original_snippet.strip()
                if normalized_current != normalized_original:
                    return ""

                replacement_line = prefix + fixed_snippet
                replacement_line = replacement_line.rstrip() + ""
                new_lines = lines[:line_idx] + [replacement_line] + lines[line_idx + 1:]

                # Build a standard patch(1) style diff that can be applied with the
                # system patch utility, which is more tolerant of local file layout.
                old_line = original_line.rstrip()
                new_line = replacement_line.rstrip()
                patch_lines = [
                    f"--- {file_path}",
                    f"+++ {file_path}",
                    f"@@ -{violation_line},{1} +{violation_line},{1} @@",
                    f"-{old_line}",
                    f"+{new_line}",
                ]
                return '\n'.join(patch_lines)

        # Fallback: minimal diff from snippets only
        original_lines = fix.original_code.split('\n')
        fixed_lines = fix.fixed_code.split('\n')

        diff = difflib.unified_diff(
            original_lines,
            fixed_lines,
            fromfile=file_path,
            tofile=file_path,
            lineterm=""
        )

        return '\n'.join(diff)