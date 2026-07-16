"""
Code Context Extractor

Extracts surrounding code context for violations from source files
in the src/ directory.
"""

import os
import re
from typing import Optional

from backend.utils.models import Violation, CodeContext
from backend.utils.config import config
from backend.analysis.dump_parser import DumpParser


class CodeContextExtractor:
    """
    Extracts code context around MISRA violations.
    
    Reads source files from the src/ directory and extracts:
    - Surrounding lines around the violation
    - Enclosing function scope
    - Full file content for reference
    """

    def __init__(self, src_dir: Optional[str] = None):
        """
        Initialize the context extractor.
        
        Args:
            src_dir: Path to the source code directory.
        """
        self.src_dir = src_dir or config.SRC_DIR
        self.dump_parser = DumpParser()

    def extract(self, violation: Violation) -> Optional[CodeContext]:
        """
        Extract full code context for a violation.
        
        Args:
            violation: The violation to extract context for.
            
        Returns:
            CodeContext object, or None if file not found.
        """
        # Use the file path from the CSV report directly;
        # fall back to prepending src_dir only if not found as-is.
        if os.path.exists(violation.file):
            file_path = violation.file
        elif os.path.exists(os.path.join(self.src_dir, violation.file)):
            file_path = os.path.join(self.src_dir, violation.file)
        else:
            print(f"Warning: Source file not found: {violation.file}")
            return None
        
        # Read full file content
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Extract surrounding lines
        surrounding = self._extract_surrounding_lines(lines, violation.line)
        
        # Extract function scope
        function_scope = self._extract_function_scope(lines, violation.line)
        
        # Extract static analysis context from .dump and .ctu-info files
        dump_context, ctu_context = self.dump_parser.get_context(
            violation.file, violation.line
        )

        return CodeContext(
            file_path=file_path,
            line_number=violation.line,
            surrounding_lines=surrounding,
            function_scope=function_scope,
            full_file_content=content,
            dump_context=dump_context,
            ctu_context=ctu_context
        )

    def _extract_surrounding_lines(
        self, lines: list, violation_line: int
    ) -> str:
        """
        Extract lines surrounding the violation.
        
        Args:
            lines: All lines in the file.
            violation_line: 1-indexed line number of violation.
            
        Returns:
            Formatted string of surrounding code with line numbers.
        """
        start = max(1, violation_line - config.CONTEXT_LINES_ABOVE)
        end = min(len(lines), violation_line + config.CONTEXT_LINES_BELOW)
        
        surrounding_parts = []
        for i in range(start - 1, end):
            marker = " >>>" if i + 1 == violation_line else "    "
            surrounding_parts.append(f"{marker} {i + 1}: {lines[i]}")
        
        return '\n'.join(surrounding_parts)

    def _extract_function_scope(
        self, lines: list, violation_line: int
    ) -> str:
        """
        Extract the enclosing function's code.
        
        Args:
            lines: All lines in the file.
            violation_line: 1-indexed line number of violation.
            
        Returns:
            The full function containing the violation.
        """
        # Find the function containing the violation line
        func_start = self._find_function_start(lines, violation_line)
        if func_start:
            func_end = self._find_function_end(lines, func_start)
            if func_end:
                return '\n'.join(lines[func_start - 1:func_end])
        
        return ""

    def _find_function_start(
        self, lines: list, target_line: int
    ) -> Optional[int]:
        """
        Find the start of the function containing target_line.
        
        Args:
            lines: All lines in the file.
            target_line: 1-indexed line number.
            
        Returns:
            1-indexed line number of function start, or None.
        """
        # Search backwards from target line for function definition
        for i in range(target_line - 2, -1, -1):
            line = lines[i].strip()
            
            # Skip comments and preprocessor directives
            if line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                continue
            if line.startswith('#'):
                continue
            
            # Check for function definition pattern
            # Look for a line ending with { or a signature line
            if '{' in line:
                # Check if previous line is a function signature
                if i > 0 and self._is_function_signature(lines[i - 1].strip()):
                    return i  # Return signature line (0-indexed) -> 1-indexed
                return i + 1  # 1-indexed
            elif self._is_function_signature(line):
                return i + 1  # 1-indexed
        
        return None

    def _find_function_end(
        self, lines: list, start_line: int
    ) -> Optional[int]:
        """
        Find the end of a function starting at start_line.
        
        Args:
            lines: All lines in the file.
            start_line: 1-indexed line number of function start.
            
        Returns:
            1-indexed line number of function end, or None.
        """
        brace_count = 0
        started = False
        
        for i in range(start_line - 1, len(lines)):
            line = lines[i]
            
            for char in line:
                if char == '{':
                    brace_count += 1
                    started = True
                elif char == '}':
                    brace_count -= 1
            
            if started and brace_count == 0:
                return i + 1  # 1-indexed
        
        return None

    def _is_function_signature(self, line: str) -> bool:
        """
        Check if a line looks like a C function signature.
        
        Args:
            line: Line to check.
            
        Returns:
            True if the line appears to be a function signature.
        """
        # Pattern: type name(params) or type name(params) {
        pattern = r'^\s*(?:static|inline|extern|\w+[\s*]+)+\w+\s*\([^)]*\)\s*(?:\{|$)'
        return bool(re.match(pattern, line))