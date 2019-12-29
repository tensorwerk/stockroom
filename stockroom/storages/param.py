import numbers
from ..repository import StockRepository
from .. import parser


class ParamStore:
    def __init__(self, write):
        self._write = write
        self._repo = StockRepository()

    def save(self, key, value):
        if not isinstance(value, numbers.Real):
            raise TypeError("ParamStore accepts only numbers as input")
        co = self._repo.checkout(write=True)
        # TODO: Perhaps a hangar backend that could take int, float, string
        co.metadata[parser.params_metakey(key)] = str(value)
        co.close()

    def load(self, key):
        co = self._repo.checkout()
        ret = co.metadata[parser.params_metakey(key)]
        co.close()
        return float(ret)


def paramstore(write=False):
    return ParamStore(write=write)
