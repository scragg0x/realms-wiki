from gevent import monkey, pywsgi
monkey.patch_all()
from realms import config, init_db, make_app, SubdomainDispatcher


if __name__ == '__main__':
    init_db(config.db['dbname'])
    app = SubdomainDispatcher(config.domain, make_app)
    pywsgi.WSGIServer(('', config.port), app).serve_forever()
