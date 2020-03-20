from ..repository import StockRepository


class Column:
    """
    Column wrapper object which will be returned to user from the :class: `Data` storage.
    All the sample access and write is enabled only thorugh this class. This might change
    in the future.
    """
    def __init__(self, name, repo):
        self.name = name
        self._stock_repo = repo
        self._column = self._stock_repo.reader[name]

    def __getitem__(self, sample_key):
        return self._column[sample_key]

    def __setitem__(self, sample_key, value):
        with self._stock_repo.get_writer_cm() as writer:
            col = writer[self.name]
            col[sample_key] = value


class Data:
    """
    Data storage is essentially a wrapper over hangar's column API which let stockroom
    handles the checkout scope. The instance creation is not something user would
    directly do here. Instead, a created instance will be available at :class:`stockroom.StockRoom`

    Note
    ----
    Each ``__getitem__`` or ``__setitem__`` call will open & close a hangar checkout.
    Unlike other storages, this is a crucial information for data storage because both
    reading and writing of data happens quite frequently in a pipeline unlike saving or
    retrieving model or parameters or metrics. So for optimizing, this you could make the
    data read/write inside the context manager :meth:`stockroom.StockRoom.optimize`

    Examples
    --------
    >>> stock = StockRoom()
    >>> stock.data['column1']['sample1'] = np.arange(20).reshape(5, 4)
    >>> sample = stock.data['column1']['sample5']

    Inside context manager

    >>> with stock.optimize():
    ...     sample = stock.data['coloumn1']['sample1']
    """
    def __init__(self, repo: StockRepository):
        self._stock_repo = repo

    def __setitem__(self, key, value):
        raise RuntimeError("Data storage does not take sample values. Add data to your "
                           "column. Ex: ``stock.data[column][sample] = array``")

    def __getitem__(self, key):
        self.__dict__[key] = Column(key, self._stock_repo)
        return self.__dict__[key]
