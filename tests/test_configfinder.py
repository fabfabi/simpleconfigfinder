import pytest

from src.configfinder import find_file


def test_file_finder():
    with pytest.raises(FileNotFoundError):
        find_file()
