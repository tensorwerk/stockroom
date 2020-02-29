import pytest


def test_basic(stock):
    stock.tag['lr'] = 0.01
    stock.tag['epochs'] = 500
    stock.tag['optimizer'] = 'adam'
    stock.commit('Saved lr')
    assert stock.tag['lr'] == 0.01
    assert stock.tag['optimizer'] == 'adam'
    assert stock.tag['epochs'] == 500


def test_save_string(stock):
    with pytest.raises(TypeError):
        stock.tag['wrongdata'] = bytes('hi')


@pytest.mark.skip(reason="Commit level metadata needs to be implemented in hangar")
def test_no_commit_history(stock):
    stock.tag['lr'] = 0
    stock.commit('adding lr')
    stock.tag['key'] = 'val'
    stock.commit('adding someval')
    with pytest.raises(KeyError):
        stock.tag['lr']
