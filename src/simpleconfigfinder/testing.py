"""Testing frameworks like [pytest](https://docs.pytest.org/) create a test environment that might impacts
functionalities of the configfinder. Especially when trying to read from `pyproject.toml`.

Here are some fixtures to work around that.

* find file
* reader

>>> import pytest
>>> @pytest.fixture(scope="function")
    def some_fixture():
        with patch(__name__ + ".function_inner", return_value="mock"):
            yield
>>> def function_inner():
        return "original"
>>> def function_outer():
        return f"calling {function_inner()}"
>>> True
False
>>> def test_mockfun(some_fixture):

        assert function_outer() == "calling mockkkk"

asdfasdf
"""
