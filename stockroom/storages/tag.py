from .. import parser


class Tag:
    """
    A generic data storage class that does the functionality of
    hangar metadata
    """
    def __init__(self, repo):
        self._repo = repo

    def __setitem__(self, key, value):
        co = self._repo.checkout(write=True)
        try:
            co.metadata[parser.generic_metakey(key)] = value
        finally:
            co.close()

    def __getitem__(self, key):
        co = self._repo.checkout()
        try:
            value = co.metadata[parser.generic_metakey(key)]
        finally:
            co.close()
        return value
