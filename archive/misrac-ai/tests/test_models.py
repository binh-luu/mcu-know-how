"""
Tests for Data Models
"""

import pytest

from backend.utils.models import (
    Violation, Rule, CodeContext, Fix, RuleGroupFix, RuleType, RuleCategory
)


def test_violation_model():
    """Test Violation data model."""
    v = Violation(
        file='test.c',
        line=42,
        column=None,
        rule_id='8.4',
        category='Mandatory',
        description='Test violation'
    )
    
    assert v.file == 'test.c'
    assert v.line == 42
    assert v.column is None
    assert v.rule_id == '8.4'
    assert v.category == 'Mandatory'


def test_rule_model():
    """Test Rule data model."""
    r = Rule(
        rule_id='8.4',
        rule_type=RuleType.RULE,
        category='Mandatory',
        description='Test rule',
        example_files=['R_08_04.c'],
        example_content='/* test */'
    )
    
    assert r.rule_id == '8.4'
    assert r.rule_type == RuleType.RULE
    assert 'R_08_04.c' in r.example_files


def test_code_context_model():
    """Test CodeContext data model."""
    ctx = CodeContext(
        file_path='src/test.c',
        line_number=42,
        surrounding_lines='int x = 10;',
        function_scope='void func() { int x = 10; }'
    )
    
    assert ctx.file_path == 'src/test.c'
    assert ctx.line_number == 42


def test_fix_model():
    """Test Fix data model."""
    v = Violation('test.c', 42, None, '8.4', 'Mandatory', 'Test')
    f = Fix(
        violation=v,
        description='Test fix',
        original_code='int x = 10;',
        fixed_code='int16_t x = 10;'
    )
    
    assert f.violation == v
    assert f.description == 'Test fix'
    assert f.git_patch == ""
    assert f.self_review == ""


def test_rule_group_fix_model():
    """Test RuleGroupFix data model."""
    v = Violation('test.c', 42, None, '8.4', 'Mandatory', 'Test')
    f = Fix(v, 'Test fix', 'int x;', 'int16_t x;')
    
    rgf = RuleGroupFix(
        rule_id='8.4',
        fixes=[f]
    )
    
    assert rgf.rule_id == '8.4'
    assert len(rgf.fixes) == 1


def test_enum_values():
    """Test enum values."""
    assert RuleType.RULE.value == "Rule"
    assert RuleType.DIRECTIVE.value == "Directive"
    assert RuleCategory.REQUIRED.value == "Required"
    assert RuleCategory.ADVISORY.value == "Advisory"
    assert RuleCategory.MANDATORY.value == "Mandatory"