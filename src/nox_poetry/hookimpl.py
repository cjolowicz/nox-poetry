"""Hook implementations."""
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from nox.hookspec import Done
from nox.hookspec import hookimpl
from nox.sessions import Session

from nox_poetry import build_package
from nox_poetry import export_requirements
from nox_poetry import WHEEL


@hookimpl
def nox_session_install(
    session: Session, args: List[str], kwargs: Dict[str, Any]
) -> Optional[Done]:
    """Implement the `nox_session_install` hook."""
    requirements = export_requirements(session)
    args.insert(0, f"--constraint={requirements}")

    if "." in args:
        package = build_package(session, distribution_format=WHEEL)
        session.run("pip", "uninstall", "--yes", package, silent=True)
        args[:] = [package if arg == "." else arg for arg in args]

    return None
