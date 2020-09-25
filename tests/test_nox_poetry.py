"""Tests."""
from pathlib import Path
from typing import Any
from typing import cast

import pytest
from nox.sessions import Session

from nox_poetry import export_requirements
from nox_poetry import install
from nox_poetry import install_package


class FakeSession:
    """Fake session."""

    def __init__(self, tmpdir: Path) -> None:
        """Initialize."""
        self.tmpdir = tmpdir

    def run(self, *args: str, **kargs: Any) -> str:
        """Run."""
        return "example.whl"

    def install(self, *args: str, **kargs: Any) -> None:
        """Install."""
        pass

    def create_tmp(self, *args: str, **kargs: Any) -> str:
        """Create temporary directory."""
        return str(self.tmpdir)


@pytest.fixture
def session(tmp_path: Path) -> Session:
    """Return a fake Nox session."""
    session = FakeSession(tmp_path)
    return cast(Session, session)


def test_install(session: Session) -> None:
    """It installs the dependencies."""
    install(session, "pip")


def test_install_package(session: Session) -> None:
    """It installs the package."""
    install_package(session)


def test_export_requirements(session: Session) -> None:
    """It exports the requirements."""
    export_requirements(session, dev=True).touch()
    export_requirements(session, dev=True)
