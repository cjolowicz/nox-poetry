"""Using Poetry in Nox sessions.

This package provides a facility to monkey-patch Nox so ``session.install``
installs packages at the versions specified in the Poetry lock file, and
``"."`` is replaced by a wheel built from the local package.
See :mod:`nox_poetry.patch`.

It also provides helper functions that allow more fine-grained control:

- :func:`install`
- :func:`build_package`
- :func:`export_requirements`

Two constants are defined to specify the format for distribution archives:

- :const:`WHEEL`
- :const:`SDIST`
"""
from nox_poetry.core import build_package
from nox_poetry.core import export_requirements
from nox_poetry.core import install
from nox_poetry.core import installroot
from nox_poetry.poetry import DistributionFormat


#: A wheel archive.
WHEEL = DistributionFormat.WHEEL

#: A source archive.
SDIST = DistributionFormat.SDIST

__all__ = [
    "build_package",
    "export_requirements",
    "install",
    "installroot",
    "SDIST",
    "WHEEL",
]
