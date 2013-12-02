from gevent import monkey, pywsgi
monkey.patch_all()
import logging
from realms import app, config


if __name__ == '__main__':
    print "Starting server"
    app.logger.setLevel(logging.INFO)
    pywsgi.WSGIServer(('', config.PORT), app).serve_forever()
