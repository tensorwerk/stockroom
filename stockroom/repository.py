from typing import Union
from pathlib import Path
from hangar import Repository
from .utils import get_stock_root, get_current_head, set_current_head


class StockRepository:
    """
    A StockRoom wrapper class for hangar repo operations. Every hangar repo
    interactions that is being done through stockroom (other than stock init)
    should go through this class. Unlike hangar Repository, this class constructor
    assumes the hangar repo is already initialized. Three class variables keep the
    reference required for all the storages to interact with hangar repository.
        1. Hangar repo object
        2. Hangar repository root
        3. Write checkout
    Since these are class variables, they are not re-created on each initialization
    and hence we can make sure at most, there will be only one writer checkout object
    active at any point in time (Hangar will make sure this assertion is True anyways)
    """
    _write_checkout = None
    _root: Union[Path, None] = None
    _hangar_repo = None

    def __init__(self):
        self._setup()

    @classmethod
    def _setup(cls):
        """
        Setup the stock repository object by assuming the current working directory as
        the point of operation. It doesn't require user to pass the path but used the
        ``cwd``. This function creates the hangar repo object only if it is not creates
        already. It also assumes that the hangar repo is already initialized and expect
        the presence of stock file
        """
        if cls._hangar_repo is None:
            cwd = Path.cwd()
            cls._root = get_stock_root(cwd)
            if not cls._root:
                raise FileNotFoundError("Could not find stock file. "
                                        "Did you forget to `stock init`?")
            cls._hangar_repo = Repository(cls._root)
            if not cls._hangar_repo.initialized:
                raise RuntimeError("Repository has not been initialized")

    @classmethod
    def _teardown(cls):
        cls._hangar_repo._env._close_environments()
        cls._write_checkout = None
        cls._root = None
        cls._hangar_repo = None

    @classmethod
    def checkout(cls, write=False):
        """
        An api similar to hangar checkout but creates the checkout object using the
        commit hash from stock file instead of user supplying one. This enalbes users
        to rely on git checkout for hangar checkout as well.
        :param write: bool, write enabled checkout or not
        """
        if write:
            if cls._write_checkout and hasattr(cls._write_checkout, '_writer_lock'):
                raise PermissionError("Another write operation is in progress. "
                                      "Could not acquire the lock")
            cls._write_checkout = cls._hangar_repo.checkout(write=True)
            return cls._write_checkout
        else:
            head_commit = get_current_head(cls._root)
            return cls._hangar_repo.checkout(commit=head_commit)
    
    @property
    def stockroot(self):
        return self._root


# ================================== User facing Repository functions ================================

def init(name=None, email=None, overwrite=False):
    """ init hangar repo, create stock file and add details to .gitignore """
    if not Path.cwd().joinpath('.git').exists():
        raise RuntimeError("stock init should execute only in a"
                           " git repository. Try running stock "
                           "init after git init")
    repo = Repository(Path.cwd(), exists=False)
    if repo.initialized and (not overwrite):
        commit_hash = repo.log(return_contents=True)['head']
        print(f'Hangar Repo already exists at {repo.path}. '
              f'Initializing it as stock repository')
    else:
        if not all([name, email]):
            raise ValueError("Both ``name`` and ``email`` has to be non-empty"
                             " strings for initializing hangar repository")
        commit_hash = ''
        repo.init(user_name=name, user_email=email, remove_old=overwrite)

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


def commit(message):
    """
    Make a stock commit. A stock commit is a hangar commit plus writing the
    commit hash to the stock file. This function opens the stock checkout in
    write mode and close after the commit. Which means, no other write
    operations should be running while stock commit is in progress
    """
    repo = StockRepository()
    with repo.checkout(write=True) as co:
        digest = co.commit(message)
    co.close()
    set_current_head(repo.stockroot, digest)
    return digest
