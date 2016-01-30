from realms import config, create_app, db, __version__, flask_cli as cli, cache
from realms.lib.util import random_string, in_virtualenv, green, yellow, red
from subprocess import call, Popen
from multiprocessing import cpu_count
import click
import json
import sys
import os
import pip
import time
import subprocess

# called to discover commands in modules
app = create_app()

def get_user():
    for name in ('SUDO_USER', 'LOGNAME', 'USER', 'LNAME', 'USERNAME'):
        user = os.environ.get(name)
        if user:
            return user


def get_pid():
    try:
        with file(config.PIDFILE) as f:
            return f.read().strip()
    except IOError:
        return None


def is_running(pid):
    if not pid:
        return False

    pid = int(pid)

    try:
        os.kill(pid, 0)
    except OSError:
        return False

    return True


def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True


def prompt_and_invoke(ctx, fn):
    # This is a workaround for a bug in click.
    # See https://github.com/mitsuhiko/click/issues/429
    # This isn't perfect - we are ignoring some information (type mostly)

    kw = {}

    for p in fn.params:
        v = click.prompt(p.prompt, p.default, p.hide_input,
                         p.confirmation_prompt, p.type)
        kw[p.name] = v

    ctx.invoke(fn, **kw)

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
              prompt='Enter wiki data directory.',
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
@click.option('--search-type',
              default=config.SEARCH_TYPE,
              type=click.Choice(['simple', 'whoosh', 'elasticsearch']),
              prompt='Search type?')
@click.option('--db-uri',
              default=config.DB_URI,
              prompt='Database URI? Examples: http://goo.gl/RyW0cl')
@click.pass_context
def setup(ctx, **kw):
    """ Start setup wizard
    """

    try:
        os.mkdir('/etc/realms-wiki')
    except OSError:
        pass

    conf = {}

    for k, v in kw.items():
        conf[k.upper()] = v

    conf_path = config.update(conf)

    if conf['CACHE_TYPE'] == 'redis':
        prompt_and_invoke(ctx, setup_redis)
    elif conf['CACHE_TYPE'] == 'memcached':
        prompt_and_invoke(ctx, setup_memcached)

    if conf['SEARCH_TYPE'] == 'elasticsearch':
        prompt_and_invoke(ctx, setup_elasticsearch)
    elif conf['SEARCH_TYPE'] == 'whoosh':
        install_whoosh()

    green('Config saved to %s' % conf_path)

    if not conf_path.startswith('/etc/realms-wiki'):
        yellow('Note: You can move file to /etc/realms-wiki/realms-wiki.json')
        click.echo()

    yellow('Type "realms-wiki start" to start server')
    yellow('Type "realms-wiki dev" to start server in development mode')
    yellow('Full usage: realms-wiki --help')


@click.command()
@click.option('--cache-redis-host',
              default=getattr(config, 'CACHE_REDIS_HOST', "127.0.0.1"),
              prompt='Redis host')
@click.option('--cache-redis-port',
              default=getattr(config, 'CACHE_REDIS_POST', 6379),
              prompt='Redis port',
              type=int)
@click.option('--cache-redis-password',
              default=getattr(config, 'CACHE_REDIS_PASSWORD', None),
              prompt='Redis password')
@click.option('--cache-redis-db',
              default=getattr(config, 'CACHE_REDIS_DB', 0),
              prompt='Redis db')
@click.pass_context
def setup_redis(ctx, **kw):
    conf = config.read()

    for k, v in kw.items():
        conf[k.upper()] = v

    config.update(conf)
    install_redis()

@click.command()
@click.option('--elasticsearch-url',
              default=getattr(config, 'ELASTICSEARCH_URL', 'http://127.0.0.1:9200'),
              prompt='Elasticsearch URL')
def setup_elasticsearch(**kw):
    conf = config.read()

    for k, v in kw.items():
        conf[k.upper()] = v

    config.update(conf)

cli.add_command(setup_redis)
cli.add_command(setup_elasticsearch)


def get_prefix():
    return sys.prefix


@cli.command(name='pip')
@click.argument('cmd', nargs=-1)
def pip_(cmd):
    """ Execute pip commands, useful for virtualenvs
    """
    pip.main(cmd)


def install_redis():
    pip.main(['install', 'redis'])


def install_whoosh():
    pip.main(['install', 'Whoosh'])


def install_mysql():
    pip.main(['install', 'MySQL-Python'])


def install_postgres():
    pip.main(['install', 'psycopg2'])


def install_crate():
    pip.main(['install', 'crate'])


def install_memcached():
    pip.main(['install', 'python-memcached'])


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
@click.option('--user',
              default=get_user(),
              type=click.STRING,
              prompt='Run as which user? (it must exist)')
@click.option('--port',
              default=config.PORT,
              type=click.INT,
              prompt='What port to listen on?')
@click.option('--workers',
              default=cpu_count() * 2 + 1,
              type=click.INT,
              prompt="Number of workers? (defaults to ncpu*2+1)")
