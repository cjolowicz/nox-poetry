"""Fixtures."""
from pathlib import Path
from typing import Any
from typing import cast

import pytest
from _pytest.monkeypatch import MonkeyPatch
from nox.sessions import Session


class FakeVirtualenv:
    """Fake virtual environment."""

    def __init__(self, path: Path) -> None:
        """Initialize."""
        self.location = str(path)


class FakeSession:
    """Fake session."""

    def __init__(self, path: Path) -> None:
        """Initialize."""
        self.virtualenv = FakeVirtualenv(path)

    @property
    def _session(self) -> "FakeSession":
        """Allow passing this instance to PoetrySession."""
        return self

    def run_always(self, *args: str, **kargs: Any) -> str:
        """Run."""
        path = Path("dist") / "example.whl"
        path.touch()
        return path.name

    def install(self, *args: str, **kargs: Any) -> None:
        """Install."""


@pytest.fixture
def session(tmp_path: Path, monkeypatch: MonkeyPatch) -> Session:
    """Return a fake Nox session."""
    monkeypatch.setattr("nox_poetry.core.Session_install", FakeSession.install)
    session = FakeSession(tmp_path)
    return cast(Session, session)
