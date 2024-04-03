from pathlib import Path
import errno
import os
import sys
import tempfile

from configupdater import ConfigUpdater

TEST = True


if TEST:
    app_dir = Path(__file__).parent
    # User resources
    resource_path = app_dir / "resources"
    CONFIG_PATH = resource_path / "configurations.ini"
    # App resources
    ENV_PATH = app_dir / ".env" # not used
    LOG_FILE = app_dir / "logs" / "sys.log"
    APP_ICON = resource_path / "app.ico"
    TRAY_ICON = resource_path / "sys_tray.ico"
    FSL_DOC_PATH = resource_path / "fsl_stamp.pdf"
else:
    # User resources
    user_resources: Path = Path.home() / "AppData" / "Local" / "QuickDraw"
    CONFIG_PATH: Path = user_resources / "configurations.ini"
    # App resources
    LOG_FILE = user_resources / "sys.log"
    app_dir: Path = Path("C:/Program Files/QuickDraw")
    app_resources: Path = app_dir / "_internal" / "resources"
    APP_ICON: Path = app_resources / "img" / "app.ico"
    TRAY_ICON: Path = app_resources / "img" / "sys_tray.ico"
    FSL_DOC_PATH = (
        Path(__file__).parents[2]
        / "resources"
        / "forms"
        / "east_coast_forms"
        / "fsl_stamp.pdf"
    )
    ENV_PATH = Path.home() / "AppData" / "Local" / "QuickDraw" / ".env" # not used

def open_config() -> ConfigUpdater:  # GOOD
    """This is a helper to read config when called using ConfigUpdater,  an improvement on configParser."""
    open_read_update = ConfigUpdater(comment_prefixes=("^",))
    open_read_update.read(CONFIG_PATH)
    return open_read_update


#######################################################
#######################################################
################   PATH VALIDATION   ##################
#######################################################
#######################################################
ERROR_INVALID_NAME = 123
"""
Windows-specific error code indicating an invalid pathname.
"""


def validate_paths(pathnames: str|Path | list[str]|tuple[Path]) -> Path | list[Path]:
    if isinstance(pathnames, str | Path):
        if _is_path_exists_or_creatable_portable(pathnames):
            return Path(pathnames).resolve()
        else:
            raise OSError
    else:
        validated_paths = []
        for path in pathnames:
            if _is_path_exists_or_creatable_portable(path):
                validated_paths.append(Path(path).resolve())
            else:
                raise OSError
        return validated_paths


def _is_path_exists_or_creatable_portable(pathname: str) -> bool:
    """
    `True` if the passed pathname is a valid pathname on the current OS _and_
    either currently exists or is hypothetically creatable in a cross-platform
    manner optimized for POSIX-unfriendly filesystems; `False` otherwise.

    This function is guaranteed to _never_ raise exceptions.
    """
    try:
        # To prevent "os" module calls from raising undesirable exceptions on
        # invalid pathnames, __is_pathname_valid() is explicitly called first.
        return __is_pathname_valid(pathname) and (
            os.path.exists(pathname) or __is_path_sibling_creatable(pathname)
        )
    # Report failure on non-fatal filesystem complaints (e.g., connection
    # timeouts, permissions issues) implying this path to be inaccessible. All
    # other exceptions are unrelated fatal issues and should not be caught here.
    except OSError:
        return False


def __is_pathname_valid(pathname: str | Path) -> bool:
    """
    `True` if the passed pathname is a valid pathname for the current OS;
    `False` otherwise.
    """
    try:
        if not isinstance(pathname, str | Path) or not pathname:
            return False
        _, pathname = os.path.splitdrive(pathname)

        root_dirname = (
            os.environ.get("HOMEDRIVE", "C:")
            if sys.platform == "win32"
            else os.path.sep
        )
        assert os.path.isdir(root_dirname)  # ...Murphy and her ironclad Law

        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)
            except OSError as exc:
                if hasattr(exc, "winerror"):
                    if exc.winerror == ERROR_INVALID_NAME:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    except TypeError as exc:
        return False
    else:
        return True


def __is_path_sibling_creatable(pathname: str) -> bool:
    """
    `True` if the current user has sufficient permissions to create **siblings**
    (i.e., arbitrary files in the parent directory) of the passed pathname;
    `False` otherwise.
    """
    dirname = os.path.dirname(pathname) or os.getcwd()
    try:
        with tempfile.TemporaryFile(dir=dirname):
            pass
        return True
    except EnvironmentError:
        return False
