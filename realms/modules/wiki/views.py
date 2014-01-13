from flask import g, render_template, request, redirect, Blueprint, flash, url_for
from flask.ext.login import login_required
from realms.lib.util import to_canonical, remove_ext

blueprint = Blueprint('wiki', __name__, url_prefix='/wiki')


@blueprint.route("/_commit/<sha>/<name>")
def commit(name, sha):
    cname = to_canonical(name)

    data = g.current_wiki.get_page(cname, sha=sha)
    if data:
        return render_template('wiki/page.html', name=name, page=data, commit=sha)
    else:
        return redirect(url_for('.create', name=cname))


@blueprint.route("/_compare/<name>/<regex('[^.]+'):fsha><regex('\.{2,3}'):dots><regex('.+'):lsha>")
def compare(name, fsha, dots, lsha):
    diff = g.current_wiki.compare(name, fsha, lsha)
    return render_template('wiki/compare.html', name=name, diff=diff, old=fsha, new=lsha)


@blueprint.route("/_revert", methods=['POST'])
def revert():
    if request.method == 'POST':
        name = request.form.get('name')
        commit = request.form.get('commit')
        cname = to_canonical(name)
        g.current_wiki.revert_page(name, commit, message="Reverting %s" % cname,
                                   username=g.current_user.get('username'))
        flash('Page reverted', 'success')
        return redirect(url_for('.page', name=cname))
    
@blueprint.route("/_history/<name>")
def history(name):
    history = g.current_wiki.get_history(name)
    return render_template('wiki/history.html', name=name, history=history, wiki_home=url_for('wiki.page'))


@blueprint.route("/_edit/<name>", methods=['GET', 'POST'])
def edit(name):
    data = g.current_wiki.get_page(name)
    cname = to_canonical(name)
    if request.method == 'POST':
        edit_cname = to_canonical(request.form['name'])
        if edit_cname.lower() != cname.lower():
            g.current_wiki.rename_page(cname, edit_cname)
        g.current_wiki.write_page(edit_cname,
                                  request.form['content'],
                                  message=request.form['message'],
                                  username=g.current_user.get('username'))
        return redirect(url_for('.page', name=edit_cname))
    else:
        if data:
            name = remove_ext(data['name'])
            content = data['data']
            return render_template('wiki/edit.html', name=name, content=content)
        else:
            return redirect(url_for('.create', name=cname))


@blueprint.route("/_delete/<name>", methods=['POST'])
@login_required
def delete(name):
    pass


@blueprint.route("/_create/", defaults={'name': None}, methods=['GET', 'POST'])
@blueprint.route("/_create/<name>", methods=['GET', 'POST'])
def create(name):
    cname = ""
    if name:
        cname = to_canonical(name)
        if g.current_wiki.get_page(cname):
            # Page exists, edit instead
            return redirect(url_for('.edit', name=cname))

    if request.method == 'POST':
        g.current_wiki.write_page(request.form['name'],
                                  request.form['content'],
                                  message=request.form['message'],
                                  create=True,
                                  username=g.current_user.get('username'))
        return redirect(url_for('.page', name=cname))
    else:
        return render_template('wiki/edit.html', name=cname, content="")


@blueprint.route("/", defaults={'name': 'home'})
@blueprint.route("/<name>")
def page(name):
    cname = to_canonical(name)
    if cname != name:
        return redirect(url_for('.page', name=cname))

    data = g.current_wiki.get_page(cname)

    if data:
        return render_template('wiki/page.html', name=cname, page=data)
    else:
        return redirect(url_for('.create', name=cname))