import pytest


def test_basic(writer_stock):
    writer_stock.experiment['lr'] = 0.01
    writer_stock.experiment['epochs'] = 500
    writer_stock.experiment['optimizer'] = 'adam'
    writer_stock.commit('Saved lr')

    assert writer_stock.experiment['lr'] == 0.01
    assert writer_stock.experiment['optimizer'] == 'adam'
    assert writer_stock.experiment['epochs'] == 500


def test_save_string(writer_stock):
    with pytest.raises(TypeError):
        writer_stock.experiment['wrongdata'] = bytes('hi')
