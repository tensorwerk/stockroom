from stockroom import StockRoom
from random import randint
import numpy as np
import pytest


class TestSameProcess:

    def test_opening_two_instances(self, repo_with_aset):
        # todo: should we allow this?
        stk1 = StockRoom()
        stk2 = StockRoom()
        arr = np.arange(20).reshape(4, 5)
        oldarr = arr * randint(1, 100)
        newarr = arr * randint(1, 100)

        stk1.data['aset', 1] = oldarr
        stk2.data['aset', 1] = newarr
        stk1.commit('added data')

        assert np.allclose(stk2.data['aset', 1], newarr)
        assert not np.allclose(stk2.data['aset', 1], oldarr)

    def test_operating_one_in_another_write_contextmanager(self, repo_with_aset):
        stk1 = StockRoom()
        stk2 = StockRoom()
        arr = np.arange(20).reshape(4, 5)
        oldarr = arr * randint(1, 100)

        with stk1.optimize(write=True):
            assert stk1._repo._optimized_Rcheckout is not None
            assert stk1._repo._optimized_Wcheckout is not None
            assert stk2._repo._optimized_Rcheckout is not None
            assert stk2._repo._optimized_Wcheckout is not None
            stk2.data['aset', 1] = oldarr
            stk1.commit('adding data inside cm')
            with pytest.raises(KeyError):
                # TODO: document this scenario
                data = stk1.data['aset', 1]

            stk3 = StockRoom()
            assert stk3._repo._optimized_Rcheckout is not None
            assert stk3._repo._optimized_Wcheckout is not None

        assert np.allclose(oldarr, stk1.data['aset', 1])

    def test_opening_one_contextmanager_in_another(self, repo_with_aset):
        stk1 = StockRoom()
        stk2 = StockRoom()

        with stk1.optimize(write=True):
            with pytest.raises(RuntimeError):
                with stk2.optimize():
                    pass
            assert stk2._repo._optimized_Rcheckout is not None
            assert stk2._repo._optimized_Wcheckout is not None
        assert stk1._repo._optimized_Rcheckout is None
        assert stk1._repo._optimized_Wcheckout is None
        assert stk2._repo._optimized_Rcheckout is None
        assert stk2._repo._optimized_Wcheckout is None

    def test_one_inside_another_read_contextmanager(self, repo_with_aset):
        stk1 = StockRoom()
        stk2 = StockRoom()
        arr = np.arange(20).reshape(4, 5)

        with stk1.optimize():
            # non-optimized write inside read CM
            assert stk2._repo._optimized_Wcheckout is None
            stk2.data['aset', 1] = arr
            stk2.commit('adding data')

            with pytest.raises(RuntimeError):
                with stk2.optimize(write=True):
                    pass

        with stk1.optimize():
            assert np.allclose(stk2.data['aset', 1], arr)