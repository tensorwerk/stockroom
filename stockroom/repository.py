from pathlib import Path
from contextlib import contextmanager

from hangar import Repository
from .utils import get_current_head


class RootTracker(type):
    """
    A metaclass that make sure singleton-like implementation restricted on repository
    path. This class checks for the repository path and returns an existing instance of
    :class:`StorckRepository` for that path if exists. A path based singleton is
    essential since we need the ability to open one write checkout for each repository
    and make sure no another attempt to open the write checkout for the same repository
    triggers from stockroom.
    """
    _instances = {}

    def __call__(cls, root, *args, **kwargs):
        if root not in cls._instances:
            cls._instances[root] = super().__call__(root, *args, **kwargs)
        return cls._instances[root]


class StockRepository(metaclass=RootTracker):
    """
    A StockRoom wrapper class for hangar repo operations. Every hangar repo interactions
    that is being done through stockroom (other than stock init) should go through the
    checkout created from this class. Unlike hangar Repository, this class constructor
    assumes the hangar repo is already initialized. Hangar will make sure there are only
    one writer class active always. The constructor creates the hangar repo object on
    instantiation.
    """

    def __init__(self, root):
        self._root = root
        self._hangar_repo = Repository(root)
        self._optimized_Rcheckout = None
        self._optimized_Wcheckout = None
        self._has_optimized = {'R': False, 'W': False}

    @property
    def hangar_repository(self):
        return self._hangar_repo

    @property
    def is_optimized(self):
        return any(self._has_optimized.values())

    def open_global_checkout(self, write):
        head_commit = get_current_head(self._root)
        self._optimized_Rcheckout = self._hangar_repo.checkout(commit=head_commit)
        self._optimized_Rcheckout.__enter__()
        self._has_optimized['R'] = True
        if write:
            self._optimized_Wcheckout = self._hangar_repo.checkout(write=True)
            self._optimized_Wcheckout.__enter__()
            self._has_optimized['W'] = True

    def close_global_checkout(self):
        self._has_optimized['R'] = False
        self._optimized_Rcheckout.__exit__()
        self._optimized_Rcheckout.close()
        self._optimized_Rcheckout = None
        if self._has_optimized['W']:
            self._has_optimized['W'] = False
            self._optimized_Wcheckout.__exit__()
            self._optimized_Wcheckout.close()
            self._optimized_Wcheckout = None

    @contextmanager
    def read_checkout(self):
        """
        An api similar to hangar checkout in read mode but creates the checkout object
        using the commit hash from stock file instead of user supplying one. This enables
        users to rely on git checkout for hangar checkout as well. This checkout is being
        designed as a context manager that makes sure the checkout is closed. On entry
        and exit, the CM checks the existence of a global checkout. On entry, if global
        checkout exists, it returns the that instead of creating a new checkout. On exit,
        it doesn't close in case of global checkout instead it lets the CM do the closure
        """
        if self._has_optimized['R']:
            co = self._optimized_Rcheckout
        else:
            head_commit = get_current_head(self._root)
            co = self._hangar_repo.checkout(commit=head_commit)
        try:
            yield co
        finally:
            if not self._has_optimized['R']:
                co.close()

    @contextmanager
    def write_checkout(self):
        """
        An API similar to hangar checkout in write mode but does the closure of checkout
        on the exit of CM. It also monitors the existence of global checkout and open
        or close a local checkout if the global checkout doesn't exist
        """
        if self._has_optimized['W']:
            co = self._optimized_Wcheckout
        else:
            co = self._hangar_repo.checkout(write=True)
        try:
            yield co
        finally:
            if not self._has_optimized['W']:
                co.close()

    @property
    def stockroot(self) -> Path:
        """
        Returns the root of stock repository
        """
        return self._root


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
