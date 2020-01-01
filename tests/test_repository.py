from pathlib import Path
import stockroom
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
        stockroom.init('s', 'a@b.c', overwrite=True)
        with open(cwd.joinpath('.gitignore')) as f:
            assert '\n.hangar\n' in f.read()
        assert cwd.joinpath('.hangar').exists()
        assert cwd.joinpath('head.stock').exists()

    def test_init_on_non_git_folder(self, repo_path):
        with pytest.raises(RuntimeError):
            stockroom.init('s', 'a@b.c', overwrite=True)

    def test_stock_init_on_existing_hangar_repo(self, cwd):
        repo = hangar.Repository(cwd, exists=False)
        repo.init('a', 'a@b.c')
        assert not cwd.joinpath('head.stock').exists()
        stockroom.init()
        assert cwd.joinpath('head.stock').exists()
        with open(cwd.joinpath('.gitignore')) as f:
            assert '\n.hangar\n' in f.read()


class TestCommit:
    def test_basic(self, repo):
        genericstore = stockroom.genericstore(write=True)
        genericstore.save('key1', 'value')
        stockroom.commit('generic data')
        read_gs = stockroom.genericstore()
        assert read_gs.load("key1") == 'value'
        genericstore.save('key2', 'value2')
        assert genericstore.load('key2') == 'value2'
        read_gs = stockroom.genericstore()
        with pytest.raises(KeyError):
            read_gs.load('key2')

    def test_commit_hash(self, repo):
        genericstore = stockroom.genericstore(write=True)
        genericstore.save('key1', 'value')
        stockroom.commit('generic data')
        with open(genericstore._repo.stockroot/'head.stock') as f:
            digest1 = f.read()
        genericstore.save('key2', 'value2')
        stockroom.commit('generic data 2')
        with open(genericstore._repo.stockroot/'head.stock') as f:
            digest2 = f.read()
        log = genericstore._repo._hangar_repo.log(return_contents=True)
        assert log['order'] == [digest2, digest1]

