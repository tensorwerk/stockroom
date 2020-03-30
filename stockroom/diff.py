from typing import NamedTuple

class ParsedDiff(NamedTuple):
    tagName: str
    samples: list

class TagDiff:
    """
    The Diff object for tags
    """

    def __init__(self, ref_commit: str = None, dest_commit: str = None):
        self.ref_commit = ref_commit
        self.dest_commit = dest_commit

        self._added: list = list()
        self._deleted: list = list()
        self._mutated: list = list()

    def gen_tables(self):
        return ''

    def parse_diff(self):
        return ''

    def __repr__(self):
        return ''

    def _repr_html_(self):
        return ''


