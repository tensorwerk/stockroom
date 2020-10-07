from collections import namedtuple
import abc
from typing import Optional, Tuple


ColumnSchema = namedtuple(
    "ColumnSchema", field_names=["name", "shape", "dtype", "is_variable_shaped"]
)


class BaseImporter(abc.ABC):
    _column_schemas = []

    def __init__(self, split: str):
        self.split = split

    def register_column(
        self,
        name: str,
        shape: Optional[Tuple] = None,
        dtype: Optional = None,
        is_variable_shaped: Optional[bool] = False,
    ):
        if is_variable_shaped and not isinstance(shape, tuple):
            raise ValueError("`shape` argument is not valid for a variable shaped column")

        if any([shape is None, dtype is None]):
            i = len(self._column_schemas)
            element = next(iter(self))[i]
            shape = element.shape if shape is None else shape
            dtype = element.dtype if dtype is None else dtype

        schema = ColumnSchema(name, shape, dtype, is_variable_shaped)
        self._column_schemas.append(schema)

    @abc.abstractmethod
    def __iter__(self):
        """
        Should be defined by child class and should return an iterator or yield
        instead of return.
        """
        pass

    @classmethod
    def gen_splits(cls):
        """
        This is a factory method which creates a tuple of Dataset objects
        corresponding to the different splits a dataset can have. Almost always,
        it's not necessary to override this method
        """
        for split in ("train", "test", "val"):
            yield cls(split)
