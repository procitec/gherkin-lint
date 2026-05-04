"""
Scenario Outline Examples check module for Gherkin linter.
"""

from typing import List, Dict
from .base import GherkinCheckBase


class ScenarioOutlineExamplesCheck(GherkinCheckBase):
    """Check that Scenario Outline has Examples with proper formatting."""

    def __init__(self, indent_size: int = 4, logger=None):
        super().__init__(logger)
        self.indent_size = indent_size
        self.current_file = None
        self.lines: List[str] = []

    @property
    def check_name(self) -> str:
        return "scenario_outline_examples"

    @property
    def check_description(self) -> str:
        return "Checks that Scenario Outline has properly formatted Examples section"

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        # Collect lines for end-of-file analysis
        if file_path != self.current_file:
            self.current_file = file_path
            self.lines = []
        self.lines.append(line)
        return []

    def _has_blank_line_between(self, start_index: int, end_index: int) -> bool:
        """Check if there's at least one blank line between start_index and end_index."""
        for i in range(start_index + 1, end_index):
            if self.lines[i].strip() == "":
                return True
        return False

    def check_end_of_file(self, file_path: str) -> List[Dict]:
        errors: List[Dict] = []

        block_keywords = ["Scenario:", "Scenario Outline:", "Background:", "Rule:", "Feature:"]
        i = 0

        while i < len(self.lines):
            line = self.lines[i]
            stripped = line.strip()

            # Find Scenario Outline
            if stripped.startswith("Scenario Outline:"):
                outline_line = i + 1  # 1-based line number
                # outline_indent = len(line) - len(line.lstrip())
                i += 1

                # Scan through the scenario outline block
                last_step_line_index = None
                has_examples = False
                examples_line = None
                examples_line_index = None
                examples_indent = None

                while i < len(self.lines):
                    current_line = self.lines[i]
                    current = current_line.strip()

                    # Stop at next block keyword
                    if any(current.startswith(kw) for kw in block_keywords):
                        break

                    # Skip empty lines and comments for step tracking
                    if not current or current.startswith("#"):
                        i += 1
                        continue

                    # Check for step keywords
                    if any(current.startswith(kw + " ") for kw in ["Given", "When", "Then", "And", "*"]):
                        last_step_line_index = i  # 0-based for internal use
                        i += 1
                        continue

                    elif current.startswith("Examples:"):
                        has_examples = True
                        examples_line = i + 1  # 1-based line number
                        examples_line_index = i  # 0-based for internal use
                        examples_indent = len(current_line) - len(current_line.lstrip())

                        # Check for blank line between last step and Examples
                        if last_step_line_index is not None and not self._has_blank_line_between(last_step_line_index, examples_line_index):
                            errors.append(
                                {
                                    "file": file_path,
                                    "line": examples_line,
                                    "type": "SCENARIO_OUTLINE_EXAMPLES_ERROR",
                                    "message": "Examples must be separated from steps by a blank line",
                                }
                            )

                        # Check Examples content
                        i += 1
                        table_started = False
                        first_table_line_index = None

                        # Find first table line and check for blank line between Examples and table
                        j = i
                        while j < len(self.lines):
                            check_line = self.lines[j]
                            check_current = check_line.strip()

                            # Stop at next block keyword
                            if any(check_current.startswith(kw) for kw in block_keywords):
                                break

                            # Skip comments - they don't count as content
                            if check_current.startswith("#"):
                                j += 1
                                continue

                            # Found first table line
                            if check_current.startswith("|"):
                                first_table_line_index = j

                                # Check if there's a blank line between Examples: and first table row
                                if self._has_blank_line_between(examples_line_index, first_table_line_index):
                                    errors.append(
                                        {
                                            "file": file_path,
                                            "line": j + 1,
                                            "type": "SCENARIO_OUTLINE_EXAMPLES_ERROR",
                                            "message": "No blank line allowed between Examples and table rows",
                                        }
                                    )
                                break

                            # Found non-empty, non-comment, non-table line
                            if check_current:
                                errors.append(
                                    {
                                        "file": file_path,
                                        "line": j + 1,
                                        "type": "SCENARIO_OUTLINE_EXAMPLES_ERROR",
                                        "message": "Examples section must contain table rows starting with '|'",
                                    }
                                )
                                break

                            j += 1

                        # Now process the actual table content
                        while i < len(self.lines):
                            table_line = self.lines[i]
                            table_current = table_line.strip()

                            # Stop at next block keyword
                            if any(table_current.startswith(kw) for kw in block_keywords):
                                break

                            # Skip completely empty lines
                            if not table_current:
                                i += 1
                                continue

                            # Skip comments - they are ignored and don't get validated
                            if table_current.startswith("#"):
                                i += 1
                                continue

                            # Check table rows (only non-comment lines)
                            if table_current.startswith("|"):
                                table_started = True
                                # Check indentation of table rows
                                table_indent = len(table_line) - len(table_line.lstrip())
                                expected_table_indent = examples_indent + self.indent_size

                                if table_indent != expected_table_indent:
                                    errors.append(
                                        {
                                            "file": file_path,
                                            "line": i + 1,
                                            "type": "SCENARIO_OUTLINE_EXAMPLES_ERROR",
                                            "message": f"Examples table row must be indented {expected_table_indent} spaces, found {table_indent}",
                                        }
                                    )
                            else:
                                # Non-table, non-empty, non-comment line after Examples
                                if table_started:
                                    # We've seen table rows, so this is the end of Examples
                                    break
                                else:
                                    # No table rows yet, this is an error
                                    errors.append(
                                        {
                                            "file": file_path,
                                            "line": i + 1,
                                            "type": "SCENARIO_OUTLINE_EXAMPLES_ERROR",
                                            "message": "Examples section must contain table rows starting with '|'",
                                        }
                                    )

                            i += 1

                        # Check if Examples had any table rows (ignoring comments)
                        if not table_started:
                            errors.append(
                                {
                                    "file": file_path,
                                    "line": examples_line,
                                    "type": "SCENARIO_OUTLINE_EXAMPLES_ERROR",
                                    "message": "Examples section must contain table rows starting with '|'",
                                }
                            )

                        break  # Break out of scenario processing
                    else:
                        # This could be a description line or other content - skip it
                        i += 1
                        continue

                # Check if Scenario Outline is missing Examples
                if not has_examples:
                    errors.append(
                        {
                            "file": file_path,
                            "line": outline_line,
                            "type": "SCENARIO_OUTLINE_EXAMPLES_ERROR",
                            "message": "Scenario Outline must have Examples section",
                        }
                    )
            else:
                i += 1

        return errors
