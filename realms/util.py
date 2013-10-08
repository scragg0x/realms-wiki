import re
import os
import hashlib


def escape_repl(m):
    print "group 0"
    print m.group(0)
    print "group 1"
    print m.group(1)
    if m.group(1):
        return "```" + escape_html(m.group(1)) + "```"


def unescape_repl(m):
    if m.group(1):
        return "```" + unescape_html(m.group(1)) + "```"


def escape_html(s):
    s = s.replace("&", '&amp;')
    s = s.replace("<", '&lt;')
    s = s.replace(">", '&gt;')
    s = s.replace('"', '&quot;')
    s = s.replace("'", '&#39;')
    return s


def unescape_html(s):
    s = s.replace('&amp;', "&")
    s = s.replace('&lt;', "<")
    s = s.replace('&gt;', ">")
    s = s.replace('&quot;', '"')
    s = s.replace('&#39;', "'")
    return s

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
    return s


def gravatar_url(email):
    return "https://www.gravatar.com/avatar/" + hashlib.md5(email).hexdigest()