import re
import os


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
        return re.sub(r"//+", '/')


def extract_name(file_path):
    if file_path[-1] == "/":
        return None
    return os.path.basename(file_path)


def clean_url(url):
    if not url:
        return url

    url = url.replace('%2F', '/')
    url = re.sub(r"^/+", "", url)
    return re.sub(r"//+", '/', url)
