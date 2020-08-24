import numpy as np
import pytest
import stockroom.cli as cli
from click.testing import CliRunner
from stockroom import StockRoom


@pytest.mark.parametrize(
    "dataset, splits, columns", [("cifar10", ["test", "train"], ["image", "label"])]
)
def test_import_cifar(repo, torchvision_datasets, dataset, splits, columns):
    runner = CliRunner()
    res = runner.invoke(cli.import_data, [f"torchvision.{dataset}"])
    assert res.exit_code == 0

    keys = [f"{dataset}-{split}-{column}" for split in splits for column in columns]
    stock = StockRoom()
    assert stock.data.keys() == tuple(keys)

    assert stock.data[f"{dataset}-train-image"][0].shape == (3, 32, 32)
    assert stock.data[f"{dataset}-test-label"][0].shape == tuple()
    assert stock.data[f"{dataset}-train-image"][0].dtype == np.float32


@pytest.mark.parametrize(
    "dataset, splits, columns",
    [
        ("fashion_mnist", ["test", "train"], ["image", "label"]),
        ("mnist", ["test", "train"], ["image", "label"]),
    ],
)
def test_import_mnist(repo, torchvision_datasets, dataset, splits, columns):
    runner = CliRunner()
    res = runner.invoke(cli.import_data, [f"torchvision.{dataset}"])
    assert res.exit_code == 0

    keys = [f"{dataset}-{split}-{column}" for split in splits for column in columns]
    keys = sorted(keys)
    stock = StockRoom()
    data_keys = sorted(list(stock.data.keys()))
    assert data_keys == keys

    assert stock.data[f"{dataset}-train-image"][0].shape == (28, 28)
    assert stock.data[f"{dataset}-test-label"][0].shape == tuple()
    assert stock.data[f"{dataset}-train-image"][0].dtype == np.float32


@pytest.mark.parametrize(
    "dataset, splits, columns", [("image_folder", ["test"], ["image", "label"])]
)
def test_import_imagefolder(repo, torchvision_datasets, dataset, splits, columns):
    runner = CliRunner()
    res = runner.invoke(
        cli.import_data, [f"torchvision.{dataset}", "-d", f"{str(repo)}"]
    )
    assert res.exit_code == 0

    splits = [repo.name]
    keys = [f"{dataset}-{split}-{column}" for split in splits for column in columns]
    stock = StockRoom()
    assert stock.data.keys() == tuple(keys)

    assert stock.data[f"{dataset}-{splits[0]}-image"][0].shape == (500, 500, 3)
    assert stock.data[f"{dataset}-{splits[0]}-label"][0].shape == tuple()
    assert stock.data[f"{dataset}-{splits[0]}-image"][0].dtype == np.uint8


@pytest.mark.parametrize(
    "dataset, splits, columns",
    [
        ("voc_segmentation", ["train", "val", "trainval"], ["image", "segment"]),
        ("voc_detection", ["train", "val", "trainval"], ["image", "names", "boxes"]),
    ],
)
def test_import_voc(repo, torchvision_datasets, dataset, splits, columns):
    runner = CliRunner()
    res = runner.invoke(cli.import_data, [f"torchvision.{dataset}"])
    assert res.exit_code == 0

    keys = [f"{dataset}-{split}-{column}" for split in splits for column in columns]
    stock = StockRoom()
    assert sorted(stock.data.keys()) == sorted(keys)

    assert stock.data[f"{dataset}-train-image"][0].shape == (3, 500, 500)
    assert stock.data[f"{dataset}-train-image"][0].dtype == np.uint8
    assert stock.data[f"{dataset}-val-image"][0].shape == (3, 500, 500)
    assert stock.data[f"{dataset}-trainval-image"][0].shape == (3, 500, 500)
    if dataset == "voc_segmentation":
        assert stock.data[f"{dataset}-train-segment"][0].shape == (500, 500)
    elif dataset == "voc_detection":
        assert stock.data[f"{dataset}-train-names"][0][0] == "testname"
        assert stock.data[f"{dataset}-train-boxes"][0][0].shape == (2, 2)


@pytest.mark.parametrize(
    "dataset, splits, columns",
    [
        ("coco_captions", ["train", "val"], ["image", "captions"]),
        ("coco_detection", ["train", "val"], ["image", "boxes"]),
    ],
)
def test_import_coco(
    repo, torchvision_datasets, get_coco_files, dataset, splits, columns
):
    runner = CliRunner()
    with runner.isolated_filesystem():
        print(dataset)
        res = runner.invoke(cli.import_data, [f"torchvision.{dataset}"])
        assert res.exit_code == 0

    keys = [f"{dataset}-{split}-{column}" for split in splits for column in columns]
    stock = StockRoom()
    assert sorted(stock.data.keys()) == sorted(keys)
