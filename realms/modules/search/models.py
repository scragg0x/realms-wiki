from realms import elastic
from realms.lib.model import HookMixin


class Search(HookMixin):

    @classmethod
    def index(cls, index, doc_type, id_=None, body=None):
        return elastic.index(index=index, doc_type=doc_type, id=id_, body=body)

    @classmethod
    def wiki(cls, query):
        return elastic.search(index='wiki', body={"query": {"match_all": {}}})

    @classmethod
    def users(cls, query):
        pass