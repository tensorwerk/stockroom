from pathlib import Path
import shutil
import pytest
import hangar
import numpy as np
import lmdb
import stockroom.repository
from stockroom import init_repo, StockRoom


@pytest.fixture()
def managed_tmpdir(monkeypatch, tmp_path):
    monkeypatch.setitem(hangar.constants.LMDB_SETTINGS, 'map_size', 2_000_000)
    monkeypatch.setitem(hangar.constants.LMDB_SETTINGS, 'map_size', 2_000_000)
    monkeypatch.setattr(hangar.backends.hdf5_00, 'COLLECTION_COUNT', 10)
    monkeypatch.setattr(hangar.backends.hdf5_00, 'COLLECTION_SIZE', 50)
    monkeypatch.setattr(hangar.backends.hdf5_01, 'COLLECTION_COUNT', 10)
    monkeypatch.setattr(hangar.backends.hdf5_01, 'COLLECTION_SIZE', 50)
    monkeypatch.setattr(hangar.backends.numpy_10, 'COLLECTION_SIZE', 50)
    stockroom.repository.RootTracker._instances = {}
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
    repo._env._close_environments()
    stock = StockRoom()
    stock._repo.hangar_repository._env._close_environments()
