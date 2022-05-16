"""Functional tests using ``path``."""
import nox.sessions

import nox_poetry.patch
from tests.functional.conftest import Project
from tests.functional.conftest import list_packages
from tests.functional.conftest import run_nox_with_noxfile


def test_local(project: Project) -> None:
    """It installs the local package."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        session.install(".")

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry.patch])

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_local_with_extras(project: Project) -> None:
    """It installs the extra."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        session.install(".[pygments]")

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry.patch])

    expected = [
        project.package,
        *project.dependencies,
        project.get_dependency("pygments"),
    ]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_dependency(project: Project) -> None:
    """It installs the pinned dependency."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the dependency."""
        session.install("pyflakes")

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry.patch])

    expected = [project.get_dependency("pyflakes")]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_local_wheel_and_dependency(project: Project) -> None:
    """It installs the wheel with pinned dependencies."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the dependency."""
        session.install(".", "pyflakes")

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry.patch])

    expected = [
        project.package,
        *project.dependencies,
        project.get_dependency("pyflakes"),
    ]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)
