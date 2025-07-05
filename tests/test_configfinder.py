import pytest

from configfinder.configfinder import (
    ConfigNotFound,
    config_finder,
    config_walker,
    find_file,
)


def test_file_finder():
    with pytest.raises(FileNotFoundError):
        find_file("wrongfile.ext")

    find_file("pyproject.toml")


def test_config_walker():
    dictionary_test = {
        "a": {
            "b1": {
                "c": 1,
                "d": 2,
            },
            "b2": {
                "c": 10,
                "d": 22,
            },
        },
    }

    assert config_walker(dictionary_test, ["a", "b1"]) == {
        "c": 1,
        "d": 2,
    }

    assert config_walker(dictionary_test, ["a", "b2"]) == {
        "c": 10,
        "d": 22,
    }

    with pytest.raises(ConfigNotFound):
        config_walker(dictionary_test, ["a", "b3"])

    with pytest.raises(ConfigNotFound):
        config_walker(dictionary_test, ["b", "b3"])


def test_config_finder():
    with pytest.raises(NotImplementedError):
        config_finder("somefile.ext", ["a"])
