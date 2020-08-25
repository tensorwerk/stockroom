import inspect
import shutil
from pathlib import Path

import hangar
import numpy as np
import pytest
import torchvision_mocks as torchvision
from stockroom import StockRoom, keeper
from torchvision import datasets


@pytest.fixture()
def managed_tmpdir(monkeypatch, tmp_path):
    monkeypatch.setitem(hangar.constants.LMDB_SETTINGS, "map_size", 2_000_000)
    monkeypatch.setitem(hangar.constants.LMDB_SETTINGS, "map_size", 2_000_000)
    monkeypatch.setattr(hangar.backends.hdf5_00, "COLLECTION_COUNT", 10)
    monkeypatch.setattr(hangar.backends.hdf5_00, "COLLECTION_SIZE", 50)
    monkeypatch.setattr(hangar.backends.hdf5_01, "COLLECTION_COUNT", 10)
    monkeypatch.setattr(hangar.backends.hdf5_01, "COLLECTION_SIZE", 50)
    monkeypatch.setattr(hangar.backends.numpy_10, "COLLECTION_SIZE", 50)
    yield tmp_path
    shutil.rmtree(tmp_path)


@pytest.fixture()
def repo(monkeypatch, managed_tmpdir):
    cwd = Path(managed_tmpdir)
    monkeypatch.setattr(Path, "cwd", lambda: cwd)
    cwd.joinpath(".git").mkdir()
    cwd.joinpath(".gitignore").touch()
    keeper.init_repo("s", "a@b.c", overwrite=True)
    yield None


@pytest.fixture()
def repo_with_col(repo):
    repo = hangar.Repository(Path.cwd())
    co = repo.checkout(write=True)
    arr = np.arange(20).reshape(4, 5)
    co.add_ndarray_column("ndcol", prototype=arr)
    co.commit("init column")
    co.close()
    yield None
    repo._env._close_environments()


@pytest.fixture()
def writer_stock(repo_with_col):
    stock_obj = StockRoom(enable_write=True)
    yield stock_obj
    stock_obj._repo._env._close_environments()


@pytest.fixture()
def reader_stock(writer_stock):
    arr = np.arange(20).reshape(4, 5)
    col = writer_stock.data["ndcol"]
    col[1] = arr
    writer_stock.commit("added first data point")
    writer_stock.close()
    stock_obj = StockRoom()
    yield stock_obj
    stock_obj._repo._env._close_environments()


def is_valid(x):
    return (
        inspect.isclass(x)
        and issubclass(x, torchvision.Torchvision)
        and x != torchvision.Torchvision
    )


@pytest.fixture()
def torchvision_datasets(monkeypatch):
    for n, cls in inspect.getmembers(torchvision, is_valid):
        monkeypatch.setattr(datasets, n, cls)
