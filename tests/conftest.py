from pathlib import Path
import shutil
import pytest
import hangar
import numpy as np
import lmdb
from stockroom import init_repo, StockRoom


@pytest.fixture()
def managed_tmpdir(monkeypatch, tmp_path):
    monkeypatch.setitem(hangar.constants.LMDB_SETTINGS, 'map_size', 2_000_000)
    yield tmp_path
    shutil.rmtree(tmp_path)


@pytest.fixture()
def repo(monkeypatch, managed_tmpdir):
    cwd = Path(managed_tmpdir)
    monkeypatch.setattr(Path, 'cwd', lambda: cwd)
    cwd.joinpath(".git").mkdir()
    cwd.joinpath(".gitignore").touch()
    init_repo('s', 'a@b.c', overwrite=True)
    yield None
    stock = StockRoom()
    # TODO: It's better to have the `close_environment` as public attribute in hangar
    try:
        stock._repo.hangar_repository._env._close_environments()
    except lmdb.Error:
        pass  # environment already closed by downstream functions


@pytest.fixture()
def repo_with_aset(repo):
    repo = hangar.Repository(Path.cwd())
    co = repo.checkout(write=True)
    arr = np.arange(20).reshape(4, 5)
    co.arraysets.init_arrayset('aset', prototype=arr)
    co.commit('init aset')
    co.close()
    yield None
    # TODO: It's better to have the `close_environment` as public attribute in hangar
    repo._env._close_environments()
    stock = StockRoom()
    stock._repo.hangar_repository._env._close_environments()
