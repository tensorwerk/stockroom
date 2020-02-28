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

        stock.data['aset', 1] = oldarr
        stock2.data['aset', 1] = newarr
        stock.commit('added data')

        assert np.allclose(stock2.data['aset', 1], newarr)
        assert not np.allclose(stock2.data['aset', 1], oldarr)
        stock2._repo.hangar_repository._env._close_environments()

    def test_one_in_write_contextmanager(self, stock):
        stock2 = StockRoom()
        arr = np.arange(20).reshape(4, 5)
        oldarr = arr * randint(1, 100)

        with stock.optimize(write=True):
            assert stock._repo._optimized_Rcheckout is not None
            assert stock._repo._optimized_Wcheckout is not None
            assert stock2._repo._optimized_Rcheckout is None
            assert stock2._repo._optimized_Wcheckout is None

            with stock2.optimize():
                pass

            # write optimization
            with pytest.raises(PermissionError):
                with stock2.optimize(write=True):
                    pass

            with pytest.raises(PermissionError):
                stock2.data['aset', 1] = oldarr

            stock.data['aset', 1] = oldarr
            stock.commit('adding data inside cm')

            with pytest.raises(KeyError):
                # TODO: document this scenario
                data = stock.data['aset', 1]

            stock3 = StockRoom()
            assert stock3._repo._optimized_Rcheckout is None
            assert stock3._repo._optimized_Wcheckout is None

        assert np.allclose(oldarr, stock.data['aset', 1])
        stock2._repo.hangar_repository._env._close_environments()
        stock3._repo.hangar_repository._env._close_environments()

    def test_one_in_read_contextmanager(self, stock):
        stock2 = StockRoom()
        arr = np.arange(20).reshape(4, 5)

        with stock.optimize():
            stock2.data['aset', 1] = arr
            stock2.commit('adding data')

            with stock2.optimize(write=True):
                assert stock2._repo._optimized_Wcheckout is not None
                assert stock2._repo._optimized_Rcheckout is not None
                assert stock._repo._optimized_Rcheckout is not None
                assert stock._repo._optimized_Wcheckout is None

                stock2.data['aset', 2] = arr
                stock2.commit('adding data')
        assert np.allclose(stock.data['aset', 1], arr)
        assert np.allclose(stock.data['aset', 2], arr)
        stock2._repo.hangar_repository._env._close_environments()
