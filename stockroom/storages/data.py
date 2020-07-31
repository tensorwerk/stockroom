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

    >>> with stock.run():
    ...     sample = stock.data['coloumn1']['sample1']
    """
    def __init__(self, accessor):
        self.accessor = accessor

    def __getattr__(self, item):
        # TODO: guard for non-allowed
        return getattr(self.accessor, item)

    def __setitem__(self, key, value):
        self.accessor[key] = value

    def __getitem__(self, key):
        return self.accessor[key]
