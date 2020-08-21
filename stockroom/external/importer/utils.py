import inspect
import os.path
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Iterable
from urllib.request import urlopen
from zipfile import ZipFile

from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
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
    transient=True,
)

unzipbar = Progress(transient=True,)


def download_url(task_id: TaskID, url: str, path: str) -> None:
    """Copy data from a url to a local file."""
    response = urlopen(url)
    # This will break if the response doesn't contain content length
    downloadbar.update(task_id, total=int(response.info()["Content-length"]))
    with open(path, "wb") as dest_file:
        downloadbar.start_task(task_id)
        for data in iter(partial(response.read, 32768), b""):
            dest_file.write(data)
            downloadbar.update(task_id, advance=len(data), refresh=True)


def unzip(task_id: TaskID, zipfile: str, extract_to: str):
    with ZipFile(zipfile, "r") as z:
        unzipbar.update(task_id, total=len(z.namelist()))
        unzipbar.start_task(task_id)
        for file in z.namelist():
            z.extract(file, extract_to)
            unzipbar.update(task_id, advance=1, refresh=True)


def get_files(urls: dict, dest_dir: str):
    """
    Download multuple files to the given directory and extract them.
    """
    with downloadbar:
        with ThreadPoolExecutor(max_workers=5) as pool:
            for url in urls:
                filename = url
                dest_path = os.path.join(dest_dir, filename)
                task_id = downloadbar.add_task(
                    "download", filename=filename, start=False
                )
                pool.submit(download_url, task_id, urls[url], dest_path)
    print("Downloaded required files!")

    with unzipbar:
        with ThreadPoolExecutor(max_workers=5) as pool:
            for url in urls:
                file = os.path.join(dest_dir, url)
                task_id = unzipbar.add_task(
                    "extracting", filename=filename, start=False
                )
                pool.submit(unzip, task_id, file, dest_dir)
    print("Extracted downloaded files!")
