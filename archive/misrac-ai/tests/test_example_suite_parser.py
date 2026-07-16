"""
Tests for Example Suite Parser
"""

import os
import tempfile
import pytest

from backend.ingestion.example_suite_parser import parse_example_suite, _parse_rule_id


def test_parse_rule_id():
    """Test parsing rule ID strings."""
    assert _parse_rule_id("8.4") == (8, 4)
    assert _parse_rule_id("10.12") == (10, 12)
    assert _parse_rule_id("invalid") == (None, None)


def test_parse_example_suite_basic():
    """Test parsing a minimal Example Suite."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a minimal rule file
        rule_content = """/*
 * R.8.4
 *
 * A compatible declaration shall be visible when an object or function with
 * external linkage is defined
 */

extern int count;
int count = 0;  /* Compliant */
"""
        rule_path = os.path.join(tmpdir, 'R_08_04.c')
        with open(rule_path, 'w') as f:
            f.write(rule_content)
        
        # Create common headers
        for header in ['mc3_header.h', 'mc3_types.h']:
            with open(os.path.join(tmpdir, header), 'w') as f:
                f.write("/* Common header */\n")
        
        rules = parse_example_suite(tmpdir)
        
        assert len(rules) == 1
        assert "8.4" in rules
        assert rules["8.4"].rule_id == "8.4"
        assert "R_08_04.c" in rules["8.4"].example_files


def test_parse_example_suite_nonexistent_dir():
    """Test parsing non-existent directory."""
    rules = parse_example_suite('/nonexistent/path')
    assert len(rules) == 0