"""Unit tests for the poetry module."""
from pathlib import Path
from typing import Any
from typing import Dict

import nox._options
import nox.command
import nox.manifest
import nox.sessions
import pytest
from packaging.version import Version

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


@pytest.mark.parametrize(
    "poetry_version,expected", [("1.1.10", False), ("1.2.0", True), ("1.3.0", True)]
)
def test_is_compatible_with_group_deps(
    monkeypatch: pytest.MonkeyPatch, poetry_version: str, expected: bool
) -> None:
    """It is only compatible if installed version of poetry is >=1.2.0."""
    monkeypatch.setattr(
        "nox_poetry.poetry.Config.version", lambda: Version(poetry_version)
    )
    assert poetry.Config.is_compatible_with_group_deps() is expected
