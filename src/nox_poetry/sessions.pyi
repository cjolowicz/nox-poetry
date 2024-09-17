"""Type stubs for nox_poetry.sessions."""

from pathlib import Path
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Sequence
from typing import overload

import nox.sessions
import nox.virtualenv

Python = str | Sequence[str] | bool | None

class _PoetrySession:
    def install(self, *args: str, **kwargs: Any) -> None: ...
    def installroot(
        self, *, distribution_format: str = ..., extras: Iterable[str] = ...
    ) -> None: ...
    def export_requirements(self) -> Path: ...
    def build_package(self, *, distribution_format: str = ...) -> str: ...

class Session(nox.Session):
    def __init__(self, session: nox.Session) -> None: ...
    poetry: _PoetrySession

SessionFunction = Callable[..., None]
SessionDecorator = Callable[[SessionFunction], SessionFunction]

@overload
def session(__func: SessionFunction) -> SessionFunction: ...
@overload
def session(
    __func: None = ...,
    python: Python = ...,
    py: Python = ...,
    reuse_venv: bool | None = ...,
    name: str | None = ...,
    venv_backend: Any = ...,
    venv_params: Any = ...,
    tags: Sequence[str] = ...,
) -> SessionDecorator: ...
