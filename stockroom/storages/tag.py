from .. import parser


class Tag:
    """
    A generic data storage class that does the functionality of
    hangar metadata
    """
    def __init__(self, repo):
        self.typecaster = {'int': int, 'float': float, 'str': str}
        self._repo = repo

    def __setitem__(self, key, value):
        with self._repo.checkout(write=True) as co:
            if isinstance(value, int):
                value_type = 'int'
            elif isinstance(value, float):
                value_type = 'float'
            elif isinstance(value, str):
                value_type = 'str'
            else:
                raise TypeError("Tag store can accept only ``int``, ``float`` or ``str``")
            co.metadata[parser.tagkey(key)] = str(value)
            co.metadata[parser.tag_typekey(key)] = value_type

    def __getitem__(self, key):
        with self._repo.checkout() as co:
            try:
                value = co.metadata[parser.tagkey(key)]
                value_type = co.metadata[parser.tag_typekey(key)]
            except KeyError:
                raise KeyError(f"Data not found with key {key}")
            try:
                return self.typecaster[value_type](value)
            except KeyError:
                raise KeyError(f"Data tampering suspected. Could not "
                               f"read the data type {value_type}")
