import json
from nose.tools import *
from flask import url_for
from realms.lib.util import cname_to_filename, filename_to_cname
from realms.lib.test import BaseTest


class WikiBaseTest(BaseTest):
    def update_page(self, name, message=None, content=None):
        return self.client.post(url_for('wiki.page_write', name=name),
                                data=dict(message=message, content=content))

    def create_page(self, name, message=None, content=None):
        return self.client.post(url_for('wiki.page_write', name=name),
                                data=dict(message=message, content=content))


class UtilTest(WikiBaseTest):
    def test_cname_to_filename(self):
        eq_(cname_to_filename('test'), 'test.md')

    def test_filename_to_cname(self):
        eq_(filename_to_cname('test-1-2-3.md'), 'test-1-2-3')


class WikiTest(WikiBaseTest):
    def test_routes(self):
        self.assert_200(self.client.get(url_for("wiki.create")))
        self.create_page('test', message='test message', content='testing')

        for route in ['page', 'edit', 'history']:
            rv = self.client.get(url_for("wiki.%s" % route, name='test'))
            self.assert_200(rv, "wiki.%s: %s" % (route, rv.status_code))

        self.assert_200(self.client.get(url_for('wiki.index')))

    def test_write_page(self):
        self.assert_200(self.create_page('test', message='test message', content='testing'))

        rv = self.client.get(url_for('wiki.page', name='test'))
        self.assert_200(rv)

        self.assert_context('name', 'test')
        eq_(self.get_context_variable('page')['info']['message'], 'test message')
        eq_(self.get_context_variable('page')['data'], 'testing')

    def test_history(self):
        self.assert_200(self.client.get(url_for('wiki.history', name='test')))

    def test_delete_page(self):
        self.app.config['WIKI_LOCKED_PAGES'] = ['test']
        self.assert_403(self.client.delete(url_for('wiki.page_write', name='test')))
        self.app.config['WIKI_LOCKED_PAGES'] = []

        # Create page, check it exists
        self.create_page('test', message='test message', content='testing')
        self.assert_200(self.client.get(url_for('wiki.page', name='test')))

        # Delete page
        self.assert_200(self.client.delete(url_for('wiki.page_write', name='test')))

        rv = self.client.get(url_for('wiki.page', name='test'))
        self.assert_status(rv, 302)

    def test_revert(self):
        rv1 = self.create_page('test', message='test message', content='testing_old')
        self.update_page('test', message='test message', content='testing_new')
        data = json.loads(rv1.data)
        self.client.post(url_for('wiki.revert'), data=dict(name='test', commit=data['sha']))
        self.client.get(url_for('wiki.page', name='test'))
        eq_(self.get_context_variable('page')['data'], 'testing_old')
        self.assert_404(self.client.post(url_for('wiki.revert'), data=dict(name='test', commit='does not exist')))

        self.app.config['WIKI_LOCKED_PAGES'] = ['test']
        self.assert_403(self.client.post(url_for('wiki.revert'), data=dict(name='test', commit=data['sha'])))
        self.app.config['WIKI_LOCKED_PAGES'] = []

    def test_anon(self):
        rv1 = self.create_page('test', message='test message', content='testing_old')
        self.update_page('test', message='test message', content='testing_new')
        data = json.loads(rv1.data)
        self.app.config['ALLOW_ANON'] = False
        self.assert_403(self.update_page('test', message='test message', content='testing_again'))
        self.assert_403(self.client.post(url_for('wiki.revert'), data=dict(name='test', commit=data['sha'])))


class RelativePathTest(WikiTest):
    def configure(self):
        return dict(RELATIVE_PATH='wiki')
