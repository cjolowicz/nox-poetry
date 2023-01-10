"""Functional tests for ``installroot``."""
import base64
import os
import tempfile
from functools import partial
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from typing import Any
from typing import Tuple

import nox_poetry
from tests.functional.conftest import Project
from tests.functional.conftest import list_packages
from tests.functional.conftest import run_nox_with_noxfile


def test_wheel(project: Project) -> None:
    """It builds and installs a wheel from the local package."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.poetry.installroot(distribution_format=nox_poetry.WHEEL)

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_wheel_with_extras(project: Project) -> None:
    """It installs the extra."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.poetry.installroot(
            distribution_format=nox_poetry.WHEEL, extras=["pygments"]
        )

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [
        project.package,
        *project.dependencies,
        project.get_dependency("pygments"),
    ]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_sdist(project: Project) -> None:
    """It builds and installs an sdist from the local package."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.poetry.installroot(distribution_format=nox_poetry.SDIST)

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [project.package, *project.dependencies]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


def test_sdist_with_extras(project: Project) -> None:
    """It installs the extra."""

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        """Install the local package."""
        session.poetry.installroot(
            distribution_format=nox_poetry.SDIST, extras=["pygments"]
        )

    run_nox_with_noxfile(project, [test], [nox_poetry])

    expected = [
        project.package,
        *project.dependencies,
        project.get_dependency("pygments"),
    ]
    packages = list_packages(project, test)

    assert set(expected) == set(packages)


class AuthenticatingSimpleHTTPRequestHandler(SimpleHTTPRequestHandler):
    """A version of SimpleHTTPRequestHandler that throws a 401 error if the request
    does not come with the specified username and password sent via basic http
    authentication. See RFC 7617 for details. This is designed for tests, and does not
    offer any real protection."""

    def __init__(
        self,
        request: Any,
        client_address: Any,
        server: Any,
        directory: Any,
        username: str,
        password: str,
    ):
        authstring = f"{username}:{password}"
        self.encoded_authstring = base64.b64encode(authstring.encode("utf-8")).decode(
            "utf-8"
        )
        super().__init__(request, client_address, server, directory=directory)

    def is_authenticated(self) -> bool:
        if "Authorization" in self.headers:
            return bool(
                self.headers["Authorization"] == f"Basic {self.encoded_authstring}"
            )
        return False

    def send_auth_error(self) -> None:
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="everything"')
        self.end_headers()

    def do_GET(self) -> None:
        if self.is_authenticated():
            super().do_GET()
        else:
            self.send_auth_error()

    def do_HEAD(self) -> None:
        if self.is_authenticated():
            super().do_HEAD()
        else:
            self.send_auth_error()


def get_pyproject(address: str) -> str:
    return f"""\
[tool.poetry]
name = "foo"
version = "0.1.1"
description = "foo"
authors = []

[tool.poetry.dependencies]
"thispackagedoesnotexist" = {{version = "0.1.0", source = "baz"}}

[[tool.poetry.source]]
name = "baz"
url = "{address}"
default = false
secondary = true
"""


def serve_directory_with_http_and_auth(
    directory: str, username: str, password: str
) -> Tuple[HTTPServer, str]:
    hostname = "localhost"
    port = 0
    handler = partial(
        AuthenticatingSimpleHTTPRequestHandler,
        directory=directory,
        username=username,
        password=password,
    )
    httpd = HTTPServer((hostname, port), handler, False)
    httpd.timeout = 0.5

    httpd.server_bind()
    address = "http://%s:%d" % (hostname, httpd.server_port)

    httpd.server_activate()

    def serve_forever(httpd: HTTPServer) -> None:
        with httpd:  # to make sure httpd.server_close is called
            httpd.serve_forever()

    thread = Thread(target=serve_forever, args=(httpd,))
    thread.setDaemon(True)
    thread.start()

    return httpd, address


def test_dependency_from_private_index(shared_datadir: Path) -> None:
    input_dir = tempfile.TemporaryDirectory()

    server, address = serve_directory_with_http_and_auth(
        str(shared_datadir / "simple503"), username="alice", password="password"
    )

    with open(os.path.join(input_dir.name, "pyproject.toml"), "w") as pyproject_file:
        pyproject_file.write(get_pyproject(address))
    (Path(input_dir.name) / "foo").mkdir()
    (Path(input_dir.name) / "foo" / "__init__.py").touch()

    @nox_poetry.session
    def test(session: nox_poetry.Session) -> None:
        session.run_always(
            "poetry",
            "config",
            "http-basic.baz",
            "alice",
            "password",
            external=True,
            silent=True,
            stderr=None,
        )
        session.run_always("poetry", "lock")
        session.poetry.installroot()

    project = Project(Path(input_dir.name))

    try:
        run_nox_with_noxfile(project, [test], [nox_poetry])

    finally:
        server.shutdown()
