from pathlib import Path
from stockroom import init_repo
import pytest
import hangar
import hangar.checkout


class TestInit:
    @staticmethod
    @pytest.fixture(autouse=False)
    def repo_path(monkeypatch, managed_tmpdir):
        path = Path(managed_tmpdir)
        monkeypatch.setattr(Path, 'cwd', lambda: path)
        return path

    @staticmethod
    @pytest.fixture(autouse=False)
    def cwd(repo_path):
        repo_path.joinpath('.git').mkdir()
        return repo_path

    def test_init(self, repo_path):
        cwd = repo_path
        cwd.joinpath(".git").mkdir()
        with pytest.raises(ValueError):
            init_repo(overwrite=True)
        with pytest.raises(ValueError):
            init_repo(name='some', overwrite=True)
        with pytest.raises(ValueError):
            init_repo(email='some', overwrite=True)
        init_repo('s', 'a@b.c', overwrite=True)
        with open(cwd.joinpath('.gitignore')) as f:
            assert '\n.hangar\n' in f.read()
        assert cwd.joinpath('.hangar').exists()
        assert cwd.joinpath('head.stock').exists()

    def test_stock_init_on_existing_hangar_repo(self, cwd):
        repo = hangar.Repository(cwd, exists=False)
        repo.init('a', 'a@b.c')
        repo._env._close_environments()
        assert not cwd.joinpath('head.stock').exists()
        init_repo()
        assert cwd.joinpath('head.stock').exists()
        with open(cwd.joinpath('.gitignore')) as f:
            assert '\n.hangar\n' in f.read()


class TestCommit:
    def test_basic(self, writer_stock):
        writer_stock.experiment['key1'] = 'value'
        writer_stock.commit('generic data')
        assert writer_stock.experiment['key1'] == 'value'
        writer_stock.experiment['key2'] = 'value2'

    def test_commit_hash(self, writer_stock):
        writer_stock.experiment['key1'] = 'value'
        writer_stock.commit('generic data')
        with open(writer_stock.stockroot/'head.stock') as f:
            digest1 = f.read()
        writer_stock.experiment['key2'] = 'value2'
        writer_stock.commit('generic data 2')
        with open(writer_stock.stockroot/'head.stock') as f:
            digest2 = f.read()
        log = writer_stock._repo.log(return_contents=True)
        log['order'].pop()  # removing the digest from conftest.py
        assert log['order'] == [digest2, digest1]


def test_hangar_checkout_from_stock_obj(writer_stock):
    co = writer_stock.accessor
    assert isinstance(co, hangar.checkout.WriterCheckout)
    assert hasattr(co, '_writer_lock')

    co.close()
    with pytest.raises(PermissionError):
        writer_stock.experiment['key1'] = 'value'
