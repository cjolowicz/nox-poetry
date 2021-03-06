nox-poetry
==========

|Status| |PyPI| |Python Version| |License|

|Read the Docs| |Tests| |Codecov|

|pre-commit| |Black|

.. |Status| image:: https://badgen.net/badge/status/alpha/d8624d
   :target: https://badgen.net/badge/status/alpha/d8624d
   :alt: Project Status
.. |PyPI| image:: https://img.shields.io/pypi/v/nox-poetry.svg
   :target: https://pypi.org/project/nox-poetry/
   :alt: PyPI
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/nox-poetry
   :target: https://pypi.org/project/nox-poetry
   :alt: Python Version
.. |License| image:: https://img.shields.io/pypi/l/nox-poetry
   :target: https://opensource.org/licenses/MIT
   :alt: License
.. |Read the Docs| image:: https://img.shields.io/readthedocs/nox-poetry/latest.svg?label=Read%20the%20Docs
   :target: https://nox-poetry.readthedocs.io/
   :alt: Read the documentation at https://nox-poetry.readthedocs.io/
.. |Tests| image:: https://github.com/cjolowicz/nox-poetry/workflows/Tests/badge.svg
   :target: https://github.com/cjolowicz/nox-poetry/actions?workflow=Tests
   :alt: Tests
.. |Codecov| image:: https://codecov.io/gh/cjolowicz/nox-poetry/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/cjolowicz/nox-poetry
   :alt: Codecov
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Black


Use Poetry_ inside Nox_ sessions

This package provides a drop-in replacement for ``session.install`` in Nox sessions.
It modifies its behavior in two ways:

- Packages are pinned to the versions specified in Poetry's lock file.
- The argument ``"."`` is replaced by a wheel built from the package.


Installation
------------

Install ``nox-poetry`` from the Python Package Index:

.. code:: console

   $ pip install nox-poetry


**Important:**
This package must be installed into the same environment that Nox is run from.
If you installed Nox using pipx_,
use the following command to install this package into the same environment:

.. code:: console

   $ pipx inject nox nox-poetry


Usage
-----

Import ``nox_poetry.patch`` at the top of your ``noxfile.py``.

``nox-poetry`` intercepts calls to ``session.install``
and uses Poetry to export a `constraints file`_ and build the package behind the scenes.
All packages installed in Nox sessions must be managed as dependencies in Poetry.

For example, the following Nox session runs your test suite:

.. code:: python

   # noxfile.py
   import nox
   import nox_poetry.patch
   from nox.sessions import Session

   @nox.session
   def tests(session: Session) -> None:
       """Run the test suite."""
       session.install(".")
       session.install("pytest")
       session.run("pytest")

More precisely, the session builds a wheel from the local package,
installs the wheel as well as the ``pytest`` package, and
invokes ``pytest`` to run the test suite against the installation.

If you prefer a more explicit approach,
invoke ``nox_poetry.install`` and ``nox_poetry.installroot`` instead of ``session.install``.
Use the ``nox_poetry.WHEEL`` or ``nox_poetry.SDIST`` constants to specify the distribution format for the local package.

Here is the example above using the more explicit approach:

.. code:: python

   # noxfile.py
   import nox
   import nox_poetry
   from nox.sessions import Session

   @nox.session
   def tests(session: Session) -> None:
       """Run the test suite."""
       nox_poetry.installroot(session, distribution_format=nox_poetry.WHEEL)
       #nox_poetry.install(session, ".")  # this is equivalent to the statement above
       nox_poetry.install(session, "pytest")
       session.run("pytest")


Why?
----

Consider what would happen in the first version without the line importing ``nox-poetry.patch``:

- Package dependencies would only be constrained by the wheel metadata, not by the lock file.
  In other words, their versions would not be *pinned*.
- The ``pytest`` dependency would not be constrained at all.
- Poetry would be installed as a build backend every time
  (although this could be avoided by passing the option ``--no-build-isolation``).

Unpinned dependencies mean that your checks are not reproducible and deterministic,
which can lead to surprises in Continuous Integration and when collaborating with others.
You can solve these issues by declaring ``pytest`` as a development dependency,
and installing your package and its dependencies using ``poetry install``:

.. code:: python

   @nox.session
   def tests(session: Session) -> None:
       """Run the test suite."""
       session.run("poetry", "install", external=True)
       session.run("pytest")

Unfortunately, this approach comes with its own set of problems:

- Checks run against an editable installation of your package,
  i.e. your local copy of the code, instead of the installed wheel your users see.
  In the best case, any mistakes will still be caught during Continuous Integration.
  In the worst case, you publish a buggy release because you forgot to commit some changes.
- The package is installed, as well as all of its core and development dependencies,
  no matter which tools a session actually runs.
  Code formatters or linters, for example, don't need your package installed at all.
  Besides being wasteful, it goes against the idea of running checks in isolated environments.

``nox-poetry`` uses a third approach:

- Installations are performed by pip, via the ``session.install`` method.
- When installing your own package, Poetry is used to build a wheel, which is passed to pip.
- When installing third-party packages, Poetry is used to export a `constraints file`_,
  which is passed to pip along with the packages.
  The constraints file ensures that package versions are pinned by the lock file,
  without forcing an installation of every listed dependency and sub-dependency.

In summary, this approach brings the following advantages:

- You can manage tools like ``pytest`` as development dependencies in Poetry.
- Dependencies are pinned by Poetry's lock file, making checks predictable and deterministic.
- You can run checks against an installed wheel, instead of your local copy of the code.
- Every tool can run in an isolated environment with minimal dependencies.
- No need to install your package with all its dependencies if all you need is some linter.

For more details, take a look at `this article`__.

__ https://cjolowicz.github.io/posts/hypermodern-python-03-linting/#managing-dependencies-in-nox-sessions-with-poetry


Contributing
------------

Contributions are very welcome.
To learn more, see the `Contributor Guide`_.


License
-------

``nox-poetry`` is free and open source software,
distributed under the terms of the MIT_ license.


Issues
------

If you encounter any problems,
please `file an issue`_ along with a detailed description.


Credits
-------

This project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.


.. _@cjolowicz: https://github.com/cjolowicz
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python
.. _MIT: http://opensource.org/licenses/MIT
.. _Nox: https://nox.thea.codes/
.. _Poetry: https://python-poetry.org/
.. _constraints file: https://pip.pypa.io/en/stable/user_guide/#constraints-files
.. _file an issue: https://github.com/cjolowicz/nox-poetry/issues
.. _nox.sessions.Session.install: https://nox.thea.codes/en/stable/config.html#nox.sessions.Session.install
.. _nox.sessions.Session.run: https://nox.thea.codes/en/stable/config.html#nox.sessions.Session.run
.. _pip install: https://pip.pypa.io/en/stable/reference/pip_install/
.. _pip: https://pip.pypa.io/
.. _pipx: https://pipxproject.github.io/pipx/
.. github-only
.. _Contributor Guide: CONTRIBUTING.rst
