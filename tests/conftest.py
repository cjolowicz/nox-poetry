"""Global configuration for pytest."""

from importlib.metadata import version


def pytest_report_header() -> list[str]:
    """Return a list of strings to be displayed in the header of the report."""
    return [
        f"poetry: {version('poetry')}",
        f"poetry-plugin-export: {version('poetry-plugin-export')}",
    ]
