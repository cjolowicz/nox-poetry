"""Global configuration for pytest."""

from typing import List

from poetry.__version__ import __version__ as poetry_version


def pytest_report_header() -> List[str]:
    """Return a list of strings to be displayed in the header of the report."""
    return [f"poetry: {poetry_version}"]
