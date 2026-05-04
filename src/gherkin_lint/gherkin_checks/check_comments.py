"""
Comment spacing check module for Gherkin linter.
"""

from typing import List, Dict
from .base import GherkinCheckBase


class CommentSpacingCheck(GherkinCheckBase):
    """Check that comments (#) are followed by a space before text."""

    def __init__(self, logger=None):
        super().__init__(logger)

    @property
    def check_name(self) -> str:
        return "comment_spacing"

    @property
    def check_description(self) -> str:
        return "Checks that comments start with '#' optionally followed by space before text"

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        errors: List[Dict] = []
        stripped = line.lstrip()

        # Only pure comment lines
        if stripped.startswith("#"):
            # Remove leading spaces
            content = stripped[1:]
            # If there's text after #
            if content:
                # content starts with space then text: valid
                if not content.startswith(" "):
                    errors.append(
                        {
                            "file": file_path,
                            "line": line_num,
                            "type": "COMMENT_SPACING_ERROR",
                            "message": "Comments with text must start with '# ' (hash and space)",
                        }
                    )
            # If no content after '#', i.e. line is exactly '#', that's OK
        return errors
