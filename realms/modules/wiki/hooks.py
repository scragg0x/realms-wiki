from flask import g, current_app
from .models import Wiki


def before_request():
    g.current_wiki = Wiki(current_app.config['WIKI_PATH'])
