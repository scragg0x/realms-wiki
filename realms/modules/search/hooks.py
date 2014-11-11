from realms.modules.wiki.models import Wiki
from realms.modules.search.models import Search


@Wiki.after('write_page')
def wiki_write_page(name, content, message=None, username=None, email=None, **kwargs):
    body = dict(name=name,
                content=content,
                message=message,
                email=email,
                username=username)
    return Search.index('wiki', 'page', id_=name, body=body)


@Wiki.after('rename_page')
def wiki_rename_page(*args, **kwargs):
    pass