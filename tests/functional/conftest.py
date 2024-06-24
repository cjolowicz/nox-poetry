"""Fixtures for functional tests."""

import inspect
import os
import subprocess  # noqa: S404
import sys
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from types import ModuleType
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Iterable
from typing import List

import pytest
import tomlkit.api  # https://github.com/sdispater/tomlkit/issues/128
from packaging.utils import canonicalize_name


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
        return tomlkit.api.parse(text)

    def _get_config(self, key: str) -> Any:
        data: Any = self._read_toml("pyproject.toml")
        poetry_config = data.get("tool", {}).get("poetry", {})
        pyproject = data.get("project", {})
        return poetry_config.get(key, pyproject.get(key))

    def get_dependency(self, name: str, data: Any = None) -> Package:
        """Return the package with the given name."""
        if data is None:
            data = self._read_toml("poetry.lock")

        for package in data["package"]:
            if package["name"] == name:
                url = package.get("source", {}).get("url")
                if url is not None:
                    # Abuse Package.version to store the URL (for ``list_packages``).  # noqa: E501
                    return Package(name, url)
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
        data = self._read_toml("poetry.lock")
        dependencies: List[str] = [
            package["name"]
            for package in data["package"]
            if package["category"] == "main" and not package["optional"]
        ]
        return [self.get_dependency(package) for package in dependencies]

    @property
    def development_dependencies(self) -> List[Package]:
        """Return the development dependencies."""
        dependencies: List[str] = list(self._get_config("dev-dependencies"))
        return [self.get_dependency(package) for package in dependencies]

    @property
    def locked_packages(self) -> List[Package]:
        """Return all packages from the lockfile."""
        data = self._read_toml("poetry.lock")
        return [
            self.get_dependency(package["name"], data) for package in data["package"]
        ]


@pytest.fixture
def project(shared_datadir: Path) -> Project:
    """Return an example Poetry project."""
    return Project(shared_datadir / "example")


def _run_nox(project: Project, *nox_args: str) -> CompletedProcess:
    env = os.environ.copy()
    env.pop("NOXSESSION", None)

    try:
        return subprocess.run(  # noqa: S603, S607
            ["nox", *nox_args],
            check=True,
            text=True,
            capture_output=True,
            cwd=project.path,
            env=env,
        )
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"{error}\n{error.stderr}") from None


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


def run_nox_with_noxfile(
    project: Project,
    sessions: Iterable[SessionFunction],
    imports: Iterable[ModuleType],
    *nox_args: str,
) -> CompletedProcess:
    """Write a noxfile and run Nox in the project."""
    _write_noxfile(project, sessions, imports)
    return _run_nox(project, *nox_args)


def list_packages(project: Project, session: SessionFunction) -> List[Package]:
    """List the installed packages for a session in the given project."""
    bindir = "Scripts" if sys.platform == "win32" else "bin"
    pip = project.path / ".nox" / session.__name__ / bindir / "pip"
    process = subprocess.run(  # noqa: S603
        [str(pip), "freeze"],
        check=True,
        text=True,
        capture_output=True,
    )

    def parse(line: str) -> Package:
        name, _, version = line.partition("==")
        if not version and " @ " in line:
            # Abuse Package.version to store the URL or path.
            name, _, version = line.partition(" @ ")

            # Strip hashes returned by pip freeze.
            pos = version.rfind("#sha256=")
            if pos != -1:
                version = version[:pos]

            if name == project.package.name:
                # But use the known version for the local package.
                return project.package

        name = canonicalize_name(name)
        return Package(name, version)

    return [parse(line) for line in process.stdout.splitlines()]
