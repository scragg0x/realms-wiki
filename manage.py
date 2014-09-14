from gevent import wsgi
from realms import config, app, cli, db
from werkzeug.serving import run_with_reloader
import click
import os


@cli.command()
@click.option('--port', default=5000)
def runserver(port):
    """ Run development server
    """
    click.secho("Starting development server", fg='green')
    app.run(host="0.0.0.0",
            port=port,
            debug=True)


@cli.command()
def run():
    """ Run production server
    """
    click.echo("Server started. Env: %s Port: %s" % (config.ENV, config.PORT))
    wsgi.WSGIServer(('', int(config.PORT)), app).serve_forever()


@cli.command()
def create_db():
    """ Creates DB tables
    """
    click.echo("Creating all tables")
    db.create_all()


@cli.command()
def drop_db():
    """ Drops DB tables
    """
    click.echo("Dropping all tables")
    db.drop_all()

if __name__ == '__main__':
    cli()
