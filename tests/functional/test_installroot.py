"""Functional tests for ``installroot``."""
import nox.sessions

import nox_poetry
from tests.functional.conftest import Project
from tests.functional.conftest import list_packages
from tests.functional.conftest import run_nox_with_noxfile


def test_wheel(project: Project) -> None:
    """It builds and installs a wheel from the local package."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        nox_poetry.installroot(session, distribution_format=nox_poetry.WHEEL)

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_wheel_with_extras(project: Project) -> None:
    """It installs the extra."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        nox_poetry.installroot(
            session, distribution_format=nox_poetry.WHEEL, extras=["pygments"]
        )

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry])

    expected = [
        project.package,
        *project.dependencies,
        project.get_dependency("pygments"),
    ]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_sdist(project: Project) -> None:
    """It builds and installs an sdist from the local package."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        nox_poetry.installroot(session, distribution_format=nox_poetry.SDIST)

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_sdist_with_extras(project: Project) -> None:
    """It installs the extra."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        nox_poetry.installroot(
            session, distribution_format=nox_poetry.SDIST, extras=["pygments"]
        )

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry])

    expected = [
        project.package,
        *project.dependencies,
        project.get_dependency("pygments"),
    ]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)
