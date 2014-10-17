import re
import os
import hashlib
import json
import string
import random
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
    return os.path.splitext(path)[0]


def clean_url(url):
    if not url:
        return url

    url = url.replace('%2F', '/')
    url = re.sub(r"^/+", "", url)
    return re.sub(r"//+", '/', url)


def to_canonical(s):
    """
    Double space -> single dash
    Double dash -> single dash
    Remove all non alphanumeric and dash
    Limit to first 64 chars
    """
    s = s.encode('ascii', 'ignore')
    s = str(s)
    s = re.sub(r"\s\s*", "-", s)
    s = re.sub(r"\-\-+", "-", s)
    s = re.sub(r"[^a-zA-Z0-9\-]", "", s)
    s = s[:64]
    s = s.lower()
    return s


def gravatar_url(email):
    return "//www.gravatar.com/avatar/" + hashlib.md5(email).hexdigest()

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
  realms:app

"""
    template = Template(script)
    return template.render(user=user, app_dir=app_dir, port=port, workers=workers, path=path)
