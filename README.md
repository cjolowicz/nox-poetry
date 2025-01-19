# nox-poetry

[![PyPI](https://img.shields.io/pypi/v/nox-poetry.svg)][pypi_]
[![Python Version](https://img.shields.io/pypi/pyversions/nox-poetry)][python version]
[![License](https://img.shields.io/pypi/l/nox-poetry)][license]

[![Read the documentation at https://nox-poetry.readthedocs.io/](https://img.shields.io/readthedocs/nox-poetry/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/cjolowicz/nox-poetry/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/cjolowicz/nox-poetry/branch/main/graph/badge.svg)][codecov]

[pypi_]: https://pypi.org/project/nox-poetry/
[python version]: https://pypi.org/project/nox-poetry
[read the docs]: https://nox-poetry.readthedocs.io/
[tests]: https://github.com/cjolowicz/nox-poetry/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/cjolowicz/nox-poetry

Use [Poetry] inside [Nox] sessions

This package provides a drop-in replacement for the `nox.session` decorator,
and for the `nox.Session` object passed to user-defined session functions.
This enables `session.install` to install packages at the versions specified in the Poetry lock file.

```python
from nox_poetry import session

@session(python=["3.10", "3.9"])
def tests(session):
    session.install("pytest", ".")
    session.run("pytest")
```

**Disclaimer:** _This project is not affiliated with Nox, and not an official Nox plugin._

## Installation

Install `nox-poetry` from the Python Package Index:

```console
$ pip install nox-poetry
```

**Important:**
This package must be installed into the same environment that Nox is run from.
If you installed Nox using [pipx],
use the following command to install this package into the same environment:

```console
$ pipx inject nox nox-poetry
```

`nox-poetry` relies on functionality from
[`poetry-export-plugin`](https://github.com/python-poetry/poetry-plugin-export), which
is bundled by default in Poetry 1, but not in Poetry >= 2. In Poetry 2, define it
as a required plugin in your `pyproject.toml`:

```toml
[tool.poetry.requires-plugins]
poetry-plugin-export = ">=1.8"
```

## Requirements

- Python 3.8+
- Poetry >= 1.0.0

You need to have a Poetry installation on your system.
`nox-poetry` uses Poetry via its command-line interface.

## Usage

Import the `@session` decorator from `nox_poetry` instead of `nox`.
There is nothing else you need to do.
The `session.install` method automatically honors the Poetry lock file when installing dependencies.
This allows you to manage packages used in Nox sessions as development dependencies in Poetry.

This works because session functions are passed instances of `nox_poetry.Session`,
a proxy for `nox.Session` adding Poetry-related functionality.
Behind the scenes, nox-poetry uses Poetry to export a [constraints file] and build the package.

For more fine-grained control, additional utilities are available under the `session.poetry` attribute:

- `session.poetry.installroot(distribution_format=["wheel"|"sdist"])`
- `session.poetry.build_package(distribution_format=["wheel"|"sdist"])`
- `session.poetry.export_requirements()`

Note that `distribution_format` is a [keyword-only parameter].

Here is a comparison of the different installation methods:

- Use `session.install(...)` to install specific development dependencies, e.g. `session.install("pytest")`.
- Use `session.install(".")` (or `session.poetry.installroot()`) to install your own package.
- Use `session.run_always("poetry", "install", external=True)` to install your package with _all_ development dependencies.

Please read the next section for the tradeoffs of each method.

## Why?

Let's look at an example:

```python
from nox_poetry import session

@session(python=["3.10", "3.9"])
def tests(session):
    session.install("pytest", ".")
    session.run("pytest")
```

This session performs the following steps:

- Build a wheel from the local package.
- Install the wheel as well as the `pytest` package.
- Invoke `pytest` to run the test suite against the installation.

Consider what would happen in this session
if we had imported `@session` from `nox` instead of `nox_poetry`:

- Package dependencies would only be constrained by the wheel metadata, not by the lock file.
  In other words, their versions would not be _pinned_.
- The `pytest` dependency would not be constrained at all.
- Poetry would be installed as a build backend every time.

Unpinned dependencies mean that your checks are not reproducible and deterministic,
which can lead to surprises in Continuous Integration and when collaborating with others.
You can solve these issues by declaring `pytest` as a development dependency,
and installing your package and its dependencies using `poetry install`:

```python
@nox.session
def tests(session: Session) -> None:
    """Run the test suite."""
    session.run_always("poetry", "install", external=True)
    session.run("pytest")
```

Unfortunately, this approach comes with its own set of problems:

- Checks run against an editable installation of your package,
  i.e. your local copy of the code, instead of the installed wheel your users see.
  In the best case, any mistakes will still be caught during Continuous Integration.
  In the worst case, you publish a buggy release because you forgot to commit some changes.
- The package is installed, as well as all of its core and development dependencies,
  no matter which tools a session actually runs.
  Code formatters or linters, for example, don't need your package installed at all.
  Besides being wasteful, it goes against the idea of running checks in isolated environments.

`nox-poetry` uses a third approach:

- Installations are performed by pip, via the `session.install` method.
- When installing your own package, Poetry is used to build a wheel, which is passed to pip.
- When installing third-party packages, Poetry is used to export a [constraints file],
  which is passed to pip along with the packages.
  The constraints file ensures that package versions are pinned by the lock file,
  without forcing an installation of every listed dependency and sub-dependency.

In summary, this approach brings the following advantages:

- You can manage tools like `pytest` as development dependencies in Poetry.
- Dependencies are pinned by Poetry's lock file, making checks predictable and deterministic.
- You can run checks against an installed wheel, instead of your local copy of the code.
- Every tool can run in an isolated environment with minimal dependencies.
- No need to install your package with all its dependencies if all you need is some linter.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_nox-poetry_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[nox]: https://nox.thea.codes/
[poetry]: https://python-poetry.org/
[constraints file]: https://pip.pypa.io/en/stable/user_guide/#constraints-files
[file an issue]: https://github.com/cjolowicz/nox-poetry/issues
[keyword-only parameter]: https://docs.python.org/3/glossary.html#keyword-only-parameter
[nox.sessions.session.install]: https://nox.thea.codes/en/stable/config.html#nox.sessions.Session.install
[nox.sessions.session.run]: https://nox.thea.codes/en/stable/config.html#nox.sessions.Session.run
[pip install]: https://pip.pypa.io/en/stable/reference/pip_install/
[pip]: https://pip.pypa.io/
[pipx]: https://pipxproject.github.io/pipx/

<!-- github-only -->

[license]: https://github.com/cjolowicz/nox-poetry/blob/main/LICENSE
[contributor guide]: https://github.com/cjolowicz/nox-poetry/blob/main/CONTRIBUTING.md
