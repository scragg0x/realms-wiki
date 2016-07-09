from realms.config import conf
from realms.modules.wiki.models import Wiki


@Wiki.after('commit')
def sync_push(wiki, *args, **kwargs):
    wiki.gittle.auth(conf.SYNC_AUTH)
    if not conf.SYNC_PUSH:
        return
    wiki.gittle.push_to(conf.SYNC_REPO)
