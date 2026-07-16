"""
Cppcheck Dump Parser

Parses cppcheck .dump XML files and .ctu-info JSON files to extract
static analysis context (types, symbols, AST, control flow) for MISRA
violation analysis.
"""

import json
import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple


def _find_dump_file(source_file: str) -> Optional[str]:
    """
    Find the .dump file corresponding to a source file.

    Searches common locations:
    - Same directory as the source file (e.g., src/example.c -> src/example.c.dump)
    - Workspace root

    Args:
        source_file: Path to the source file (e.g., "src/example.c" or "example.c").

    Returns:
        Path to the .dump file, or None if not found.
    """
    # Try same directory as source file
    dump_path = source_file + ".dump"
    if os.path.exists(dump_path):
        return dump_path

    # Try just the basename (in case source_file is relative to src/)
    basename = os.path.basename(source_file)
    for candidate in [
        basename + ".dump",
        os.path.join("src", basename + ".dump"),
    ]:
        if os.path.exists(candidate):
            return candidate

    return None


def _find_ctu_info_file(source_file: str) -> Optional[str]:
    """
    Find the .ctu-info file corresponding to a source file.

    Args:
        source_file: Path to the source file.

    Returns:
        Path to the .ctu-info file, or None if not found.
    """
    ctu_path = source_file + ".ctu-info"
    if os.path.exists(ctu_path):
        return ctu_path

    basename = os.path.basename(source_file)
    for candidate in [
        basename + ".ctu-info",
        os.path.join("src", basename + ".ctu-info"),
    ]:
        if os.path.exists(candidate):
            return candidate

    return None


def _extract_platform_info(root: ET.Element) -> str:
    """Extract platform type size information."""
    platform = root.find("platform")
    if platform is None:
        return ""

    parts = []
    for attr in ["char_bit", "short_bit", "int_bit", "long_bit",
                 "long_long_bit", "pointer_bit"]:
        val = platform.get(attr)
        if val:
            parts.append(f"{attr}={val}")
    return ", ".join(parts)


def _extract_typedefs(root: ET.Element) -> List[str]:
    """Extract typedef definitions from the dump file."""
    typedefs = []
    # Look for typedef tokens in rawtokens
    rawtokens = root.find("rawtokens")
    if rawtokens is None:
        return typedefs

    tokens = rawtokens.findall("tok")
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.get("str") == "typedef":
            # Collect tokens until semicolon
            typedef_parts = []
            j = i + 1
            while j < len(tokens):
                next_tok = tokens[j]
                if next_tok.get("str") == ";":
                    typedef_parts.append(";")
                    break
                typedef_parts.append(next_tok.get("str", ""))
                j += 1
            if typedef_parts:
                typedefs.append("typedef " + " ".join(typedef_parts))
            i = j + 1
        else:
            i += 1

    return typedefs


def _extract_variables(root: ET.Element) -> List[str]:
    """Extract variable declarations with their types from the dump file."""
    variables = []
    var_section = root.find("var")
    if var_section is None:
        # Try finding all <var> elements under the root
        pass

    # Variables are in the tokenlist with variable attributes
    tokenlist = root.find("tokenlist")
    if tokenlist is None:
        return variables

    seen_vars = set()
    for token in tokenlist.findall("token"):
        var_id = token.get("variable")
        if var_id and var_id not in seen_vars:
            seen_vars.add(var_id)
            name = token.get("str", "")
            line = token.get("linenr", "?")
            value_type = _get_value_type(token)
            if name and value_type:
                variables.append(f"{value_type} {name} (line {line})")

    return variables


def _get_value_type(token: ET.Element) -> str:
    """Build a type string from valueType attributes on a token."""
    parts = []

    sign = token.get("valueType-sign")
    if sign:
        parts.append(sign)

    type_str = token.get("valueType-type")
    if type_str:
        parts.append(type_str)

    pointer = token.get("valueType-pointer")
    if pointer:
        parts.append("*" * int(pointer))

    return " ".join(parts) if parts else ""


def _extract_functions(root: ET.Element) -> List[str]:
    """Extract function signatures from the dump file."""
    functions = []
    tokenlist = root.find("tokenlist")
    if tokenlist is None:
        return functions

    seen_funcs = set()
    for token in tokenlist.findall("token"):
        func_id = token.get("function")
        if func_id and func_id not in seen_funcs:
            seen_funcs.add(func_id)
            name = token.get("str", "")
            line = token.get("linenr", "?")
            value_type = _get_value_type(token)
            if name and value_type:
                functions.append(f"{value_type} {name}() (line {line})")

    return functions


