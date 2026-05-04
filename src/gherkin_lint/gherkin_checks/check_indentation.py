"""
Indentation check module for Gherkin linter.
"""

from typing import List, Dict
from .base import GherkinCheckBase


class IndentationCheck(GherkinCheckBase):
    """Check for correct indentation of Gherkin keywords, steps, and comments."""

    def __init__(self, indent_size: int = 4, logger=None):
        super().__init__(logger)
        self.indent_size = indent_size

    @property
    def check_name(self) -> str:
        return "indentation"

    @property
    def check_description(self) -> str:
        return "Checks correct indentation of keywords, steps, and comments"

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        errors: List[Dict] = []
        stripped = line.strip()
        actual_indent = len(line) - len(line.lstrip())

        # 1. Check for tab characters in indentation
        if line.startswith("\t") or ("\t" in line[: len(line) - len(line.lstrip())]):
            return []  # Don't check further if tabs found, tabs are recognized in whitespace test

        # 0) Top-level comments (no indent) are always OK if actual_indent == 0
        if stripped.startswith("#") and actual_indent == 0:
            return []

        # 1) Feature, Rule: no indent
        if stripped.startswith("Feature:") or stripped.startswith("Rule:"):
            if actual_indent != 0:
                errors.append(
                    {"file": file_path, "line": line_num, "type": "INDENTATION_ERROR", "message": f"{stripped.split()[0]} should have no indentation"}
                )
            if stripped.startswith("Rule:"):
                context["in_rule"] = True
            return errors

        # 2) Background, Scenario, Scenario Outline
        for keyword in ("Background:", "Scenario:", "Scenario Outline:"):
            if stripped.startswith(keyword):
                expected = self.indent_size if context.get("in_rule") else 0
                if actual_indent != expected:
                    loc = "inside a Rule" if context.get("in_rule") else "outside a Rule"
                    errors.append(
                        {
                            "file": file_path,
                            "line": line_num,
                            "type": "INDENTATION_ERROR",
                            "message": f"{keyword} should be indented {expected} spaces {loc}, found {actual_indent}",
                        }
                    )
                return errors

        # 3) Steps and Examples
        if any(stripped.startswith(k + " ") or stripped == "Examples:" for k in ("Given", "When", "Then", "And", "*")):
            expected = self.indent_size * (2 if context.get("in_rule") else 1)
            if actual_indent != expected:
                errors.append(
                    {
                        "file": file_path,
                        "line": line_num,
                        "type": "INDENTATION_ERROR",
                        "message": f"Step/Examples should be indented {expected} spaces, found {actual_indent}",
                    }
                )
            return errors

        # 4) Comments: context-sensitive indentation
        if stripped.startswith("#"):
            # Check if we're inside an Examples table
            examples_indent = None
            all_lines = context.get("all_lines", [])

            # Look backwards to find Examples: keyword
            for j in range(line_num - 2, -1, -1):  # line_num is 1-based, convert to 0-based
                if j < len(all_lines):
                    prev_line = all_lines[j]
                    prev_stripped = prev_line.strip()

                    if prev_stripped.startswith("Examples:"):
                        examples_indent = len(prev_line) - len(prev_line.lstrip())
                        break
                    elif prev_stripped and not prev_stripped.startswith("#") and not prev_stripped.startswith("|") and not prev_stripped == "":
                        # Found non-comment, non-table, non-empty content - not in table
                        break

            if examples_indent is not None:
                # Inside Examples table - indent like table rows
                expected = examples_indent + self.indent_size
            else:
                # Regular comment - indent like steps
                expected = self.indent_size * (2 if context.get("in_rule") else 1)

            if actual_indent != expected:
                context_msg = "table row" if examples_indent is not None else "step"
                errors.append(
                    {
                        "file": file_path,
                        "line": line_num,
                        "type": "INDENTATION_ERROR",
                        "message": f"Comment should be indented {expected} spaces like {context_msg}, found {actual_indent}",
                    }
                )
            return errors

        return errors
