from gevent import wsgi
from realms import config, app, cli, db
from realms.lib.util import random_string
from subprocess import call
import click
import json


@cli.command()
@click.option('--site-title',
              default=config.SITE_TITLE,
              prompt='Enter site title.')
@click.option('--base_url',
              default=config.BASE_URL,
              prompt='Enter base URL.')
@click.option('--port',
              default=config.PORT,
              prompt='Enter port number.')
@click.option('--secret-key',
              default=config.SECRET_KEY if config.SECRET_KEY != "CHANGE_ME" else random_string(64),
              prompt='Enter secret key.')
@click.option('--wiki-path',
              default=config.WIKI_PATH,
              prompt='Where do you want to store wiki data?',
              help='Wiki Directory (git repo)')
@click.option('--allow-anon',
              default=config.ALLOW_ANON,
              is_flag=True,
              prompt='Allow anonymous edits?')
@click.option('--registration-enabled',
              default=config.REGISTRATION_ENABLED,
              is_flag=True,
              prompt='Enable registration?')
@click.option('--cache-type',
              default=config.CACHE_TYPE,
              type=click.Choice([None, 'simple', 'redis', 'memcached']),
              prompt='Cache type?')
@click.option('--db-uri',
              default=config.DB_URI,
              prompt='Database URI, Examples: http://goo.gl/RyW0cl')
@click.pass_context
def setup(ctx, **kw):
    """ Start setup wizard
    """
    conf = {}

    for k, v in kw.items():
        conf[k.upper()] = v

    config.update(conf)

    if conf['CACHE_TYPE'] == 'redis':
        ctx.invoke(setup_redis)
    elif conf['CACHE_TYPE'] == 'memcached':
        ctx.invoke(setup_memcached)

    click.secho('Config saved to %s/config.json' % config.APP_PATH, fg='green')
    click.secho('Type "realms-wiki run" to start server', fg='yellow')


@click.command()
@click.option('--cache-redis-host',
              default=getattr(config, 'CACHE_REDIS_HOST', "127.0.0.1"),
              prompt='Redis host')
@click.option('--cache-redis-port',
              default=getattr(config, 'CACHE_REDIS_POST', 6379),
              prompt='Redis port')
@click.option('--cache-redis-password',
              default=getattr(config, 'CACHE_REDIS_PASSWORD', None),
              prompt='Redis password')
@click.option('--cache-redis-db',
              default=getattr(config, 'CACHE_REDIS_DB', 0),
              prompt='Redis db')
def setup_redis(**kw):
    conf = {}

    for k, v in kw.items():
        conf[k.upper()] = v

    config.update(conf)
    install_redis()


def get_pip():
    """ Get virtualenv path for pip
    """
    import sys
    return sys.prefix + '/bin/pip'


@cli.command()
@click.argument('cmd', nargs=-1)
def pip(cmd):
    """ Execute pip commands for this virtualenv
    """
    call(get_pip() + ' ' + ' '.join(cmd), shell=True)


def install_redis():
    call([get_pip(), 'install', 'redis'])


def install_mysql():
    call([get_pip(), 'install', 'MySQL-Python'])


def install_postgres():
    call([get_pip(), 'install', 'psycopg2'])


def install_memcached():
    call([get_pip(), 'install', 'python-memcached'])


@click.command()
@click.option('--cache-memcached-servers',
              default=getattr(config, 'CACHE_MEMCACHED_SERVERS', ["127.0.0.1:11211"]),
              type=click.STRING,
              prompt='Memcached servers, separate with a space')
def setup_memcached(**kw):
    conf = {}

    for k, v in kw.items():
        conf[k.upper()] = v

    config.update(conf)


@cli.command()
@click.argument('config_json')
def configure(config_json):
    """ Set config.json, expects JSON encoded string
    """
    try:
        config.update(json.loads(config_json))
    except ValueError, e:
        click.secho('Config value should be valid JSON', fg='red')


@cli.command()
@click.option('--port', default=5000)
def dev(port):
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
    click.secho("Server started. Env: %s Port: %s" % (config.ENV, config.PORT), fg='green')
    wsgi.WSGIServer(('', int(config.PORT)), app).serve_forever()


@cli.command()
def create_db():
    """ Creates DB tables
    """
    click.echo("Creating all tables")
    db.create_all()


@cli.command()
@click.confirmation_option(help='Are you sure you want to drop the db?')
def drop_db():
    """ Drops DB tables
    """
    click.echo("Dropping all tables")
    db.drop_all()


@cli.command()
def version():
    """ Output version
    """
    with open('VERSION') as f:
        return f.read().strip()

if __name__ == '__main__':
    cli()