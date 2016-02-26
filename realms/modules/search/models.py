import re
import sys

from flask import g, current_app
from realms.lib.util import filename_to_cname


def simple(app):
    return SimpleSearch()


def whoosh(app):
    return WhooshSearch(app.config['WHOOSH_INDEX'], app.config['WHOOSH_LANGUAGE'])


def elasticsearch(app):
    from flask.ext.elastic import Elastic
    fields = app.config.get('ELASTICSEARCH_FIELDS')
    return ElasticSearch(Elastic(app), fields)


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
            name = re.sub(r"//+", '/', name)
            if set(query.split()).intersection(name.replace('/', '-').split('-')):
                page = g.current_wiki.get_page(name)

                # this can be None, not sure how
                if page:
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
        import os

        if not has_stemmer(language) or not has_stopwords(language):
            # TODO Display a warning?
            analyzer = SimpleAnalyzer()
        else:
            analyzer = LanguageAnalyzer(language)

        self.schema = Schema(path=ID(unique=True, stored=True), body=TEXT(analyzer=analyzer))
        self.formatter = UppercaseFormatter()

        self.index_path = index_path

        if not os.path.exists(index_path):
            try:
                os.mkdir(index_path)
            except OSError as e:
                sys.exit("Error creating Whoosh index: %s" % e)

        if whoosh_index.exists_in(index_path):
            try:
                self.search_index = whoosh_index.open_dir(index_path)
            except whoosh_index.IndexError as e:
                sys.exit("Error opening whoosh index: %s" % (e))
        else:
            self.search_index = whoosh_index.create_in(index_path, self.schema)

        self.query_parser = qparser.MultifieldParser(["body", "path"], schema=self.schema)
        self.query_parser.add_plugin(qparser.FuzzyTermPlugin())

    def index(self, index, doc_type, id_=None, body=None):
        writer = self.search_index.writer()
        writer.update_document(path=id_.decode("utf-8"), body=body["content"].decode("utf-8"))
        writer.commit()

    def delete(self, id_):
        with self.search_index.searcher() as s:
            doc_num = s.document_number(path=id_.decode("utf-8"))
            writer = self.search_index.writer()
            writer.delete_document(doc_num)
            writer.commit()

    def index_wiki(self, name, body):
        self.index('wiki', 'page', id_=name, body=body)

    def delete_wiki(self, name):
        self.delete(id_=name)

    def delete_index(self, index):
        from whoosh import index as whoosh_index
        self.search_index.close()
        self.search_index = whoosh_index.create_in(self.index_path, schema=self.schema)

    def wiki(self, query):
        if not query:
            return []

        q = self.query_parser.parse(query)

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
    def __init__(self, elastic, fields):
        self.elastic = elastic
        self.fields = fields

    def index(self, index, doc_type, id_=None, body=None):
        return self.elastic.index(index=index, doc_type=doc_type, id=id_, body=body)

    def delete(self, index, doc_type, id_):
        return self.elastic.delete(index=index, doc_type=doc_type, id=id_)

    def index_wiki(self, name, body):
        self.index('wiki', 'page', id_=name, body=body)

    def delete_wiki(self, name):
        self.delete('wiki', 'page', id_=name)

    def delete_index(self, index):
        return self.elastic.indices.delete(index=index, ignore=[400, 404])

    def wiki(self, query):
        if not query:
            return []

        res = self.elastic.search(index='wiki', body={"query": {
            "multi_match": {
                "query": query,
                "fields": self.fields
            }}})

        return [hit["_source"] for hit in res['hits']['hits']]

    def users(self, query):
        pass
