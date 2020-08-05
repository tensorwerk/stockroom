from pathlib import Path
import click
from hangar import Repository
from stockroom.keeper import init_repo
from stockroom.core import StockRoom
from stockroom import __version__
from stockroom import external


@click.group(no_args_is_help=True, add_help_option=True, invoke_without_command=True)
@click.version_option(version=__version__, help='display current stockroom version')
def stock():
    """
    The `stock` CLI provides a git-like experience (whenever possible) to interact with
    the stock repository. It also means that the *current working directory* is where
    the stock repository would exist (like git 😊 ).
    """
    pass


@stock.command()
@click.option('--name', prompt='User Name', help='First and last name of user')
@click.option('--email', prompt='User Email', help='Email address of the user')
@click.option('--overwrite', is_flag=True, default=False,
              help='overwrite a repository if it exists at the current path')
def init(name, email, overwrite):
    """
    Init stockroom repository. This will create a .hangar directory and a `head.stock`
    file in your `cwd`. `stock init` would be triggered implicitly if you are making
    a stock repository by using `stock import` but in all other case, you'd need to
    initialize a stock repository to start operating on it with the python APIs
    """
    try:
        init_repo(name, email, overwrite)
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
