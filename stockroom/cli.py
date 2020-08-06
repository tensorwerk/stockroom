from pathlib import Path
from contextlib import ExitStack

import click
from click_didyoumean import DYMGroup
from hangar import Repository

from stockroom.keeper import init_repo
from stockroom.core import StockRoom
from stockroom import __version__
from stockroom import external


@click.group(no_args_is_help=True, add_help_option=True,
             invoke_without_command=True, cls=DYMGroup)
@click.version_option(version=__version__, help='display current stockroom version')
def stock():
    """
    The `stock` CLI provides a git-like experience (whenever possible) to interact with
    the stock repository. It also means that the *current working directory* is where
    the stock repository would exist (like git 😊 ).
    """
    pass


@stock.command()
@click.option('--username', prompt='Username', help='Username of the user')
@click.option('--email', prompt='User Email', help='Email address of the user')
@click.option('--overwrite', is_flag=True, default=False,
              help='overwrite a repository if it exists at the current path')
def init(username, email, overwrite):
    """
    Init stockroom repository. This will create a .hangar directory and a `head.stock`
    file in your `cwd`. `stock init` would be triggered implicitly if you are making
    a stock repository by using `stock import` but in all other case, you'd need to
    initialize a stock repository to start operating on it with the python APIs
    """
    try:
        init_repo(username, email, overwrite)
    except RuntimeError as e:
        raise click.ClickException(e)  # type: ignore


@stock.command()
@click.option('--message', '-m', multiple=True,
              help=('The commit message. If multiple arguments are provided, '
                    'each of them gets converted into a new line'))
def commit(message):
    """
    It does a stock commit. Stock commit consists of two actions

    1. Make a hangar commit
    2. Update the `head.stock` file (git will track this file if you are using git)
    """
    if len(message) < 1:
        raise click.ClickException(ValueError("Require commit message"))
    # TODO: There should be a way to share the write enabled checkout if user need to
    #  commit let's say when he has a writer checkout open in jupyter notebook
    stock_obj = StockRoom(write=True)
    msg = '\n'.join(message)
    click.echo('Commit message:\n' + msg)
    try:
        digest = stock_obj.commit(message)
    except (FileNotFoundError, RuntimeError) as e:
        raise click.ClickException(e)  # type: ignore
    click.echo(f'Commit Successful. Digest: {digest}')


@stock.command(name='import')
@click.argument('dataset_name')
@click.option('--download-dir', '-d', default=Path.home(), type=click.Path(),
              help=('If you have the dataset downloaded in a non-default path or want '
                    'to download it to a non-default path, pass it here'))
def import_data(dataset_name, download_dir):
    """
    Downloads and add a pytorch dataset (from torchvision, torchtext or torchaudio)
    to StockRoom. It creates the repo if it doesn't exist and loads the dataset
    into a repo for you
    """
    try:
        stock_obj = StockRoom(write=True)
    except RuntimeError:
        repo = Repository('.', exists=False)
        if not repo.initialized:
            raise RuntimeError("Repository is not initialized. Check `stock init --help` "
                               "details about how to initialize a repository")
        else:
            raise
    # TODO: use the auto-column-creation logic in stockroom later
    co = stock_obj.accessor
    importers = external.get_importers(dataset_name, download_dir)
    total_len = sum([len(importer) for importer in importers])
    with click.progressbar(label='Adding data to StockRoom', length=total_len) as bar:
        for importer in importers:
            column_names = importer.column_names()
            dtypes = importer.dtypes()
            shapes = importer.shapes()
            for colname, dtype, shape in zip(column_names, dtypes, shapes):
                if colname not in co.keys():
                    # TODO: this assuming importer always return a numpy flat array
                    co.add_ndarray_column(colname, dtype=dtype, shape=shape)
            columns = [co[name] for name in column_names]
            with ExitStack() as stack:
                for col in columns:
                    stack.enter_context(col)
                for i, data in enumerate(importer):
                    bar.update(1)
                    for col, dt in zip(columns, data):
                        # TODO: use the keys from importer
                        col[i] = dt
    stock_obj.commit(f'Data from {dataset_name} added through stock import')
    stock_obj.close()
    click.echo(f'The {dataset_name} dataset has been added to StockRoom')
