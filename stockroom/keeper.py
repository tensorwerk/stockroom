from pathlib import Path
import warnings
from hangar import Repository


def init_repo(name=None, email=None, overwrite=False):
    """ init hangar repo, create stock file and add details to .gitignore """
    if not Path.cwd().joinpath('.git').exists():
        warnings.warn("initializing stock repository in a directory which is not a "
                      "git repository. Some features won't work", UserWarning)
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
    if stock_file.exists():
        warnings.warn("Trying to initialize an already initialized stock repository. "
                      "No action taken", UserWarning)
    else:
        with open(str(stock_file), 'w+') as f:
            f.write(commit_hash)
        print("Stock file created")

    gitignore = Path.cwd()/'.gitignore'
    with open(str(gitignore), 'a+') as f:
        f.seek(0)
        if '.hangar' not in f.read():
            f.write('\n# hangar artifacts\n.hangar\n')
