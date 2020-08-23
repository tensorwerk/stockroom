import numpy as np
import pytest


def test_save_data(writer_stock):
    stock = writer_stock
    arr = np.arange(20).reshape(4, 5)
    col = stock.data["ndcol"]
    col[1] = arr
    stock.commit("added data")
    assert np.allclose(stock.data["ndcol", 1], arr)
    del stock


def test_save_with_reader(reader_stock):
    stock = reader_stock
    arr = np.arange(20).reshape(4, 5)
    with pytest.raises(TypeError):
        stock.data["ndcol"][1] = arr + 1
    with stock.enable_write():
        stock.data["ndcol"][1] = arr + 1
        stock.commit("added data")
    with pytest.raises(AttributeError):
        stock.commit("added data")


def test_fetch_non_existing_column(writer_stock):
    with pytest.raises(KeyError):
        writer_stock.data["wrongcol"]


def test_save_to_different_typed_column(writer_stock):
    arr = np.arange(20).reshape(4, 5).astype(np.float)
    col = writer_stock.data["ndcol"]
    with pytest.raises(ValueError):
        col[1] = arr


def test_fetch_non_existing_sample_key(writer_stock):
    arr = np.arange(20).reshape(4, 5)
    col = writer_stock.data["ndcol"]
    col[1] = arr
    with pytest.raises(KeyError):
        col[2]
