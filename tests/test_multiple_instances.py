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

    def test_one_in_write_contextmanager(self, repo_with_aset):
        stk1 = StockRoom()
        stk2 = StockRoom()
        arr = np.arange(20).reshape(4, 5)
        oldarr = arr * randint(1, 100)

        with stk1.optimize(write=True):
            assert stk1._repo._optimized_Rcheckout is not None
            assert stk1._repo._optimized_Wcheckout is not None
            assert stk2._repo._optimized_Rcheckout is None
            assert stk2._repo._optimized_Wcheckout is None

            with stk2.optimize():
                pass

            # write optimization
            with pytest.raises(PermissionError):
                with stk2.optimize(write=True):
                    pass

            with pytest.raises(PermissionError):
                stk2.data['aset', 1] = oldarr

            stk1.data['aset', 1] = oldarr
            stk1.commit('adding data inside cm')

            with pytest.raises(KeyError):
                # TODO: document this scenario
                data = stk1.data['aset', 1]

            stk3 = StockRoom()
            assert stk3._repo._optimized_Rcheckout is None
            assert stk3._repo._optimized_Wcheckout is None

        assert np.allclose(oldarr, stk1.data['aset', 1])

    def test_one_in_read_contextmanager(self, repo_with_aset):
        stk1 = StockRoom()
        stk2 = StockRoom()
        arr = np.arange(20).reshape(4, 5)

        with stk1.optimize():
            stk2.data['aset', 1] = arr
            stk2.commit('adding data')

            with stk2.optimize(write=True):
                assert stk2._repo._optimized_Wcheckout is not None
                assert stk2._repo._optimized_Rcheckout is not None
                assert stk1._repo._optimized_Rcheckout is not None
                assert stk1._repo._optimized_Wcheckout is None

                stk2.data['aset', 2] = arr
                stk2.commit('adding data')
        assert np.allclose(stk1.data['aset', 1], arr)
        assert np.allclose(stk1.data['aset', 2], arr)
