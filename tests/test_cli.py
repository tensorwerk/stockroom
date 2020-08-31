from pathlib import Path

import numpy as np
import pytest
import stockroom.cli as cli
from click.testing import CliRunner
from stockroom import StockRoom, console, init_repo
from test_model import get_model


def test_version():
    import stockroom

    runner = CliRunner()
    res = runner.invoke(cli.stock, ["--version"])
    assert res.exit_code == 0
    assert res.stdout == f"stock, version {stockroom.__version__}\n"


@pytest.mark.filterwarnings("ignore: initializing stock")
def test_init_repo():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with pytest.raises(RuntimeError):
            StockRoom()
        res = runner.invoke(cli.init, ["--username", "test", "--email", "test@foo.com"])
        assert res.exit_code == 0
        StockRoom()


def test_commit(repo_with_col):
    runner = CliRunner()
    stock = StockRoom(enable_write=True)
    stock.experiment["key"] = "value"
    stock.close()
    res = runner.invoke(cli.commit, [])
    assert "Error: Require commit message\n" in res.stdout
    res = runner.invoke(cli.commit, ["-m", "test commit"])
    assert res.exit_code == 0
    assert "Commit message:\ntest commit" in res.stdout
    assert "Commit Successful. Digest" in res.stdout
    stock._repo._env._close_environments()


def test_liberate(writer_stock):
    with pytest.raises(PermissionError):
        StockRoom(enable_write=True)
    runner = CliRunner()
    res = runner.invoke(cli.liberate)
    assert res.exit_code == 0
    stock = StockRoom(enable_write=True)
    stock.close()


def mock_model_table(models: tuple):
    if not models == ():
        assert isinstance(models, tuple)
        assert models[0] == "test_model"


def mock_experiment_table(tags: dict):
    if not tags == {}:
        assert isinstance(tags, dict)
        assert tags == {"test_tag": "0.01"}


def mock_data_table(column_info: list):
    if not column_info == []:
        name, length, shape, dtype = column_info[0]
        assert name == "ndcol"
        assert length == 1
        assert shape == (4, 5)
        assert dtype == np.int64


@pytest.mark.parametrize("flag", ["model", "data", "experiment"])
def test_list(writer_stock, monkeypatch, flag):
    monkeypatch.setattr(console, "print_models_table", mock_model_table)
    monkeypatch.setattr(console, "print_experiment_tags", mock_experiment_table)
    monkeypatch.setattr(console, "print_data_summary", mock_data_table)

    runner = CliRunner()
    res = runner.invoke(cli.list_shelf, [f"--{flag}"])
    # TODO: test the output
    assert res.exit_code == 0
    model = get_model()
    writer_stock.model["test_model"] = model.state_dict()
    writer_stock.experiment["test_tag"] = "0.01"
    writer_stock.data["ndcol"][0] = np.zeros((4, 5)).astype(np.int64)
    writer_stock.commit("added model")
    res = runner.invoke(cli.list_shelf, [f"--{flag}"])
    assert res.exit_code == 0


def test_get_stock_obj(managed_tmpdir, monkeypatch):
    cwd = Path(managed_tmpdir)
    monkeypatch.setattr(Path, "cwd", lambda: cwd)
    with pytest.raises(RuntimeError):
        cli.get_stock_obj(cwd)
    cwd.joinpath(".git").mkdir()
    cwd.joinpath(".gitignore").touch()
    init_repo("test", "t@est.com")
    stock_obj = cli.get_stock_obj(cwd)
    assert stock_obj.path == cwd
