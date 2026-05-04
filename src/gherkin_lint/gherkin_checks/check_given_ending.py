"""
Given keyword ending check module for Gherkin linter.
"""

from typing import List, Dict
from .base import GherkinCheckBase


class GivenEndingCheck(GherkinCheckBase):
    """Check that scenarios don't end with Given steps - must be followed by When/Then."""

    def __init__(self, logger=None):
        super().__init__(logger)
        self.current_file = None
        self.lines: List[str] = []

    @property
    def check_name(self) -> str:
        return "given_ending"

    @property
    def check_description(self) -> str:
        return "Checks that scenarios (not backgrounds) don't end with Given steps without When/Then follow-up"

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        # Collect lines for end-of-file analysis
        if file_path != self.current_file:
            self.current_file = file_path
            self.lines = []
        self.lines.append(line)
        return []

    def check_end_of_file(self, file_path: str) -> List[Dict]:
        errors: List[Dict] = []

        # Only check scenarios and rules, NOT backgrounds
        scenario_keywords = ["Scenario:", "Scenario Outline:", "Rule:"]
        i = 0

        while i < len(self.lines):
            line = self.lines[i]
            stripped = line.strip()

            # Find start of scenario/rule block (excluding Background)
            current_keyword = None
            for kw in scenario_keywords:
                if stripped.startswith(kw):
                    current_keyword = kw
                    break

            if current_keyword:
                # block_start = i
                # Scan through the block to find steps
                i += 1
                last_given_line = None
                has_when_then_after_given = False

                while i < len(self.lines):
                    current = self.lines[i].strip()

                    # Stop at next scenario/background/rule or end
                    if any(current.startswith(kw) for kw in ["Scenario:", "Scenario Outline:", "Background:", "Rule:"]):
                        break

                    # Check for Given steps (including * continuations)
                    if current.startswith("Given "):
                        last_given_line = i + 1  # 1-based line numbers
                        has_when_then_after_given = False
                    elif current.startswith("* ") and last_given_line is not None:
                        # * after Given is still part of Given block
                        if not has_when_then_after_given:
                            last_given_line = i + 1
                    elif current.startswith("When ") or current.startswith("Then "):
                        if last_given_line is not None:
                            has_when_then_after_given = True
                    elif current.startswith("And "):
                        # And continues the previous step type, need to check context
                        # For simplicity, we'll treat And as neutral
                        pass

                    i += 1

                # If we found Given steps but no When/Then after them
                if last_given_line is not None and not has_when_then_after_given:
                    errors.append(
                        {
                            "file": file_path,
                            "line": last_given_line,
                            "type": "GIVEN_ENDING_ERROR",
                            "message": f"{current_keyword.rstrip(':')} cannot end with Given steps - must be followed by When or Then",
                        }
                    )
            else:
                i += 1

        return errors
