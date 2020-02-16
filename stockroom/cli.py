import click
from .repository import init_repo
from .main import StockRoom


@click.group(no_args_is_help=True, add_help_option=True, invoke_without_command=True)
def main():
    """
    With ``stock`` we introduces a minimal set of commands which are necessary to run a
    git + stockroom workflow. You will also be able to setup github hooks for few
    ``stock`` actions in the upcoming release.
    """
    pass


@main.command()
@click.option('--name', prompt='User Name', help='First and last name of user')
@click.option('--email', prompt='User Email', help='Email address of the user')
@click.option('--overwrite', is_flag=True, default=False,
              help='overwrite a repository if it exists at the current path')
def init(name, email, overwrite):
    """
    Init stockroom repository. A stockroom repository is a hangar repository plus
    a `head.stock` that will be tracked by git.
    """
    try:
        init_repo(name, email, overwrite)
    except RuntimeError as e:
        raise click.ClickException(e)  # type: ignore


@main.command()
@click.option('--message', '-m', multiple=True,
              help=('The commit message. If multiple arguments are provided, '
                    'each of them gets converted into a new line'))
def commit(message):
    """
    It does a stock commit. Stock commit consists of two actions

    1. Make a hangar commit and add the changed data to the repository
    2. Update the `head.stock` file which should be tracked with a git commit
    """
    stock = StockRoom()
    msg = '\n'.join(message)
    click.echo('Commit message:\n' + msg)
    try:
        digest = stock.commit(message)
    except (FileNotFoundError, RuntimeError) as e:
        raise click.ClickException(e)  # type: ignore
    click.echo(f'Commit Successful. Digest: {digest}')
