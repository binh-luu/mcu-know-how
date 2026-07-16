"""
Tests for CSV Report Loader
"""

import os
import csv
import tempfile
import pytest

from backend.ingestion.csv_loader import load_csv_report, load_all_reports


def test_load_csv_report():
    """Test loading a single CSV report."""
    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['File', 'Line', 'Column', 'Rule ID', 'Rule Category', 'Description'])
        writer.writerow(['test.c', '42', '', '8.4', 'Mandatory', 'Test violation'])
        writer.writerow(['test.c', '55', '', '10.4', 'Mandatory', 'Another violation'])
        tmp_path = f.name
    
    try:
        violations = load_csv_report(tmp_path)
        
        assert len(violations) == 2
        assert violations[0].file == 'test.c'
        assert violations[0].line == 42
        assert violations[0].rule_id == '8.4'
        assert violations[0].category == 'Mandatory'
        assert violations[0].column is None
        
        assert violations[1].line == 55
        assert violations[1].rule_id == '10.4'
    finally:
        os.unlink(tmp_path)


def test_load_all_reports():
    """Test loading all reports from a directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test CSV files
        for i in range(2):
            csv_path = os.path.join(tmpdir, f'file{i}.csv')
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['File', 'Line', 'Column', 'Rule ID', 'Rule Category', 'Description'])
                writer.writerow([f'file{i}.c', '10', '', '8.4', 'Mandatory', f'Violation {i}'])
        
        violations = load_all_reports(tmpdir)
        
        assert len(violations) == 2


def test_load_all_reports_empty_dir():
    """Test loading from empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        violations = load_all_reports(tmpdir)
        assert len(violations) == 0


def test_load_all_reports_nonexistent_dir():
    """Test loading from non-existent directory."""
    violations = load_all_reports('/nonexistent/path')
    assert len(violations) == 0