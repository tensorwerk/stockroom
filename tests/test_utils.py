from pathlib import Path
import pytest
import os
import stockroom.utils as utils


def test_get_stock_root(repo):
    cwd = Path.cwd()
    root = utils.get_stock_root(cwd)
    assert root == cwd

    os.rmdir(cwd/'.git')
    root = utils.get_stock_root(cwd)
    assert root == cwd

    root = utils.get_stock_root(cwd/'dummy/path')
    assert root == cwd

    path = Path('/down/the/rabbit/hole')
    with pytest.raises(RuntimeError):
        utils.get_stock_root(path)
