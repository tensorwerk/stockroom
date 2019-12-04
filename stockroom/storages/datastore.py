from .storagebase import StorageBase
from ..utils import get_current_head, get_stock_root


def datastore(write=False):
    root = get_stock_root()
    StorageBase.__init__()
    return StorageBase.repo.checkout(commit=get_current_head(root), write=write)




