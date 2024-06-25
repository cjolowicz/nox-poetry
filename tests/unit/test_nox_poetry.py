"""Unit tests."""

from typing import Iterable

import pytest
from nox.sessions import Session

import nox_poetry
from nox_poetry.poetry import Poetry


@pytest.mark.parametrize(
    "args",
    [
        ["."],
        ["pyflakes"],
        [".", "pyflakes"],
        [".[noodles]"],
        ["pyflakes[honey]"],
        [".[spicy, noodles]", "pyflakes[honey]"],
    ],
)
def test_install(session: Session, args: Iterable[str]) -> None:
    """It installs the specified packages."""
    nox_poetry.Session(session).install(*args)


@pytest.mark.parametrize(
    "distribution_format",
    [
        nox_poetry.WHEEL,
        nox_poetry.SDIST,
        "wheel",
        "sdist",
    ],
)
def test_installroot(session: Session, distribution_format: str) -> None:
    """It installs the package."""
    nox_poetry.Session(session).poetry.installroot(
        distribution_format=distribution_format
    )


def test_installroot_invalid_format(session: Session) -> None:
    """It raises an error."""
    with pytest.raises(ValueError):
        nox_poetry.Session(session).poetry.installroot(distribution_format="egg")


@pytest.mark.parametrize(
    "distribution_format",
    [
        nox_poetry.WHEEL,
        nox_poetry.SDIST,
        "wheel",
        "sdist",
    ],
)
@pytest.mark.parametrize("extras", [[], ["noodles"], ["spicy", "noodles"]])
def test_installroot_with_extras(
    session: Session,
    distribution_format: str,
    extras: Iterable[str],
) -> None:
    """It installs the package with extras."""
    nox_poetry.Session(session).poetry.installroot(
        distribution_format=distribution_format, extras=extras
    )


@pytest.mark.parametrize("distribution_format", [nox_poetry.WHEEL, nox_poetry.SDIST])
def test_build_package(session: Session, distribution_format: str) -> None:
    """It builds the package."""
    nox_poetry.Session(session).poetry.build_package(
        distribution_format=distribution_format
    )


def test_export_requirements(session: Session) -> None:
    """It exports the requirements."""
    nox_poetry.Session(session).poetry.export_requirements().touch()
    nox_poetry.Session(session).poetry.export_requirements()


def test_poetry_config(session: Session) -> None:
    """It caches the configuration when accessed multiple times."""
    poetry = Poetry(session)
    poetry.config
    assert poetry.config.name == "nox-poetry"
