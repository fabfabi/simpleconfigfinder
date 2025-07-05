import json
from copy import deepcopy

import pytest

import __main__
from simpleconfigfinder.configfinder import (
    ConfigNotFound,
    config_finder,
    config_walker,
    find_file,
)

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


def test_file_finder(tmp_path):
    fname = "test.toml"
    file_config = tmp_path / fname
    file_python = tmp_path / "src" / "some_program.py"

    file_config.write_text("test")

    with pytest.MonkeyPatch.context() as context:
        context.setattr(__main__, "__file__", file_python)

        with pytest.raises(FileNotFoundError):
            find_file("wrongfile.ext")

        assert find_file(fname) == file_config


def test_config_walker():
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
        config_walker(dictionary_test, ["a", "b3"])


def test_config_finder(tmp_path):
    test_input_toml = [
        "[a.b1]",
        "c = 11",
        "d = 12",
        "[a.b2]",
        "c = 31",
        "e = 42",
    ]

    file_python = tmp_path / "some_program.py"

    file_toml = "test.toml"
    file_config_toml = tmp_path / file_toml
    file_config_toml.write_text("\n".join(s for s in test_input_toml))

    dt = deepcopy(dictionary_test)
    dt["a"]["b1"]

    file_json = "test.json"
    file_config_json = tmp_path / file_json
    file_config_json.write_text(json.dumps(dictionary_test))

    with pytest.MonkeyPatch.context() as context:
        context.setattr(__main__, "__file__", file_python)

        # test TOML
        assert config_finder(file_toml, ["a", "b1"]) == {
            "c": 11,
            "d": 12,
        }

        # test JSON
        assert config_finder(file_json, ["a", "b1"]) == {
            "c": 1,
            "d": 2,
        }

        # test iterable
        assert config_finder([file_toml], ["a", "b1"]) == {
            "c": 11,
            "d": 12,
        }

        # test multiple
        assert config_finder([file_toml, file_json], ["a", "b2"]) == {
            "c": 10,
            "d": 22,
            "e": 42,
        }

        # errors for missing files
        assert config_finder("somefile.json", [], raise_error=False) == {}

        # errors for missing files with multiple inputs
        assert config_finder(
            [file_toml, "wrongfile.json"], ["a", "b1"], raise_error=False
        ) == {
            "c": 11,
            "d": 12,
        }
        # verify unknown extensions
        with pytest.raises(NotImplementedError):
            config_finder("somefile.ext", ["a"])
