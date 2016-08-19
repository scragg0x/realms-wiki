from __future__ import absolute_import

from ..wiki.models import WikiPage
from ... import search


@WikiPage.after('write')
def wiki_write_page(page, content, message=None, username=None, email=None, **kwargs):

    if not hasattr(search, 'index_wiki'):
        # using simple search or none
        return

    body = dict(name=page.name,
                content=content,
                message=message,
                email=email,
                username=username)
    return search.index_wiki(page.name, body)


@WikiPage.before('rename')
def wiki_rename_page_del(page, *args, **kwargs):

    if not hasattr(search, 'index_wiki'):
        return

    return search.delete_wiki(page.name)


@WikiPage.after('rename')
def wiki_rename_page_add(page, new_name, *args, **kwargs):
    wiki_write_page(page, page.data, *args, **kwargs)


@WikiPage.after('delete')
def wiki_delete_page(page, *args, **kwargs):

    if not hasattr(search, 'index_wiki'):
        return

    return search.delete_wiki(page.name)
