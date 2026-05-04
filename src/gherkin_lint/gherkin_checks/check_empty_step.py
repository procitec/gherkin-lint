"""
Empty step check module for Gherkin linter.
"""

from typing import List, Dict
from .base import GherkinCheckBase


class EmptyStepCheck(GherkinCheckBase):
    """Check for Given/When/Then/step repeats with no text."""

    def __init__(self, logger=None):
        super().__init__(logger)

    @property
    def check_name(self) -> str:
        return "empty_step"

    @property
    def check_description(self) -> str:
        return "Checks for Given/When/Then/* steps without any text"

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        errors: List[Dict] = []
        stripped = line.strip()
        step_keywords = ["Given", "When", "Then", "And", "*"]
        for keyword in step_keywords:
            if stripped == keyword or (stripped.startswith(keyword + " ") and len(stripped) == len(keyword)):
                errors.append(
                    {
                        "file": file_path,
                        "line": line_num,
                        "type": "EMPTY_STEP_ERROR",
                        "message": f"Step '{keyword}' contains no text. Each step must contain a description or action.",
                    }
                )
                return errors
            if stripped.startswith(keyword + " "):
                # e.g. "Given " only whitespace after
                if not stripped[len(keyword) :].strip():
                    errors.append(
                        {
                            "file": file_path,
                            "line": line_num,
                            "type": "EMPTY_STEP_ERROR",
                            "message": f"Step '{keyword}' contains only whitespace. Each step must contain text.",
                        }
                    )
                    return errors
        return errors
