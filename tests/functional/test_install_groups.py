"""Functional tests for the `install_groups`."""
import pytest

import nox_poetry
from tests.functional.conftest import Project
from tests.functional.conftest import list_packages
from tests.functional.conftest import run_nox_with_noxfile


skipif_poetry_version_is_under_1_2_0 = pytest.mark.skipif(
    not nox_poetry.poetry.Config.is_compatible_with_group_deps(),
    reason="session.install_groups() requires poetry>=1.2.0",
)


@skipif_poetry_version_is_under_1_2_0
def test_dev_dependencies(project: Project) -> None:
    """It installs only dev-dependencies on <1.2.0 example pyproject.toml."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.install_groups(["dev"])

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [
        project.get_dependency("pyflakes"),
        project.get_dependency("pycodestyle"),
    ]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


@skipif_poetry_version_is_under_1_2_0
def test_group_dev(group_project: Project) -> None:
    """It installs only dev group on >=1.2.0 example pyproject.toml."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.install_groups(["dev"])

    run_nox_with_noxfile(group_project, [test], [nox_poetry])

    expected = [
        group_project.get_dependency("pyflakes"),
        group_project.get_dependency("pycodestyle"),
    ]
    packages = list_packages(group_project, test)

    assert set(expected) == set(packages)


@skipif_poetry_version_is_under_1_2_0
def test_two_groups(group_project: Project) -> None:
    """It installs only 2 dependency groups on >=1.2.0 example pyproject.toml."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.install_groups(["test", "lint"])

    run_nox_with_noxfile(group_project, [test], [nox_poetry])

    expected = [
        group_project.get_dependency("isort"),
        group_project.get_dependency("darglint"),
    ]
    packages = list_packages(group_project, test)

    assert set(expected) == set(packages)
