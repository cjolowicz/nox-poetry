"""Global configuration for pytest."""

from importlib.metadata import version
from typing import List


def pytest_report_header() -> List[str]:
    """Return a list of strings to be displayed in the header of the report."""
    return [
        f"poetry: {version('poetry')}",
        f"poetry-plugin-export: {version('poetry-plugin-export')}",
    ]
