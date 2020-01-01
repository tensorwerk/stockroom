from pathlib import Path
import shutil
import pytest
import hangar
import stockroom


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
    yield stockroom.init('s', 'a@b.c', overwrite=True)
    stockrepo = stockroom.repository.StockRepository()
    stockrepo._hangar_repo._env._close_environments()
    stockrepo._root = None
    stockrepo._hangar_repo = None

