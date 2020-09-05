import logging
import time
import warnings
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Union

from hangar import Repository
from hangar.checkout import WriterCheckout
from stockroom.storages import Data, Experiment, Model
from stockroom.utils import get_current_head, get_stock_root, set_current_head

logger = logging.getLogger(__name__)


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
    """

    def __init__(self, path: Union[str, Path] = None, enable_write: bool = False):
        self.path = Path(path) if path else get_stock_root(Path.cwd())
        self._repo = Repository(self.path)
        self.head = get_current_head(
            self.path
        )  # TODO: should this be None if writer enabled
        if enable_write:
            self.accessor = self._repo.checkout(write=True)
        else:
            if not self.head:
                self.accessor = None
            else:
                self.accessor = self._repo.checkout(commit=self.head)
        # TODO: Test this extensively
        if self.accessor is not None:
            with ExitStack() as stack:
                stack.enter_context(self.accessor)
                self._stack = stack.pop_all()

        self.data = Data(self.accessor)
        self.model = Model(self.accessor)
        self.experiment = Experiment(self.accessor)

    @contextmanager
    def enable_write(
        self, autocommit=True, commit_msg=f"Auto-committing at {time.time()}"
    ):
        if isinstance(self.accessor, WriterCheckout):
            warnings.warn(
                "Write access is already enabled. Doing nothing!!", UserWarning
            )
            yield
        else:
            self.accessor = self._repo.checkout(write=True)
            self.data = Data(self.accessor)
            self.model = Model(self.accessor)
            self.experiment = Experiment(self.accessor)

            with self.accessor:
                yield
            if autocommit and self.accessor.diff.status() != "CLEAN":
                self.commit(commit_msg)
            self.accessor.close()

            # TODO: these objects doesn't need to recreate no column creation inside the CM.
            #   Find a way to track that
            self.accessor = self._repo.checkout()
            self.data = Data(self.accessor)
            self.model = Model(self.accessor)
            self.experiment = Experiment(self.accessor)

    def update_head(self):
        if self._repo.writer_lock_held:
            logger.info(
                "Write enabled checkouts will always be on the latest head "
                "(staging). Doing nothing"
            )
            return
        self.head = get_current_head(self.path)
        self.accessor.__exit__()
        self.accessor.close()
        self.accessor = self._repo.checkout(commit=self.head).__enter__()

    def close(self):
        self._stack.close()
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

    def __getstate__(self):
        if isinstance(self.accessor, WriterCheckout):
            raise RuntimeError("Write enabled instance is not pickle-able")
        return self.__dict__
