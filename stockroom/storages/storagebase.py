from hangar import Repository
from ..utils import get_stock_root


root = get_stock_root()
if root is None:
    raise RuntimeError("Could not find the stock root. "
                       "Did you forget to `stock init`?")


class StorageBase(object):
    root = root
    repo = Repository(root)
