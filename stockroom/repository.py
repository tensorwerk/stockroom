from pathlib import Path
from contextlib import contextmanager

from hangar import Repository
from .utils import get_current_head


class Reader:
    # TODO: explain the need
    def __get__(self, stock, obj_type=None) -> object:
        if 'reader' not in stock.__dict__:
            stock.__dict__['reader'] = stock.hangar_repo.checkout(commit=stock.head)
            stock.__dict__['reader'].__enter__()
        return stock.__dict__['reader']


class StockRepository:
    # TODO: Document specifically about reader & writer
    """
    A StockRoom wrapper class for hangar repo operations. Every hangar repo interactions
    that is being done through stockroom (other than stock init) should go through the
    checkout created from this class. Unlike hangar Repository, this class constructor
    assumes the hangar repo is already initialized. Hangar will make sure there are only
    one writer class active always. The constructor creates the hangar repo object on
    instantiation.
    """

    reader = Reader()

    def __init__(self, root):
        self._root = root
        self.head = get_current_head(self._root)
        self.hangar_repo = Repository(root)
        # TODO: Write test cases for read optimized always
        if self.head:
            self.reader = self.hangar_repo.checkout(commit=self.head).__enter__()
        self._writer = None

    @property
    def is_write_optimized(self):
        return False if self._writer is None else True

    def open_global_writer(self):
        self._writer = self.hangar_repo.checkout(write=True)
        if self.head and self._writer.commit_hash != self.head:
            self._writer.close()
            self._writer = None
            raise RuntimeError("Writing on top of the old commit's are not allowed. "
                               "Checkout to the latest commit")
        self._writer.__enter__()

    def close_global_writer(self):
        self._writer.__exit__()
        self._writer.close()
        self._writer = None

    @contextmanager
    def get_writer_cm(self):
        # TODO: Do the function assignment as at the time of global checkout creation and
        # check if that improves time
        """
        An API similar to hangar checkout in write mode but does the closure of checkout
        on the exit of CM. It also monitors the existence of global checkout and open
        or close a local checkout if the global checkout doesn't exist
        """
        if self._writer:
            co = self._writer
        else:
            co = self.hangar_repo.checkout(write=True)
            if self.head and co.commit_hash != self.head:
                co.close()
                raise RuntimeError("Writing on top of the old commit's are not allowed. "
                                   "Checkout to the latest commit")
        try:
            yield co
        finally:
            if self._writer is None:
                co.close()

    @property
    def stockroot(self) -> Path:
        """
        Returns the root of stock repository
        """
        return self._root

    def update_head(self):
        self.head = get_current_head(self._root)
        self.reader.__exit__()
        self.reader.close()
        self.reader = self.hangar_repo.checkout(commit=self.head).__enter__()


# ================================== User facing Repository functions ================================

def init_repo(name=None, email=None, overwrite=False):
    """ init hangar repo, create stock file and add details to .gitignore """
    if not Path.cwd().joinpath('.git').exists():
        raise RuntimeError("stock init should execute only in a"
                           " git repository. Try running stock "
                           "init after git init")
    repo = Repository(Path.cwd(), exists=False)
    if not overwrite and repo.initialized:
        commit_hash = repo.log(return_contents=True)['head']
        print(f'Hangar Repo already exists at {repo.path}. '
              f'Initializing it as stock repository')
    else:
        if name is None or email is None:
            raise ValueError("Both ``name`` and ``email`` cannot be None")
        commit_hash = ''
        repo.init(user_name=name, user_email=email, remove_old=overwrite)
    # closing the environment for avoiding issues in windows
    repo._env._close_environments()

    stock_file = Path.cwd()/'head.stock'
    if not stock_file.exists():
        with open(stock_file, 'w+') as f:
            f.write(commit_hash)
        print("Stock file created")

    gitignore = Path.cwd()/'.gitignore'
    with open(gitignore, 'a+') as f:
        f.seek(0)
        if '.hangar' not in f.read():
            f.write('\n# hangar artifacts\n.hangar\n')
