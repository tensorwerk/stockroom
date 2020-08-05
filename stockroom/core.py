from typing import Union
from pathlib import Path
from contextlib import contextmanager, ExitStack
import logging
import time

from hangar import Repository
from stockroom.storages import Model, Data, Experiment
from stockroom.utils import get_stock_root, get_current_head, set_current_head

logger = logging.getLogger(__name__)  # TODO make the formatter and stuffs like that


class StockRoom:
    """
    This class is the only user entrypoint of stockroom that interacts with an existing
    stock repository i.e. all the repository interaction a user would do will have to go
    through an object of this class. Also, stockroom comes with three different storages

    1. Model: Weights of models built with ``keras.Model`` or ``torch.nn``
    2. Data: Dataset as numpy arrays/tensors
    3. Experiment: Information related to an experiment such as metrics, parameters etc

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
    def __init__(self, path: Union[str, Path] = None, write: bool = False):
        # TODO: context manager on Object creation
        # TODO: make force_release_writer_lock easier with stockroom?
        self.path = Path(path) if path else get_stock_root(Path.cwd())
        self._repo = Repository(self.path)
        self.head = get_current_head(self.path)  # TODO: should this be None if writer enabled
        if write:
            self.accessor = self._repo.checkout(write=True)
        else:
            if not self.head:
                self.accessor = None
            else:
                self.accessor = self._repo.checkout(commit=self.head).__enter__()

        if self.accessor:
            self.model = Model(self.accessor)
            self.data = Data(self.accessor)
            self.experiment = Experiment(self.accessor)
        else:
            self.model = None
            self.data = None
            self.experiment = None

    @contextmanager
    def run(self, autocommit=True, commit_msg=f'Auto-committing at {time.time()}'):
        # TODO: check whether opening in multiple context managers has any problem or not
        with ExitStack() as stack:
            stack.enter_context(self.accessor)
            yield
        if autocommit and self.accessor.diff.status() != 'CLEAN':
            self.accessor.commit(commit_msg)

    def update_head(self):
        if self._repo.writer_lock_held:
            logger.info("Write enabled checkouts will always be on the latest head "
                        "(staging). Doing nothing")
            return
        self.head = get_current_head(self.path)
        self.accessor.__exit__()
        self.accessor.close()
        self.accessor = self._repo.checkout(commit=self.head).__enter__()

    def close(self):
        self.accessor.close()

    @property
    def stockroot(self) -> Path:
        """
        Returns the root of stock repository
        """
        return self.path

    def commit(self, message: str, update_head=True) -> str:
        """
        Make a stock commit. A stock commit is a hangar commit plus writing the commit
        hash to the stock file. This function opens the stock checkout in write mode and
        close after the commit. Which means, no other write operations should be running
        while stock commit is in progress
        """
        digest = self.accessor.commit(message)
        set_current_head(self.stockroot, digest)
        if update_head:
            self.update_head()
        return digest
