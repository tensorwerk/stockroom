import pytest
from stockroom import StockRoom
import numpy as np


def test_save_data(repo_with_aset):
    arr = np.arange(20).reshape(4, 5)
    stock = StockRoom()
    stock.data['aset', 1] = arr
    stock.commit("added data")
    assert np.allclose(stock.data['aset', 1], arr)


def test_save_to_non_existing_column(repo):
    arr = np.arange(20).reshape(4, 5)
    stock = StockRoom()
    with pytest.raises(KeyError):
        stock.data['wrongaset', 1] = arr


def test_save_to_different_typed_column(repo_with_aset):
    arr = np.arange(20).reshape(4, 5).astype(np.float)
    stock = StockRoom()
    with pytest.raises(ValueError):
        stock.data['aset', 1] = arr


def test_fetch_non_existing_sample_key(repo_with_aset):
    stock = StockRoom()
    with pytest.raises(KeyError):
        stock.data['aset', 1]
