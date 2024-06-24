"""Functional tests for the `@session` decorator."""

from importlib.metadata import version
from pathlib import Path

import nox.sessions
import pytest
from packaging.version import Version

import nox_poetry
from tests.functional.conftest import Project
from tests.functional.conftest import list_packages
from tests.functional.conftest import run_nox_with_noxfile


def test_local(project: Project) -> None:
    """It installs the local package."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.install(".")

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_local_with_extras(project: Project) -> None:
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


def test_dependency(project: Project) -> None:
    """It installs the pinned dependency."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the dependency."""
        session.install("pyflakes")

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [project.get_dependency("pyflakes")]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_local_wheel_and_dependency(project: Project) -> None:
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


def test_url_dependency(shared_datadir: Path) -> None:
    """It installs the package."""
    project = Project(shared_datadir / "url-dependency")

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
def test_path_dependency(shared_datadir: Path) -> None:
    """It installs the package."""
    project = Project(shared_datadir / "path-dependency")

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.install(".")

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_no_install(project: Project) -> None:
    """It skips installation when --no-install is passed."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.install(".")

    run_nox_with_noxfile(project, [test], [nox_poetry])
    run_nox_with_noxfile(project, [test], [nox_poetry], "-R")

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_poetry_warnings(shared_datadir: Path) -> None:
    """It writes warnings from Poetry to the console."""
    project = Project(shared_datadir / "outdated-lockfile")

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.install(".")

    process = run_nox_with_noxfile(project, [test], [nox_poetry])

    assert "Warning:" in process.stderr


@pytest.mark.skipif(
    Version(version("poetry")) < Version("1.2"),
    reason="Poetry < 1.2 does not support dependency groups",
)
def test_dependency_group(shared_datadir: Path) -> None:
    """It pins packages in dependency groups."""
    project = Project(shared_datadir / "dependency-group")

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the dependencies."""
        session.install(".", "pyflakes")

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [project.package, *project.locked_packages]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


@pytest.mark.skipif(
    Version(version("poetry")) < Version("2.0.0.dev0"),
    reason=f"Poetry {version('poetry')} < 2.0 does not support PEP 621",
)
def test_pep621_pyproject_support(shared_datadir: Path) -> None:
    """It installs packages from PEP 621 pyproject.toml."""
    project = Project(shared_datadir / "pep-621")

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the dependencies."""
        session.install(".")

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [project.package, *project.locked_packages]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)
