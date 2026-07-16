"""
Tests for Violation Categorizer
"""

import pytest

from backend.utils.models import Violation
from backend.analysis.categorizer import ViolationCategorizer


@pytest.fixture
def sample_violations():
    """Create sample violations for testing."""
    return [
        Violation('test.c', 10, None, '8.4', 'Mandatory', 'Violation 1'),
        Violation('test.c', 20, None, '8.4', 'Mandatory', 'Violation 2'),
        Violation('test.c', 30, None, '10.4', 'Advisory', 'Violation 3'),
        Violation('other.c', 40, None, '15.3', 'Required', 'Violation 4'),
    ]


def test_group_by_rule(sample_violations):
    """Test grouping violations by rule."""
    categorizer = ViolationCategorizer()
    grouped = categorizer.group_by_rule(sample_violations)
    
    assert len(grouped) == 3
    assert len(grouped['8.4']) == 2
    assert len(grouped['10.4']) == 1
    assert len(grouped['15.3']) == 1


def test_get_priority():
    """Test priority assignment."""
    categorizer = ViolationCategorizer()
    
    assert categorizer.get_priority('Mandatory') == 1
    assert categorizer.get_priority('Required') == 2
    assert categorizer.get_priority('Advisory') == 3
    assert categorizer.get_priority('Unknown') == 99


def test_sort_by_priority(sample_violations):
    """Test sorting violations by priority."""
    categorizer = ViolationCategorizer()
    sorted_violations = categorizer.sort_by_priority(sample_violations)
    
    # Mandatory violations should come first
    assert sorted_violations[0].category == 'Mandatory'
    assert sorted_violations[1].category == 'Mandatory'


def test_get_processing_order(sample_violations):
    """Test getting processing order."""
    categorizer = ViolationCategorizer()
    order = categorizer.get_processing_order(sample_violations)
    
    # Should be sorted by priority (Mandatory first)
    assert order[0][0] in ['8.4']  # Mandatory rules first


def test_get_summary(sample_violations):
    """Test getting violation summary."""
    categorizer = ViolationCategorizer()
    summary = categorizer.get_summary(sample_violations)
    
    assert summary['total'] == 4
    assert summary['by_category']['Mandatory'] == 2
    assert summary['by_category']['Advisory'] == 1
    assert summary['by_category']['Required'] == 1
    assert summary['by_file']['test.c'] == 3
    assert summary['by_file']['other.c'] == 1