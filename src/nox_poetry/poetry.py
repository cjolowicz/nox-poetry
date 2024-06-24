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

import tomlkit
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


VERSION_PATTERN = re.compile(r"[0-9]+(\.[0-9+])+[-+.0-9a-zA-Z]+")


class Poetry:
    """Helper class for invoking Poetry inside a Nox session.

    Attributes:
        session: The Session object.
    """

    def __init__(self, session: Session) -> None:
        """Initialize."""
        self.session = session
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
            stderr=None,  # type: ignore[arg-type]
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
            self._config = Config(Path.cwd())
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
            stderr=None,  # type: ignore[arg-type]
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

        The filename of the archive is extracted from the output Poetry writes
        to standard output, which currently looks like this::

           Building foobar (0.1.0)
            - Building wheel
            - Built foobar-0.1.0-py3-none-any.whl

        This is brittle, but it has the advantage that it does not rely on
        assumptions such as having a clean ``dist`` directory, or
        reconstructing the filename from the package metadata. (Poetry does not
        use PEP 440 for version numbers, so this is non-trivial.)

        Args:
            format: The distribution format, either wheel or sdist.

        Returns:
            The basename of the wheel built by Poetry.

        Raises:
            CommandSkippedError: The command `poetry build` was not executed.
        """
        if not isinstance(format, DistributionFormat):
            format = DistributionFormat(format)

        output = self.session.run_always(
            "poetry",
            "build",
            f"--format={format.value}",
            "--no-ansi",
            external=True,
            silent=True,
            stderr=None,  # type: ignore[arg-type]
        )

        if output is None:
            raise CommandSkippedError(
                "The command `poetry build` was not executed"
                " (a possible cause is specifying `--no-install`)"
            )

        assert isinstance(output, str)  # noqa: S101
        return output.split()[-1]
