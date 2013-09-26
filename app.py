from gevent import monkey, pywsgi
monkey.patch_all()
import logging
from reimagine import app

if __name__ == '__main__':
    app.logger.setLevel(logging.INFO)
    pywsgi.WSGIServer(('', 9999), app).serve_forever()
