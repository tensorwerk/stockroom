from .storagebase import StorageBase


class ParamStore(StorageBase):
    def __init__(self, write):
        self.write = write
        super().__init__()


def paramstore(write=False):
    return ParamStore(write=write)