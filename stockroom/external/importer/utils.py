import inspect
import os.path
from functools import partial
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from stockroom.external.importer import torchvision_importers
from stockroom.external.importer.base import BaseImporter


def is_valid(x):
    return inspect.isclass(x) and issubclass(x, BaseImporter) and x != BaseImporter


importers_dict = {
    "torchvision": {
        cls.name: cls for _, cls in inspect.getmembers(torchvision_importers, is_valid)
    }
}


def get_importers(source: str, download_dir: Path):
    try:
        package, dataset = source.split(".")
    except ValueError:
        raise RuntimeError(f"Could not parse the source string '{source}'")

    try:
        return importers_dict[package][dataset].gen_splits(download_dir)
    except KeyError:
        raise RuntimeError(
            "Could not fetch the dataset you were looking for. "
            "Create a request for new importers"
        )


downloadbar = Progress(
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
    transient=False,
)

unzipbar = Progress(transient=True,)


def download(urls: dict, dest_dir: str):
    """
    Downloads multiple files into the given directory.

    Parameters
    ----------
    urls: a dict which maps the final filename to the url you want to download.
    dest_dir: the path to which you want to download.
    """
    total_size = sum(
        [int(urlopen(url).info()["Content-length"]) for url in urls.values()]
    )

    with downloadbar:
        t = downloadbar.add_task("Downloading...", total=total_size, filename="")
        for url in urls:
            filename = url
            dest_path = os.path.join(dest_dir, filename)
            response = urlopen(urls[url])
            downloadbar.update(t, filename=filename)
            with open(dest_path, "wb") as dest_file:
                for data in iter(partial(response.read, 32768), b""):
                    dest_file.write(data)
                    downloadbar.update(t, advance=len(data), refresh=True)


def unzip(files: list, dest_dir: str):
    """
    Extracts a list of file to the destination directory.

    Parameters
    ----------
    files:  The list of zip files you want to extract.
    dest_dir: The directory to which you want to extract it to.
    """
    print("Extracting files...")
    for file in files:
        file = os.path.join(dest_dir, file)
        with ZipFile(file, "r") as z:
            z.extractall(dest_dir)

        file_name = file.split("/")[-1]
        print(f"Extracted {file_name}!")
