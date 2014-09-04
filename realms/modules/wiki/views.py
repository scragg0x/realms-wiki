from flask import g, render_template, request, redirect, Blueprint, flash, url_for, current_app
from flask.ext.login import login_required
from realms.lib.util import to_canonical, remove_ext
from realms.modules.wiki.models import Wiki
from realms import config, current_user

blueprint = Blueprint('wiki', __name__, url_prefix=config.RELATIVE_PATH)

wiki = Wiki(config.WIKI_PATH)


@blueprint.route("/_commit/<sha>/<name>")
def commit(name, sha):
    cname = to_canonical(name)

    data = wiki.get_page(cname, sha=sha)
    if data:
        return render_template('wiki/page.html', name=name, page=data, commit=sha)
    else:
        return redirect(url_for('wiki.create', name=cname))


@blueprint.route("/_compare/<name>/<regex('[^.]+'):fsha><regex('\.{2,3}'):dots><regex('.+'):lsha>")
def compare(name, fsha, dots, lsha):
    diff = wiki.compare(name, fsha, lsha)
    return render_template('wiki/compare.html', name=name, diff=diff, old=fsha, new=lsha)


@blueprint.route("/_revert", methods=['POST'])
@login_required
def revert():
    name = request.form.get('name')
    commit = request.form.get('commit')
    cname = to_canonical(name)
    wiki.revert_page(name, commit, message="Reverting %s" % cname,
                     username=current_user.username)
    flash('Page reverted', 'success')
    return redirect(url_for('wiki.page', name=cname))


@blueprint.route("/_history/<name>")
def history(name):
    history = wiki.get_history(name)
    return render_template('wiki/history.html', name=name, history=history, wiki_home=url_for('wiki.page'))


@blueprint.route("/_edit/<name>", methods=['GET', 'POST'])
@login_required
def edit(name):
    data = wiki.get_page(name)
    cname = to_canonical(name)
    if request.method == 'POST':
        edit_cname = to_canonical(request.form['name'])
        if edit_cname.lower() != cname.lower():
            wiki.rename_page(cname, edit_cname)

        wiki.write_page(edit_cname,
                        request.form['content'],
                        message=request.form['message'],
                        username=current_user.username)
    else:
        if data:
            name = remove_ext(data['name'])
            content = data['data']
            g.assets['js'].append('editor.js')
            return render_template('wiki/edit.html', name=name, content=content)
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
        wiki.write_page(request.form['name'],
                        request.form['content'],
                        message=request.form['message'],
                        create=True,
                        username=current_user.username)
    else:
        cname = to_canonical(name) if name else ""
        if cname and wiki.get_page(cname):
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

    data = wiki.get_page(cname)

    if data:
        return render_template('wiki/page.html', name=cname, page=data)
    else:
        return redirect(url_for('wiki.create', name=cname))