# Testing
Testing frameworks like [pytest](https://docs.pytest.org/) create a test environment that impacts
functionalities of the configfinder. Especially when trying to read from `pyproject.toml`. Here are some easy ways how to create some fixtures via a [monkey patch](https://en.wikipedia.org/wiki/Monkey_patch).


    from pathlib import Path
    from unittest.mock import patch

    import pytest

    from simpleconfigfinder import ConfigNotFound, config_finder

!!! caution
    If you're just calling the `config_finder` from a pytest environment this will raise the ConfigNotFound Error. 

        def test_direct_call():
            config_finder("pyproject.toml", ["tool", "some_tool", "key1"])  == "some_value_1"


This requires the creation of a [fixture](https://en.wikipedia.org/wiki/Test_fixture).

    @pytest.fixture(scope="function")
    def fixture_starting_file():
        with patch(
            "simpleconfigfinder.configfinder.get_starting_file",
            return_value=Path(__file__),
        ):
            yield


And now also the test environment will correctly read the values from the pyproject.toml.

    def test_config_finder(fixture_starting_file):
        assert (
            config_finder("pyproject.toml", ["tool", "some_tool", "key1"]) == "some_value_1"
        )

Going one step further, you can also create a fixture that will always return `custom_config` for the testing environment.

    @pytest.fixture(scope="function")
    def fixture_test_config():
        custom_config = {"tool": {"some_tool": {"key1": "different_value_1"}}}
        with patch(
            "simpleconfigfinder.configfinder.config_reader",
            return_value = custom_config,
        ):
            yield


    def test_mock(fixture_test_config):
        assert (
            config_finder("pyproject.toml", ["tool", "some_tool", "key1"])
            == "different_value_1"
        )