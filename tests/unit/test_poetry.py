"""Unit tests for the poetry module."""

from pathlib import Path
from textwrap import dedent
from typing import Any
from typing import Callable
from typing import Dict

import nox._options
import nox.command
import nox.manifest
import nox.sessions
import pytest

from nox_poetry import poetry


CreateConfig = Callable[[str], poetry.Config]


@pytest.fixture
def create_config(tmp_path: Path) -> CreateConfig:
    """Factory fixture for a Poetry config."""

    def _(text: str) -> poetry.Config:
        path = tmp_path / "pyproject.toml"
        path.write_text(dedent(text), encoding="utf-8")

        return poetry.Config(path.parent)

    return _


def test_config_non_ascii(create_config: CreateConfig) -> None:
    """It decodes non-ASCII characters in pyproject.toml."""
    config = create_config(
        """
        [tool.poetry]
        name = "África"
        """
    )
    assert config.name == "África"


def test_config_dependency_groups(create_config: CreateConfig) -> None:
    """It returns the dependency groups from pyproject.toml."""
    config = create_config(
        """
        [tool.poetry.group.tests.dependencies]
        pytest = "^1.0.0"

        [tool.poetry.group.docs.dependencies]
        sphinx = "^1.0.0"
        """
    )
    assert config.dependency_groups == ["tests", "docs"]


def test_config_no_dependency_groups(create_config: CreateConfig) -> None:
    """It returns an empty list."""
    config = create_config(
        """
        [tool.poetry]
        """
    )
    assert config.dependency_groups == []


def test_config_dev_dependency_group(create_config: CreateConfig) -> None:
    """It returns the dev dependency group."""
    config = create_config(
        """
        [tool.poetry.dev-dependencies]
        pytest = "^1.0.0"
        """
    )
    assert config.dependency_groups == ["dev"]


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


def test_poetry_version(session: nox.Session) -> None:
    """It returns the Poetry version."""
    version = poetry.Poetry(session).version
    assert all(part.isnumeric() for part in version.split(".")[:3])


def test_poetry_cached_version(session: nox.Session) -> None:
    """It caches the Poetry version."""
    p = poetry.Poetry(session)
    assert p.version == p.version


def test_poetry_invalid_version(
    session: nox.Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """It raises an exception if the Poetry version cannot be parsed."""

    def _run(*args: Any, **kwargs: Any) -> str:
        return "bogus"

    monkeypatch.setattr("nox.command.run", _run)

    with pytest.raises(RuntimeError):
        poetry.Poetry(session).version


@pytest.mark.parametrize(
    ("version", "expected"),
    [
        ("1.0.10", False),
        ("1.1.15", False),
        ("1.2.2", True),
        ("1.6.0.dev0", True),
    ],
)
def test_poetry_has_dependency_groups(
    session: nox.Session,
    monkeypatch: pytest.MonkeyPatch,
    version: str,
    expected: bool,
) -> None:
    """It returns True if Poetry supports dependency groups."""

    def _run(*args: Any, **kwargs: Any) -> str:
        return version

    monkeypatch.setattr("nox.command.run", _run)

    assert poetry.Poetry(session).has_dependency_groups is expected


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
