from .storagebase import StorageBase


class MetricStore(StorageBase):
    def __init__(self, write):
        self.write = write
        super().__init__()


def metricstore(write=False):
    return MetricStore(write=write)
