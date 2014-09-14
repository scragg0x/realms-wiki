import click
from realms.lib.util import random_string
from realms.modules.auth.models import User


@click.group()
def cli():
    pass


@cli.command()
@click.argument('username')
@click.argument('email')
@click.option('--password', help='Leave blank for random password')
def create_user(username, email, password):
    """ Create a new user
    """
    show_pass = not password

    if not password:
        password = random_string(12)

    if User.get_by_username(username):
        click.secho("Username %s already exists" % username, fg='red')
        return

    if User.get_by_email(email):
        click.secho("Email %s already exists" % email, fg='red')
        return

    User.create(username, email, password)
    click.secho("User %s created" % username, fg='green')

    if show_pass:
        click.secho("Password: %s" % password, fg='yellow')
