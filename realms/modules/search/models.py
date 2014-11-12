from flask import g, current_app
from realms.lib.util import filename_to_cname


def simple(app):
    return SimpleSearch()


def elasticsearch(app):
    from flask.ext.elastic import Elastic
    return ElasticSearch(Elastic(app))


class Search(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        search_obj = globals()[app.config['SEARCH_TYPE']]
        app.extensions['search'] = search_obj(app)

    def __getattr__(self, item):
        return getattr(current_app.extensions['search'], item)


class BaseSearch():
    pass


class SimpleSearch(BaseSearch):
    def wiki(self, query):
        res = []
        for entry in g.current_wiki.get_index():
            name = filename_to_cname(entry['name'])
            if query in name.split('-'):
                page = g.current_wiki.get_page(name)
                res.append(dict(name=name, content=page['data']))
        return res

    def users(self, query):
        pass


class ElasticSearch(BaseSearch):
    def __init__(self, elastic):
        self.elastic = elastic

    def index(self, index, doc_type, id_=None, body=None):
        return self.elastic.index(index=index, doc_type=doc_type, id=id_, body=body)

    def index_wiki(self, name, body):
        self.index('wiki', 'page', id_=name, body=body)

    def delete_index(self, index):
        return self.elastic.indices.delete(index=index, ignore=[400, 404])

    def wiki(self, query):
        if not query:
            return []

        res = self.elastic.search(index='wiki', body={"query": {
            "multi_match": {
                "query": query,
                "fields": ["name"]
            }}})

        return [hit["_source"] for hit in res['hits']['hits']]

    def users(self, query):
        pass
