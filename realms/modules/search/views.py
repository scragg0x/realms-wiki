from flask import abort, g, render_template, request, redirect, Blueprint, flash, url_for, current_app
from .models import Search
blueprint = Blueprint('search', __name__)


@blueprint.route('/_search')
def search():
    results = Search.wiki(request.args.get('q'))
    print results
    return render_template('search/search.html', results=results)