import inspect

import pytest
import stockroom.external.importer.utils as importer_utils
import torchvision_datasets as t_datasets
from torchvision import datasets


def mock_download(urls, dest_dir):
    pass


def mock_unzip(files, dest_dir):
    pass


@pytest.fixture()
def get_coco_files(monkeypatch):
    monkeypatch.setattr(importer_utils, "download", mock_download)
    monkeypatch.setattr(importer_utils, "unzip", mock_unzip)


def is_valid(x):
    return (
        inspect.isclass(x)
        and issubclass(x, t_datasets.Torchvision)
        and x != t_datasets.Torchvision
    )


@pytest.fixture()
def torchvision_datasets(monkeypatch):
    for n, cls in inspect.getmembers(t_datasets, is_valid):
        monkeypatch.setattr(datasets, n, cls)