def _extract_tokens_near_line(root: ET.Element, target_line: int,
                               radius: int = 5) -> List[str]:
    """
    Extract analyzed tokens near a specific line number.

    This gives type information about expressions around the violation point.

    Args:
        root: XML root element.
        target_line: The line number of interest.
        radius: Number of lines above/below to include.

    Returns:
        List of formatted token info strings.
    """
    tokenlist = root.find("tokenlist")
    if tokenlist is None:
        return []

    results = []
    start_line = max(1, target_line - radius)
    end_line = target_line + radius

    for token in tokenlist.findall("token"):
        line = int(token.get("linenr", 0))
        if start_line <= line <= end_line:
            name = token.get("str", "")
            if not name or name in (";", ",", "(", ")", "{", "}", "[", "]"):
                continue

            info_parts = [f"line {line}: {name}"]
            value_type = _get_value_type(token)
            if value_type:
                info_parts.append(f"type={value_type}")

            var_id = token.get("varId")
            if var_id:
                info_parts.append(f"varId={var_id}")

            is_signed = token.get("isSigned")
            is_unsigned = token.get("isUnsigned")
            if is_signed:
                info_parts.append("signed")
            if is_unsigned:
                info_parts.append("unsigned")

            results.append(" | ".join(info_parts))

    return results


def _extract_macros(root: ET.Element) -> List[str]:
    """Extract #define macros from raw tokens."""
    macros = []
    rawtokens = root.find("rawtokens")
    if rawtokens is None:
        return macros

    tokens = rawtokens.findall("tok")
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.get("str") == "#":
            # Check if next token is 'define'
            if i + 1 < len(tokens) and tokens[i + 1].get("str") == "define":
                # Collect macro name and value
                macro_parts = []
                j = i + 2
                while j < len(tokens):
                    next_tok = tokens[j]
                    # Stop at newline (indicated by next preprocessor or end)
                    if next_tok.get("str") == "#":
                        break
                    macro_parts.append(next_tok.get("str", ""))
                    j += 1
                if macro_parts:
                    macros.append("#define " + " ".join(macro_parts))
                i = j
            else:
                i += 1
        else:
            i += 1

    return macros


def parse_dump_file(dump_path: str, target_line: Optional[int] = None) -> Dict:
    """
    Parse a cppcheck .dump XML file and extract relevant static analysis data.

    Args:
        dump_path: Path to the .dump file.
        target_line: If provided, extract extra context around this line.

    Returns:
        Dictionary with keys:
        - platform: Platform type sizes
        - typedefs: List of typedef declarations
        - macros: List of #define macros
        - variables: List of variables with types
        - functions: List of function signatures with types
        - tokens_near_line: Type info for tokens near target_line (if provided)
    """
    result = {
        "platform": "",
        "typedefs": [],
        "macros": [],
        "variables": [],
        "functions": [],
        "tokens_near_line": [],
    }

    if not os.path.exists(dump_path):
        return result

    try:
        tree = ET.parse(dump_path)
        root = tree.getroot()
    except ET.ParseError:
        return result

    result["platform"] = _extract_platform_info(root)
    result["typedefs"] = _extract_typedefs(root)
    result["macros"] = _extract_macros(root)
    result["variables"] = _extract_variables(root)
    result["functions"] = _extract_functions(root)

    if target_line:
        result["tokens_near_line"] = _extract_tokens_near_line(root, target_line)

    return result


