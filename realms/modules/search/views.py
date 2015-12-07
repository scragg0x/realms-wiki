from flask import render_template, request, Blueprint
from realms import search as search_engine

blueprint = Blueprint('search', __name__)


@blueprint.route('/_search')
def search():
    results = search_engine.wiki(request.args.get('q'))
    return render_template('search/search.html', results=results)
