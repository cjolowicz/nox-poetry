"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """nox-poetry."""


if __name__ == "__main__":
    main(prog_name="nox-poetry")  # pragma: no cover
