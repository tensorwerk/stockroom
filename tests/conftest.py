from pathlib import Path
import shutil
import pytest
import hangar
import numpy as np
from stockroom import init_repo


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


@pytest.fixture()
def repo_with_aset(repo):
    repo = hangar.Repository(Path.cwd())
    co = repo.checkout(write=True)
    arr = np.arange(20).reshape(4, 5)
    co.arraysets.init_arrayset('aset', prototype=arr)
    co.commit('init aset')
    co.close()
    yield None