def parse_ctu_info_file(ctu_path: str) -> Dict:
    """
    Parse a cppcheck .ctu-info JSON lines file.

    Each line is a JSON object with "summary" and "data" fields.

    Args:
        ctu_path: Path to the .ctu-info file.

    Returns:
        Dictionary with keys:
        - typedefs: Typedef info
        - tags: Struct/union tag names
        - macros: Macro definitions
        - external_ids: External identifiers
        - internal_ids: Internal (static) identifiers
        - local_ids: Local variable identifiers
        - usage: Symbol usage info
    """
    result = {
        "typedefs": [],
        "tags": [],
        "macros": [],
        "external_ids": [],
        "internal_ids": [],
        "local_ids": [],
        "usage": [],
    }

    if not os.path.exists(ctu_path):
        return result

    try:
        with open(ctu_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                summary = obj.get("summary", "")
                data = obj.get("data", [])

                if summary == "MisraTypedefInfo":
                    result["typedefs"] = data
                elif summary == "MisraTagName":
                    result["tags"] = data
                elif summary == "MisraMacro":
                    result["macros"] = data
                elif summary == "MisraExternalIdentifiers":
                    result["external_ids"] = data
                elif summary == "MisraInternalIdentifiers":
                    result["internal_ids"] = data
                elif summary == "MisraLocalIdentifiers":
                    result["local_ids"] = data
                elif summary == "MisraUsage":
                    result["usage"] = data
    except (json.JSONDecodeError, IOError):
        pass

    return result


def format_dump_context(dump_data: Dict, target_line: Optional[int] = None) -> str:
    """
    Format parsed dump data into a human-readable string for LLM context.

    Args:
        dump_data: Dictionary from parse_dump_file().
        target_line: Line number being analyzed (for header).

    Returns:
        Formatted multi-line string.
    """
    lines = []

    if target_line:
        lines.append(f"--- Static Analysis Context (line {target_line}) ---")
    else:
        lines.append("--- Static Analysis Context ---")

    # Platform info
    if dump_data.get("platform"):
        lines.append(f"\nPlatform: {dump_data['platform']}")

    # Typedefs
    typedefs = dump_data.get("typedefs", [])
    if typedefs:
        lines.append("\nType Definitions:")
        for td in typedefs:
            lines.append(f"  {td}")

    # Macros
    macros = dump_data.get("macros", [])
    if macros:
        lines.append("\nMacros:")
        for macro in macros:
            lines.append(f"  {macro}")

    # Variables with types
    variables = dump_data.get("variables", [])
    if variables:
        lines.append("\nVariables (with resolved types):")
        for var in variables:
            lines.append(f"  {var}")

    # Functions with types
    functions = dump_data.get("functions", [])
    if functions:
        lines.append("\nFunctions (with resolved types):")
        for func in functions:
            lines.append(f"  {func}")

    # Tokens near target line
    tokens = dump_data.get("tokens_near_line", [])
    if tokens:
        lines.append(f"\nType Info Near Line {target_line}:")
        for tok in tokens:
            lines.append(f"  {tok}")

    return "\n".join(lines)


def format_ctu_context(ctu_data: Dict) -> str:
    """
    Format parsed CTU info into a human-readable string for LLM context.

    Args:
        ctu_data: Dictionary from parse_ctu_info_file().

    Returns:
        Formatted multi-line string.
    """
    lines = ["--- Cross-Translation-Unit Info ---"]

    # Typedefs
    typedefs = ctu_data.get("typedefs", [])
    if typedefs:
        lines.append("\nExported Typedefs:")
        for td in typedefs:
            name = td.get("name", "?")
            used = "used" if td.get("used") else "unused"
            lines.append(f"  {name} ({used})")

    # Tags
    tags = ctu_data.get("tags", [])
    if tags:
        lines.append("\nStruct/Union Tags:")
        for tag in tags:
            name = tag.get("name", "?")
            used = "used" if tag.get("used") else "unused"
            lines.append(f"  {name} ({used})")

    # Macros
    macros = ctu_data.get("macros", [])
    if macros:
        lines.append("\nMacros:")
        for macro in macros:
            name = macro.get("name", "?")
            used = "used" if macro.get("used") else "unused"
            lines.append(f"  {name} ({used})")

    # External identifiers
    ext_ids = ctu_data.get("external_ids", [])
    if ext_ids:
        lines.append("\nExternal Identifiers:")
        for eid in ext_ids:
            name = eid.get("name", "?")
            lines.append(f"  {name}")

    # Internal identifiers
    int_ids = ctu_data.get("internal_ids", [])
    if int_ids:
        lines.append("\nInternal (static) Identifiers:")
        for iid in int_ids:
            name = iid.get("name", "?")
            inline = " inline" if iid.get("inlinefunc") else ""
            lines.append(f"  {name}{inline}")

    # Usage
    usage = ctu_data.get("usage", [])
    if usage:
        lines.append("\nSymbol Usage:")
        for u in usage:
            name = u.get("name", "?")
            file = u.get("file", "?")
            lines.append(f"  {name} used in {file}")

    return "\n".join(lines)


class DumpParser:
    """
    High-level parser that finds and parses .dump and .ctu-info files
    for a given source file.
    """

    def __init__(self):
        pass

    def get_context(self, source_file: str, target_line: Optional[int] = None
                    ) -> Tuple[str, str]:
        """
        Get formatted dump and CTU context for a source file.

        Args:
            source_file: Path to the source file (e.g., "src/example.c").
            target_line: Line number of the violation (for focused context).

        Returns:
            Tuple of (dump_context_str, ctu_context_str).
            Empty strings if files not found.
        """
        dump_context = ""
        ctu_context = ""

        dump_path = _find_dump_file(source_file)
        if dump_path:
            dump_data = parse_dump_file(dump_path, target_line)
            dump_context = format_dump_context(dump_data, target_line)

        ctu_path = _find_ctu_info_file(source_file)
        if ctu_path:
            ctu_data = parse_ctu_info_file(ctu_path)
            ctu_context = format_ctu_context(ctu_data)

        return dump_context, ctu_context