from .storagebase import StorageBase
from ..utils import get_current_head, get_stock_root


class DataStore(StorageBase):
    def __init__(self):
        super().__init__()

    def __getitem__(self, item):
        root = get_stock_root()
        dset = self.repo.checkout(commit=get_current_head(root))
        # TODO: rigorous check like in hangar
        if isinstance(item, tuple):
            aset = item[0]
            index = item[1]
            return dset[aset, index]
        return dset[item]

    def __setitem__(self, item, value):
        # TODO: optimized set item like context manager
        dset = self.repo.checkout(write=True)
        # TODO: rigorous check like in hangar
        if isinstance(item, tuple):
            aset = item[0]
            index = item[1]
            dset[aset, index] = value
        dset[item] = value  # this will raise error downstream
        dset.close()




