"""Unit tests for the poetry module."""
from pathlib import Path
from typing import Any
from typing import Dict

import nox._options
import nox.command
import nox.manifest
import nox.sessions
import pytest

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


def test_config_dependency_groups(tmp_path: Path) -> None:
    """It returns the dependency groups from pyproject.toml."""
    text = """\
[tool.poetry.group.tests.dependencies]
pytest = "^1.0.0"

[tool.poetry.group.docs.dependencies]
sphinx = "^1.0.0"
"""

    path = tmp_path / "pyproject.toml"
    path.write_text(text, encoding="utf-8")

    config = poetry.Config(path.parent)
    assert config.dependency_groups == ["tests", "docs"]


@pytest.fixture
def session(monkeypatch: pytest.MonkeyPatch) -> nox.Session:
    """Fixture for a Nox session."""
    registry: Dict[str, Any] = {}
    monkeypatch.setattr("nox.registry._REGISTRY", registry)

    @nox.session(venv_backend="none")
    def test(session: nox.Session) -> None:
        """Example session."""

    config = nox._options.options.namespace(posargs=[])
    [runner] = nox.manifest.Manifest(registry, config)
    runner._create_venv()

    return nox.Session(runner)


def test_export_with_warnings(
    session: nox.Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """It removes warnings from the output."""
    requirements = "first==2.0.2\n"
    warning = (
        "Warning: The lock file is not up to date with the latest changes in"
        " pyproject.toml. You may be getting outdated dependencies. Run update"
        " to update them.\n"
    )

    def _run(*args: Any, **kwargs: Any) -> str:
        return warning + requirements

    monkeypatch.setattr("nox.command.run", _run)

    output = poetry.Poetry(session).export()
    assert output == requirements
