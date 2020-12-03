"""Fixtures for functional tests."""
import functools
import inspect
import os
import re
import subprocess  # noqa: S404
import sys
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from types import ModuleType
from typing import Any
from typing import Callable
from typing import Iterable
from typing import List
from typing import TYPE_CHECKING

import pytest
import tomlkit


if TYPE_CHECKING:
    CompletedProcess = subprocess.CompletedProcess[str]
else:
    from subprocess import CompletedProcess  # noqa: S404


@dataclass(frozen=True)
class Package:
    """Python package."""

    name: str
    version: str


@dataclass
class Project:
    """Poetry project."""

    path: Path

    def _read_toml(self, filename: str) -> Any:
        path = self.path / filename
        text = path.read_text()
        return tomlkit.parse(text)

    def _get_config(self, key: str) -> Any:
        data = self._read_toml("pyproject.toml")
        return data["tool"]["poetry"][key]

    def get_dependency(self, name: str) -> Package:
        """Return the package with the given name."""
        data = self._read_toml("poetry.lock")
        for package in data["package"]:
            if package["name"] == name:
                return Package(name, package["version"])
        raise ValueError(f"{name}: package not found")

    @property
    def package(self) -> Package:
        """Return the package name."""
        name: str = self._get_config("name")
        version: str = self._get_config("version")
        return Package(name, version)

    @property
    def dependencies(self) -> List[Package]:
        """Return the package dependencies."""
        table = self._get_config("dependencies")
        dependencies: List[str] = [
            package
            for package, info in table.items()
            if not (
                package == "python"
                or isinstance(info, dict)
                and info.get("optional", None)
            )
        ]
        return [self.get_dependency(package) for package in dependencies]

    @property
    def development_dependencies(self) -> List[Package]:
        """Return the development dependencies."""
        dependencies: List[str] = list(self._get_config("dev-dependencies"))
        return [self.get_dependency(package) for package in dependencies]


@pytest.fixture
def project(datadir: Path) -> Project:
    """Return an example Poetry project."""
    return Project(datadir / "example")


def _run_nox(project: Project) -> CompletedProcess:
    env = os.environ.copy()
    env.pop("NOXSESSION", None)

    try:
        return subprocess.run(  # noqa: S603, S607
            ["nox"],
            check=True,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=project.path,
            env=env,
        )
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"{error}\n{error.stderr}")


RunNox = Callable[[], CompletedProcess]


@pytest.fixture
def run_nox(project: Project) -> RunNox:
    """Invoke Nox in the project."""
    return functools.partial(_run_nox, project)


SessionFunction = Callable[..., Any]


def _write_noxfile(
    project: Project,
    sessions: Iterable[SessionFunction],
    imports: Iterable[ModuleType],
) -> None:
    header = "\n".join(f"import {module.__name__}" for module in imports)
    stanzas = [dedent(inspect.getsource(session)) for session in sessions]
    text = "\n\n".join([header, *stanzas])

    path = project.path / "noxfile.py"
    path.write_text(text)


WriteNoxfile = Callable[
    [
        Iterable[SessionFunction],
        Iterable[ModuleType],
    ],
    None,
]


@pytest.fixture
def write_noxfile(project: Project) -> WriteNoxfile:
    """Write a noxfile with the given session functions."""
    return functools.partial(_write_noxfile, project)


def _run_nox_with_noxfile(
    project: Project,
    sessions: Iterable[SessionFunction],
    imports: Iterable[ModuleType],
) -> None:
    _write_noxfile(project, sessions, imports)
    _run_nox(project)


RunNoxWithNoxfile = Callable[
    [
        Iterable[SessionFunction],
        Iterable[ModuleType],
    ],
    None,
]


@pytest.fixture
def run_nox_with_noxfile(project: Project) -> RunNoxWithNoxfile:
    """Write a noxfile and run Nox in the project."""
    return functools.partial(_run_nox_with_noxfile, project)


_CANONICALIZE_PATTERN = re.compile(r"[-_.]+")


def _canonicalize_name(name: str) -> str:
    # From ``packaging.utils.canonicalize_name`` (PEP 503)
    return _CANONICALIZE_PATTERN.sub("-", name).lower()


def _list_packages(project: Project, session: SessionFunction) -> List[Package]:
    bindir = "Scripts" if sys.platform == "win32" else "bin"
    pip = project.path / ".nox" / session.__name__ / bindir / "pip"
    process = subprocess.run(  # noqa: S603
        [str(pip), "freeze"],
        check=True,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    def parse(line: str) -> Package:
        name, _, version = line.partition("==")
        name = _canonicalize_name(name)
        if not version and name.startswith(f"{project.package.name} @ file://"):
            # Local package is listed without version, but it does not matter.
            return project.package
        return Package(name, version)

    return [parse(line) for line in process.stdout.splitlines()]


ListPackages = Callable[[SessionFunction], List[Package]]


@pytest.fixture
def list_packages(project: Project) -> ListPackages:
    """Return a function that lists the installed packages for a session."""
    return functools.partial(_list_packages, project)
