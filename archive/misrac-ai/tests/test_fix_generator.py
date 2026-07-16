"""
Tests for Fix Generator (mocked LLM)
"""

import pytest
from unittest.mock import MagicMock, patch
import json

from backend.utils.models import Violation, CodeContext, Fix
from backend.fix_generation.fix_generator import FixGenerator


@pytest.fixture
def mock_openai_client():
    """Create a mocked OpenAI client."""
    client = MagicMock()
    
    # Mock chat completions
    completion = MagicMock()
    completion.choices[0].message.content = json.dumps({
        "description": "Test fix description",
        "original_code": "int x = 10;",
        "fixed_code": "int16_t x = 10;"
    })
    client.chat.completions.create.return_value = completion
    
    return client


def test_generate_fix(mock_openai_client):
    """Test generating a fix."""
    generator = FixGenerator(openai_client=mock_openai_client)
    
    violation = Violation('test.c', 10, None, '8.4', 'Mandatory', 'Test violation')
    context = CodeContext(
        file_path='src/test.c',
        line_number=10,
        surrounding_lines='int x = 10;',
        function_scope='void func() { int x = 10; }'
    )
    
    fix = generator.generate_fix(
        violation=violation,
        code_context=context,
        rag_context="Rule 8.4 context"
    )
    
    assert isinstance(fix, Fix)
    assert fix.description == "Test fix description"
    assert fix.original_code == "int x = 10;"
    assert fix.fixed_code == "int16_t x = 10;"


def test_generate_git_patch():
    """Test generating git patch."""
    violation = Violation('test.c', 10, None, '8.4', 'Mandatory', 'Test')
    fix = Fix(
        violation=violation,
        description="Test fix",
        original_code="int x = 10;",
        fixed_code="int16_t x = 10;"
    )
    
    # Use mocked client to avoid needing API key
    mock_client = MagicMock()
    generator = FixGenerator(openai_client=mock_client)
    patch_str = generator.generate_git_patch(fix)
    
    assert '---' in patch_str
    assert '+++' in patch_str
    assert 'test.c' in patch_str