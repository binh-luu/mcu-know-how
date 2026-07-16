"""
Violation Categorization

Categorizes and prioritizes MISRA violations for processing.
"""

from typing import Dict, List, Tuple

from backend.utils.models import Violation, RuleCategory


class ViolationCategorizer:
    """
    Categorizes violations by rule and priority.
    
    Groups violations by rule ID and assigns priority based on
    rule category (Mandatory > Required > Advisory).
    """

    # Priority mapping for rule categories
    PRIORITY_MAP = {
        'Mandatory': 1,   # Highest priority
        'Required': 2,
        'Advisory': 3,    # Lowest priority
    }

    def group_by_rule(self, violations: List[Violation]) -> Dict[str, List[Violation]]:
        """
        Group violations by their rule ID.
        
        Args:
            violations: List of violations to group.
            
        Returns:
            Dictionary mapping rule_id to list of violations.
        """
        grouped = {}
        for violation in violations:
            if violation.rule_id not in grouped:
                grouped[violation.rule_id] = []
            grouped[violation.rule_id].append(violation)
        return grouped

    def get_priority(self, category: str) -> int:
        """
        Get numeric priority for a category.
        
        Args:
            category: Rule category string.
            
        Returns:
            Priority number (lower = higher priority).
        """
        return self.PRIORITY_MAP.get(category, 99)

    def sort_by_priority(
        self, violations: List[Violation]
    ) -> List[Violation]:
        """
        Sort violations by priority (Mandatory first).
        
        Args:
            violations: List of violations to sort.
            
        Returns:
            Sorted list of violations.
        """
        return sorted(
            violations,
            key=lambda v: self.get_priority(v.category)
        )

    def get_processing_order(
        self, violations: List[Violation]
    ) -> List[Tuple[str, List[Violation]]]:
        """
        Get violations grouped by rule and sorted by priority.
        
        Args:
            violations: List of all violations.
            
        Returns:
            List of (rule_id, violations) tuples sorted by priority.
        """
        grouped = self.group_by_rule(violations)
        
        # Sort groups by highest priority violation in each group
        sorted_groups = sorted(
            grouped.items(),
            key=lambda item: min(
                self.get_priority(v.category) for v in item[1]
            )
        )
        
        return sorted_groups

    def get_summary(self, violations: List[Violation]) -> Dict:
        """
        Get a summary of violations by category and rule.
        
        Args:
            violations: List of violations.
            
        Returns:
            Dictionary with summary statistics.
        """
        summary = {
            'total': len(violations),
            'by_category': {},
            'by_rule': {},
            'by_file': {},
        }
        
        for v in violations:
            # By category
            cat = v.category
            summary['by_category'][cat] = summary['by_category'].get(cat, 0) + 1
            
            # By rule
            rule = v.rule_id
            summary['by_rule'][rule] = summary['by_rule'].get(rule, 0) + 1
            
            # By file
            file = v.file
            summary['by_file'][file] = summary['by_file'].get(file, 0) + 1
        
        return summary