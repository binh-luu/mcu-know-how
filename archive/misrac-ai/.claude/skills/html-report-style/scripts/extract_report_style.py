#!/usr/bin/env python3
"""
extract_report_style.py
=======================

Extract the <style>...</style> CSS block from a reference HTML report so the
`html-report-style` skill ships a stylesheet that is byte-for-byte identical to
the original MISRA_C_AI_Assistant.html look & feel.

Usage
-----
    python extract_report_style.py --source <reference.html> --output <reference-style.css>

If --source is omitted it searches the workspace for MISRA_C_AI_Assistant.html
(or any *.html file passed positionally). If --output is omitted it writes next
to this script into ../assets/reference-style.css.

Exit codes
----------
    0  success
    1  no <style> block found / source missing
"""

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(HERE, "..", "assets", "reference-style.css")


def find_reference_html():
    """Search a few likely locations for an HTML report to extract from."""
    candidates = [
        os.path.join(HERE, "..", "..", "MISRA_C_AI_Assistant.html"),
        os.path.join(HERE, "..", "assets", "reference-report.html"),
        os.path.join(HERE, "..", "..", "..", "MISRA_C_AI_Assistant.html"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return os.path.abspath(c)
    # Fallback: walk up three levels for the first *.html
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            if f.lower().endswith(".html"):
                return os.path.join(dirpath, f)
    return None


def extract_style(html_path):
    with open(html_path, "r", encoding="utf-8") as fh:
        content = fh.read()
    m = re.search(r"<style[^>]*>(.*?)</style>", content, re.DOTALL | re.IGNORECASE)
    if not m:
        raise RuntimeError(f"No <style> block found in {html_path}")
    return m.group(1).strip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Extract CSS from a reference HTML report.")
    parser.add_argument("--source", "-s", help="Path to the reference HTML file.")
    parser.add_argument("--output", "-o", help="Path to write the extracted CSS.")
    args = parser.parse_args(argv)

    source = args.source or find_reference_html()
    if not source or not os.path.isfile(source):
        print("ERROR: could not locate a source HTML file.", file=sys.stderr)
        return 1

    try:
        css = extract_style(source)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    output = os.path.abspath(args.output or DEFAULT_OUTPUT)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as fh:
        fh.write(css)

    print(f"Extracted {len(css)} chars of CSS")
    print(f"  source: {source}")
    print(f"  output: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
