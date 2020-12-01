"""Unit tests."""
from pathlib import Path
from typing import Any
from typing import cast

import pytest
from _pytest.monkeypatch import MonkeyPatch
from nox.sessions import Session

import nox_poetry


class FakeSession:
    """Fake session."""

    def __init__(self, path: Path) -> None:
        """Initialize."""
        self.path = path

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
        return str(self.path)


@pytest.fixture
def session(tmp_path: Path, monkeypatch: MonkeyPatch) -> Session:
    """Return a fake Nox session."""
    monkeypatch.setattr("nox_poetry.core.Session_install", FakeSession.install)
    session = FakeSession(tmp_path)
    return cast(Session, session)


def test_install(session: Session) -> None:
    """It installs the dependencies."""
    nox_poetry.install(session, nox_poetry.WHEEL, "pip")


def test_export_requirements(session: Session) -> None:
    """It exports the requirements."""
    nox_poetry.export_requirements(session).touch()
    nox_poetry.export_requirements(session)


def test_patch(session: Session) -> None:
    """It patches Session.install."""
    import nox_poetry.patch  # noqa: F401

    Session.install(session, ".")
