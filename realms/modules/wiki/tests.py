from nose.tools import *
from flask import url_for
from realms.modules.wiki.models import Wiki, cname_to_filename, filename_to_cname
from realms.lib.test import BaseTest


class WikiTest(BaseTest):

    def test_wiki_routes(self):

        self.assert_200(self.client.get(url_for("wiki.create")))

        """ Create a test page first!
        for route in ['page', 'edit', 'history', 'index']:
            rv = self.client.get(url_for("wiki.%s" % route, name='test'))
            self.assert_200(rv, "wiki.%s: %s" % (route, rv.status_code))
        """

    def test_write_page(self):
        self.assert_200(
            self.client.post(url_for('wiki.page_write', name='test'), data=dict(
                content='testing',
                message='test message'
            )))

        self.assert_200(self.client.get(url_for('wiki.page', name='test')))

    def test_delete_page(self):
        self.assert_200(self.client.delete(url_for('wiki.page_write', name='test')))
        self.assert_status(self.client.get(url_for('wiki.page', name='test')), 302)

    def test_revert(self):
        pass

    def test_cname_to_filename(self):
        eq_(cname_to_filename('test'), 'test.md')

    def test_filename_to_cname(self):
        eq_(filename_to_cname('test-1-2-3.md'), 'test-1-2-3')