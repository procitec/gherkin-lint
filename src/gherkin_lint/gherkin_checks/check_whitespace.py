"""
Whitespace and line ending check module for Gherkin linter.
"""

from typing import List, Dict
from .base import GherkinCheckBase


class WhitespaceCheck(GherkinCheckBase):
    """Check for correct whitespace and line ending usage."""

    def __init__(self, logger=None):
        super().__init__(logger)
        self.line_ending_type = None  # Will be determined from first line
        self.file_lines = []  # Store all lines for end-of-file checks
        self.current_file_path = None

    @property
    def check_name(self) -> str:
        return "whitespace"

    @property
    def check_description(self) -> str:
        return "Checks for correct whitespace usage and line endings"

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        """Check whitespace and line ending rules."""
        errors = []

        # Initialize for new file
        if file_path != self.current_file_path:
            self.current_file_path = file_path
            self.line_ending_type = None
            self.file_lines = []

        # Store line for end-of-file analysis
        self.file_lines.append(line)

        # 1. Check for tabs (should be spaces only)
        if "\t" in line:
            # Find all tab positions
            tab_positions = [i for i, char in enumerate(line) if char == "\t"]
            for pos in tab_positions:
                error = {
                    "file": file_path,
                    "line": line_num,
                    "type": "WHITESPACE_ERROR",
                    "message": f"Tab character found at position {pos + 1}, use spaces instead",
                }
                errors.append(error)
                self.logger.debug(f"Tab character found: Line {line_num}, position {pos + 1}")

        # 2. Check for trailing whitespace (but not on empty lines)
        if line.rstrip("\r\n") != line.rstrip():
            trailing_spaces = len(line.rstrip("\r\n")) - len(line.rstrip())
            error = {
                "file": file_path,
                "line": line_num,
                "type": "WHITESPACE_ERROR",
                "message": f"Trailing whitespace found ({trailing_spaces} character{'s' if trailing_spaces > 1 else ''})",
            }
            errors.append(error)
            self.logger.debug(f"Trailing whitespace found: Line {line_num}, {trailing_spaces} characters")

        # 3. Determine and check line ending consistency
        line_ending = self._get_line_ending(line)
        if line_ending:
            if self.line_ending_type is None:
                self.line_ending_type = line_ending
                self.logger.debug(f"Detected line ending type: {repr(self.line_ending_type)}")
            elif self.line_ending_type != line_ending:
                error = {
                    "file": file_path,
                    "line": line_num,
                    "type": "LINE_ENDING_ERROR",
                    "message": f"Inconsistent line ending: expected {repr(self.line_ending_type)}, found {repr(line_ending)}",
                }
                errors.append(error)
                self.logger.debug(f"Inconsistent line ending: Line {line_num}, expected {repr(self.line_ending_type)}, found {repr(line_ending)}")

        return errors

    def check_end_of_file(self, file_path: str) -> List[Dict]:
        """Check end-of-file requirements. Call this after processing all lines."""
        errors = []

        if not self.file_lines:
            return errors

        # Check if file ends with newline and count trailing empty lines
        last_line = self.file_lines[-1]

        # 1. Check if file ends with newline
        if not last_line.endswith(("\n", "\r\n")):
            error = {"file": file_path, "line": len(self.file_lines), "type": "EOF_ERROR", "message": "File should end with a newline character"}
            errors.append(error)
            self.logger.debug(f"Missing final newline in file: {file_path}")
            return errors  # If no newline, don't check for multiple empty lines

        # 2. Check for multiple trailing empty lines
        # Count empty lines from the end (excluding the very last line which should have content)
        trailing_empty_count = 0
        for i in range(len(self.file_lines) - 1, -1, -1):
            line_content = self.file_lines[i].rstrip("\r\n")
            if line_content.strip() == "":  # Empty or whitespace-only line
                trailing_empty_count += 1
            else:
                break

        # If the last line is just a newline (empty content), that's the expected single newline
        # But if there are more than 1 trailing empty lines, that's an error
        if trailing_empty_count > 1:
            # Find the line number where excess empty lines start
            first_excess_line = len(self.file_lines) - trailing_empty_count + 2  # +2 because we allow one empty line

            error = {
                "file": file_path,
                "line": first_excess_line,
                "type": "EOF_ERROR",
                "message": f"Too many empty lines at end of file ({trailing_empty_count} found, max 1 allowed)",
            }
            errors.append(error)
            self.logger.debug(f"Multiple trailing empty lines in file: {file_path}, found {trailing_empty_count}")

        return errors

    def _get_line_ending(self, line: str) -> str:
        """Determine the line ending type of a line."""
        if line.endswith("\r\n"):
            return "\r\n"  # Windows
        elif line.endswith("\n"):
            return "\n"  # Unix
        elif line.endswith("\r"):
            return "\r"  # Mac (legacy)
        else:
            return ""  # No line ending (probably last line)

    def reset_for_new_file(self):
        """Reset state for a new file."""
        self.line_ending_type = None
        self.file_lines = []
        self.current_file_path = None
