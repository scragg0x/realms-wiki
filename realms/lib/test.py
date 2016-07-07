import os
import shutil
import tempfile
from flask.ext.testing import TestCase
from realms.lib.util import random_string
from realms import create_app


class BaseTest(TestCase):

    def create_app(self):
        self.tempdir = tempfile.mkdtemp()
        app = create_app()
        app.config['TESTING'] = True
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        app.config['WIKI_PATH'] = os.path.join(self.tempdir, random_string(12))
        app.config['DB_URI'] = 'sqlite:///%s/%s.db' % (self.tempdir, random_string(12))
        app.config.update(self.configure())
        return app

    def configure(self):
        return {}

    def tearDown(self):
        shutil.rmtree(self.tempdir)
