"""Poetry interface."""

import re
import sys
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional

import build
import tomlkit
from build.env import DefaultIsolatedEnv
from nox.sessions import Session


class CommandSkippedError(Exception):
    """The command was not executed by Nox."""


class DistributionFormat(str, Enum):
    """Type of distribution archive for a Python package."""

    WHEEL = "wheel"
    SDIST = "sdist"


class Config:
    """Poetry configuration."""

    def __init__(self, project: Path) -> None:
        """Initialize."""
        path = project / "pyproject.toml"
        text = path.read_text(encoding="utf-8")
        data: Any = tomlkit.parse(text)
        self._build_system = data.get("build-system", {})
        self._config = data.get("tool", {}).get("poetry", {})
        self._pyproject = data.get("project", {})

    @property
    def name(self) -> str:
        """Return the package name."""
        name = self._config.get("name", self._pyproject.get("name"))
        assert isinstance(name, str)  # noqa: S101
        return name

    @property
    def extras(self) -> List[str]:
        """Return the package extras."""
        extras = self._config.get("extras", {})
        assert isinstance(extras, dict) and all(  # noqa: S101
            isinstance(extra, str) for extra in extras
        )
        return list(extras)

    @property
    def dependency_groups(self) -> List[str]:
        """Return the dependency groups."""
        groups = self._config.get("group", {})
        if not groups and "dev-dependencies" in self._config:
            return ["dev"]
        return list(groups)

    @property
    def build_system_requires(self) -> set[str]:
        """Build dependencies.

        The dependencies defined in the ``pyproject.toml``'s
        ``build-system.requires`` field.
        """
        return set(self._build_system.get("requires", []))


VERSION_PATTERN = re.compile(r"[0-9]+(\.[0-9+])+[-+.0-9a-zA-Z]+")


class Poetry:
    """Helper class for invoking Poetry inside a Nox session.

    Attributes:
        session: The Session object.
    """

    def __init__(self, session: Session) -> None:
        """Initialize."""
        self.session = session
        self.project = Path.cwd()
        self._config: Optional[Config] = None
        self._version: Optional[str] = None

    @property
    def version(self) -> str:
        """Return the Poetry version."""
        if self._version is not None:
            return self._version

        output = self.session.run_always(
            "poetry",
            "--version",
            "--no-ansi",
            external=True,
            silent=True,
            stderr=None,
        )
        if output is None:
            raise CommandSkippedError(
                "The command `poetry --version` was not executed"
                " (a possible cause is specifying `--no-install`)"
            )

        assert isinstance(output, str)  # noqa: S101

        match = VERSION_PATTERN.search(output)
        if match:
            self._version = match.group()
            return self._version

        raise RuntimeError("Cannot parse output of `poetry --version`")

    @property
    def has_dependency_groups(self) -> bool:
        """Return True if Poetry version supports dependency groups."""
        version = tuple(int(part) for part in self.version.split(".")[:2])
        return version >= (1, 2)

    @property
    def config(self) -> Config:
        """Return the package configuration."""
        if self._config is None:
            self._config = Config(self.project)
        return self._config

    def export(self) -> str:
        """Export the lock file to requirements format.

        Returns:
            The generated requirements as text.

        Raises:
            CommandSkippedError: The command `poetry export` was not executed.
        """
        dependency_groups = (
            [f"--with={group}" for group in self.config.dependency_groups]
            if self.has_dependency_groups
            else ["--dev"]
        )

        output = self.session.run_always(
            "poetry",
            "export",
            "--format=requirements.txt",
            *dependency_groups,
            *[f"--extras={extra}" for extra in self.config.extras],
            "--without-hashes",
            external=True,
            silent=True,
            stderr=None,
        )

        if output is None:
            raise CommandSkippedError(  # pragma: no cover
                "The command `poetry export` was not executed"
                " (a possible cause is specifying `--no-install`)"
            )

        assert isinstance(output, str)  # noqa: S101

        def _stripwarnings(lines: Iterable[str]) -> Iterator[str]:
            for line in lines:
                if line.startswith("Warning:"):
                    print(line, file=sys.stderr)
                    continue
                yield line

        return "".join(_stripwarnings(output.splitlines(keepends=True)))

    def build(self, *, format: str) -> str:
        """Build the package.

        The filename of the archive is retrieved from the output of
        ``ProjectBuilder.build()``.

        Args:
            format: The distribution format, either wheel or sdist.

        Returns:
            The full path to the built distribution.
        """
        if not isinstance(format, DistributionFormat):
            format = DistributionFormat(format)

        with DefaultIsolatedEnv() as env:
            env.install(self.config.build_system_requires)
            builder = build.ProjectBuilder(
                self.project,
                python_executable=env.python_executable,
            )

            return builder.build(distribution=format.value, output_directory="dist")