def setup_upstart(**kwargs):
    """ Start upstart conf creation wizard
    """
    from realms.lib.util import upstart_script

    if in_virtualenv():
        app_dir = get_prefix()
        path = '/'.join(sys.executable.split('/')[:-1])
    else:
        # Assumed root install, not sure if this matters?
        app_dir = '/'
        path = None

    kwargs.update(dict(app_dir=app_dir, path=path))

    conf_file = '/etc/init/realms-wiki.conf'
    script = upstart_script(**kwargs)

    try:
        with open(conf_file, 'w') as f:
            f.write(script)
        green('Wrote file to %s' % conf_file)
    except IOError:
        with open('/tmp/realms-wiki.conf', 'w') as f:
            f.write(script)
        yellow("Wrote file to /tmp/realms-wiki.conf, to install type:")
        yellow("sudo mv /tmp/realms-wiki.conf /etc/init/realms-wiki.conf")

    click.echo()
    click.echo("Upstart usage:")
    green("sudo start realms-wiki")
    green("sudo stop realms-wiki")
    green("sudo restart realms-wiki")
    green("sudo status realms-wiki")


@cli.command()
@click.argument('json_string')
def configure(json_string):
    """ Set config, expects JSON encoded string
    """
    try:
        config.update(json.loads(json_string))
    except ValueError, e:
        red('Config value should be valid JSON')


@cli.command()
@click.option('--port', default=config.PORT)
@click.option('--host', default=config.HOST)
def dev(port, host):
    """ Run development server
    """
    green("Starting development server")

    config_path = config.get_path()
    if config_path:
        green("Using config: %s" % config_path)
    else:
        yellow("Using default configuration")

    create_app().run(host=host,
                     port=port,
                     debug=True)


def start_server():
    if is_running(get_pid()):
        yellow("Server is already running")
        return

    try:
        open(config.PIDFILE, 'w')
    except IOError:
        red("PID file not writeable (%s) " % config.PIDFILE)
        return

    flags = '--daemon --pid %s' % config.PIDFILE

    green("Server started. Port: %s" % config.PORT)

    config_path = config.get_path()
    if config_path:
        green("Using config: %s" % config_path)
    else:
        yellow("Using default configuration")

    prefix = ''
    if in_virtualenv():
        prefix = get_prefix() + "/bin/"

    Popen("%sgunicorn 'realms:create_app()' -b %s:%s -k gevent %s" %
          (prefix, config.HOST, config.PORT, flags), shell=True, executable='/bin/bash')


def stop_server():
    pid = get_pid()
    if not is_running(pid):
        yellow("Server is not running")
    else:
        yellow("Shutting down server")
        call(['kill', pid])
        while is_running(pid):
            time.sleep(1)


@cli.command()
def run():
    """ Run production server (alias for start)
    """
    start_server()


@cli.command()
def start():
    """ Run server daemon
    """
    start_server()


@cli.command()
def stop():
    """ Stop server
    """
    stop_server()


@cli.command()
def restart():
    """ Restart server
    """
    stop_server()
    start_server()


@cli.command()
def status():
    """ Get server status
    """
    pid = get_pid()
    if not is_running(pid):
        yellow("Server is not running")
    else:
        green("Server is running PID: %s" % pid)


@cli.command()
def create_db():
    """ Creates DB tables
    """
    green("Creating all tables")
    with app.app_context():
        green('DB_URI: %s' % app.config.get('DB_URI'))
        db.metadata.create_all(db.get_engine(app))


@cli.command()
@click.confirmation_option(help='Are you sure you want to drop the db?')
def drop_db():
    """ Drops DB tables
    """
    yellow("Dropping all tables")
    with app.app_context():
        db.metadata.drop_all(db.get_engine(app))


@cli.command()
def clear_cache():
    """ Clears cache
    """
    yellow("Clearing the cache")
    with app.app_context():
        cache.clear()


@cli.command()
def test():
    """ Run tests
    """
    for mod in [('flask.ext.testing', 'Flask-Testing'), ('nose', 'nose'), ('blinker', 'blinker')]:
        if not module_exists(mod[0]):
            pip.main(['install', mod[1]])

    nosetests = get_prefix() + "/bin/nosetests" if in_virtualenv() else "nosetests"

    call([nosetests, 'realms'])


@cli.command()
def version():
    """ Output version
    """
    green(__version__)


@cli.command(add_help_option=False)
def deploy():
    """ Deploy to PyPI and docker hub
    """
    call("python setup.py sdist upload", shell=True)
    call("sudo docker build --no-cache -t realms/realms-wiki %s/docker" % app.config['APP_PATH'], shell=True)
    id_ = json.loads(Popen("sudo docker inspect realms/realms-wiki".split(), stdout=subprocess.PIPE).communicate()[0])[0]['Id']
    call("sudo docker tag %s realms/realms-wiki:%s" % (id_, __version__), shell=True)
    call("sudo docker push realms/realms-wiki", shell=True)

if __name__ == '__main__':
    cli()
