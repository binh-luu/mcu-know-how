"""
Tests for Code Context Extractor
"""

import os
import tempfile
import pytest

from backend.utils.models import Violation
from backend.analysis.context_extractor import CodeContextExtractor


@pytest.fixture
def sample_source_file(tmp_path):
    """Create a sample C source file."""
    content = """#include <stdio.h>

int global_var = 0;

void function_one(void)
{
    int a = 10;
    int b = 20;
    int c = a + b;  /* Line 10 - violation here */
    printf("%d\\n", c);
}

void function_two(void)
{
    int x = 100;
    int y = 200;
    int z = x + y;  /* Line 18 - violation here */
}

int main(void)
{
    function_one();
    function_two();
    return 0;
}
"""
    filepath = tmp_path / "test.c"
    filepath.write_text(content)
    return str(tmp_path), content


def test_extract_context(sample_source_file):
    """Test extracting code context for a violation."""
    src_dir, _ = sample_source_file
    
    extractor = CodeContextExtractor(src_dir=src_dir)
    violation = Violation('test.c', 10, None, '8.4', 'Mandatory', 'Test violation')
    
    context = extractor.extract(violation)
    
    assert context is not None
    assert context.file_path == os.path.join(src_dir, 'test.c')
    assert context.line_number == 10
    assert 'a + b' in context.surrounding_lines
    assert 'function_one' in context.function_scope


def test_extract_nonexistent_file():
    """Test extracting from non-existent file."""
    extractor = CodeContextExtractor(src_dir='/nonexistent')
    violation = Violation('test.c', 10, None, '8.4', 'Mandatory', 'Test')
    
    context = extractor.extract(violation)
    assert context is None


def test_extract_function_scope(sample_source_file):
    """Test extracting function scope."""
    src_dir, _ = sample_source_file
    
    extractor = CodeContextExtractor(src_dir=src_dir)
    violation = Violation('test.c', 10, None, '8.4', 'Mandatory', 'Test')
    
    context = extractor.extract(violation)
    
    assert 'function_one' in context.function_scope
    assert 'function_two' not in context.function_scope