from stockroom import StockRoom
from random import randint
import numpy as np
import pytest


class TestSameProcess:

    def test_opening_two_instances(self, stock):
        # todo: should we allow this?
        stock2 = StockRoom()
        arr = np.arange(20).reshape(4, 5)
        oldarr = arr * randint(1, 100)
        newarr = arr * randint(1, 100)

        stock.data['ndcol', 1] = oldarr
        stock2.data['ndcol', 1] = newarr
        stock.commit('added data')

        assert np.allclose(stock2.data['ndcol', 1], newarr)
        assert not np.allclose(stock2.data['ndcol', 1], oldarr)
        stock2._stock_repo.hangar_repo._env._close_environments()

    def test_one_in_write_contextmanager(self, stock):
        stock2 = StockRoom()
        arr = np.arange(20).reshape(4, 5)
        oldarr = arr * randint(1, 100)

        with stock.optimize():
            assert stock._stock_repo.is_write_optimized
            assert not stock2._stock_repo.is_write_optimized

            # another write optimization
            with pytest.raises(PermissionError):
                with stock2.optimize():
                    pass

            with pytest.raises(PermissionError):
                stock2.data['ndcol', 1] = oldarr

            stock.data['ndcol', 1] = oldarr
            stock.commit('adding data inside cm')
            assert np.allclose(stock.data['ndcol', 1], oldarr)

            stock3 = StockRoom()
            assert not stock3._stock_repo.is_write_optimized

        assert np.allclose(oldarr, stock.data['ndcol', 1])
        stock2._stock_repo.hangar_repo._env._close_environments()
        stock3._stock_repo.hangar_repo._env._close_environments()
