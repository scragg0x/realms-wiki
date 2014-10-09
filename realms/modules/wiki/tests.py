from nose.tools import *
from flask import url_for
from realms import app, g
from realms.modules.wiki.models import Wiki, cname_to_filename, filename_to_cname
from flask.ext.testing import TestCase


class WikiTest(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_wiki_routes(self):

        self.assert_200(self.client.get(url_for("wiki.create")))

        for route in ['page', 'edit', 'history', 'index']:
            rv = self.client.get(url_for("wiki.%s" % route, name='test'))
            self.assert_200(rv, "wiki.%s: %s" % (route, rv.status_code))

    def test_write_page(self):
        pass

    def test_revert(self):
        pass

    def test_cname_to_filename(self):
        eq_(cname_to_filename('test'), 'test.md')

    def test_filename_to_cname(self):
        eq_(filename_to_cname('test-1-2-3.md'), 'test-1-2-3')