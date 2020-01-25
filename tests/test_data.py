from stockroom import StockRoom
import numpy as np


def test_save_data(repo_with_aset):
    arr = np.arange(20).reshape(4, 5)
    stock = StockRoom()
    stock.data['aset', 1] = arr
    assert np.allclose(stock.data['aset', 1], arr)


def test_save_to_non_existing_column():
    pass


def test_save_to_different_typed_column():
    pass


def test_fetch_non_existing_sample_key():
    pass


def test_add_batch_data():
    pass