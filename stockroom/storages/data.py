
class Data:
    def __init__(self, repo):
        self._repo = repo

    def __setitem__(self, key, value):
        co = self._repo.checkout(write=True)
        try:
            co[key] = value
        finally:
            co.close()

    def __getitem__(self, item):
        co = self._repo.checkout()
        try:
            value = co[item]
            return value
        finally:
            co.close()
