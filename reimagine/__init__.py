import config
import redis
import logging
import rethinkdb as rdb
from flask import Flask, request, render_template, url_for, redirect
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager
from flask.ext.assets import Environment
from session import RedisSessionInterface
from gittle import Gittle
from os import sep, path
from wiki import Wiki

app = Flask(__name__)
app.config.update(config.flask)
app.debug = (config.ENV is not 'PROD')
app.secret_key = config.secret_key
app.static_path = sep + 'static'
app.session_interface = RedisSessionInterface()

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)

assets = Environment(app)
assets.url = app.static_url_path
assets.directory = app.static_folder

cache = redis.StrictRedis(host=config.cache['host'], port=config.cache['port'])

conn = rdb.connect(config.db['host'], config.db['port'])

from models import Site

site = Site.get_by_name(".")

w = Wiki(site.get('repo'))


def redirect_url():
    return request.args.get('next') or request.referrer or url_for('index')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def page_error(e):
    logging.exception(e)
    return render_template('errors/500.html'), 500


@app.route("/")
def root():
    return redirect('/Home')


@app.route("/rename/<page>", methods=['POST'])
def rename(page):
    pass


@app.route("/edit/<page>", methods=['GET', 'POST'])
def edit(page):
    data = w.get_page(page)
    if data:
        return render_template('page/edit.html', page=data)
    else:
        return redirect('/create/'+page)

@app.route("/delete/<page>", methods=['POST'])
def delete(page):
    pass


@app.route("/create/<page>")
def create(page):
    return render_template('page/create.html')


@app.route("/<page>")
def render(page):
    data = w.get_page(page)
    if data:
        return render_template('page/page.html', page=data)
    else:
        return redirect('/create/'+page)

import ratelimit
