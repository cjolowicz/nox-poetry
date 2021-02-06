"""Unit tests for the sessions module."""
from typing import Callable
from typing import Iterator

import nox._options
import nox.manifest
import nox.registry
import pytest

import nox_poetry


IterSessions = Callable[[], Iterator[str]]


@pytest.fixture
def iter_sessions() -> IterSessions:
    """List the registered nox sessions."""
    nox.registry._REGISTRY.clear()

    def _iter_sessions() -> Iterator[str]:
        options = nox._options.options.namespace()
        manifest = nox.manifest.Manifest(nox.registry.get(), options)
        for session in manifest:
            yield session.name
            yield from session.signatures

    return _iter_sessions


def test_register(iter_sessions: IterSessions) -> None:
    """It registers the session function."""

    @nox_poetry.session
    def tests(session: nox_poetry.Session) -> None:
        pass

    assert "tests" in iter_sessions()


def test_name(iter_sessions: IterSessions) -> None:
    """It registers the session function under the given name."""

    @nox_poetry.session(name="tests-renamed")
    def tests(session: nox_poetry.Session) -> None:
        pass

    assert "tests-renamed" in iter_sessions()


def test_wrapper(session: nox.Session) -> None:
    """It invokes the session function."""
    calls = []

    @nox_poetry.session
    def tests(proxy: nox_poetry.Session) -> None:
        calls.append(proxy)

    tests(session)

    [proxy] = calls

    assert proxy._session is session


@pytest.fixture
def proxy(session: nox.Session) -> nox_poetry.Session:
    """Fixture for session proxy."""
    return nox_poetry.Session(session)


def test_session_getattr(proxy: nox_poetry.Session) -> None:
    """It delegates to the real session."""
    assert proxy.create_tmp()


def test_session_install(proxy: nox_poetry.Session) -> None:
    """It installs the package."""
    proxy.install(".")


def test_session_installroot(proxy: nox_poetry.Session) -> None:
    """It installs the package."""
    proxy.poetry.installroot(distribution_format=nox_poetry.WHEEL)


def test_session_export_requirements(proxy: nox_poetry.Session) -> None:
    """It exports the requirements."""
    proxy.poetry.export_requirements()


def test_session_build_package(proxy: nox_poetry.Session) -> None:
    """It exports the requirements."""
    proxy.poetry.build_package(distribution_format=nox_poetry.SDIST)
