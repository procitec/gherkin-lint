"""
Step keyword repetition check module for Gherkin linter.
"""

from typing import List, Dict
from .base import GherkinCheckBase


class StepKeywordRepetitionCheck(GherkinCheckBase):
    """Check for repeated step keywords that should use '*' instead."""

    def __init__(self, logger=None):
        super().__init__(logger)
        self.previous_step_keyword = None
        self.current_file = None
        self.last_blank_line = None
        self.last_step_line = None

    @property
    def check_name(self) -> str:
        return "step_keyword_repetition"

    @property
    def check_description(self) -> str:
        return "Checks for repeated step keywords that should use '*' instead"

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        errors: List[Dict] = []

        # Reset for new file
        if file_path != self.current_file:
            self.current_file = file_path
            self.previous_step_keyword = None
            self.last_blank_line = None
            self.last_step_line = None

        stripped = line.strip()

        # Track blank lines
        if not stripped:
            self.last_blank_line = line_num
            return errors

        # Skip comments
        if stripped.startswith("#"):
            return errors

        # Check for step keywords
        step_keywords = ["Given", "When", "Then", "And", "*"]
        current_keyword = None

        for keyword in step_keywords:
            if stripped.startswith(keyword + " "):
                current_keyword = keyword
                break

        # If current line is a step
        if current_keyword:
            # Skip And and * keywords from the check
            if current_keyword not in ["And", "*"]:
                # Check if there was a blank line between the last step and this one
                blank_line_between = self.last_step_line and self.last_blank_line and self.last_step_line < self.last_blank_line < line_num

                # If same keyword as previous step AND no blank line between them
                if self.previous_step_keyword and current_keyword == self.previous_step_keyword and not blank_line_between:
                    errors.append(
                        {
                            "file": file_path,
                            "line": line_num,
                            "type": "STEP_KEYWORD_REPETITION_WARNING",
                            "message": f"Repeated '{current_keyword}' keyword should be replaced with '*'",
                        }
                    )

                # Update previous keyword and last step line
                self.previous_step_keyword = current_keyword
                self.last_step_line = line_num
        else:
            # Only reset on scenario/background/feature/rule keywords
            reset_keywords = ["Scenario:", "Scenario Outline:", "Background:", "Feature:", "Rule:", "Examples:"]
            if any(stripped.startswith(kw) for kw in reset_keywords):
                self.previous_step_keyword = None
                self.last_blank_line = None
                self.last_step_line = None

        return errors
