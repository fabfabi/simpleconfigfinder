from pathlib import Path, PurePath
from typing import Any, Dict

import tomllib

import __main__


class ConfigNotFound(Exception):
    """will be raised when the given keys for the sub-configuration do not exist in the configuration file"""

    pass


def find_file(config_fname: str | PurePath) -> PurePath:
    """finds the configuration file

    Args:
        config_fname: the name of the configuration file"""

    directory = Path(__main__.__file__).parent

    while directory.parent != directory:
        if (directory / config_fname).exists:
            return directory / config_fname

    raise FileNotFoundError(f"'{config_fname}' was not found")


def config_walker(
    configuration_dictionary: Dict[str, Any], sub_config_keys: list[str]
) -> Dict[str, Any]:
    """goes upstream from the currently executed file and finds the file config_fname and returns the sub_config_keys"""

    for i, key in enumerate(sub_config_keys):
        if key in configuration_dictionary:
            configuration_dictionary = configuration_dictionary[key]
        else:
            raise ConfigNotFound(f"configuration {sub_config_keys[:i+1]} not found")

    return configuration_dictionary


def configfinder(
    config_fname: str | PurePath, sub_config_keys: list[str]
) -> Dict[str, Any]:
    """goes upstream from the currently executed file and finds the file config_fname and returns the sub_config_keys"""

    fname = find_file(config_fname)

    with open(fname, "rb") as file:
        configuration = tomllib.load(file)

    return config_walker(configuration, sub_config_keys)
