"""Tests."""
from pathlib import Path
from typing import Any
from typing import cast

import pytest
from nox.sessions import Session

import nox_poetry.core


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


def test_export_requirements(session: Session) -> None:
    """It exports the requirements."""
    nox_poetry.export_requirements(session).touch()
    nox_poetry.export_requirements(session)
