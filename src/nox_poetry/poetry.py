"""Poetry interface."""
from pathlib import Path

from nox.sessions import Session


class Poetry:
    """Helper class for invoking Poetry inside a Nox session.

    Attributes:
        session: The Session object.
    """

    def __init__(self, session: Session) -> None:
        """Initialize."""
        self.session = session

    def export(self, path: Path, *, dev: bool) -> None:
        """Export the lock file to requirements format.

        Args:
            path: The destination path.
            dev: If True, include development dependencies.
        """
        options = ["--dev"] if dev else []
        self.session.run(
            "poetry",
            "export",
            "--format=requirements.txt",
            f"--output={path}",
            *options,
            external=True,
        )

    def build(self, *args: str) -> str:
        """Build the package.

        Args:
            args: Command-line arguments for ``poetry build``.

        Returns:
            The basename of the wheel built by Poetry.
        """
        output = self.session.run(
            "poetry", "build", *args, external=True, silent=True, stderr=None
        )
        assert isinstance(output, str)  # noqa: S101
        return output.split()[-1]
