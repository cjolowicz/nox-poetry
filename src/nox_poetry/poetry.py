"""Poetry interface."""
from enum import Enum
from pathlib import Path

from nox.sessions import Session


class DistributionFormat(Enum):
    """Type of distribution archive for a Python package."""

    WHEEL = "wheel"
    SDIST = "sdist"


class Poetry:
    """Helper class for invoking Poetry inside a Nox session.

    Attributes:
        session: The Session object.
    """

    def __init__(self, session: Session) -> None:
        """Initialize."""
        self.session = session

    def export(self, path: Path) -> None:
        """Export the lock file to requirements format.

        Args:
            path: The destination path.
        """
        self.session.run(
            "poetry",
            "export",
            "--format=requirements.txt",
            f"--output={path}",
            "--dev",
            external=True,
        )

    def build(self, *, format: DistributionFormat) -> str:
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
        """
        output = self.session.run(
            "poetry",
            "build",
            f"--format={format.value}",
            external=True,
            silent=True,
            stderr=None,
        )
        assert isinstance(output, str)  # noqa: S101
        return output.split()[-1]
