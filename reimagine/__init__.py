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
from wiki import Wiki
from util import to_canonical, remove_ext

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

repo_dir = config.repo['dir']

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


@app.route("/edit/<name>", methods=['GET', 'POST'])
def edit(name):
    data = w.get_page(name)
    cname = to_canonical(name)
    if request.method == 'POST':
        edit_cname = to_canonical(request.form['name'])
        if edit_cname != cname:
            w.rename_page(cname, edit_cname)
        w.write_page(edit_cname, request.form['content'])
        return redirect("/" + edit_cname)
    else:
        if data:
            name = remove_ext(data['name'])
            content = data['data']
            return render_template('page/edit.html', name=name, content=content)
        else:
            return redirect('/create/'+cname)


@app.route("/delete/<name>", methods=['POST'])
def delete(name):
    pass


@app.route("/create/<name>", methods=['GET', 'POST'])
def create(name):
    cname = to_canonical(name)
    if w.get_page(cname):
        # Page exists, edit instead
        return redirect("/edit/" + cname)

    if request.method == 'POST':
        w.write_page(request.form['name'], request.form['content'], create=True)
        return redirect("/" + cname)
    else:
        return render_template('page/create.html', name=cname)


@app.route("/<name>")
def render(name):
    cname = to_canonical(name)
    if cname != name:
        return redirect('/' + cname)

    data = w.get_page(cname)
    if data:
        return render_template('page/page.html', page=data)
    else:
        return redirect('/create/'+cname)

import ratelimit
