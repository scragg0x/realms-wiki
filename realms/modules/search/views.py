from __future__ import absolute_import

from flask import render_template, request, Blueprint, current_app
from flask_login import current_user

from realms import search as search_engine


blueprint = Blueprint('search', __name__, template_folder='templates')


@blueprint.route('/_search')
def search():
    if current_app.config.get('PRIVATE_WIKI') and current_user.is_anonymous():
        return current_app.login_manager.unauthorized()

    results = search_engine.wiki(request.args.get('q'))
    return render_template('search/search.html', results=results)
