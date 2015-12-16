import os
import posixpath
import re
import ghdiff
import gittle.utils
import yaml
from gittle import Gittle
from dulwich.repo import NotGitRepository
from realms.lib.util import to_canonical, cname_to_filename, filename_to_cname
from realms import cache
from realms.lib.hook import HookMixin


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

    def _get_user(self, username, email):
        if not username:
            username = self.default_committer_name

        if not email:
            email = self.default_committer_email

        return username, email

    def _cache_key(self, name, sha='HEAD'):
        return 'page/%s[%s]' % (name, sha)

    def revert_page(self, name, commit_sha, message, username, email):
        """Revert page to passed commit sha1

        :param name:  Name of page to revert.
        :param commit_sha: Commit Sha1 to revert to.
        :param message: Commit message.
        :param username: Committer name.
        :param email: Committer email.
        :return: Git commit sha1

        """
        page = self.get_page(name, commit_sha)
        if not page:
            raise PageNotFound('Commit not found')

        if not message:
            commit_info = gittle.utils.git.commit_info(self.gittle[commit_sha.encode('latin-1')])
            message = commit_info['message']

        return self.write_page(name, page['data'], message=message, username=username, email=email)

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
        dirname = posixpath.join(self.path, posixpath.dirname(filename))

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(self.path + "/" + filename, 'w') as f:
            f.write(content)

        if create:
            self.gittle.add(filename)

        if not message:
            message = "Updated %s" % name

        username, email = self._get_user(username, email)

        ret = self.gittle.commit(name=username,
                                 email=email,
                                 message=message,
                                 files=[filename])

        cache.delete(self._cache_key(cname))

        return ret

    def rename_page(self, old_name, new_name, username=None, email=None, message=None):
        """Rename page.

        :param old_name: Page that will be renamed.
        :param new_name: New name of page.
        :param username: Committer name
        :param email: Committer email
        :return: str -- Commit sha1

        """
        old_filename, new_filename = map(cname_to_filename, [old_name, new_name])
        if old_filename not in self.gittle.index:
            # old doesn't exist
            return None

        if old_filename == new_filename:
            return

        if new_filename in self.gittle.index:
            # file is being overwritten, but that is ok, it's git!
            pass

        username, email = self._get_user(username, email)

        if not message:
            message = "Moved %s to %s" % (old_name, new_name)

        os.rename(os.path.join(self.path, old_filename), os.path.join(self.path, new_filename))

        self.gittle.add(new_filename)
        self.gittle.rm(old_filename)

        commit = self.gittle.commit(name=username,
                                    email=email,
                                    message=message,
                                    files=[old_filename, new_filename])

        cache.delete_many(self._cache_key(old_name), self._cache_key(new_name))

        return commit

    def delete_page(self, name, username=None, email=None, message=None):
        """Delete page.
        :param name: Page that will be deleted
        :param username: Committer name
        :param email: Committer email
        :return: str -- Commit sha1

        """

        username, email = self._get_user(username, email)

        if not message:
            message = "Deleted %s" % name

        filename = cname_to_filename(name)

        # gittle.rm won't actually remove the file, have to do it ourselves
        os.remove(os.path.join(self.path, filename))
        self.gittle.rm(filename)
        commit = self.gittle.commit(name=username,
                                    email=email,
                                    message=message,
                                    files=[filename])
        cache.delete_many(self._cache_key(name))
        return commit

    def get_page(self, name, sha='HEAD'):
        """Get page data, partials, commit info.

        :param name: Name of page.
        :param sha: Commit sha.
        :return: dict

        """
        cached = cache.get(self._cache_key(name, sha))
        if cached:
            return cached

        # commit = gittle.utils.git.commit_info(self.repo[sha])
        filename = cname_to_filename(name).encode('utf8')
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
            cache.set(self._cache_key(name, sha), data)
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
            author_name, author_email = entry.commit.author.rstrip('>').split('<')
            versions.append(dict(
                author=author_name.strip(),
                author_email=author_email,
                time=entry.commit.author_time,
                message=entry.commit.message,
                sha=entry.commit.id,
                type=change_type))

        return versions
