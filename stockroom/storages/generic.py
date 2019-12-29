from .. import parser
from ..repository import StockRepository


# TODO: Maybe need another name than `GenericStore` but keeping it-
# since scope of the name MetricStore seems to be too narrow

class GenericStore:
    """
    A generic data storage class that does the functionality of
    hangar metadata
    """
    def __init__(self, write):
        self._write = write
        self._repo = StockRepository()

    def save(self, key, value):
        co = self._repo.checkout(write=True)
        co.metadata[parser.generic_metakey(key)] = value
        co.close()

    def load(self, key):
        co = self._repo.checkout()
        value = co.metadata[parser.generic_metakey(key)]
        co.close()
        return value


def genericstore(write=False):
    return GenericStore(write=write)
