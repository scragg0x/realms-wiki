from gevent import wsgi
from realms import config, app, manager


@manager.command
def server(port=10000):
    print "Server started (%s)" % config.ENV
    wsgi.WSGIServer(('', int(port)), app).serve_forever()


@manager.command
def init_db():
    from realms import db
    import realms.models
    print "Init DB"
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    manager.run()
