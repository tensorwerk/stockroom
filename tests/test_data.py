import pytest
import numpy as np


def test_save_data(stock):
    arr = np.arange(20).reshape(4, 5)
    stock.data['aset', 1] = arr
    stock.commit("added data")
    assert np.allclose(stock.data['aset', 1], arr)
    del stock


def test_save_to_non_existing_column(stock):
    arr = np.arange(20).reshape(4, 5)
    with pytest.raises(KeyError):
        stock.data['wrongaset', 1] = arr


def test_save_to_different_typed_column(stock):
    arr = np.arange(20).reshape(4, 5).astype(np.float)
    with pytest.raises(ValueError):
        stock.data['aset', 1] = arr


def test_fetch_non_existing_sample_key(stock):
    with pytest.raises(KeyError):
        stock.data['aset', 1]
