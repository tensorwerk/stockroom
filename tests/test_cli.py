from pathlib import Path

import pytest
from click.testing import CliRunner

import stockroom.cli as cli
from stockroom import StockRoom


def test_version():
    import stockroom
    runner = CliRunner()
    res = runner.invoke(cli.stock, ['--version'])
    assert res.exit_code == 0
    assert res.stdout == f'stock, version {stockroom.__version__}\n'


def test_init_repo():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with pytest.raises(RuntimeError):
            StockRoom()
        res = runner.invoke(cli.init, ['--username', 'test', '--email', 'test@foo.com'])
        assert res.exit_code == 0
        StockRoom()


def test_commit(repo_with_col):
    runner = CliRunner()
    stock = StockRoom(write=True)
    stock.experiment['key'] = 'value'
    stock.close()
    res = runner.invoke(cli.commit, [])
    assert 'Error: Require commit message\n' in res.stdout
    res = runner.invoke(cli.commit, ['-m', 'test commit'])
    assert res.exit_code == 0
    assert 'Commit message:\ntest commit' in res.stdout
    assert 'Commit Successful. Digest' in res.stdout
    stock._repo._env._close_environments()
