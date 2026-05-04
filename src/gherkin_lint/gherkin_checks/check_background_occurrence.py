"""
Background occurrence and position check module for Gherkin linter.
"""

from typing import List, Dict
from .base import GherkinCheckBase


class BackgroundOccurrenceCheck(GherkinCheckBase):
    """Check that Background appears only once at feature level and in correct position."""

    def __init__(self, logger=None):
        super().__init__(logger)
        self.feature_level_background_count = 0
        self.feature_level_background_line = None
        self.feature_level_has_other_keywords = False

        # Rule-specific tracking
        self.current_rule_has_background = False
        self.current_rule_has_other_keywords = False
        self.current_rule_background_line = None

        # File state tracking
        self.current_file_path = None
        self.in_rule = False

    @property
    def check_name(self) -> str:
        return "background_occurrence"

    @property
    def check_description(self) -> str:
        return "Checks that Background appears only once at feature level and in correct position"

    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        """Check Background occurrence and position rules."""
        errors = []
        stripped = line.strip()

        # Check if this is a new file (reset counters)
        if file_path != self.current_file_path:
            self._reset_for_new_file()
            self.current_file_path = file_path

        # Update rule context
        if stripped.startswith("Rule:"):
            # Starting a new rule - reset rule-specific tracking
            self._reset_for_new_rule()
            self.in_rule = True
        elif stripped.startswith("Feature:"):
            self.in_rule = False

        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            return errors

        actual_indent = len(line) - len(line.lstrip())

        # Check if line contains Background keyword
        if stripped.startswith("Background:"):
            if actual_indent == 0:
                # Feature-level Background
                self.feature_level_background_count += 1
                self.feature_level_background_line = line_num

                # Check if this is not the first Background
                if self.feature_level_background_count > 1:
                    error = {
                        "file": file_path,
                        "line": line_num,
                        "type": "BACKGROUND_OCCURRENCE_ERROR",
                        "message": f"Background can only appear once at feature-level (occurrence #{self.feature_level_background_count})",
                    }
                    errors.append(error)
                    self.logger.debug(f"Multiple feature-level Backgrounds found: Line {line_num}")

                # Check if Background appears after other keywords at feature level
                if self.feature_level_has_other_keywords:
                    error = {
                        "file": file_path,
                        "line": line_num,
                        "type": "BACKGROUND_POSITION_ERROR",
                        "message": "Feature-level Background must appear before any Scenarios",
                    }
                    errors.append(error)
                    self.logger.debug(f"Feature-level Background after other keywords: Line {line_num}")

            else:
                # Rule-level Background (indented)
                if self.in_rule:
                    self.current_rule_has_background = True
                    self.current_rule_background_line = line_num

                    # Check if Background appears after other keywords in this rule
                    if self.current_rule_has_other_keywords:
                        error = {
                            "file": file_path,
                            "line": line_num,
                            "type": "BACKGROUND_POSITION_ERROR",
                            "message": "Rule-level Background must appear before any Scenarios in the rule",
                        }
                        errors.append(error)
                        self.logger.debug(f"Rule-level Background after other keywords: Line {line_num}")

        # Track other keywords that should come after Background
        elif stripped.startswith(("Scenario:", "Scenario Outline:")):
            if actual_indent == 0:
                # Feature-level Scenario
                self.feature_level_has_other_keywords = True
            elif self.in_rule:
                # Rule-level Scenario
                self.current_rule_has_other_keywords = True

        return errors

    def _reset_for_new_file(self):
        """Reset all counters for a new file."""
        self.feature_level_background_count = 0
        self.feature_level_background_line = None
        self.feature_level_has_other_keywords = False
        self.in_rule = False
        self._reset_for_new_rule()

    def _reset_for_new_rule(self):
        """Reset rule-specific counters."""
        self.current_rule_has_background = False
        self.current_rule_has_other_keywords = False
        self.current_rule_background_line = None
