
class Data:
    def __init__(self, repo):
        self._repo = repo

    def __setitem__(self, key, value):
        with self._repo.checkout(write=True) as co:
            co[key] = value

    def __getitem__(self, key):
        with self._repo.checkout() as co:
            return co[key]