from gevent import wsgi
from realms import config, app, manager


@manager.command
def server():
    print "Server started. Env: %s Port: %s" % (config.ENV, config.PORT)
    wsgi.WSGIServer(('', int(config.PORT)), app).serve_forever()


if __name__ == '__main__':
    manager.run()
