# TODO: move this hangar import to repository.py
from hangar import Repository
from ..utils import get_stock_root


class StorageBase(object):
    root = None
    repo = None

    def __init__(self):
        if StorageBase.repo is None:
            root = get_stock_root()
            if root is None:
                raise RuntimeError("Could not find the stock root. "
                                   "Did you forget to `stock init`?")
            StorageBase.root = root
            StorageBase.repo = Repository(root)
