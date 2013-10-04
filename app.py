from gevent import monkey, pywsgi
monkey.patch_all()
import logging
from realms import app, config

if __name__ == '__main__':
    app.logger.setLevel(logging.INFO)
    pywsgi.WSGIServer(('', config.port), app).serve_forever()
