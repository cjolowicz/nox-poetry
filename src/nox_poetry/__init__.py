"""Using Poetry in Nox sessions."""
import contextlib
import tempfile
from pathlib import Path
from typing import Iterator

from nox.sessions import Session


class _Poetry:
    """Helper class for invoking Poetry inside a Nox session.

    Attributes:
        session: The Session object.
    """

    def __init__(self, session: Session) -> None:
        """Constructor."""
        self.session = session

    def install(self, *args: str) -> None:
        """Install the dependencies."""
        self.session.run("poetry", "install", *args, external=True)

    @contextlib.contextmanager
    def export(self, *args: str) -> Iterator[Path]:
        """Export the lock file to requirements format.

        Args:
            args: Command-line arguments for ``poetry export``.

        Yields:
            The path to the requirements file.
        """
        with tempfile.TemporaryDirectory() as directory:
            requirements = Path(directory) / "requirements.txt"
            self.session.run(
                "poetry",
                "export",
                *args,
                "--format=requirements.txt",
                f"--output={requirements}",
                external=True,
            )
            yield requirements

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


def install_package(session: Session) -> None:
    """Build and install the package.

    Build a wheel from the package, and install it into the virtual environment
    of the specified Nox session.

    The package requirements are installed using the versions specified in
    Poetry's lock file.

    Args:
        session: The Session object.
    """
    poetry = _Poetry(session)

    poetry.install("--no-root")
    wheel = poetry.build("--format=wheel")

    session.install("--no-deps", "--force-reinstall", f"dist/{wheel}")


def install(session: Session, *args: str) -> None:
    """Install development dependencies into the session's virtual environment.

    This function is a wrapper for nox.sessions.Session.install.

    The packages must be managed as development dependencies in Poetry.

    Args:
        session: The Session object.
        args: Command-line arguments for ``pip install``.
    """
    poetry = _Poetry(session)
    with poetry.export("--dev") as requirements:
        session.install(f"--constraint={requirements}", *args)
