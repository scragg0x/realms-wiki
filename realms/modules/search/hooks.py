from realms.modules.wiki.models import Wiki
from realms import search


@Wiki.after('write_page')
def wiki_write_page(name, content, message=None, username=None, email=None, **kwargs):

    if not hasattr(search, 'index_wiki'):
        # using simple search or none
        return

    body = dict(name=name,
                content=content,
                message=message,
                email=email,
                username=username)
    return search.index_wiki(name, body)


@Wiki.after('rename_page')
def wiki_rename_page(old_name, *args, **kwargs):

    if not hasattr(search, 'index_wiki'):
        return

    return search.delete_wiki(old_name)


@Wiki.after('delete_page')
def wiki_delete_page(name, *args, **kwargs):

    if not hasattr(search, 'index_wiki'):
        return

    return search.delete_wiki(name)
