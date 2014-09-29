from flask import g, render_template, request, redirect, Blueprint, flash, url_for, current_app
from flask.ext.login import login_required
from realms.lib.util import to_canonical, remove_ext
from realms.modules.wiki.models import Wiki
from realms import current_user, app

blueprint = Blueprint('wiki', __name__, url_prefix=app.config['RELATIVE_PATH'])


@app.before_request
def init_wiki():
    g.current_wiki = Wiki(app.config['WIKI_PATH'])


@blueprint.route("/_commit/<sha>/<name>")
def commit(name, sha):
    cname = to_canonical(name)

    data = g.current_wiki.get_page(cname, sha=sha)
    if data:
        return render_template('wiki/page.html', name=name, page=data, commit=sha)
    else:
        return redirect(url_for('wiki.create', name=cname))


@blueprint.route("/_compare/<name>/<regex('[^.]+'):fsha><regex('\.{2,3}'):dots><regex('.+'):lsha>")
def compare(name, fsha, dots, lsha):
    diff = g.current_wiki.compare(name, fsha, lsha)
    return render_template('wiki/compare.html', name=name, diff=diff, old=fsha, new=lsha)


@blueprint.route("/_revert", methods=['POST'])
@login_required
def revert():
    name = request.form.get('name')
    commit = request.form.get('commit')
    cname = to_canonical(name)

    if cname.lower() in app.config.WIKI_LOCKED_PAGES:
        flash("Page is locked")
        return redirect(url_for(app.config['ROOT_ENDPOINT']))

    g.current_wiki.revert_page(name, commit, message="Reverting %s" % cname,
                               username=current_user.username)
    flash('Page reverted', 'success')
    return redirect(url_for('wiki.page', name=cname))


@blueprint.route("/_history/<name>")
def history(name):
    return render_template('wiki/history.html', name=name, history=g.current_wiki.get_history(name))


@blueprint.route("/_edit/<name>", methods=['GET', 'POST'])
@login_required
def edit(name):
    data = g.current_wiki.get_page(name)
    cname = to_canonical(name)
    if request.method == 'POST':
        edit_cname = to_canonical(request.form['name'])

        if edit_cname.lower() in app.config['WIKI_LOCKED_PAGES']:
            return redirect(url_for(app.config['ROOT_ENDPOINT']))

        if edit_cname.lower() != cname.lower():
            g.current_wiki.rename_page(cname, edit_cname)

        g.current_wiki.write_page(edit_cname,
                                  request.form['content'],
                                  message=request.form['message'],
                                  username=current_user.username)
    else:
        if data:
            name = remove_ext(data['name'])
            content = data.get('data')
            g.assets['js'].append('editor.js')
            return render_template('wiki/edit.html', name=name, content=content, partials=data.get('partials'))
        else:
            return redirect(url_for('wiki.create', name=cname))


@blueprint.route("/_delete/<name>", methods=['POST'])
@login_required
def delete(name):
    pass


@blueprint.route("/_create/", defaults={'name': None}, methods=['GET', 'POST'])
@blueprint.route("/_create/<name>", methods=['GET', 'POST'])
@login_required
def create(name):
    if request.method == 'POST':
        cname = to_canonical(request.form['name'])

        if cname in app.config['WIKI_LOCKED_PAGES']:
            return redirect(url_for("wiki.create"))

        if not cname:
            return redirect(url_for("wiki.create"))

        g.current_wiki.write_page(request.form['name'],
                                  request.form['content'],
                                  message=request.form['message'],
                                  create=True,
                                  username=current_user.username)
    else:
        cname = to_canonical(name) if name else ""
        if cname and g.current_wiki.get_page(cname):
            # Page exists, edit instead
            return redirect(url_for('wiki.edit', name=cname))

        g.assets['js'].append('editor.js')
        return render_template('wiki/edit.html', name=cname, content="")


@blueprint.route("/", defaults={'name': 'home'})
@blueprint.route("/<name>")
def page(name):
    cname = to_canonical(name)
    if cname != name:
        return redirect(url_for('wiki.page', name=cname))

    data = g.current_wiki.get_page(cname)

    if data:
        return render_template('wiki/page.html', name=cname, page=data, partials=data.get('partials'))
    else:
        return redirect(url_for('wiki.create', name=cname))