from pathlib import Path
import click
from hangar import Repository
from . import repository


# TODO: move repetative code in hangar and here to a common function
pass_repo = click.make_pass_decorator(Repository, ensure=True)


@click.group(no_args_is_help=True, add_help_option=True, invoke_without_command=True)
@click.pass_context
def main(ctx):
    cwd = Path.cwd()
    ctx.obj = Repository(path=cwd, exists=False)


@main.command()
@click.option('--message', '-m', multiple=True,
              help=('The commit message. If provided multiple times '
                    'each argument gets converted into a new line.'))
@pass_repo
def commit(repo: Repository, message):
    """Commits outstanding changes.

    Commit changes to the given files into the repository. You will need to
    'push' to push up your changes to other repositories.
    """
    from hangar.records.summarize import status
    if not message:
        with repo.checkout(write=True) as co:
            diff = co.diff.staged()
            status_txt = status(co.branch_name, diff.diff)
            status_txt.seek(0)
            marker = '# Changes To Be committed: \n'
            hint = ['\n', '\n', marker, '# \n']
            for line in status_txt.readlines():
                hint.append(f'# {line}')
            # open default system editor
            message = click.edit(''.join(hint))
            if message is None:
                click.echo('Aborted!')
                return
            msg = message.split(marker)[0].rstrip()
            if not msg:
                click.echo('Aborted! Empty commit message')
                return
        # TODO: should be done in the __exit__ of hangar checkout
        co.close()
    else:
        msg = '\n'.join(message)
    click.echo('Commit message:\n' + msg)
    try:
        digest = repository.commit(message)
    except (FileNotFoundError, RuntimeError) as e:
        raise click.ClickException(e)
    click.echo(f'Commit Successful. Digest: {digest}')


@main.command()
@click.option('--name', prompt='User Name', help='first and last name of user')
@click.option('--email', prompt='User Email', help='email address of the user')
@click.option('--overwrite', is_flag=True, default=False,
              help='overwrite a repository if it exists at the current path')
def init(name, email, overwrite):
    try:
        repository.init(name, email, overwrite)
    except RuntimeError as e:
        raise click.ClickException(e)


