from __future__ import absolute_import

import os
import shutil
import tempfile

from flask_testing import TestCase

from realms import create_app
from realms.lib.util import random_string
from realms.lib.flask_csrf_test_client import FlaskClient


class BaseTest(TestCase):

    def create_app(self):
        self.tempdir = tempfile.mkdtemp()
        app = create_app()
        app.config['TESTING'] = True
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        app.config['WIKI_PATH'] = os.path.join(self.tempdir, random_string(12))
        app.config['DB_URI'] = 'sqlite:///%s/%s.db' % (self.tempdir, random_string(12))
        app.test_client_class = FlaskClient
        app.testing = True
        app.config.update(self.configure())
        return app

    def configure(self):
        return {}

    def tearDown(self):
        shutil.rmtree(self.tempdir)
