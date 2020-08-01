from stockroom import parser


class Experiment:
    """
    Tag store, as the name suggests, is to store tags related to an experiment. Ideally/
    eventually this store information on commit level and would not pass it down the
    commit history tree. But currently the internal implementation of hangar doesn't
    allow that and hence we store the information on metadata store in hangar. It
    currently takes `int`, `float` & `str` data types and convert it to a string which
    is the only data type supported by hangar metadata. But :class:`Tag` stores the type
    of the data in another metadata "column" which will be uesd while pulling the data
    back from the Tag store.

    Examples
    --------
    >>> stock.experiment['epochs'] = 1000
    >>> stock.experiment['lr'] = 0.0001
    >>> stock.experiment['optimizer'] = 'adam'
    """
    def __init__(self, accessor):
        self.typecaster = {'int': int, 'float': float, 'str': str}
        self.accessor = accessor
        self.tagkey = parser.tagkey()
        self.tagtypekey = parser.tag_typekey()

    def __setitem__(self, key, value):
        writer = self.accessor
        if isinstance(value, int):
            value_type = 'int'
        elif isinstance(value, float):
            value_type = 'float'
        elif isinstance(value, str):
            value_type = 'str'
        else:
            raise TypeError("Tag store can accept only ``int``, ``float`` or ``str``")
        if self.tagkey not in writer.columns.keys():
            writer.add_str_column(self.tagkey)
        if self.tagtypekey not in writer.columns.keys():
            writer.add_str_column(self.tagtypekey)
        writer[self.tagkey][key] = str(value)
        writer[self.tagtypekey][key] = value_type

    def __getitem__(self, key):
        reader = self.accessor
        try:
            value = reader[self.tagkey, key]
            value_type = reader[self.tagtypekey, key]
        except KeyError:
            raise KeyError(f"Data not found with key {key}")
        try:
            return self.typecaster[value_type](value)
        except KeyError:
            raise KeyError(f"Data tampering suspected. Could not "
                           f"read the data type {value_type}")
