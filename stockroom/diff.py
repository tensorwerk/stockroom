from typing import NamedTuple

from hangar import Repository
from rich.jupyter import print
from rich.table import Table
from rich.segment import Segment
from rich.console import Console

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
        self.repo = Repository(root)
        self.all_keys = set()

        self._added: dict = dict()
        self._deleted: dict = dict()
        self._mutated: dict = dict()

        self.parse_diff()

    def gen_tables(self):

        table = Table(title='Diff %s..%s'%(self.ref_commit[2:7], self.dest_commit[2:7]))

        # Generate Columns
        column_headings = ['Tags'] + [self.ref_commit, self.dest_commit]
        for column in column_headings:
            table.add_column(column[:10], no_wrap=True)

        # Generate rows
        for row in self.all_keys:
            ref_row = ""
            dest_row = ""

            if row in self._added:
                dest_row = "[green] %s [/green]"%(self._added[row])

            elif row in self._mutated:
                ref_row = "[red] %s [/red]"%(self._mutated[row][0])
                dest_row = "[red] %s [/red]"%(self._mutated[row][1])

            elif row in self._deleted:
                ref_row = "[green] %s [/green]"%(self._deleted[row])

            table.add_row(row, ref_row, dest_row)
        return table

    def parse_diff(self):
        print('Accessing ref_commit')
        ref_checkout = self.repo.checkout(commit = self.ref_commit)

        print("Accessing def_commit")
        dest_checkout = self.repo.checkout(commit = self.dest_commit)
        diff = ref_checkout.diff.commit(self.dest_commit).diff

        # Get all the keys in both checkouts
        all_keys = set()

        for tag in ref_checkout.metadata.keys():
            key = tag.split(SEP)[-1]
            if key != "type":
                all_keys.add(key)

        for tag in dest_checkout.metadata.keys():
            key = tag.split(SEP)[-1]
            if key not in all_keys and key != "type":
                all_keys.add(key)
        self.all_keys = all_keys

        if len(diff.added.metadata) > 0:
            for keyRecord  in diff.added.metadata:
                key = keyRecord.key.split(SEP)[-1]
                if key != "type":
                    keyvalue = dest_checkout.metadata[tagkey(key)]
                    self._added[key] = keyvalue

        if len(diff.mutated.metadata) > 0:
            for keyRecord in diff.mutated.metadata:
                key = keyRecord.key.split(SEP)[-1]
                if key != "type":
                    keyvalue_ref = ref_checkout.metadata[tagkey(key)]
                    keyvalue_dest = dest_checkout.metadata[tagkey(key)]
                    self._mutated[key] = (keyvalue_ref, keyvalue_dest)

        if len(diff.deleted.metadata) > 0:
            for keyRecord in diff.deleted.metadata:
                key = keyRecord.key.split(SEP)[-1]
                if key != "type":
                    keyvalue_ref = ref_checkout.metadata[tagkey(key)]
                    self._deleted[key] = keyvalue_ref

    def __repr__(self):
        output = list()
        append = output.append
        console = Console()
        for line in Segment.split_and_crop_lines(console.render(self.gen_tables(), None), 90):
            for text, style in line:
                if style:
                    append(style.render(text))
                else:
                    append(text)
        return ''.join(output)

    def _repr_html_(self):
        return print(self.gen_tables())._repr_html_()

