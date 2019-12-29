import stockroom
import pytest


def test_basic(repo):
    genericstore = stockroom.genericstore(write=True)
    genericstore.save('key1', 'value1')
    stockroom.commit('data saved')
    assert genericstore.load('key1') == 'value1'


def test_save_nonstring(repo):
    genericstore = stockroom.genericstore(write=True)
    with pytest.raises(ValueError):
        genericstore.save('key1', 0.01)
