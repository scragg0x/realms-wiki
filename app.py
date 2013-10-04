from gevent import monkey, pywsgi
monkey.patch_all()
from realms import create_app, config
from threading import Lock

class SubdomainDispatcher(object):

    def __init__(self, domain, create_app):
        self.domain = domain
        self.create_app = create_app
        self.lock = Lock()
        self.instances = {}

    def get_application(self, host):
        host = host.split(':')[0]
        assert host.endswith(self.domain), 'Configuration error'
        subdomain = host[:-len(self.domain)].rstrip('.')
        with self.lock:
            app = self.instances.get(subdomain)
            if app is None:
                app = self.create_app(subdomain)
                self.instances[subdomain] = app
            return app

    def __call__(self, environ, start_response):
        app = self.get_application(environ['HTTP_HOST'])
        return app(environ, start_response)


def make_app(subdomain):
    return create_app(subdomain)

if __name__ == '__main__':
    app = SubdomainDispatcher(config.domain, make_app)
    pywsgi.WSGIServer(('', config.port), app).serve_forever()
