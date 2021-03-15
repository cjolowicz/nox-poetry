"""Unit tests for the sessions module."""
from typing import Callable
from typing import Iterator

import nox._options
import nox.manifest
import nox.registry
import pytest

import nox_poetry
from nox_poetry.sessions import to_constraints  # type: ignore[attr-defined]


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


def test_python(iter_sessions: IterSessions) -> None:
    """It registers the session function for every python version."""

    @nox_poetry.session(python=["3.8", "3.9"])
    def tests(session: nox_poetry.Session) -> None:
        pass

    assert set(iter_sessions()) == {"tests", "tests-3.8", "tests-3.9"}


def test_parametrize(iter_sessions: IterSessions) -> None:
    """It registers the session function for every parameter."""

    @nox_poetry.session
    @nox.parametrize("sphinx", ["2.4.4", "3.4.3"])
    def tests(session: nox_poetry.Session, sphinx: str) -> None:
        session.install(f"sphinx=={sphinx}")

    assert set(iter_sessions()) == {
        "tests",
        "tests(sphinx='2.4.4')",
        "tests(sphinx='3.4.3')",
    }


def test_wrapper(session: nox.Session) -> None:
    """It invokes the session function."""
    calls = []

    @nox_poetry.session
    def tests(proxy: nox_poetry.Session) -> None:
        calls.append(proxy)

    tests(session)

    [proxy] = calls

    assert proxy._session is session


def test_wrapper_parametrize(session: nox.Session) -> None:
    """It forwards parameters to the session function."""
    calls = []

    @nox_poetry.session
    @nox.parametrize("number", [1, 2])
    def tests(proxy: nox_poetry.Session, number: int) -> None:
        calls.append((proxy, number))

    tests(session, 1)  # type: ignore[no-untyped-call]
    tests(session, 2)  # type: ignore[no-untyped-call]

    proxies, numbers = zip(*calls)

    assert all(proxy._session is session for proxy in proxies)
    assert numbers == (1, 2)


@pytest.fixture
def proxy(session: nox.Session) -> nox_poetry.Session:
    """Fixture for session proxy."""
    return nox_poetry.Session(session)


def test_session_getattr(proxy: nox_poetry.Session) -> None:
    """It delegates to the real session."""
    # Fixed in https://github.com/theacodes/nox/pull/377
    assert proxy.virtualenv.location  # type: ignore[attr-defined]


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


@pytest.mark.parametrize(
    "requirements,expected",
    [
        ("", ""),
        (" ", ""),
        ("first @ https://github.com/hynek/first/archive/main.zip", ""),
        ("https://github.com/hynek/first/archive/main.zip", ""),
        ("first==2.0.2", "first==2.0.2"),
        ("httpx[http2]==0.17.0", "httpx==0.17.0"),
        (
            "regex==2020.10.28; python_version == '3.5'",
            'regex==2020.10.28; python_version == "3.5"',
        ),
        ("-e ../lib/foo", ""),
        (
            """
            --extra-index-url https://example.com/pypi/simple

            boltons==20.2.1
            """,
            "boltons==20.2.1",
        ),
    ],
)
def test_to_constraints(requirements: str, expected: str) -> None:
    """It converts requirements to constraints."""
    assert to_constraints(requirements) == expected


def test_invalid_constraint() -> None:
    """It raises an exception."""
    with pytest.raises(Exception):
        to_constraints("example @ /tmp/example")
