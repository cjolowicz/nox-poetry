"""Type stubs for nox_poetry.sessions."""
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Mapping
from typing import NoReturn
from typing import Optional
from typing import Sequence
from typing import TypeVar
from typing import Union
from typing import overload

import nox.sessions
import nox.virtualenv

Python = Optional[Union[str, Sequence[str], bool]]

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
    reuse_venv: Optional[bool] = ...,
    name: Optional[str] = ...,
    venv_backend: Any = ...,
    venv_params: Any = ...,
) -> SessionDecorator: ...
