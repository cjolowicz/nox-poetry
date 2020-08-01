"""Tests."""
from typing import Any
from typing import cast

from nox.sessions import Session

from nox_poetry import install
from nox_poetry import install_package


class FakeSession:
    """Fake session."""

    def run(self, *args: str, **kargs: Any) -> str:
        """Run."""
        return "example.whl"

    def install(self, *args: str, **kargs: Any) -> None:
        """Install."""
        pass


def test_install() -> None:
    """It installs."""
    session = cast(Session, FakeSession())
    install(session, "pip")


def test_install_package() -> None:
    """It installs."""
    session = cast(Session, FakeSession())
    install_package(session)
