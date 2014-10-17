from realms import config, app, cli, db
from realms.lib.util import random_string
from subprocess import call, Popen
from multiprocessing import cpu_count
import click
import json
import sys
import os


def check_su(f):
    if not in_virtualenv() and not is_su():
        # This does not account for people the have user level python installs
        # that aren't virtual environments!  Should be rare I think
        red("This command requires root privileges, use sudo or run as root.")
        sys.exit()
    return f


def get_user():
    for name in ('SUDO_USER', 'LOGNAME', 'USER', 'LNAME', 'USERNAME'):
        user = os.environ.get(name)
        if user:
            return user


def in_virtualenv():
    return hasattr(sys, 'real_prefix')


def is_su():
    return os.geteuid() == 0


def get_pid():
    try:
        with file(config.PIDFILE) as f:
            pid = f.read().strip()
            return pid if pid and int(pid) > 0 and not call(['kill', '-s', '0', pid]) else False
    except IOError:
        return False


def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True


def green(s):
    click.secho(s, fg='green')


def yellow(s):
    click.secho(s, fg='yellow')


def red(s):
    click.secho(s, fg='red')


@cli.command()
@check_su
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
@click.option('--db-uri',
              default=config.DB_URI,
              prompt='Database URI? Examples: http://goo.gl/RyW0cl')
@click.pass_context
def setup(ctx, **kw):
    """ Start setup wizard
    """

    conf = {}

    for k, v in kw.items():
        conf[k.upper()] = v

    conf_path = config.update(conf)

    if conf['CACHE_TYPE'] == 'redis':
        ctx.invoke(setup_redis)
    elif conf['CACHE_TYPE'] == 'memcached':
        ctx.invoke(setup_memcached)

    green('Config saved to %s' % conf_path)
    yellow('Type "realms-wiki start" to start server')
    yellow('Type "realms-wiki dev" to start server in development mode')


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


def get_prefix():
    return sys.prefix


def get_pip():
    """ Get virtualenv path for pip
    """
    if in_virtualenv():
        return get_prefix() + '/bin/pip'
    else:
        return 'pip'


@cli.command()
@check_su
@click.argument('cmd', nargs=-1)
def pip(cmd):
    """ Execute pip commands, useful for virtualenvs
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
@check_su
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

    with open('/etc/init/realms-wiki.conf', 'w') as f:
        f.write(upstart_script(**kwargs))

    green('Wrote file to %s' % conf_file)
    green("Type 'sudo start realms-wiki' to start")
    green("Type 'sudo stop realms-wiki' to stop")
    green("Type 'sudo restart realms-wiki' to restart")


@cli.command()
@click.argument('json_string')
def configure(json_string):
    """ Set config.json, expects JSON encoded string
    """
    try:
        config.update(json.loads(json_string))
    except ValueError, e:
        red('Config value should be valid JSON')


@cli.command()
@click.option('--port', default=5000)
def dev(port):
    """ Run development server
    """
    green("Starting development server")
    app.run(host="0.0.0.0",
            port=port,
            debug=True)


def start_server():
    if get_pid():
        yellow("Server is already running")
        return

    flags = '--daemon --pid %s' % config.PIDFILE

    green("Server started. Port: %s" % config.PORT)

    Popen('gunicorn realms:app -b 0.0.0.0:%s -k gevent %s' %
         (config.PORT, flags), shell=True, executable='/bin/bash')


def stop_server():
    pid = get_pid()
    if not pid:
        yellow("Server is not running")
    else:
        yellow("Shutting down server")
        call(['kill', pid])


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
    if not pid:
        yellow("Server is not running")
    else:
        green("Server is running PID: %s" % pid)


@cli.command()
def create_db():
    """ Creates DB tables
    """
    green("Creating all tables")
    db.create_all()


@cli.command()
@click.confirmation_option(help='Are you sure you want to drop the db?')
def drop_db():
    """ Drops DB tables
    """
    yellow("Dropping all tables")
    db.drop_all()


@cli.command()
def test():
    """ Run tests
    """
    for mod in [('flask.ext.testing', 'Flask-Testing'), ('nose', 'nose')]:
        if not module_exists(mod[0]):
            call([get_pip(), 'install', mod[1]])

    nosetests = get_prefix() + "/bin/nosetests" if in_virtualenv() else "nosetests"

    call([nosetests, config.APP_PATH])


@cli.command()
def version():
    """ Output version
    """
    with open('VERSION') as f:
        return f.read().strip()


if __name__ == '__main__':
    cli()