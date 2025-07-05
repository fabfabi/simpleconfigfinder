import pytest

import __main__
from simpleconfigfinder.configfinder import (
    ConfigNotFound,
    config_finder,
    config_walker,
    find_file,
)


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


def test_config_finder(tmp_path):
    test_input = [
        "[a.b1]",
        "c = 1",
        "d = 2",
        "[a.b2]",
        "c = 10",
        "d = 22",
    ]
    fname = "test.toml"
    file_config = tmp_path / fname
    file_python = tmp_path / "some_program.py"

    file_config.write_text("\n".join(s for s in test_input))

    with pytest.MonkeyPatch.context() as context:
        context.setattr(__main__, "__file__", file_python)

        assert config_finder(fname, ["a", "b1"]) == {
            "c": 1,
            "d": 2,
        }

    with pytest.raises(NotImplementedError):
        config_finder("somefile.ext", ["a"])
