from realms import elastic
from realms.lib.model import HookMixin


class Search(HookMixin):

    @classmethod
    def index(cls, index, doc_type, id_=None, body=None):
        return elastic.index(index=index, doc_type=doc_type, id=id_, body=body)

    @classmethod
    def wiki(cls, query):
        if not query:
            return []

        res = elastic.search(index='wiki', body={"query": {
            "multi_match": {
                "query": query,
                "fields": ["name^3", "content"]
            }}})

        return [hit["_source"] for hit in res['hits']['hits']]

    @classmethod
    def users(cls, query):
        pass