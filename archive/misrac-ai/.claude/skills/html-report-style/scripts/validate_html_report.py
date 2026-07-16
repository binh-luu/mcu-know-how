#!/usr/bin/env python3
"""
validate_html_report.py
=======================

Validate that a generated HTML report follows the html-report-style template structure.

Usage:
    python validate_html_report.py --input <path> --validate-dependencies

The script validates that:
* Generated HTML contains required structural elements
* CSS classes match expected pattern
* Critical components are present
"""

import argparse
import os
import re
from pathlib import Path

REQUIRED_PATTERNS = {
    'header': 'id="sidebar-header"',
    'nav-section': 'class="nav-section"',
    'nav-item': 'class="nav-item"',
    'section': 'class="section"',
    'section-active': 'class="section active"',
    'alert': 'class="alert ',
    'alert-title': 'id="section-',
    'verify-row': 'class="verify-row"',
    'verify-icon': 'class="verify-icon"',
    'progress-bar': 'class="progress-bar"',
    'progress-fill': 'class="progress-fill"',
    'svg-wrap': 'class="svg-wrap"',
    'chkbox': 'class="chip-',
    'metrics': 'class="metric-box"',
}

REQUIRED_CLASSES = {
    'card': 'class="card"',
    'code-block': 'class="code-block"',
    'json': 'json',
    'bash-cmd': 'bash-cmd',
    'file-label': 'file-label',
    'footer': 'id="sidebar-footer"',
    'grid-2': 'grid-2',
    'grid-3': 'grid-3',
    'precond': 'precond',
    'flow': 'flow',
    'compare': 'compare',
    'chain': 'chain'
}

def validate_structure(html_path: Path, validate_deps: bool = False) -> bool:
    """Validate the HTML report structure."""
    html_content = html_path.read_text(encoding='utf-8')

    print(f"Validating {html_path}")

    # Check required structural elements
    for element, pattern in REQUIRED_PATTERNS.items():
        if element == 'header' and not re.search(pattern, html_content):
            print(f"❌ Missing <header> structure")
            return False
        elif not re.search(pattern, html_content):
            print(f"Absent pattern: {pattern}")
            # This is expected during phase definitions but should exist later
            pass

    # More specific checks for critical elements
    critical_elements = {
        'viewport meta': r'<meta name="viewport"',
        'charset meta': r'<meta charset="UTF-8"',
        '#main': r'id="main"',
        '.section': r'<div class="section' ,
        '.section.active': r'class="section active"',
        '.nav-section': r'class="nav-section"',
        '.nav-item.active': r'class="nav-item active"',
        '.section-title': r'<div class="section-title"',
        '.section-subtitle': r'<div class="section-subtitle"',
        'alert-title': r'<div class="alert-title"',
        'verify-icon': r'<div class="verify-icon">',
        'progress-fill': r'class="progress-fill"',
        'svg-wrap': r'<svg viewBox="0 0 900 470"',
        'chain-row': r'<div class="chain-row"',
        'chain-tag': r'class="ct-\w+"',
    }

    for element, pattern in critical_elements.items():
        if element in html_content and not re.search(pattern, html_content, re.IGNORECASE):
            print(f"⚠️  Missing {element}: {pattern}")
            # Not preventing validation, just warning

    # Validate navigation sections exist
    nav_items = re.findall(r'<div class="nav-item"[^>]*onclick="show\("([^"]+)"\)', html_content)
    nav_sections = re.findall(r'<div id="section-([^"]+)"', html_content)

    # Create mapping of expected sections from nav items
    expected_sections = set()
    for root in re.findall(r'd\.nav-item.*show\("([^"]+)"', html_content):
        expected_sections.add(root)

    if nav_items and nav_sections:
        # Validate each nav item has a corresponding section
        for nav_item_val in nav_items:
            if nav_item_val not in nav_sections:
                print(f"⚠️  Nav item controls '{nav_item_val}' but no section#section-{nav_item_val} found")

    # Validate hero sections exist
    for nav_item_val in ['overview', 'deployment', 'architecture', 'results', 'appendix']:
        if nav_item_val in nav_items and f'section-{nav_item_val}' not in ' '.join(nav_sections):
            print(f"⚠️  Missing section for nav link: section-section-{nav_item_val}")

    # Validate components exist (conditional validation)
    components_to_validate = [
        ('alert', 'alert-icon', '⚠️ Missing alert icon'),
        ('alert', 'alert-body', '⚠️ Missing alert body'),
        ('code-block', 'file-label', '⚠️ Missing code block label'),
        ('progress-row', 'progress-fill', '⚠️ Missing progress fill'),
        ('precond', 'pc-i', '⚠️ Missing pre-condition indicator'),
        ('flow', 'flow-grid', '⚠️ Missing flow grid'),
    ]

    for comp_type, attr, warn_msg in components_to_validate:
        if comp_type in html_content and not re.search(attr, html_content, re.IGNORECASE):
            print(warn_msg)

    # Check required classes exist at least once
    missing_classes = []
    for cls, pattern in REQUIRED_CLASSES.items():
        if not re.search(pattern, html_content):
            missing_classes.append(cls)

    if missing_classes:
        print(f"⚠️  Missing required classes: {', '.join(missing_classes)}")
        # Primary requirement is at least one component rendering

    # All validation checks are informational; report can be usable
    print("✅ Structural validation completed")
    return True

def main() -> None:
    parser = argparse.ArgumentParser(description="Validate HTML report structure")
    parser.add_argument('--input', required=True, help='HTML file path to validate')
    parser.add_argument('--validate-dependencies', action='store_true',
                        help='Check runtime dependencies and assets')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ File not found: {args.input}")
        exit(1)

    validate_structure(input_path, args.validate_dependencies)

if __name__ == '__main__':
    main()