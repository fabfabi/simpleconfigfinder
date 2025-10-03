from pathlib import Path
from unittest.mock import patch

import pytest

from simpleconfigfinder import config_finder


@pytest.fixture(scope="function")
def unmock_reader():
    with patch(
        "simpleconfigfinder.configfinder.get_starting_file",
        return_value=Path(__file__),
    ):
        yield


def test_unmock(unmock_reader):
    assert (
        config_finder("pyproject.toml", ["tool", "some_tool", "key1"]) == "some_value_1"
    )


@pytest.fixture(scope="function")
def mock_reader():
    with patch(
        "simpleconfigfinder.configfinder.config_reader",
        return_value={"tool": {"some_tool": {"key1": "different_value_1"}}},
    ):
        yield


def test_mock(mock_reader):
    assert (
        config_finder("pyproject.toml", ["tool", "some_tool", "key1"])
        == "different_value_1"
    )


@pytest.fixture(scope="function")
def some_fixture():
    with patch(
        __name__ + ".function_inner",
        return_value="mock",
    ):
        yield


def function_inner():
    return "original"


def function_outer():
    return f"calling {function_inner()}"


def test_fun():
    assert function_outer() == "calling original"


def test_mockfun(some_fixture):
    assert function_outer() == "calling mock"
