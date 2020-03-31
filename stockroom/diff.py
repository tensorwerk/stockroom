from typing import NamedTuple

from hangar import Repository

from .parser import tagkey, SEP

class ParsedDiff(NamedTuple):
    tagName: str
    ref_sample: str = ''
    dest_samples: list = list()

class TagDiff:
    """
    The Diff object for tags
    """

    def __init__(self, ref_commit: str = None, dest_commit: str = None,
                    root: str = None):
        self.ref_commit = ref_commit
        self.dest_commit = dest_commit
        self.root = '.'

        self._added: list = list()
        self._deleted: list = list()
        self._mutated: list = list()

        self.parse_diff()

    def gen_tables(self):
        return ''

    def parse_diff(self):
        repo = Repository(self.root)
        print('Accessing ref_commit')
        ref_checkout = repo.checkout(commit = self.ref_commit)

        print("Accessing def_commit")
        dest_checkout = repo.checkout(commit = self.dest_commit)
        diff = ref_checkout.diff.commit(self.dest_commit).diff

        if len(diff.added.metadata) > 0:
            for keyRecord  in diff.added.metadata:
                key = keyRecord.key.split(SEP)[-1]
                if key != "type":
                    keyvalue = dest_checkout.metadata[tagkey(key)]
                    self._added.append(
                            ParsedDiff(key, dest_samples=[keyvalue])
                            )

        if len(diff.mutated.metadata) > 0:
            for keyRecord in diff.mutated.metadata:
                key = keyRecord.key.split(SEP)[-1]
                if key != "type":
                    keyvalue_ref = ref_checkout.metadata[tagkey(key)]
                    keyvalue_dest = dest_checkout.metadata[tagkey(key)]
                    self._mutated.append(
                            ParsedDiff(key, ref_sample=keyvalue_ref,
                                dest_samples = [keyvalue_dest]
                                )
                            )

        if len(diff.deleted.metadata) > 0:
            for keyRecord in diff.deleted.metadata:
                key = keyRecord.key.split(SEP)[-1]
                if key != "type":
                    keyvalue_ref = ref_checkout.metadata[tagkey(key)]
                    self._deleted.append(
                            ParsedDiff(key, ref_samples = [keyvalue_ref])
                            )

    def __repr__(self):
        return ''

    def _repr_html_(self):
        return ''


