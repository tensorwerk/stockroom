import pytest
from pathlib import Path
from click.testing import CliRunner
import stockroom.cli as cli
from stockroom import StockRoom


def test_version():
    import stockroom
    runner = CliRunner()
    res = runner.invoke(cli.main, ['--version'])
    assert res.exit_code == 0
    assert res.stdout == f'main, version {stockroom.__version__}\n'


def test_init_repo():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with pytest.raises(RuntimeError):
            stock = StockRoom()
        res = runner.invoke(cli.init, ['--name', 'test', '--email', 'test@foo.com'])
        assert 'Error: stock init should execute only in a git repository' in res.output

        cwd = Path.cwd()
        cwd.joinpath('.git').mkdir(exist_ok=True)
        res = runner.invoke(cli.init, ['--name', 'test', '--email', 'test@foo.com'])
        assert res.exit_code == 0
        stock = StockRoom()


def test_commit(repo_with_col):
    runner = CliRunner()
    stock = StockRoom()
    stock.tag['key'] = 'value'
    res = runner.invoke(cli.commit, [])
    assert 'Error: Require commit message\n' in res.stdout
    res = runner.invoke(cli.commit, ['-m', 'test commit'])
    assert res.exit_code == 0
    assert 'Commit message:\ntest commit' in res.stdout
    assert 'Commit Successful. Digest' in res.stdout
    stock._stock_repo.hangar_repo._env._close_environments()
