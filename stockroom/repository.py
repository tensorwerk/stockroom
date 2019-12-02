from pathlib import Path
from hangar import Repository
from .utils import get_stock_root


def init(name, email, overwrite):
    """ init hangar repo, create stock file and add details to .gitignore """
    if not Path.cwd().joinpath('.git').exists():
        raise RuntimeError("stock init should execute only in a"
                           " git repository. Try running stock "
                           "init after git init")
    repo = Repository(Path.cwd(), exists=False)
    if repo.initialized and (not overwrite):
        commit_hash = repo.log(return_contents=True)['head']
        print(f'Repo already exists at: {repo.path}')
    else:
        commit_hash = ''
        repo.init(user_name=name, user_email=email, remove_old=overwrite)

    stock_file = Path.cwd().joinpath('head.stock')
    if not stock_file.exists():
        with open(stock_file, 'w+') as f:
            f.write(commit_hash)
        print("Stock file created")

    gitignore = Path.cwd().joinpath('.gitignore')
    # TODO make sure this creates the file when file doesn't exist
    with open(gitignore, 'a+') as f:
        f.seek(0)
        if '.hangar' not in f.read():
            f.write('\n.hangar\n')


def commit(message):
    repo = Repository(Path.cwd())
    with repo.checkout(write=True) as co:
        root = get_stock_root()
        if not root:
            raise FileNotFoundError("Could not find stock file. Aborting..")
        digest = co.commit(message)
        with open(root.joinpath('head.stock'), 'w') as f:
            f.write(digest)
        # TODO: print message about file write as well
    # TODO: should be done in the __exit__ of hangar checkout
    co.close()
    return digest
