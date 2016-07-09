from flask import g, Blueprint
from realms.config import conf

blueprint = Blueprint('sync', __name__)


@blueprint.route('/_sync/webhook')
def sync_webhook():
    """Receives a github webhook, and causes new changes to be pulled."""
    if not conf.SYNC_PULL:
        return
    # TODO: Check this is a post-receive on the correct repo?
    g.current_wiki.gittle.auth(conf.SYNC_AUTH)
    g.current_wiki.gittle.pull_from(conf.SYNC_REPO)
