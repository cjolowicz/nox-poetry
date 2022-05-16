"""Functional tests for ``session.poetry``."""
import nox_poetry
from tests.functional.conftest import Project
from tests.functional.conftest import list_packages
from tests.functional.conftest import run_nox_with_noxfile


def test_passthrough_env(project: Project) -> None:
    """It stores requirements even without a virtualenv directory."""
    # https://github.com/cjolowicz/nox-poetry/issues/347

    @nox_poetry.session(venv_backend="none")
    def test(session: nox_poetry.Session) -> None:
        """Export the requirements."""
        session.poetry.export_requirements()

    run_nox_with_noxfile(project, [test], [nox_poetry])


def test_no_install_installroot(project: Project) -> None:
    """It skips installation when --no-install is passed."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.poetry.installroot()

    run_nox_with_noxfile(project, [test], [nox_poetry])
    run_nox_with_noxfile(project, [test], [nox_poetry], "-R")

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_stale_wheelcache(project: Project) -> None:
    """It removes old wheels from the wheel cache."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.poetry.installroot(distribution_format="sdist")
        session.run("python", "-c", 'import example; print(example.__doc__, end="")')

    path = project.path / "src" / "example" / "__init__.py"
    path.write_text('"a"\n')

    process = run_nox_with_noxfile(project, [test], [nox_poetry])

    assert "a" == process.stdout

    path.write_text('"b"\n')
    process = run_nox_with_noxfile(project, [test], [nox_poetry])

    assert "b" == process.stdout
