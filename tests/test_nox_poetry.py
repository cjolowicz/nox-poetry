"""Tests."""
from pathlib import Path
from typing import Any
from typing import cast
from typing import Dict

import pytest
from nox.sessions import Session

import nox_poetry.core
from nox_poetry.hookimpl import nox_session_install


class FakeSession:
    """Fake session."""

    def __init__(self, tmpdir: Path) -> None:
        """Initialize."""
        self.tmpdir = tmpdir

    def run(self, *args: str, **kargs: Any) -> str:
        """Run."""
        path = Path("dist") / "example.whl"
        path.touch()
        return path.name

    def install(self, *args: str, **kargs: Any) -> None:
        """Install."""
        pass

    def create_tmp(self, *args: str, **kargs: Any) -> str:
        """Create temporary directory."""
        return str(self.tmpdir)


nox_poetry.core.Session_install = FakeSession.install  # type: ignore[assignment]


@pytest.fixture
def session(tmp_path: Path) -> Session:
    """Return a fake Nox session."""
    session = FakeSession(tmp_path)
    return cast(Session, session)


def test_install(session: Session) -> None:
    """It installs the dependencies."""
    nox_poetry.install(session, nox_poetry.WHEEL, "pip")


def test_hookimpl_no_dot(session: Session) -> None:
    """It installs the dependencies."""
    args = ["pip"]
    kwargs: Dict[str, Any] = {}
    result = nox_session_install(session, args, kwargs)

    assert result is None
    assert any(arg.startswith("--constraint") for arg in args)
    assert "pip" in args
    assert not kwargs


def test_hookimpl_dot(session: Session) -> None:
    """It installs the dependencies."""
    args = [".", "pip"]
    kwargs: Dict[str, Any] = {}
    result = nox_session_install(session, args, kwargs)

    assert result is None
    assert any(arg.startswith("--constraint") for arg in args)
    assert "." not in args
    assert "pip" in args
    assert not kwargs


def test_hookimpl_no_lockfile(session: Session, tmp_path: Path) -> None:
    """It installs the dependencies."""
    import os

    cwd = Path.cwd()
    os.chdir(tmp_path)
    try:
        assert nox_session_install(session, [], {}) is None
    finally:
        os.chdir(cwd)


def test_export_requirements(session: Session) -> None:
    """It exports the requirements."""
    nox_poetry.export_requirements(session).touch()
    nox_poetry.export_requirements(session)


def test_patch(session: Session) -> None:
    """It patches Session.install."""
    import nox_poetry.patch  # noqa: F401

    Session.install(session, ".")
