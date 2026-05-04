"""
Step separation check module for Gherkin linter.
"""

import re
from typing import List, Dict
from .base import GherkinCheckBase


class StepSeparationCheck(GherkinCheckBase):
    """Check for proper separation between step blocks."""

    @property
    def check_name(self) -> str:
        return "step_separation"

    @property
    def check_description(self) -> str:
        return "Checks for proper separation between When..Then and Given..Then blocks"

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        """Check for proper separation between When..Then and Given..Then blocks."""
        errors = []
        stripped = line.strip()
        previous_step_type = context.get("previous_step_type")
        previous_line_empty = context.get("previous_line_empty", False)

        # Check if current line starts with When or Given
        current_step_match = re.match(r"^\s*(When|Given)", stripped)
        if not current_step_match:
            return errors

        current_step = current_step_match.group(1)

        # If we had a previous Then and now we have When/Given, check for separation
        if previous_step_type == "Then" and current_step in ["When", "Given"] and not previous_line_empty:
            error = {
                "file": file_path,
                "line": line_num,
                "type": "SEPARATION_ERROR",
                "message": f"{current_step} block should be separated from previous Then block by empty line",
            }
            errors.append(error)
            self.logger.debug(f"Separation error found: Line {line_num}, {current_step} after Then without empty line")

        return errors
