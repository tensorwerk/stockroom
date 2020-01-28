from stockroom import StockRoom
import pytest


def test_basic(repo):
    stock = StockRoom()
    stock.tag['lr'] = 0.01
    stock.tag['epochs'] = 500
    stock.tag['optimizer'] = 'adam'
    stock.commit('Saved lr')
    assert stock.tag['lr'] == 0.01
    assert stock.tag['optimizer'] == 'adam'
    assert stock.tag['epochs'] == 500


def test_save_string(repo):
    stock = StockRoom()
    with pytest.raises(TypeError):
        stock.tag['wrongdata'] = bytes('hi')

