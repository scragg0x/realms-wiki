import click
import re
import os
import hashlib
import json
import string
import random
import sys
from jinja2 import Template


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def random_string(size=6, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def to_json(data):
    return json.dumps(to_dict(data), separators=(',', ':'))


def to_dict(data):

    if not data:
        return AttrDict()

    def row2dict(row):
        d = AttrDict()
        for column in row.__table__.columns:
            d[column.name] = getattr(row, column.name)

        return d

    if isinstance(data, list):
        return [row2dict(x) for x in data]
    else:
        return row2dict(data)


def mkdir_safe(path):
    if path and not(os.path.exists(path)):
        os.makedirs(path)
    return path


def extract_path(file_path):
    if not file_path:
        return None
    last_slash = file_path.rindex("/")
    if last_slash:
        return file_path[0, last_slash]


def clean_path(path):
    if path:
        if path[0] != '/':
            path.insert(0, '/')
        return re.sub(r"//+", '/', path)


def extract_name(file_path):
    if file_path[-1] == "/":
        return None
    return os.path.basename(file_path)


def remove_ext(path):
    return re.sub(r"\..*$", "", path)


def clean_url(url):
    if not url:
        return url

    url = url.replace('%2F', '/')
    url = re.sub(r"^/+", "", url)
    return re.sub(r"//+", '/', url)


def to_canonical(s):
    """
    Remove leading/trailing whitespace (from all path components)
    Remove leading underscores and slashes "/"
    Convert spaces to dashes "-"
    Limit path components to 63 chars and total size to 436 chars
    """
    reserved_chars = "&$+,:;=?@#"
    unsafe_chars = "?<>[]{}|\^~%"

    s = s.encode("utf8")
    s = re.sub(r"\s+", " ", s)
    s = s.lstrip("_/ ")
    s = re.sub(r"[" + re.escape(reserved_chars) + "]", "", s)
    s = re.sub(r"[" + re.escape(unsafe_chars) + "]", "", s)
    # Strip leading/trailing spaces from path components, replace internal spaces
    # with '-', and truncate to 63 characters.
    parts = (part.strip().replace(" ", "-")[:63] for part in s.split("/"))
    # Join any non-empty path components back together
    s = "/".join(filter(None, parts))
    s = s[:436]
    return s


def cname_to_filename(cname):
    """ Convert canonical name to filename

    :param cname: Canonical name
    :return: str -- Filename

    """
    return cname + ".md"


def filename_to_cname(filename):
    """Convert filename to canonical name.

    .. note::

    It's assumed filename is already canonical format

    """
    return os.path.splitext(filename)[0]


def gravatar_url(email):
    email = hashlib.md5(email).hexdigest() if email else "default@realms.io"
    return "https://www.gravatar.com/avatar/" + email


def in_virtualenv():
    return hasattr(sys, 'real_prefix')


def in_vagrant():
    return os.path.isdir("/vagrant")


def is_su():
    return os.geteuid() == 0


def green(s):
    click.secho(s, fg='green')


def yellow(s):
    click.secho(s, fg='yellow')


def red(s):
    click.secho(s, fg='red')


def upstart_script(user='root', app_dir=None, port=5000, workers=2, path=None):
    script = """
limit nofile 65335 65335

respawn

description "Realms Wiki"
author "scragg@gmail.com"

chdir {{ app_dir }}

{% if path %}
env PATH={{ path }}:/usr/local/bin:/usr/bin:/bin:$PATH
export PATH
{% endif %}

env LC_ALL=en_US.UTF-8
env GEVENT_RESOLVER=ares

export LC_ALL
export GEVENT_RESOLVER

setuid {{ user }}
setgid {{ user }}

start on runlevel [2345]
stop on runlevel [!2345]

respawn

exec gunicorn \
  --name realms-wiki \
  --access-logfile - \
  --error-logfile - \
  --worker-class gevent \
  --workers {{ workers }} \
  --bind 0.0.0.0:{{ port }} \
  --user {{ user }} \
  --group {{ user }} \
  --chdir {{ app_dir }} \
  'realms:create_app()'

"""
    template = Template(script)
    return template.render(user=user, app_dir=app_dir, port=port, workers=workers, path=path)
