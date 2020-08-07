from stockroom.core import StockRoom
from stockroom.keeper import init_repo
__all__ = ['StockRoom', 'init_repo', '__version__', 'make_torch_dataset']


try:
    from hangar.dataset import make_torch_dataset
except ModuleNotFoundError:
    from hangar import make_torch_dataset


__version__ = '0.2.2'
