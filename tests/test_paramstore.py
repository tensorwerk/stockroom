import stockroom
import pytest


def test_basic(repo):
    paramstore = stockroom.paramstore(write=True)
    paramstore.save('lr', 0.01)
    paramstore.save('epochs', 500)
    stockroom.commit('Saved lr')
    assert paramstore.load('lr') == 0.01
    assert paramstore.load('epochs') == 500.0


def test_save_string(repo):
    paramstore = stockroom.paramstore(write=True)
    with pytest.raises(TypeError):
        paramstore.save('wrongdata', 'stringvalue')

