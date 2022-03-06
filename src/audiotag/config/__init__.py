from pathlib import Path
import configparser
from appdirs import AppDirs

from prompt_toolkit.enums import EditingMode


class InvalidConfigException(Exception):
    """Exception for invalid config values"""

    pass


_dirs = AppDirs(appname="audiotag")
_config_file = Path(_dirs.user_config_dir) / "config.ini"

_config = configparser.ConfigParser()
_config.read(_config_file)

_allowed_editing_modes = ["emacs", "vi"]

_config_editing_mode = _config.get("global", "editing_mode", fallback="emacs")
if _config_editing_mode not in _allowed_editing_modes:
    raise InvalidConfigException(
        f"Invalid value for config.editing_mode '{_config_editing_mode}'. "
        + f"Possible values [{', '.join(_allowed_editing_modes)}]"
    )
editing_mode = EditingMode(_config_editing_mode.upper())

value_sep = _config.get("global", "value_separator", fallback="/")
if len(value_sep) != 1:
    raise InvalidConfigException(
        f"Invalid value for config.value_sep '{value_sep}'. "
        + "Separator must b a single character."
    )


pattern_single_disc = _config.get("global", "pattern_single_disc", fallback="{N} - {T}")
pattern_multi_disc = _config.get(
    "global", "pattern_multi_disc", fallback="{D}-{N} - {T}"
)
