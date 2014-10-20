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


def cname_to_filename(cname):
    """ Convert canonical name to filename

    :param cname: Canonical name
    :return: str -- Filename

    """
    return cname.lower() + ".md"


def filename_to_cname(filename):
    """Convert filename to canonical name.

    .. note::

    It's assumed filename is already canonical format

    """
    return os.path.splitext(filename)[0]


class PageNotFound(Exception):
    pass


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
        """Revert page to passed commit sha1

        :param name:  Name of page to revert.
        :param commit_sha: Commit Sha1 to revert to.
        :param message: Commit message.
        :param username:
        :return: Git commit sha1

        """
        page = self.get_page(name, commit_sha)
        if not page:
            raise PageNotFound()

        if not message:
            commit_info = gittle.utils.git.commit_info(self.gittle[commit_sha.encode('latin-1')])
            message = commit_info['message']

        return self.write_page(name, page['data'], message=message, username=username)

    def write_page(self, name, content, message=None, create=False, username=None, email=None):
        """Write page to git repo

        :param name: Name of page.
        :param content: Content of page.
        :param message: Commit message.
        :param create: Perform git add operation?
        :param username: Commit Name.
        :param email: Commit Email.
        :return: Git commit sha1.
        """

        cname = to_canonical(name)
        filename = cname_to_filename(cname)

        content = self.clean(content)

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

    def clean(self, content):
        """Clean any HTML, this might not be necessary.

        :param content: Content of page.
        :return: str

        """
        def escape_repl(m):
            if m.group(1):
                return "```" + escape(m.group(1)) + "```"

        def unescape_repl(m):
            if m.group(1):
                return "```" + unescape(m.group(1)) + "```"

        # prevents p tag from being added, we remove this later
        content = '<div>' + content + '</div>'
        content = re.sub(r"```(.*?)```", escape_repl, content, flags=re.DOTALL)

        tree = lxml.html.fromstring(content)

        cleaner = Cleaner(remove_unknown_tags=False,
                          kill_tags={'style'},
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
        return content

    def rename_page(self, old_name, new_name, user=None):
        """Rename page.

        :param old_name: Page that will be renamed.
        :param new_name: New name of page.
        :param user: User object if any.
        :return: str -- Commit sha1

        """
        old_filename, new_filename = map(cname_to_filename, [old_name, new_name])
        if old_filename not in self.gittle.index:
            # old doesn't exist
            return None

        if new_filename in self.gittle.index:
            # file is being overwritten, but that is ok, it's git!
            pass

        os.rename(os.path.join(self.path, old_filename), os.path.join(self.path, new_filename))

        self.gittle.add(new_filename)
        self.gittle.rm(old_filename)

        commit = self.gittle.commit(name=getattr(user, 'username', self.default_committer_name),
                                    email=getattr(user, 'email', self.default_committer_email),
                                    message="Moved %s to %s" % (old_name, new_name),
                                    files=[old_filename, new_filename])

        cache.delete_many(old_filename, new_filename)

        return commit

    def delete_page(self, name, user=None):
        """Delete page.
        :param name: Page that will be deleted
        :param user: User object if any
        :return: str -- Commit sha1

        """
        self.gittle.rm(name)
        commit = self.gittle.commit(name=getattr(user, 'username', self.default_committer_name),
                                    email=getattr(user, 'email', self.default_committer_email),
                                    message="Deleted %s" % name,
                                    files=[name])
        cache.delete_many(name)
        return commit

    def get_page(self, name, sha='HEAD'):
        """Get page data, partials, commit info.

        :param name: Name of page.
        :param sha: Commit sha.
        :return: dict

        """
        cached = cache.get(name)
        if cached:
            return cached

        # commit = gittle.utils.git.commit_info(self.repo[sha])
        filename = cname_to_filename(name).encode('latin-1')
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
        """Get metadata from page if any.

        :param content: Page content
        :return: dict

        """
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
        """Compare two revisions of the same page.

        :param name: Name of page.
        :param old_sha: Older sha.
        :param new_sha: Newer sha.
        :return: str - Raw markup with styles

        """

        # TODO: This could be effectively done in the browser
        old = self.get_page(name, sha=old_sha)
        new = self.get_page(name, sha=new_sha)
        return ghdiff.diff(old['data'], new['data'])

    def get_index(self):
        """Get repo index of head.

        :return: list -- List of dicts

        """
        rv = []
        index = self.repo.open_index()
        for name in index:
            rv.append(dict(name=filename_to_cname(name),
                           filename=name,
                           ctime=index[name].ctime[0],
                           mtime=index[name].mtime[0],
                           sha=index[name].sha,
                           size=index[name].size))

        return rv

    def get_history(self, name, limit=100):
        """Get page history.

        :param name: Name of page.
        :param limit: Limit history size.
        :return: list -- List of dicts

        """
        if not len(self.repo.open_index()):
            # Index is empty, no commits
            return []

        file_path = cname_to_filename(name)
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
