"""Unit tests for the poetry module."""
import os
import pdb
import tempfile
from functools import partial
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from typing import Any
from typing import Dict
from typing import Tuple

import nox._options
import nox.command
import nox.manifest
import nox.sessions
import pytest

from nox_poetry import poetry


def test_config_non_ascii(tmp_path: Path) -> None:
    """It decodes non-ASCII characters in pyproject.toml."""
    text = """\
[tool.poetry]
name = "África"
"""

    path = tmp_path / "pyproject.toml"
    path.write_text(text, encoding="utf-8")

    config = poetry.Config(path.parent)
    assert config.name == "África"


@pytest.fixture
def session(monkeypatch: pytest.MonkeyPatch) -> nox.Session:
    """Fixture for a Nox session."""
    registry: Dict[str, Any] = {}
    monkeypatch.setattr("nox.registry._REGISTRY", registry)

    @nox.session(venv_backend="none")
    def test(session: nox.Session) -> None:
        """Example session."""

    config = nox._options.options.namespace(posargs=[])
    [runner] = nox.manifest.Manifest(registry, config)
    runner._create_venv()

    return nox.Session(runner)


def test_export_with_warnings(
    session: nox.Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """It removes warnings from the output."""
    requirements = "first==2.0.2\n"
    warning = (
        "Warning: The lock file is not up to date with the latest changes in"
        " pyproject.toml. You may be getting outdated dependencies. Run update"
        " to update them.\n"
    )

    def _run(*args: Any, **kwargs: Any) -> str:
        return warning + requirements

    monkeypatch.setattr("nox.command.run", _run)

    output = poetry.Poetry(session).export()
    assert output == requirements


def get_pyproject(address: str) -> str:
    return f"""\
[tool.poetry]
name = "foo"
version = "0.1.0"
description = "foo"
authors = []

[tool.poetry.dependencies]
"bar" = {{version = "0.1.0", source = "baz"}}

[[tool.poetry.source]]
name = "baz"
url = "{address}"
default = false
secondary = true
"""


def serve_directory_with_http(directory: str) -> Tuple[HTTPServer, str]:
    hostname = "localhost"
    port = 0
    handler = partial(SimpleHTTPRequestHandler, directory=directory)
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


@nox.session
def test_export_with_source_credentials(
    session: nox.Session, shared_datadir: Path
) -> None:
    input_dir = tempfile.TemporaryDirectory()

    server, address = serve_directory_with_http(str(shared_datadir / "simple503"))

    with open(os.path.join(input_dir.name, "pyproject.toml"), "w") as pyproject_file:
        pyproject_file.write(get_pyproject(address))

    cwd = os.getcwd()
    try:
        os.chdir(input_dir.name)
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
        test_poetry = poetry.Poetry(session)
        resources_file = test_poetry.export()
        expected_index = "http://alice:password@" + address.lstrip("http://")
        assert f"--extra-index-url {expected_index}" in resources_file
    finally:
        os.chdir(cwd)
        server.shutdown()
