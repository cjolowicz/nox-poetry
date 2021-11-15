"""Functional tests for ``install``."""
import nox.sessions
from tests.functional.conftest import list_packages
from tests.functional.conftest import Project
from tests.functional.conftest import run_nox_with_noxfile

import nox_poetry


def test_install_local_wheel(project: Project) -> None:
    """It builds and installs a wheel from the local package."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        nox_poetry.install(session, ".")

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_install_local_wheel_with_extras(project: Project) -> None:
    """It installs the extra."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        nox_poetry.install(session, ".[pygments]")

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry])

    expected = [
        project.package,
        *project.dependencies,
        project.get_dependency("pygments"),
    ]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_install_dependency(project: Project) -> None:
    """It installs the pinned dependency."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the dependency."""
        nox_poetry.install(session, "pycodestyle")

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry])

    expected = [project.get_dependency("pycodestyle")]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_install_local_wheel_and_dependency(project: Project) -> None:
    """It installs the wheel with pinned dependencies."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the dependency."""
        nox_poetry.install(session, ".", "pycodestyle")

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry])

    expected = [
        project.package,
        *project.dependencies,
        project.get_dependency("pycodestyle"),
    ]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)
