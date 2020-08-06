from stockroom.core import StockRoom
from stockroom.keeper import init_repo
__all__ = ['StockRoom', 'init_repo', '__version__']


try:
    from hangar.dataset import make_torch_dataset
except ModuleNotFoundError:
    pass
else:
    __all__.append('make_torch_dataset')


__version__ = '0.1.0'
