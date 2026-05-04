"""
Keyword description check module for Gherkin linter.
"""

from typing import List, Dict
from .base import GherkinCheckBase


class KeywordDescriptionCheck(GherkinCheckBase):
    """Check that keywords have proper description text after the colon."""

    def __init__(self, logger=None):
        super().__init__(logger)

    @property
    def check_name(self) -> str:
        return "keyword_description"

    @property
    def check_description(self) -> str:
        return "Checks that keywords have description text after the colon"

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        """Check that keywords have proper description text."""
        errors = []
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            return errors

        # Keywords that require description text
        keywords_requiring_description = ["Feature:", "Rule:", "Scenario:", "Scenario Outline:"]

        for keyword in keywords_requiring_description:
            if stripped.startswith(keyword):
                # Extract text after the keyword
                after_keyword = stripped[len(keyword) :]

                # Check if there's any text after the colon
                if not after_keyword:
                    # No text at all after colon
                    error = {
                        "file": file_path,
                        "line": line_num,
                        "type": "DESCRIPTION_ERROR",
                        "message": f"{keyword} must be followed by a space and description text",
                    }
                    errors.append(error)
                    self.logger.debug(f"Missing description: Line {line_num}, {keyword}")
                elif not after_keyword.startswith(" "):
                    # No space after colon
                    error = {
                        "file": file_path,
                        "line": line_num,
                        "type": "DESCRIPTION_ERROR",
                        "message": f"{keyword} must be followed by a space before description text",
                    }
                    errors.append(error)
                    self.logger.debug(f"Missing space after colon: Line {line_num}, {keyword}")
                elif after_keyword.strip() == "":
                    # Only whitespace after colon
                    error = {
                        "file": file_path,
                        "line": line_num,
                        "type": "DESCRIPTION_ERROR",
                        "message": f"{keyword} must have description text after the space",
                    }
                    errors.append(error)
                    self.logger.debug(f"Empty description: Line {line_num}, {keyword}")
                else:
                    # Check for proper format: space + non-empty text
                    description_text = after_keyword[1:].strip()  # Remove first space and trim
                    if not description_text:
                        error = {"file": file_path, "line": line_num, "type": "DESCRIPTION_ERROR", "message": f"{keyword} must have non-empty description text"}
                        errors.append(error)
                        self.logger.debug(f"Empty description text: Line {line_num}, {keyword}")

                # Only check the first matching keyword per line
                break

        return errors
