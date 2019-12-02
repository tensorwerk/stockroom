from stockroom.storages import DataStore
from stockroom.storages import ModelStore
from stockroom.storages import ParamStore
from stockroom.storages import MetricStore
from .repository import init, commit


# TODO: Simplify APIs by not making users initiate a storage class each time

__all__ = ['DataStore', 'ModelStore', 'ParamStore', 'MetricStore', 'init', 'commit']
