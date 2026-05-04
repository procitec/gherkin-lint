"""
Step block separation check module for Gherkin linter.
"""

import re
from typing import List, Dict
from .base import GherkinCheckBase


class StepBlockSeparationCheck(GherkinCheckBase):
    """Check that step blocks (Given/Then, When/Then) are separated by empty lines."""

    def __init__(self, logger=None):
        super().__init__(logger)
        self.current_file_path = None
        self.in_scenario = False
        self.last_then_line = None
        self.had_empty_line_after_then = False
        self.current_block_type = None  # Track current block: 'given', 'when', etc.

    @property
    def check_name(self) -> str:
        return "step_block_separation"

    @property
    def check_description(self) -> str:
        return "Checks that step blocks (Given/Then, When/Then) are separated by empty lines"

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        """Check step block separation rules."""
        errors = []
        stripped = line.strip()

        # Initialize for new file
        if file_path != self.current_file_path:
            self._reset_for_new_file()
            self.current_file_path = file_path

        # Track scenario context
        if stripped.startswith(("Scenario:", "Scenario Outline:")):
            self.in_scenario = True
            self.last_then_line = None
            self.had_empty_line_after_then = False
            self.current_block_type = None
        elif stripped.startswith(("Feature:", "Rule:", "Background:", "Examples:")):
            self.in_scenario = False
            self.last_then_line = None
            self.had_empty_line_after_then = False
            self.current_block_type = None

        # Skip if not in scenario
        if not self.in_scenario:
            return errors

        # Handle empty lines
        if not stripped or stripped.startswith("#"):
            if self.last_then_line is not None:
                self.had_empty_line_after_then = True
            return errors

        # Check for step keywords
        step_match = re.match(r"^\s*(Given|When|Then|And|\*)\s", line)
        if step_match:
            current_step = step_match.group(1)

            # Determine the actual step type (convert And/* to previous type)
            if current_step in ["And", "*"]:
                actual_step = self.current_block_type
            else:
                actual_step = current_step
                self.current_block_type = current_step

            # Check if this is a Then step
            if actual_step == "Then":
                self.last_then_line = line_num
                self.had_empty_line_after_then = False

            # Check if this starts a new block after a Then
            elif actual_step in ["Given", "When"] and self.last_then_line is not None:
                # We're starting a new Given/When block after a Then
                if not self.had_empty_line_after_then:
                    # Find the previous Then line for better error reporting
                    previous_then_line = self.last_then_line

                    error = {
                        "file": file_path,
                        "line": line_num,
                        "type": "STEP_BLOCK_SEPARATION_ERROR",
                        "message": f"Empty line required between {self._get_block_name_from_then()} block (ending line {previous_then_line}) and new {actual_step} block",
                    }
                    errors.append(error)
                    self.logger.debug(f"Missing separation between step blocks: Line {line_num}, previous Then at {previous_then_line}")

                # Reset tracking for the new block
                self.last_then_line = None
                self.had_empty_line_after_then = False
        else:
            # Non-step line (could be table data, doc strings, etc.)
            # Don't reset tracking as these belong to the current step
            pass

        return errors

    def _get_block_name_from_then(self) -> str:
        """Get a descriptive name for the block that just ended with Then."""
        if self.current_block_type == "Given":
            return "Given/Then"
        elif self.current_block_type == "When":
            return "When/Then"
        else:
            return "step"

    def _reset_for_new_file(self):
        """Reset state for a new file."""
        self.in_scenario = False
        self.last_then_line = None
        self.had_empty_line_after_then = False
        self.current_block_type = None
