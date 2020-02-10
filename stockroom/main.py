from typing import Union, Any
from pathlib import Path
from contextlib import contextmanager

from .repository import StockRepository
from .storages import Model, Data, Tag
from .utils import get_stock_root, set_current_head


class StockRoom:
    """
    This class is the only user entrypoint of stockroom that interacts with an existing
    stock repository i.e. all the repository interaction a user would do will have to go
    through an object of this class. Also, stockroom comes with three different storages

    1. Model: Weights of models built with ``keras.Model`` or ``torch.nn``
    2. Data: Dataset as numpy arrays/tensors
    3. Tag: Information related to an experiment such as metrics, parameters etc

    An object of this class holds an object to these three storages each has a dictionary
    style access machinery

    Parameters
    ----------
    path : Union[str, Path, None]
        Path the to the stock repository. If `None`, it traverse up from `pwd` till it
        finds the stock root (stock root is the location where `head.stock` file is
        located and ideally will have `.git` folder as well

    Note
    ----
    By default (if no path is provided while initializing :class:`StockRoom`), it checks
    for the stock root. A stock root is a directory that is

    1. a git repository (has .git folder)
    2. a hangar repository (has .hangar folder)
    3. a stock repository (has head.stock file)

    If you'd like to skip these checks and just use stockroom (for example: if you are a
    hangar user and use stockroom just for storing models in your hangar repository, it
    doesn't need to be a stock repository and hence can skip these checks), provide the
    path to the repository explicitly. The rationale here is, if you provide the path, we
    trust you that you know what you doing on that path
    """
    def __init__(self, path: Union[str, Path, None] = None):
        self.path = Path(path) if path else get_stock_root(Path.cwd())
        self._repo = StockRepository(self.path)

        self.model = Model(self._repo)
        self.data = Data(self._repo)
        self.tag = Tag(self._repo)

    @property
    def get_hangar_checkout(self, write: bool = False) -> Any:
        """
        Fetch the hangar checkout object that's been used by stockroom internally. Don't
        do this unless you know what you are doing. Directly interacting with hangar
        could tamper the data stored by stockroom if you are not familiar with how hangar
        stores data and it's APIs.

        Parameters
        ----------
        write : bool
            Whether you need a write enabled checkout or not

        Returns
        ------
        Union[ReaderCheckout, WriterCheckout]
            A hangar checkout object which can be used to interact with the repository
            data

        Warning
        -------
        You won't be able to fetch a write enabled checkout if you are in ``optimize``
        context manager. Similarly if you fetch a write enabled checkout from here,
        you neither be able to do any write operation through stockroom nor be able to
        open ``optimize`` context manager
        """
        return self._repo.hangar_repository.checkout(write=write)

    @contextmanager
    def optimize(self, write=False):
        """
        This context manager, on `enter`, asks the :class:`StockRepository` object to
        open the global checkout. Global checkout is being stored as property of the
        repository singleton. Hence all the downstream tasks will get this opened
        checkout until it is closed. This global checkout will be closed on the `exit` of
        this context manager
        """
        if self._repo.is_optimized:
            raise RuntimeError("Attempt to open one optimized checkout while another is "
                               "in action in the same process")
        try:
            self._repo.open_global_checkout(write)
            yield None
        finally:
            self._repo.close_global_checkout()

    def commit(self, message: str) -> str:
        """
        Make a stock commit. A stock commit is a hangar commit plus writing the commit
        hash to the stock file. This function opens the stock checkout in write mode and
        close after the commit. Which means, no other write operations should be running
        while stock commit is in progress
        """
        with self._repo.write_checkout() as co:
            digest = co.commit(message)
        set_current_head(self._repo.stockroot, digest)
        return digest
