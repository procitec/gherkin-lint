"""
Tag indentation check module for Gherkin linter.
"""

import re
from typing import List, Dict
from .base import GherkinCheckBase


class TagIndentationCheck(GherkinCheckBase):
    """Check for correct indentation of tags."""

    def __init__(self, indent_size: int = 4, logger=None):
        super().__init__(logger)
        self.indent_size = indent_size

    @property
    def check_name(self) -> str:
        return "tag_indentation"

    @property
    def check_description(self) -> str:
        return "Checks that tags have correct indentation matching their following element"

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        """Check tag indentation rules."""
        errors = []
        # stripped = line.strip()

        # Check if this line contains tags (starts with @)
        if not re.match(r"^\s*@", line):
            return errors

        # Get the next non-empty, non-comment, non-tag line from context
        next_keyword_line = context.get("next_keyword_line", "")
        next_keyword_stripped = next_keyword_line.strip() if next_keyword_line else ""

        # Skip if we don't have information about the next keyword
        if not next_keyword_stripped:
            return errors

        # Check if the next line is Background (tags not allowed)
        if next_keyword_stripped.startswith("Background:"):
            error = {"file": file_path, "line": line_num, "type": "TAG_ERROR", "message": "Tags are not allowed before Background"}
            errors.append(error)
            self.logger.debug(f"Tag before Background found: Line {line_num}")
            return errors

        # Determine expected indentation based on the following keyword
        expected_indent = self._get_expected_indent(next_keyword_stripped, context)

        # Get actual indentation of the tag line
        actual_indent = len(line) - len(line.lstrip())

        # Check if indentation matches
        if actual_indent != expected_indent:
            error = {
                "file": file_path,
                "line": line_num,
                "type": "TAG_INDENTATION_ERROR",
                "message": f"Tag should have {expected_indent} characters indentation to match following {next_keyword_stripped.split(':')[0]}, found: {actual_indent}",
            }
            errors.append(error)
            self.logger.debug(f"Tag indentation error: Line {line_num}, expected: {expected_indent}, found: {actual_indent}")

        return errors

    def _get_expected_indent(self, keyword_line: str, context: Dict) -> int:
        """Calculate expected indentation for tags based on the following keyword."""
        in_rule = context.get("in_rule", False)

        # Feature-level elements (no indentation)
        if keyword_line.startswith(("Feature:", "Rule:")):
            return 0

        # Scenario/Scenario Outline indentation depends on whether we're in a rule
        if keyword_line.startswith(("Scenario:", "Scenario Outline:")):
            return self.indent_size if in_rule else 0

        # Default: no indentation
        return 0
