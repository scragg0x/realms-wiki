from realms.modules.wiki.models import Wiki
from realms.modules.search.models import Search


@Wiki.after('write_page')
def wiki_write_page(name, content, **kwargs):
    body = dict(name=name,
                content=content)
    body.update(kwargs)
    return Search.index('wiki', 'page', body=body)


@Wiki.after('rename_page')
def wiki_rename_page(*args, **kwargs):
    pass