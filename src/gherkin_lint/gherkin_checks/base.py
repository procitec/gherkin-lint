"""
Base class for all Gherkin linter checks.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging


class GherkinCheckBase(ABC):
    """Base class for all Gherkin linter check implementations."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    @abstractmethod
    def check(self, line: str, line_num: int, file_path: str, context: Dict) -> List[Dict]:
        """
        Check a line for linting errors.

        Args:
            line: The line to check
            line_num: The line number (1-indexed)
            file_path: The file path for error reporting
            context: Additional context information

        Returns:
            List of error dictionaries
        """
        pass

    @property
    @abstractmethod
    def check_name(self) -> str:
        """Return the name of this check."""
        pass

    @property
    @abstractmethod
    def check_description(self) -> str:
        """Return a description of what this check validates."""
        pass
