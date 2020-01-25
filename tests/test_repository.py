from pathlib import Path
from stockroom import StockRoom, init_repo
import pytest
import hangar


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
        init_repo('s', 'a@b.c', overwrite=True)
        with open(cwd.joinpath('.gitignore')) as f:
            assert '\n.hangar\n' in f.read()
        assert cwd.joinpath('.hangar').exists()
        assert cwd.joinpath('head.stock').exists()

    def test_init_on_non_git_folder(self, repo_path):
        with pytest.raises(RuntimeError):
            init_repo('s', 'a@b.c', overwrite=True)

    def test_stock_init_on_existing_hangar_repo(self, cwd):
        repo = hangar.Repository(cwd, exists=False)
        repo.init('a', 'a@b.c')
        assert not cwd.joinpath('head.stock').exists()
        init_repo()
        assert cwd.joinpath('head.stock').exists()
        with open(cwd.joinpath('.gitignore')) as f:
            assert '\n.hangar\n' in f.read()


class TestCommit:
    def test_basic(self, repo):
        stock = StockRoom()
        stock.tag['key1'] = 'value'
        stock.commit('generic data')
        assert stock.tag['key1'] == 'value'
        stock.tag['key2'] = 'value2'
        assert stock.tag['key2'] == 'value2'

    def test_commit_hash(self, repo):
        stock = StockRoom()
        stock.tag['key1'] = 'value'
        stock.commit('generic data')
        with open(stock._repo.stockroot/'head.stock') as f:
            digest1 = f.read()
        stock.tag['key2'] = 'value2'
        stock.commit('generic data 2')
        with open(stock._repo.stockroot/'head.stock') as f:
            digest2 = f.read()
        log = stock._repo._hangar_repo.log(return_contents=True)
        assert log['order'] == [digest2, digest1]

