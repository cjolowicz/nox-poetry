"""Unit tests for the poetry module."""
from pathlib import Path

from nox_poetry import poetry


def test_config_non_ascii(tmp_path: Path) -> None:
    """It decodes non-ASCII characters in pyproject.toml."""
    text = """\
[tool.poetry]
name = "África"
"""

    path = tmp_path / "pyproject.toml"
    path.write_text(text, encoding="utf-8")

    config = poetry.Config(path.parent)
    assert config.name == "África"
