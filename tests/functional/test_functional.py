"""Functional tests."""
import nox.sessions
from tests.functional.conftest import ListPackages
from tests.functional.conftest import Project
from tests.functional.conftest import RunNoxWithNoxfile

import nox_poetry.patch


def test_install_local_using_patch(
    project: Project,
    run_nox_with_noxfile: RunNoxWithNoxfile,
    list_packages: ListPackages,
) -> None:
    """Invoking session.install(".") installs the local package."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        session.install(".")

    run_nox_with_noxfile([test], [nox, nox.sessions, nox_poetry.patch])

    expected = [project.package, *project.dependencies]
    packages = list_packages(test)

    assert set(expected) == set(packages)


def test_install_local_wheel(
    project: Project,
    run_nox_with_noxfile: RunNoxWithNoxfile,
    list_packages: ListPackages,
) -> None:
    """It builds and installs a wheel from the local package."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        nox_poetry.install(session, nox_poetry.WHEEL)

    run_nox_with_noxfile([test], [nox, nox.sessions, nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(test)

    assert set(expected) == set(packages)


def test_install_local_sdist(
    project: Project,
    run_nox_with_noxfile: RunNoxWithNoxfile,
    list_packages: ListPackages,
) -> None:
    """It builds and installs an sdist from the local package."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        nox_poetry.install(session, nox_poetry.SDIST)

    run_nox_with_noxfile([test], [nox, nox.sessions, nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(test)

    assert set(expected) == set(packages)


def test_installroot_wheel(
    project: Project,
    run_nox_with_noxfile: RunNoxWithNoxfile,
    list_packages: ListPackages,
) -> None:
    """It builds and installs a wheel from the local package."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        nox_poetry.installroot(session, distribution_format=nox_poetry.WHEEL)

    run_nox_with_noxfile([test], [nox, nox.sessions, nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(test)

    assert set(expected) == set(packages)


def test_installroot_sdist(
    project: Project,
    run_nox_with_noxfile: RunNoxWithNoxfile,
    list_packages: ListPackages,
) -> None:
    """It builds and installs an sdist from the local package."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        nox_poetry.installroot(session, distribution_format=nox_poetry.SDIST)

    run_nox_with_noxfile([test], [nox, nox.sessions, nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(test)

    assert set(expected) == set(packages)


def test_install_dependency_using_patch(
    project: Project,
    run_nox_with_noxfile: RunNoxWithNoxfile,
    list_packages: ListPackages,
) -> None:
    """It installs the pinned dependency."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the dependency."""
        session.install("pyflakes")

    run_nox_with_noxfile([test], [nox, nox.sessions, nox_poetry.patch])

    expected = [project.get_dependency("pyflakes")]
    packages = list_packages(test)

    assert set(expected) == set(packages)


def test_install_dependency_without_patch(
    project: Project,
    run_nox_with_noxfile: RunNoxWithNoxfile,
    list_packages: ListPackages,
) -> None:
    """It installs the pinned dependency."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the dependency."""
        nox_poetry.install(session, "pycodestyle")

    run_nox_with_noxfile([test], [nox, nox.sessions, nox_poetry])

    expected = [project.get_dependency("pycodestyle")]
    packages = list_packages(test)

    assert set(expected) == set(packages)


def test_install_local_wheel_and_dependency_using_patch(
    project: Project,
    run_nox_with_noxfile: RunNoxWithNoxfile,
    list_packages: ListPackages,
) -> None:
    """It installs the wheel with pinned dependencies."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the dependency."""
        session.install(".", "pyflakes")

    run_nox_with_noxfile([test], [nox, nox.sessions, nox_poetry.patch])

    expected = [
        project.package,
        *project.dependencies,
        project.get_dependency("pyflakes"),
    ]
    packages = list_packages(test)

    assert set(expected) == set(packages)


def test_install_local_wheel_and_dependency_without_patch(
    project: Project,
    run_nox_with_noxfile: RunNoxWithNoxfile,
    list_packages: ListPackages,
) -> None:
    """It installs the wheel with pinned dependencies."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the dependency."""
        nox_poetry.install(session, nox_poetry.WHEEL, "pycodestyle")

    run_nox_with_noxfile([test], [nox, nox.sessions, nox_poetry])

    expected = [
        project.package,
        *project.dependencies,
        project.get_dependency("pycodestyle"),
    ]
    packages = list_packages(test)

    assert set(expected) == set(packages)
