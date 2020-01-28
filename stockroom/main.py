from typing import Union
from pathlib import Path
from contextlib import contextmanager

from .repository import StockRepository
from .storages import Model, Data, Tag
from .utils import get_stock_root, set_current_head


class StockRoom:
    def __init__(self, path: Union[str, Path, None] = None):
        self.path = Path(path) if path else get_stock_root(Path.cwd())
        self._repo = StockRepository(self.path)

        self.model = Model(self._repo)
        self.data = Data(self._repo)
        self.tag = Tag(self._repo)

    @property
    def get_hangar_checkout(self, write=False):
        return self._repo.hangar_repository.checkout(write=write)

    @contextmanager
    def optimize(self):
        try:
            self._repo.enable_optimized_checkout()
            yield None
        finally:
            self._repo.disable_optimized_checkout()

    def commit(self, message: str):
        """
        Make a stock commit. A stock commit is a hangar commit plus writing the
        commit hash to the stock file. This function opens the stock checkout in
        write mode and close after the commit. Which means, no other write
        operations should be running while stock commit is in progress
        """
        with self._repo.checkout(write=True) as co:
            digest = co.commit(message)
        set_current_head(self._repo.stockroot, digest)
        return digest
