"""
And keyword check module for Gherkin linter.
"""

import re
from typing import List, Dict
from .base import GherkinCheckBase


class AndKeywordCheck(GherkinCheckBase):
    """Check for replacement of 'And' keyword with '*'."""

    @property
    def check_name(self) -> str:
        return "and_keyword"

    @property
    def check_description(self) -> str:
        return 'Checks that "And" is replaced with "*"'

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        """Check that 'And' is replaced with '*' at line start."""
        errors = []

        # Check if line starts with 'And' (after any indentation)
        if re.match(r"^\s*And\s", line):
            error = {"file": file_path, "line": line_num, "type": "AND_KEYWORD_ERROR", "message": 'Keyword "And" should be replaced with "*"'}
            errors.append(error)
            self.logger.debug(f"And-keyword error found: Line {line_num}")

        return errors
