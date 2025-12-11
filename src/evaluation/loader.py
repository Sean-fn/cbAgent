"""
Test case loader for evaluation system
Loads test cases from JSON files
"""

import json
from pathlib import Path
from src.evaluation.models import TestSuite


class TestCaseLoader:
    """Loads test cases from JSON file"""

    @staticmethod
    async def load_from_file(file_path: Path) -> TestSuite:
        """
        Load test cases from JSON file

        Args:
            file_path: Path to JSON file containing test cases

        Returns:
            TestSuite with loaded test cases

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
            ValidationError: If data doesn't match schema
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return TestSuite(**data)

    @staticmethod
    async def load_from_dict(data: dict) -> TestSuite:
        """
        Load test cases from dictionary (useful for testing)

        Args:
            data: Dictionary containing test cases

        Returns:
            TestSuite with loaded test cases
        """
        return TestSuite(**data)
