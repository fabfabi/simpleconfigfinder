import configparser
import json
import os
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

import __main__
from simpleconfigfinder.configfinder import (
    ConfigNotFound,
    combine_dictionaries,
    config_finder,
    config_walker,
    configparser_to_dict,
    find_file,
    multi_config_finder,
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
    ################################################################
    # test the jupyter notebook part
    with pytest.MonkeyPatch.context() as context:
        context.delattr(__main__, "__file__", True)
        context.setattr(os.path, "abspath", lambda _: Path(tmp_path / "src"))

        with pytest.raises(FileNotFoundError):
            find_file("wrongfile.ext")

        assert find_file(fname) == file_config
    ################################################################
    # test the strategy 'cwd'
    with pytest.MonkeyPatch.context() as context:
        context.setattr(os, "getcwd", lambda: str(tmp_path / "src"))

        with pytest.raises(FileNotFoundError):
            find_file("wrongfile.ext", strategy="cwd")

        assert find_file(fname, strategy="cwd") == file_config


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


def test_config_finder(tmp_path, tmpdir):
    test_input_toml = [
        "[a.b1]",
        "c = 11",
        "d = 12",
        "[a.b2]",
        "c = 31",
        "e = 42",
    ]

    file_python = tmp_path / "some_program.py"

    def mock_file(name, content):
        file = tmp_path / name
        file.write_text(content)

    file_toml = "test.toml"
    mock_file(file_toml, "\n".join(s for s in test_input_toml))

    dt = deepcopy(dictionary_test)
    dt["a"]["b1"]

    file_json = "test.JSON"
    mock_file(file_json, json.dumps(dictionary_test))

    file_json_like = "test.jsonlike"
    mock_file(file_json_like, json.dumps(dictionary_test))

    file_yaml = "test.yaml"
    mock_file(file_yaml, yaml.dump(dictionary_test))

    file_ini = "test.ini"
    file = tmpdir.join(file_ini)
    cfg = configparser.ConfigParser()
    cfg.read_dict(dictionary_test)
    with open(file, "w") as writer:
        cfg.write(writer)

    with pytest.MonkeyPatch.context() as context:
        context.setattr(__main__, "__file__", file_python)
        ########################################################################
        # basic formats
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

        # test INI
        cfg_ini = config_finder(file_json, ["a", "b1"])
        assert cfg_ini == {
            "c": 1,
            "d": 2,
        }
        ########################################################################
        # test keyword-arugments
        # errors for missing files
        assert config_finder("somefile.json", [], raise_error=False) == {}

        # verify unknown extensions
        with pytest.raises(NotImplementedError):
            config_finder(file_json_like, ["a"])

        # still works with the matchin reader
        assert config_finder(
            file_json_like, ["a", "b1"], additional_readers={"jsonlike": json.load}
        ) == {
            "c": 1,
            "d": 2,
        }

        # test the yaml reader
        assert config_finder(
            file_yaml, ["a", "b1"], additional_readers={"yaml": yaml.safe_load}
        ) == {
            "c": 1,
            "d": 2,
        }
        ###############################################################################
        # test multi_config_finder
        assert multi_config_finder([file_toml], ["a", "b1"]) == {
            "c": 11,
            "d": 12,
        }

        # test multiple
        assert multi_config_finder([file_toml, file_json], ["a", "b2"]) == {
            "c": 10,
            "d": 22,
            "e": 42,
        }
        # errors for missing files with multiple inputs
        assert multi_config_finder(
            [file_toml, "wrongfile.json"], ["a", "b1"], raise_error=False
        ) == {
            "c": 11,
            "d": 12,
        }


def test_configparser_to_dict():
    d = {
        "a": {"a1": "1", "a2": "2"},
    }
    cfg = configparser.ConfigParser()
    cfg.read_dict(d)

    d_parsed = configparser_to_dict(cfg)
    del d_parsed["DEFAULT"]

    assert d == d_parsed


def test_combine_dictionaries():
    d_a = {
        "a": {"a1": 1, "a2": 2},
    }
    d_b = {
        "a": {"a1": 3, "a3": 3},
    }
    t_a = {
        "a": {"a1": 1, "a2": 2, "a3": 3},
    }
    t_b = {
        "a": {"a1": 3, "a2": 2, "a3": 3},
    }

    def cd_test(a, b, c):
        assert combine_dictionaries(a, deepcopy(b)) == c

    cd_test(d_b, d_a, t_b)
    cd_test(d_a, d_b, t_a)

    d_aa = {
        "a": {
            "a1": 1,
            "a2": 2,
            "a": {
                "a1": 1,
                "a2": 2,
            },
        }
    }
    d_bb = {
        "a": {
            "a1": 3,
            "a3": 3,
            "a": {
                "a1": 3,
                "a3": 3,
            },
        },
    }

    t_aa = {
        "a": {
            "a1": 1,
            "a2": 2,
            "a3": 3,
            "a": {
                "a1": 1,
                "a2": 2,
                "a3": 3,
            },
        },
    }

    t_bb = {
        "a": {
            "a1": 3,
            "a2": 2,
            "a3": 3,
            "a": {
                "a1": 3,
                "a2": 2,
                "a3": 3,
            },
        },
    }
    cd_test(d_bb, d_aa, t_bb)
    cd_test(d_aa, d_bb, t_aa)

    d_ax = {
        "a": {"a1": 1, "a2": 2},
    }
    d_bx = {"a": 2, "b": {"a1": 1, "a2": 2}}

    t_ax = {"a": {"a1": 1, "a2": 2}, "b": {"a1": 1, "a2": 2}}
    t_bx = {"a": 2, "b": {"a1": 1, "a2": 2}}

    cd_test(d_bx, d_ax, t_bx)
    cd_test(d_ax, d_bx, t_ax)
