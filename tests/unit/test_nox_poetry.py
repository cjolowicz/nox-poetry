"""Unit tests."""
from typing import Iterable

import pytest
from nox.sessions import Session

import nox_poetry
from nox_poetry.poetry import DistributionFormat
from nox_poetry.poetry import Poetry


@pytest.mark.parametrize(
    "args",
    [
        ["."],
        ["pyflakes"],
        [".", "pyflakes"],
    ],
)
def test_install(session: Session, args: Iterable[str]) -> None:
    """It installs the specified packages."""
    nox_poetry.install(session, *args)


@pytest.mark.parametrize("distribution_format", [nox_poetry.WHEEL, nox_poetry.SDIST])
def test_installroot(session: Session, distribution_format: DistributionFormat) -> None:
    """It installs the package."""
    nox_poetry.installroot(session, distribution_format=distribution_format)


def test_export_requirements(session: Session) -> None:
    """It exports the requirements."""
    nox_poetry.export_requirements(session).touch()
    nox_poetry.export_requirements(session)


def test_patch(session: Session) -> None:
    """It patches Session.install."""
    import nox_poetry.patch  # noqa: F401

    Session.install(session, ".")


def test_poetry_config(session: Session) -> None:
    """It caches the configuration when accessed multiple times."""
    poetry = Poetry(session)
    poetry.config
    assert poetry.config.name == "nox-poetry"
