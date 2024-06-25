"""Fixtures."""

import sys
from pathlib import Path
from typing import Any
from typing import Optional
from typing import cast


if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import pytest
from nox.sessions import Session


class FakeSessionRunner:
    """Fake session runner."""

    def __init__(self, path: Path) -> None:
        """Initialize."""
        self.envdir = str(path)


class FakeSession:
    """Fake session."""

    def __init__(self, path: Path, no_install: bool) -> None:
        """Initialize."""
        self._runner = FakeSessionRunner(path)
        self.no_install = no_install
        self.install_called = False

    def run_always(self, *args: str, **kargs: Any) -> Optional[str]:
        """Run."""
        if self.no_install:
            return None

        if args[:2] == ("poetry", "--version"):
            return "1.1.15"

        path = Path("dist") / "example.whl"
        path.touch()
        return path.name

    def install(self, *args: str, **kargs: Any) -> None:
        """Install."""
        self.install_called = True


class FakeSessionFactory(Protocol):
    """Factory for fake sessions."""

    def __call__(self, *, no_install: bool) -> Session:
        """Create a fake session."""


@pytest.fixture
def sessionfactory(tmp_path: Path) -> FakeSessionFactory:
    """Return a factory for a fake Nox session."""

    def _sessionfactory(*, no_install: bool) -> Session:
        session = FakeSession(tmp_path, no_install=no_install)
        return cast(Session, session)

    return _sessionfactory


@pytest.fixture
def session(sessionfactory: FakeSessionFactory) -> Session:
    """Return a fake Nox session."""
    return sessionfactory(no_install=False)
