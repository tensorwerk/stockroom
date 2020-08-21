from pathlib import Path

import click
from click_didyoumean import DYMGroup  # type: ignore
from hangar import Repository
from rich.progress import Progress
from stockroom import __version__, external
from stockroom.core import StockRoom
from stockroom.keeper import init_repo
from stockroom.utils import clean_create_column, print_columns_added


@click.group(
    no_args_is_help=True,
    add_help_option=True,
    invoke_without_command=True,
    cls=DYMGroup,
)
@click.version_option(version=__version__, help="display current stockroom version")
def stock():
    """
    The `stock` CLI provides a git-like experience (whenever possible) to interact with
    the stock repository. It also means that the *current working directory* is where
    the stock repository would exist (like git 😊 ).
    """
    pass


@stock.command()
@click.option("--username", prompt="Username", help="Username of the user")
@click.option("--email", prompt="User Email", help="Email address of the user")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="overwrite a repository if it exists at the current path",
)
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
@click.option(
    "--message",
    "-m",
    multiple=True,
    help=(
        "The commit message. If multiple arguments are provided, "
        "each of them gets converted into a new line"
    ),
)
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
    stock_obj = StockRoom(enable_write=True)
    msg = "\n".join(message)
    click.echo("Commit message:\n" + msg)
    try:
        digest = stock_obj.commit(message)
    except (FileNotFoundError, RuntimeError) as e:
        raise click.ClickException(e)  # type: ignore
    click.echo(f"Commit Successful. Digest: {digest}")


@stock.command()
def liberate():
    """
    Release the writer lock forcefully and make the repository available for writing.

    Warning
    -------
    If another process, that has the writer lock, is writing to the repo, releasing the
    lock leads to an exception in that process. Use it carefully
    """
    repo = Repository(Path.cwd(), exists=True)
    if repo.force_release_writer_lock():
        click.echo("Writer lock released")
    else:
        click.echo("Error while attempting to release the writer lock")


@stock.command(name="import")
@click.argument("dataset_name")
@click.option(
    "--download-dir",
    "-d",
    default=Path.cwd(),
    type=click.Path(),
    help=(
        "If you have the dataset downloaded in a non-default path or want "
        "to download it to a non-default path, pass it here"
    ),
)
def import_data(dataset_name, download_dir):
    """
    Downloads and add a pytorch dataset (from torchvision, torchtext or torchaudio)
    to StockRoom. It creates the repo if it doesn't exist and loads the dataset
    into a repo for you
    """
    try:
        stock_obj = StockRoom(enable_write=True)
    except RuntimeError:
        repo = Repository(".", exists=False)
        if not repo.initialized:
            raise RuntimeError(
                "Repository is not initialized. Check `stock init --help` "
                "details about how to initialize a repository"
            )
        else:
            raise
    # TODO: use the auto-column-creation logic in stockroom later
    co = stock_obj.accessor
    importers = external.get_importers(dataset_name, download_dir)
    total_len = sum([len(importer) for importer in importers])
    splits_added = {}

    with Progress() as progress:
        stock_add_bar = progress.add_task("Adding to Stockroom: ", total=total_len)
        for importer in importers:
            column_names = importer.column_names()
            dtypes = importer.dtypes()
            shapes = importer.shapes()
            is_variable = importer.variability_status()

            new_col_details = []
            splits_added[importer.split] = (column_names, len(importer))
            for colname, dtype, shape in zip(column_names, dtypes, shapes):
                if colname not in co.keys():
                    # TODO: this assuming importer always return a numpy flat array

                    contains_subsamples = False
                    if isinstance(dtype, list):
                        contains_subsamples = True
                        dtype = dtype[0]

                    if isinstance(dtype, str):
                        new_col_details.append(
                                (
                                    "add_str_column",
                                    {"name": colname,
                                     "contains_subsamples": contains_subsamples}
                                    )
                                )
                    else:
                        new_col_details.append(
                            (
                                "add_ndarray_column",
                                {"name": colname, "dtype": dtype, "shape": shape,
                                 'contains_subsamples': contains_subsamples,
                                 'variable_shape': is_variable},
                            )
                        )
            clean_create_column(co, new_col_details)

            columns = [co[name] for name in column_names]
            for i, data in enumerate(importer):
                progress.advance(stock_add_bar)
                for col, dt in zip(columns, data):
                    # TODO: use the keys from importer
                    col[i] = dt

    stock_obj.commit(f"Data from {dataset_name} added through stock import")
    stock_obj.close()
    click.echo(f"The {dataset_name} dataset has been added to StockRoom.")
    print_columns_added(splits_added)
