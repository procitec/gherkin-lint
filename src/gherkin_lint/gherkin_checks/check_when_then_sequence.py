"""
When-Then sequence check module for Gherkin linter.
"""

from typing import List, Dict
from .base import GherkinCheckBase


class WhenThenSequenceCheck(GherkinCheckBase):
    """Check that When steps are followed by Then steps."""

    def __init__(self, logger=None):
        super().__init__(logger)
        self.current_file = None
        self.lines: List[str] = []

    @property
    def check_name(self) -> str:
        return "when_then_sequence"

    @property
    def check_description(self) -> str:
        return "Checks that When steps are followed by Then steps"

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        # Collect lines for end-of-file analysis
        if file_path != self.current_file:
            self.current_file = file_path
            self.lines = []
        self.lines.append(line)
        return []

    def _is_when_block(self, start_index: int) -> tuple:
        """Check if When at start_index forms a block (has * continuations).
        Returns (is_block, end_index)"""
        i = start_index + 1
        has_star_continuation = False

        while i < len(self.lines):
            current = self.lines[i].strip()
            if not current or current.startswith("#"):
                i += 1
                continue
            elif current.startswith("* "):
                has_star_continuation = True
                i += 1
            else:
                break

        return has_star_continuation, i - 1

    def _has_blank_line_before(self, line_index: int) -> bool:
        """Check if there's a blank line before the given line index."""
        for i in range(line_index - 1, -1, -1):
            current = self.lines[i].strip()
            if current.startswith("#"):  # Skip comments
                continue
            elif not current:  # Found blank line
                return True
            else:  # Found non-blank, non-comment line
                return False
        return False

    def check_end_of_file(self, file_path: str) -> List[Dict]:
        errors: List[Dict] = []

        scenario_keywords = ["Scenario:", "Scenario Outline:", "Background:", "Rule:"]
        i = 0

        while i < len(self.lines):
            line = self.lines[i]
            stripped = line.strip()

            # Find start of scenario/background/rule block
            if any(stripped.startswith(kw) for kw in scenario_keywords):
                # Scan through the block to find steps
                i += 1

                while i < len(self.lines):
                    current = self.lines[i].strip()

                    # Stop at next scenario/background/rule or end
                    if any(current.startswith(kw) for kw in scenario_keywords):
                        break

                    # Skip empty lines and comments
                    if not current or current.startswith("#"):
                        i += 1
                        continue

                    # Check for When steps
                    if current.startswith("When "):
                        when_line = i + 1  # 1-based line numbers
                        is_block, block_end = self._is_when_block(i)

                        # Skip to after the When block
                        i = block_end + 1

                        # Look for Then after this When block
                        has_then = False
                        while i < len(self.lines):
                            next_line = self.lines[i].strip()

                            # Stop at scenario/background/rule keywords
                            if any(next_line.startswith(kw) for kw in scenario_keywords):
                                break

                            # Skip empty lines and comments
                            if not next_line or next_line.startswith("#"):
                                i += 1
                                continue

                            # Found Then
                            if next_line.startswith("Then "):
                                has_then = True
                                break

                            # Found another When - check if it's a new block
                            elif next_line.startswith("When "):
                                # If previous When was a block and current When is new block, allow it
                                if is_block and self._has_blank_line_before(i):
                                    break  # Allow this pattern
                                else:
                                    # Single When followed by another When - error
                                    break

                            # Found Given - resets the sequence
                            elif next_line.startswith("Given "):
                                break

                            # Other steps continue
                            elif any(next_line.startswith(kw + " ") for kw in ["And", "*"]):
                                i += 1
                                continue
                            else:
                                break

                        # Check if When needs Then
                        # Single When always needs Then
                        # Block When needs Then unless followed by another block When
                        needs_then = True
                        if is_block and i < len(self.lines):
                            next_non_empty = None
                            j = i
                            while j < len(self.lines):
                                temp = self.lines[j].strip()
                                if temp and not temp.startswith("#"):
                                    next_non_empty = temp
                                    break
                                j += 1

                            # Allow block When followed by another When if there's a blank line
                            if next_non_empty and next_non_empty.startswith("When ") and self._has_blank_line_before(j):
                                needs_then = False

                        if needs_then and not has_then:
                            errors.append(
                                {"file": file_path, "line": when_line, "type": "WHEN_THEN_SEQUENCE_ERROR", "message": "When step must be followed by Then step"}
                            )
                    else:
                        i += 1
            else:
                i += 1

        return errors
