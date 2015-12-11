import click
from realms import create_app, search, flask_cli
from realms.modules.wiki.models import Wiki
from realms.lib.util import filename_to_cname


@flask_cli.group(short_help="Search Module")
def cli():
    pass


@cli.command()
def rebuild_index():
    """ Rebuild search index
    """
    app = create_app()

    if app.config.get('SEARCH_TYPE') == 'simple':
        click.echo("Search type is simple, try using elasticsearch.")
        return

    with app.app_context():
        # Wiki
        search.delete_index('wiki')
        wiki = Wiki(app.config['WIKI_PATH'])
        for entry in wiki.get_index():
            page = wiki.get_page(entry['name'])
            if not page:
                # Some non-markdown files may have issues
                continue
            name = filename_to_cname(page['path'])
            # TODO add email?
            body = dict(name=name,
                        content=page['data'],
                        message=page['info']['message'],
                        username=page['info']['author'],
                        updated_on=entry['mtime'],
                        created_on=entry['ctime'])
            search.index_wiki(name, body)
