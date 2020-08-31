import os
from pathlib import Path

import pytest
import stockroom.utils as utils


def test_get_stock_root(repo):
    cwd = Path.cwd()
    assert utils.get_stock_root(cwd) == cwd


def test_get_stock_root_convoluted(repo):
    cwd = Path.cwd()
    os.rmdir(cwd / ".git")
    assert utils.get_stock_root(cwd) == cwd
    assert utils.get_stock_root(cwd / "dummy/path") == cwd
    with pytest.raises(RuntimeError):
        utils.get_stock_root(Path("/down/the/rabbit/hole"))
