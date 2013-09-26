import config
import redis
import logging
from flask import Flask, request, render_template, url_for
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager
from flask.ext.assets import Environment
from session import RedisSessionInterface
from gittle import Gittle
from os import sep

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
    repo = Gittle('/tmp/testgit')
    if repo.has_commits():
        pass
    print repo.diff

    return render_template('page/create.html')

import ratelimit
