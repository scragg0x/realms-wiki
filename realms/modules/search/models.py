from flask import g, current_app
from realms.lib.util import filename_to_cname


def simple(app):
    return SimpleSearch()


def whoosh(app):
    import os
    import sys
    for mode in [os.W_OK, os.R_OK]:
        if not os.access(app.config['WHOOSH_INDEX'], mode):
            sys.exit('Read and write access to WHOOSH_INDEX is required (%s)' %
                     app.config['WHOOSH_INDEX'])

    return WhooshSearch(app.config['WHOOSH_INDEX'], app.config['WHOOSH_LANGUAGE'])


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
            if set(query.split()).intersection(name.split('-')):
                page = g.current_wiki.get_page(name)
                res.append(dict(name=name, content=page['data']))
        return res

    def users(self, query):
        pass


class WhooshSearch(BaseSearch):
    def __init__(self, index_path, language):
        from whoosh import index as whoosh_index
        from whoosh.fields import Schema, TEXT, ID
        from whoosh import qparser
        from whoosh.highlight import UppercaseFormatter
        from whoosh.analysis import SimpleAnalyzer, LanguageAnalyzer
        from whoosh.lang import has_stemmer, has_stopwords
        import os.path

        if not has_stemmer(language) or not has_stopwords(language):
            # TODO Display a warning?
            analyzer = SimpleAnalyzer()
        else:
            analyzer = LanguageAnalyzer(language)

        self.schema = Schema(path=ID(unique=True, stored=True), body=TEXT(analyzer=analyzer))
        self.formatter = UppercaseFormatter()

        self.index_path = index_path
        if os.path.exists(index_path):
            self.search_index = whoosh_index.open_dir(index_path)
        else:
            os.mkdir(index_path)
            self.search_index = whoosh_index.create_in(index_path, self.schema)

        self.query_parser = qparser.MultifieldParser(["body", "path"], schema=self.schema)
        self.query_parser.add_plugin(qparser.FuzzyTermPlugin())

    def index(self, index, doc_type, id_=None, body=None):
        writer = self.search_index.writer()
        writer.update_document(path=id_.decode("utf-8"), body=body["content"].decode("utf-8"))
        writer.commit()

    def index_wiki(self, name, body):
        self.index('wiki', 'page', id_=name, body=body)

    def delete_index(self, index):
        from whoosh import index as whoosh_index
        self.search_index.close()
        self.search_index = whoosh_index.create_in(self.index_path, schema=self.schema)

    def wiki(self, query):
        if not query:
            return []

        q = self.query_parser.parse("%s~2" % (query,))

        with self.search_index.searcher() as s:
            results = s.search(q)

            results.formatter = self.formatter

            res = []
            for hit in results:
                name = hit["path"]
                page_data = g.current_wiki.get_page(name)["data"].decode("utf-8")
                content = hit.highlights('body', text=page_data)

                res.append(dict(name=name, content=content))

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
