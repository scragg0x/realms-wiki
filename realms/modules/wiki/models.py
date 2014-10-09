import os
import re
import lxml.html
from lxml.html.clean import Cleaner
import ghdiff
import gittle.utils
import yaml
from gittle import Gittle
from dulwich.repo import NotGitRepository
from werkzeug.utils import escape, unescape
from realms.lib.util import to_canonical
from realms import cache
from realms.lib.hook import HookMixin


class Wiki(HookMixin):
    path = None
    base_path = '/'
    default_ref = 'master'
    default_committer_name = 'Anon'
    default_committer_email = 'anon@anon.anon'
    index_page = 'home'
    gittle = None
    repo = None

    def __init__(self, path):
        try:
            self.gittle = Gittle(path)
        except NotGitRepository:
            self.gittle = Gittle.init(path)

        # Dulwich repo
        self.repo = self.gittle.repo

        self.path = path

    def __repr__(self):
        return "Wiki: %s" % self.path

    def revert_page(self, name, commit_sha, message, username):
        page = self.get_page(name, commit_sha)
        if not page:
            # Page not found
            return None
        commit_info = gittle.utils.git.commit_info(self.gittle[commit_sha.encode('latin-1')])
        message = commit_info['message']
        return self.write_page(name, page['data'], message=message, username=username)

    def write_page(self, name, content, message=None, create=False, username=None, email=None):

        def escape_repl(m):
            if m.group(1):
                return "```" + escape(m.group(1)) + "```"

        def unescape_repl(m):
            if m.group(1):
                return "```" + unescape(m.group(1)) + "```"

        cname = to_canonical(name)

        # prevents p tag from being added, we remove this later
        content = '<div>' + content + '</div>'
        content = re.sub(r"```(.*?)```", escape_repl, content, flags=re.DOTALL)

        tree = lxml.html.fromstring(content)

        cleaner = Cleaner(remove_unknown_tags=False,
                          kill_tags=set(['style']),
                          safe_attrs_only=False)
        tree = cleaner.clean_html(tree)

        content = lxml.html.tostring(tree, encoding='utf-8', method='html')

        # remove added div tags
        content = content[5:-6]

        # FIXME this is for block quotes, doesn't work for double ">"
        content = re.sub(r"(\n&gt;)", "\n>", content)
        content = re.sub(r"(^&gt;)", ">", content)

        # Handlebars partial ">"
        content = re.sub(r"\{\{&gt;(.*?)\}\}", r'{{>\1}}', content)

        # Handlebars, allow {{}} inside HTML links
        content = content.replace("%7B", "{")
        content = content.replace("%7D", "}")

        content = re.sub(r"```(.*?)```", unescape_repl, content, flags=re.DOTALL)

        filename = self.cname_to_filename(cname)
        with open(self.path + "/" + filename, 'w') as f:
            f.write(content)

        if create:
            self.gittle.add(filename)

        if not message:
            message = "Updated %s" % name

        if not username:
            username = self.default_committer_name

        if not email:
            email = self.default_committer_email

        ret = self.gittle.commit(name=username,
                                 email=email,
                                 message=message,
                                 files=[filename])

        cache.delete(cname)

        return ret

    def rename_page(self, old_name, new_name, user=None):
        old_filename, new_filename = map(self.cname_to_filename, [old_name, new_name])
        if old_filename not in self.gittle.index:
            # old doesn't exist
            return None

        if new_filename in self.gittle.index:
            # file is being overwritten, but that is ok, it's git!
            pass

        os.rename(os.path.join(self.path, old_filename), os.path.join(self.path, new_filename))

        self.gittle.add(new_filename)
        self.gittle.rm(old_filename)

        self.gittle.commit(name=getattr(user, 'username', self.default_committer_name),
                           email=getattr(user, 'email', self.default_committer_email),
                           message="Moved %s to %s" % (old_name, new_name),
                           files=[old_filename, new_filename])

        cache.delete_many(old_filename, new_filename)

    def get_page(self, name, sha='HEAD'):
        cached = cache.get(name)
        if cached:
            return cached

        # commit = gittle.utils.git.commit_info(self.repo[sha])
        filename = self.cname_to_filename(name).encode('latin-1')
        sha = sha.encode('latin-1')

        try:
            data = self.gittle.get_commit_files(sha, paths=[filename]).get(filename)
            if not data:
                return None
            partials = {}
            if data.get('data'):
                meta = self.get_meta(data['data'])
                if meta and 'import' in meta:
                    for partial_name in meta['import']:
                        partials[partial_name] = self.get_page(partial_name)
            data['partials'] = partials
            data['info'] = self.get_history(name, limit=1)[0]
            return data

        except KeyError:
            # HEAD doesn't exist yet
            return None

    def get_meta(self, content):
        if not content.startswith("---"):
            return None
        meta_end = re.search("\n(\.{3}|\-{3})", content)
        if not meta_end:
            return None
        try:
            return yaml.safe_load(content[0:meta_end.start()])
        except Exception as e:
            return {'error': e.message}

    def compare(self, name, old_sha, new_sha):
        old = self.get_page(name, sha=old_sha)
        new = self.get_page(name, sha=new_sha)
        return ghdiff.diff(old['data'], new['data'])

    def get_history(self, name, limit=100):
        file_path = self.cname_to_filename(name)
        versions = []
        walker = self.repo.get_walker(paths=[file_path], max_entries=limit)
        for entry in walker:
            change_type = None
            for change in entry.changes():
                if change.old.path == file_path:
                    change_type = change.type
                elif change.new.path == file_path:
                    change_type = change.type
            author_name, author_email = entry.commit.author.split('<')
            versions.append(dict(
                author=author_name.strip(),
                time=entry.commit.author_time,
                message=entry.commit.message,
                sha=entry.commit.id,
                type=change_type))

        return versions

    @staticmethod
    def cname_to_filename(cname):
        return cname.lower() + ".md"