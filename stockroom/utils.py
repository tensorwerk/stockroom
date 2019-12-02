from pathlib import Path


def get_stock_root():
    # TODO: would CWD work always
    path = Path.cwd()
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
            return None
        path = path.parent


def get_current_head(root: Path):
    head = root.joinpath('head.stock')
    with open(head, 'r') as f:
        commit = f.read()
        return commit if commit else ''


def set_current_head(root: Path, commit: str):
    head = root.joinpath('head.stock')
    with open(head, 'w+') as f:
        f.write(commit)
