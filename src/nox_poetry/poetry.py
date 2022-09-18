"""Poetry interface."""
import sys
from enum import Enum
from importlib import metadata
from pathlib import Path
from typing import Any
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple

import tomlkit
from nox.sessions import Session
from packaging.version import Version


POETRY_VERSION = Version(metadata.version("poetry"))
POETRY_VERSION_1_2_0 = Version("1.2.0")


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
        self._config = data["tool"]["poetry"]

    @property
    def name(self) -> str:
        """Return the package name."""
        name = self._config["name"]
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


class Poetry:
    """Helper class for invoking Poetry inside a Nox session.

    Attributes:
        session: The Session object.
    """

    def __init__(self, session: Session) -> None:
        """Initialize."""
        self.session = session
        self._config: Optional[Config] = None

    @property
    def config(self) -> Config:
        """Return the package configuration."""
        if self._config is None:
            self._config = Config(Path.cwd())
        return self._config

    def export(
        self,
        *,
        extras: bool = True,
        with_hashes: bool = False,
        include_groups: Tuple[str] = ("dev",),
        exclude_groups: Tuple[str] = (),
    ) -> str:
        """Export the lock file to requirements format.

        Args:
            extras: Whether to include package extras.
            with_hashes: Whether to include hashes in the output.
            include_groups: The groups to include.
            exclude_groups: The groups to exclude.

        Returns:
            The generated requirements as text.

        Raises:
            CommandSkippedError: The command `poetry export` was not executed.
        """
        args = [
            "poetry",
            "export",
            "--format=requirements.txt",
        ]

        if not with_hashes:
            args.append("--without-hashes")

        if extras:
            args.extend(f"--extras={extra}" for extra in self.config.extras)

        if POETRY_VERSION >= POETRY_VERSION_1_2_0:
            if include_groups:
                args.append(f"--with={','.join(include_groups)}")

            if exclude_groups:
                args.append(f"--without={','.join(exclude_groups)}")
        else:
            args.append("--dev")

        output = self.session.run_always(
            *args,
            external=True,
            silent=True,
            stderr=None,
        )

        if output is None:
            errmsg = (
                "The command `poetry export` was not executed"
                " (a possible cause is specifying `--no-install`)"
            )
            raise CommandSkippedError(errmsg)

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
            stderr=None,
        )

        if output is None:
            errmsg = (
                "The command `poetry build` was not executed"
                " (a possible cause is specifying `--no-install`)"
            )
            raise CommandSkippedError(errmsg)

        assert isinstance(output, str)  # noqa: S101
        return output.split()[-1]
