nox-poetry
==========

|PyPI| |Python Version| |License|

|Read the Docs| |Tests| |Codecov|

|pre-commit| |Black|

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


Helper functions for using Poetry_ inside Nox_ sessions


Installation
------------

You can install ``nox-poetry`` via pip_ from the Python Package Index:

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

- Use ``nox_poetry.install_package(session)`` to install your own package.
- Use ``nox_poetry.install(session, *args)`` to install third-party packages.
- Packages installed like this must be declared as development dependencies using Poetry.

For example, the following Nox session runs your test suite:

.. code:: python

   # noxfile.py
   import nox
   from nox.sessions import Session
   from nox_poetry import install, install_package

   @nox.session
   def tests(session: Session) -> None:
       """Run the test suite."""
       install_package(session)
       install(session, "pytest")
       session.run("pytest", *session.posargs)


Why?
----

Compare the session above to one written without this package:

.. code:: python

   @nox.session
   def tests(session: Session) -> None:
       """Run the test suite."""
       session.install(".")
       session.install("pytest")
       session.run("pytest", *session.posargs)

This session has several problems:

- Poetry is installed as a build backend every time.
- Package dependencies are only constrained by the wheel metadata, not by the lock file (*pinned*).
- The ``pytest`` dependency is not constrained at all.

You can solve these issues by declaring ``pytest`` as a development dependency,
and installing your package and its dependencies using ``poetry install``:

.. code:: python

   @nox.session
   def tests(session: Session) -> None:
       """Run the test suite."""
       session.run("poetry", "install", external=True)
       session.run("pytest", *session.posargs)

Unfortunately, this approach creates problems of its own:

- Checks run against an editable installation of your package,
  i.e. your local copy of the code, instead of the installed wheel your users see.
- The package is installed, as well as all of its core and development dependencies.
  This is wasteful when you only need to run ``black`` or ``flake8``.
  It also goes against the idea of running checks in isolated environments.
- Poetry may decide to install packages into its own virtual environment instead of the one provided by Nox.

``nox-poetry`` uses a third approach.
Third-party packages are installed by exporting the lock file in ``requirements.txt`` format,
and passing it as a `constraints file`_ to pip.
When installing your own package, Poetry is used to build a wheel, which is then installed by pip.
This approach has some advantages:

- You can declare tools like ``pytest`` as development dependencies in Poetry.
- Dependencies are pinned by Poetry's lock file, making checks predictable and deterministic.
- You can run checks against an installed wheel, instead of your local copy of the code.
- Every tool can run in an isolated environment with minimal dependencies.
- No need to install your package with all its dependencies if all you need is some linter.

For more details, take a look at `this article`__.

__ https://cjolowicz.github.io/posts/hypermodern-python-03-linting/#managing-dependencies-in-nox-sessions-with-poetry


API
---

``nox_poetry.install(session, *args)``:
   Install development dependencies into a Nox session using Poetry.

   The ``nox_poetry.install`` function
   installs development dependencies into a Nox session,
   using the versions specified in Poetry's lock file.
   The function arguments are the same as those for `nox.sessions.Session.install`_:
   The first argument is the ``Session`` object,
   and the remaining arguments are command-line arguments for `pip install`_,
   typically just the package or packages to be installed.

``nox_poetry.install_package(session)``:
   Install the package into a Nox session using Poetry.

   The ``nox_poetry.install_package`` function
   installs your package into a Nox session,
   including the core dependencies as specified in Poetry's lock file.
   This is done by building a wheel from the package,
   and installing it using pip_.
   Dependencies are installed in the same way as in the ``nox_poetry.install`` function,
   i.e. using a constraints file.
   Its only argument is the ``Session`` object from Nox.


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
