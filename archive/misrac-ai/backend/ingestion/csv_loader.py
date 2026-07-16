"""
CSV Report Loader

Loads MISRA C:2012 violation reports from CSV files in the report directory.
Each CSV corresponds to a source file analyzed by the MISRA checker.
"""

import csv
import os
from typing import List

from backend.utils.models import Violation


def load_csv_report(csv_path: str) -> List[Violation]:
    """
    Load a single CSV report file and return a list of Violations.
    
    Args:
        csv_path: Path to the CSV report file.
        
    Returns:
        List of Violation objects parsed from the CSV.
    """
    violations = []
    
    with open(csv_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            violation = Violation(
                file=row.get('File', row.get('file', '')),
                line=int(row.get('Line', row.get('line', 0))),
                column=int(row['Column']) if row.get('Column', row.get('column', '')) else None,
                rule_id=row.get('Rule ID', row.get('rule', '')),
                category=row.get('Rule Category', row.get('category', '')),
                description=row.get('Description', row.get('description', ''))
            )
            violations.append(violation)
    
    return violations


def load_all_reports(report_dir: str) -> List[Violation]:
    """
    Load all CSV reports from the report directory.
    
    Args:
        report_dir: Path to the directory containing CSV reports.
        
    Returns:
        List of all Violations from all CSV files.
    """
    all_violations = []
    
    if not os.path.exists(report_dir):
        print(f"Report directory '{report_dir}' not found.")
        return all_violations
    
    for filename in os.listdir(report_dir):
        if filename.endswith('.csv'):
            csv_path = os.path.join(report_dir, filename)
            violations = load_csv_report(csv_path)
            all_violations.extend(violations)
    
    return all_violations