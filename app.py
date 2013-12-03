from gevent import monkey, pywsgi
from realms import config, app

monkey.patch_all()
import logging


if __name__ == '__main__':
    print "Starting server"
    app.logger.setLevel(logging.INFO)
    pywsgi.WSGIServer(('', config.PORT), app).serve_forever()
