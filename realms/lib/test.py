from flask.ext.testing import TestCase
from realms.lib.util import random_string
from realms import create_app
from subprocess import call


class BaseTest(TestCase):

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        app.config['WIKI_PATH'] = '/tmp/%s' % random_string(12)
        app.config['DB_URI'] = 'sqlite:////tmp/%s.db' % random_string(12)
        app.config.update(self.configure())
        return app

    def configure(self):
        return {}

    def tearDown(self):
        call(['rm', '-rf', self.app.config['WIKI_PATH']])
        call(['rm', '-f', self.app.config['DB_URI'][10:]])
