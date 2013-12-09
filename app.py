from gevent import monkey, wsgi
from realms import config, app, manager

monkey.patch_all()


@manager.command
def server(port=10000):
    print "Server started (%s)" % config.ENV
    wsgi.WSGIServer(('', int(port)), app).serve_forever()

if __name__ == '__main__':
    manager.run()
