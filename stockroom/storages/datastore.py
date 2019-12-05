from .storagebase import StorageBase
from ..utils import get_current_head, get_stock_root


def datastore(write=False):
    root = get_stock_root()
    if StorageBase.repo is None:
        StorageBase()
    return StorageBase.repo.checkout(commit=get_current_head(root), write=write)




