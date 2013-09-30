import config
import redis
import logging
import rethinkdb as rdb
import os
from flask import Flask, request, render_template, url_for, redirect
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager
from flask.ext.assets import Environment
from session import RedisSessionInterface
from gittle import Gittle
from wiki import Wiki
from util import mkdir_safe

app = Flask(__name__)
app.config.update(config.flask)
app.debug = (config.ENV is not 'PROD')
app.secret_key = config.secret_key
app.static_path = os.sep + 'static'
app.session_interface = RedisSessionInterface()

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)

assets = Environment(app)
assets.url = app.static_url_path
assets.directory = app.static_folder

cache = redis.StrictRedis(host=config.cache['host'], port=config.cache['port'])

conn = rdb.connect(config.db['host'], config.db['port'], db=config.db['dbname'])

if not config.db['dbname'] in rdb.db_list().run(conn) and config.ENV is not 'PROD':
    # Create default db and repo
    print "Creating DB %s" % config.db['dbname']
    rdb.db_create(config.db['dbname']).run(conn)
    for tbl in ['sites', 'users', 'pages']:
        rdb.table_create(tbl).run(conn)

repo_dir = config.repos['dir'] + "/" + config.repos['main']

repo = Gittle(repo_dir)
mkdir_safe(repo_dir)

if not repo.has_index():
    repo.init(repo_dir)

from models import Site

w = Wiki(repo_dir)


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
