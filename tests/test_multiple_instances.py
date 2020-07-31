from stockroom import StockRoom
from random import randint
import numpy as np
import pytest


class TestSameProcess:

    def test_opening_two_instances(self, writer_stock):
        with pytest.raises(PermissionError):
            StockRoom(write=True)
        arr = np.arange(20).reshape(4, 5)
        oldarr = arr * randint(1, 100)
        col1 = writer_stock.data['ndcol']
        col1[1] = oldarr
        writer_stock.commit('added data')

        stock2 = StockRoom()
        col2 = stock2.data['ndcol']

        assert np.allclose(col2[1], oldarr)
        stock2._repo._env._close_environments()
