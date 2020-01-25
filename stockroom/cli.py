import click
from .repository import init_repo
from .main import StockRoom


@click.group(no_args_is_help=True, add_help_option=True, invoke_without_command=True)
def main():
    """
    Grouping all stockroom commands
    """
    pass


@main.command()
@click.option('--message', '-m', multiple=True,
              help=('The commit message. If provided multiple times '
                    'each argument gets converted into a new line.'))
def commit(message):
    """Commits outstanding changes.

    Commit changes to the given files into the repository. You will need to
    'push' to push up your changes to other repositories.
    """
    stock = StockRoom()
    msg = '\n'.join(message)
    click.echo('Commit message:\n' + msg)
    try:
        digest = stock.commit(message)
    except (FileNotFoundError, RuntimeError) as e:
        raise click.ClickException(e)  # type: ignore
    click.echo(f'Commit Successful. Digest: {digest}')


@main.command()
@click.option('--name', prompt='User Name', help='first and last name of user')
@click.option('--email', prompt='User Email', help='email address of the user')
@click.option('--overwrite', is_flag=True, default=False,
              help='overwrite a repository if it exists at the current path')
def init(name, email, overwrite):
    """
    Init stockroom repository. A stockroom repository is a hangar repository plus
    a head.stock file that tracks the commits.
    """
    try:
        init_repo(name, email, overwrite)
    except RuntimeError as e:
        raise click.ClickException(e)  # type: ignore


