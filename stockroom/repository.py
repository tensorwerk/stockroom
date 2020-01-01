from typing import Union
from pathlib import Path
from hangar import Repository
from .utils import get_stock_root, get_current_head, set_current_head


class StockRepository:
    """
    A StockRoom wrapper class for hangar repo operations. Every hangar repo
    interactions that is being done through stockroom (other than stock init)
    should go through this class. Unlike hangar Repository, this class constructor
    assumes the hangar repo is already initialized. Hangar will make sure there are
    only one writer class active always.
    The constructor creates the hangar repo object on instantiation while it assumes
    that the hangar repo is already initialized and expect the presence of stock file
    and the .git folder
    """

    def __init__(self, root=None):
        if root is None:
            root = get_stock_root(Path.cwd())
        self._root: Union[Path, None] = root
        self._hangar_repo = Repository(root)
        if not self._hangar_repo.initialized:
            raise RuntimeError("Repository has not been initialized")

    def checkout(self, write=False):
        """An api similar to hangar checkout but creates the checkout object using the
        commit hash from stock file instead of user supplying one. This enables users
        to rely on git checkout for hangar checkout as well

        :param write: bool, write enabled checkout or not
        """
        if write:
            if self._hangar_repo.writer_lock_held:
                raise PermissionError("Another write operation is in progress. "
                                      "Could not acquire the lock")
            co = self._hangar_repo.checkout(write=True)
        else:
            head_commit = get_current_head(self._root)
            co = self._hangar_repo.checkout(commit=head_commit)
        return co
    
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
        if name is None or email is None:
            raise ValueError("Both ``name`` and ``email`` cannot be None")
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
