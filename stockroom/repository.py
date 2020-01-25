from pathlib import Path
from hangar import Repository
from .utils import get_current_head


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

    def __init__(self, root):
        self._root: Path = root
        self._hangar_repo = Repository(root)

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

def init_repo(name=None, email=None, overwrite=False):
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
