"""
Feature keyword check module for Gherkin linter.
"""

from typing import List, Dict
from .base import GherkinCheckBase


class FeatureKeywordCheck(GherkinCheckBase):
    """Check that Feature keyword appears only once per file."""

    def __init__(self, logger=None):
        super().__init__(logger)
        self.feature_count = 0

    @property
    def check_name(self) -> str:
        return "feature_keyword"

    @property
    def check_description(self) -> str:
        return "Checks that Feature keyword appears only once per file"

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        """Check that Feature keyword appears only once."""
        errors = []
        stripped = line.strip()

        # Check if this is a new file (reset counter when line_num is 1)
        if line_num == 1:
            self.feature_count = 0

        # Check if line contains Feature keyword
        if stripped.startswith("Feature:"):
            self.feature_count += 1

            if self.feature_count > 1:
                error = {
                    "file": file_path,
                    "line": line_num,
                    "type": "FEATURE_KEYWORD_ERROR",
                    "message": f"Feature keyword can only appear once per file (occurrence #{self.feature_count})",
                }
                errors.append(error)
                self.logger.debug(f"Multiple Feature keywords found: Line {line_num}, occurrence #{self.feature_count}")

        return errors
