from pathlib import Path
import inspect
from stockroom.external.importer.base import BaseImporter
from stockroom.external.importer import torchvision_importers


def is_valid(x):
    return inspect.isclass(x) and issubclass(x, BaseImporter) and x != BaseImporter


importers_dict = {'torchvision': {cls.name: cls
                                  for _, cls in inspect.getmembers(torchvision_importers, is_valid)}}


def get_importers(source: str, download_dir: Path):
    try:
        package, dataset = source.split('.')
    except ValueError:
        raise RuntimeError(f"Could not parse the source string '{source}'")

    try:
        return (importers_dict[package][dataset](download_dir, train=True),
                importers_dict[package][dataset](download_dir, train=False))
    except KeyError:
        raise RuntimeError("Could not fetch the dataset you were looking for. "
                           "Create a request for new importers")
