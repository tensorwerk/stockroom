import types
import importlib
from pathlib import Path


def get_stock_root(path: Path) -> Path:
    """
    Traverse from given path up till root of the system to figure out the root of the
    stock repo. A stock repo must be hangar repo, a git repo and must have a head.stock
    file. The head.stock file has the information required for stockroom to manage
    checkout, branching etc and it is git tracked.

    Parameters
    ----------
    path : Path
        path from which stock root check starts

    Returns
    -------
    Path
        Location of root of stock repo
    """
    while True:
        stock_exist = path.joinpath('head.stock').exists()
        if stock_exist:
            hangar_exist = path.joinpath('.hangar').exists()
            git_exist = path.joinpath('.git').exists()
            if not hangar_exist and not git_exist:
                raise RuntimeError("Stock root should be the root of git and"
                                   "hangar repository")
            return path
        if path == path.parent:  # system root check
            raise RuntimeError("Could not find stock root. Are you in a "
                               "stock repository")
        path = path.parent


def get_current_head(root: Path) -> str:
    """
    Reads the stock file and return the commit hash if found

    Parameters
    ----------
    root : Path
        The stock root path

    Returns
    -------
    str
        commit hash if found. Empty string other wises
    """
    with open(root/'head.stock', 'r') as f:
        commit = f.read()
        return commit if commit else ''


def set_current_head(root: Path, commit: str):
    """
    Write a commit hash to the stock file.

    Parameters
    ----------
    root : Path
        The stock root path
    commit : str
        Commit hash that will be written to the stock file
    """
    with open(root/'head.stock', 'w+') as f:
        f.write(commit)


class LazyLoader(types.ModuleType):
    """
    Lazily import a module, mainly to avoid pulling in large dependencies
    """

    def __init__(self, local_name, parent_module_globals, name):
        self._local_name = local_name
        self._parent_module_globals = parent_module_globals
        super(LazyLoader, self).__init__(name)

    def _load(self):
        """Load the module and insert it into the parent's globals.

        Import the target module and insert it into the parent's namespace
        Update this object's dict so that if someone keeps a reference to the
        LazyLoader, lookups are efficient (__getattr__ is only called on
        lookups that fail).
        """
        module = importlib.import_module(self.__name__)
        self._parent_module_globals[self._local_name] = module
        self.__dict__.update(module.__dict__)
        return module

    def __getattr__(self, item):
        module = self._load()
        return getattr(module, item)

    def __dir__(self):
        module = self._load()
        return dir(module)

