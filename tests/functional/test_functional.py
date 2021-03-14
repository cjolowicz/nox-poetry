"""Functional tests."""
from pathlib import Path

import nox.sessions
import pytest
from tests.functional.conftest import list_packages
from tests.functional.conftest import Project
from tests.functional.conftest import run_nox_with_noxfile

import nox_poetry.patch


def test_install_local_using_patch(project: Project) -> None:
    """It installs the local package."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        session.install(".")

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry.patch])

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_install_local_using_patch_with_extras(project: Project) -> None:
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


def test_installroot_wheel(project: Project) -> None:
    """It builds and installs a wheel from the local package."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        nox_poetry.installroot(session, distribution_format=nox_poetry.WHEEL)

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_installroot_wheel_with_extras(project: Project) -> None:
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


def test_installroot_sdist(project: Project) -> None:
    """It builds and installs an sdist from the local package."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the local package."""
        nox_poetry.installroot(session, distribution_format=nox_poetry.SDIST)

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_installroot_sdist_with_extras(project: Project) -> None:
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


def test_install_dependency_using_patch(project: Project) -> None:
    """It installs the pinned dependency."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the dependency."""
        session.install("pyflakes")

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry.patch])

    expected = [project.get_dependency("pyflakes")]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_install_dependency_without_patch(project: Project) -> None:
    """It installs the pinned dependency."""

    @nox.session
    def test(session: nox.sessions.Session) -> None:
        """Install the dependency."""
        nox_poetry.install(session, "pycodestyle")

    run_nox_with_noxfile(project, [test], [nox, nox.sessions, nox_poetry])

    expected = [project.get_dependency("pycodestyle")]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_install_local_wheel_and_dependency_using_patch(project: Project) -> None:
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


def test_install_local_wheel_and_dependency_without_patch(project: Project) -> None:
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


def test_session_install_local(project: Project) -> None:
    """It installs the local package."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.install(".")

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_session_install_local_with_extras(project: Project) -> None:
    """It installs the extra."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.install(".[pygments]")

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [
        project.package,
        *project.dependencies,
        project.get_dependency("pygments"),
    ]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_session_install_dependency(project: Project) -> None:
    """It installs the pinned dependency."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the dependency."""
        session.install("pyflakes")

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [project.get_dependency("pyflakes")]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_session_install_local_wheel_and_dependency(project: Project) -> None:
    """It installs the wheel with pinned dependencies."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the dependency."""
        session.install(".", "pyflakes")

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [
        project.package,
        *project.dependencies,
        project.get_dependency("pyflakes"),
    ]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_session_parametrize(project: Project) -> None:
    """It forwards parameters to sessions."""

    @nox_poetry.session
    @nox.parametrize("n", [1, 2])
    def test(session: nox_poetry.Session, n: int) -> None:
        """Do nothing."""

    run_nox_with_noxfile(project, [test], [nox, nox_poetry])


def test_install_with_url_dependency(datadir: Path) -> None:
    """It installs the package."""
    project = Project(datadir / "url-dependency")

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.install(".")

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


# https://github.com/python-poetry/poetry/issues/3468
@pytest.mark.xfail(reason="Poetry exports path requirements in an invalid format.")
def test_install_with_path_dependency(datadir: Path) -> None:
    """It installs the package."""
    project = Project(datadir / "path-dependency")

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.install(".")

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)
