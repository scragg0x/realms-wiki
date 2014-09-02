from gevent import wsgi
from realms import config, app, manager
from flask.ext.script import Server

manager.add_command("runserver", Server(host="0.0.0.0", port=5000))


@manager.command
def run():
    """
    Run production ready server
    """
    print "Server started. Env: %s Port: %s" % (config.ENV, config.PORT)
    wsgi.WSGIServer(('', int(config.PORT)), app).serve_forever()


if __name__ == '__main__':
    manager.run()
