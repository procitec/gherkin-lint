"""
Free description block check module for Gherkin linter.
"""

import re
from typing import List, Dict
from .base import GherkinCheckBase


class FreeDescriptionCheck(GherkinCheckBase):
    """Check that free description blocks are surrounded by blank lines and properly indented."""

    def __init__(self, indent_size: int = 4, logger=None):
        super().__init__(logger)
        self.indent_size = indent_size
        self.current_file = None
        self.lines: List[str] = []

    @property
    def check_name(self) -> str:
        return "free_description"

    @property
    def check_description(self) -> str:
        return "Checks that free description blocks are surrounded by blank lines and properly indented"

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        if file_path != self.current_file:
            self.current_file = file_path
            self.lines = []
        self.lines.append(line)
        return []

    def check_end_of_file(self, file_path: str) -> List[Dict]:
        errors: List[Dict] = []
        keywords = ["Feature:", "Rule:", "Background:", "Scenario:", "Scenario Outline:"]
        kw_pattern = re.compile(rf"^(\s*)({'|'.join(keywords)})")
        i = 0
        while i < len(self.lines):
            line = self.lines[i]
            m = kw_pattern.match(line)
            if m:
                indent = len(m.group(1))
                key = m.group(2)

                # Look ahead for optional description block
                j = i + 1
                while j < len(self.lines) and self.lines[j].strip() == "":
                    j += 1

                if j < len(self.lines):
                    nxt = self.lines[j]
                    # Check if next non-blank line is actually a description
                    # (not a step, tag, or another keyword, and not a comment)
                    if not re.match(r"^\s*(Given|When|Then|And|\*|@)", nxt) and not kw_pattern.match(nxt) and not nxt.strip().startswith("#"):
                        # This IS a description block - apply description rules

                        # 1. Blank line before description
                        if j - 1 <= i or self.lines[j - 1].strip() != "":
                            errors.append(
                                {
                                    "file": file_path,
                                    "line": j + 1,
                                    "type": "FREE_DESCRIPTION_ERROR",
                                    "message": f"Blank line required before description of {key}",
                                }
                            )

                        # 2. Scan description lines for proper indentation
                        k = j
                        has_desc = False
                        while k < len(self.lines):
                            cur = self.lines[k]
                            if cur.strip() == "" or kw_pattern.match(cur) or re.match(r"^\s*(Given|When|Then|And|\*|@)", cur) or cur.strip().startswith("#"):
                                break
                            has_desc = True

                            # Determine expected indent:
                            # Feature: 0
                            # Rule description: indent_size
                            # Background/Scenario/Outline: keyword_indent + indent_size
                            if key == "Feature:":
                                expected_indent = 0
                            elif key == "Rule:":
                                expected_indent = self.indent_size
                            else:
                                expected_indent = indent + self.indent_size

                            actual_indent = len(cur) - len(cur.lstrip())
                            if actual_indent != expected_indent:
                                errors.append(
                                    {
                                        "file": file_path,
                                        "line": k + 1,
                                        "type": "FREE_DESCRIPTION_ERROR",
                                        "message": f"Description line must be indented {expected_indent} spaces to match {key}",
                                    }
                                )
                            k += 1

                        # 3. Blank line after description
                        if has_desc and (k >= len(self.lines) or self.lines[k].strip() != ""):
                            errors.append(
                                {
                                    "file": file_path,
                                    "line": k + 1,
                                    "type": "FREE_DESCRIPTION_ERROR",
                                    "message": f"Blank line required after description of {key}",
                                }
                            )

                        i = k
                        continue
                    # If no description follows keyword, no special rules apply
            i += 1
        return errors
