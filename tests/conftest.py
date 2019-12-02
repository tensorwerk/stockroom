from pathlib import Path
import shutil
import pytest
import stockroom

# TODO: restructure the core and monkey patch the repo creation at CWD


@pytest.fixture()
def repo():
    yield stockroom.init('s', 'a@b.c', overwrite=True)
    cwd = Path.cwd()
    shutil.rmtree(cwd.joinpath('.hangar'))
    cwd.joinpath('head.stock').unlink()


