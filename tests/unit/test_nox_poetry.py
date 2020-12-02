"""Unit tests."""
from nox.sessions import Session

import nox_poetry


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
