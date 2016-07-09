import collections
import itertools
import os
import posixpath
import re
import ghdiff
import gittle.utils
import yaml
from gittle import Gittle
from dulwich.object_store import tree_lookup_path
from dulwich.repo import NotGitRepository
from realms.lib.util import cname_to_filename, filename_to_cname
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

    def get_page(self, name, sha='HEAD'):
        """Get page data, partials, commit info.

        :param name: Name of page.
        :param sha: Commit sha.
        :return: dict

        """
        return WikiPage(name, self, sha=sha)

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


class WikiPage(object):
    def __init__(self, name, wiki, sha='HEAD'):
        self.name = name
        self.filename = cname_to_filename(name)
        self.sha = sha.encode('latin-1')
        self.wiki = wiki

    @property
    def data(self):
        cache_key = self._cache_key('data')
        cached = cache.get(cache_key)
        if cached:
            return cached

        data = self.wiki.gittle.get_commit_files(self.sha, paths=[self.filename]).get(self.filename).get('data')
        cache.set(cache_key, data)
        return data

    @property
    def history(self):
        """Get page history.

        History can take a long time to generate for repositories with many commits.
        This returns an iterator to avoid having to load them all at once.

        :return: iter -- Iterator over dicts

        """
        cache_complete = False
        cached_revs = cache.get(self._cache_key('history')) or []
        start_sha = None
        if cached_revs:
            if cached_revs[-1] == 'TAIL':
                del cached_revs[-1]
                cache_complete = True
            else:
                start_sha = cached_revs[-1]['sha']
        for rev in cached_revs:
            yield rev
        if cache_complete:
            return
        if not len(self.wiki.repo.open_index()):
            # Index is empty, no commits
            return
        walker = iter(self.wiki.repo.get_walker(paths=[self.filename], include=start_sha, follow=True))
        if start_sha:
            # If we are not starting from HEAD, we already have the start commit
            next(walker)
        filename = self.filename
        try:
            for entry in walker:
                change_type = None
                for change in entry.changes():
                    if change.new.path == filename:
                        filename = change.old.path
                        change_type = change.type
                        break

                author_name, author_email = entry.commit.author.rstrip('>').split('<')
                r = dict(author=author_name.strip(),
                         author_email=author_email,
                         time=entry.commit.author_time,
                         message=entry.commit.message,
                         sha=entry.commit.id,
                         type=change_type)
                cached_revs.append(r)
                yield r
            cached_revs.append('TAIL')
        finally:
            cache.set(self._cache_key('history'), cached_revs)

    @property
    def history_cache(self):
        """Get info about the history cache.

        :return: tuple -- (cached items, cache complete?)
        """
        cache_complete = False
        cached_revs = cache.get(self._cache_key('history')) or []
        if cached_revs:
            if cached_revs[-1] == 'TAIL':
                del cached_revs[-1]
                cache_complete = True
        return len(cached_revs), cache_complete

    @property
    def partials(self):
        data = self.data
        if not data:
            return {}
        partials = {}
        meta = self._get_meta(data)
        if meta and 'import' in meta:
            for partial_name in meta['import']:
                partials[partial_name] = self.wiki.get_page(partial_name, sha=self.sha)
        return partials

    @staticmethod
    def _get_meta(content):
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

    def _cache_key(self, property):
        return 'page/{0}[{1}].{2}'.format(self.name, self.sha, property)

    def _get_user(self, username, email):
        if not username:
            username = self.wiki.default_committer_name

        if not email:
            email = self.wiki.default_committer_email

        return username, email

    def _clear_cache(self):
        cache.delete_many(self._cache_key(p) for p in ['data', 'info'])

    def delete(self, username=None, email=None, message=None):
        """Delete page.
        :param username: Committer name
        :param email: Committer email
        :return: str -- Commit sha1

        """
        username, email = self._get_user(username, email)

        if not message:
            message = "Deleted %s" % self.name

        # gittle.rm won't actually remove the file, have to do it ourselves
        os.remove(os.path.join(self.wiki.path, self.filename))
        self.wiki.gittle.rm(self.filename)
        commit = self.wiki.gittle.commit(name=username,
                                         email=email,
                                         message=message,
                                         files=[self.filename])
        self._clear_cache()
        return commit

    def rename(self, new_name, username=None, email=None, message=None):
        """Rename page.

        :param new_name: New name of page.
        :param username: Committer name
        :param email: Committer email
        :return: str -- Commit sha1

        """
        assert self.sha == 'HEAD'
        old_filename, new_filename = self.filename, cname_to_filename(new_name)
        if old_filename not in self.wiki.gittle.index:
            # old doesn't exist
            return None
        elif old_filename == new_filename:
            return None
        else:
            # file is being overwritten, but that is ok, it's git!
            pass

        username, email = self._get_user(username, email)

        if not message:
            message = "Moved %s to %s" % (self.name, new_name)

        os.rename(os.path.join(self.wiki.path, old_filename), os.path.join(self.wiki.path, new_filename))

        self.wiki.gittle.add(new_filename)
        self.wiki.gittle.rm(old_filename)

        commit = self.wiki.gittle.commit(name=username,
                                         email=email,
                                         message=message,
                                         files=[old_filename, new_filename])

        self._clear_cache()
        self.name = new_name
        self.filename = new_filename
        # We need to clear the cache for the new name as well as the old
        self._clear_cache()

        return commit

    def write(self, content, message=None, create=False, username=None, email=None):
        """Write page to git repo

        :param content: Content of page.
        :param message: Commit message.
        :param create: Perform git add operation?
        :param username: Commit Name.
        :param email: Commit Email.
        :return: Git commit sha1.
        """
        assert self.sha == 'HEAD'
        dirname = posixpath.join(self.wiki.path, posixpath.dirname(self.filename))

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(self.wiki.path + "/" + self.filename, 'w') as f:
            f.write(content)

        if create:
            self.wiki.gittle.add(self.filename)

        if not message:
            message = "Updated %s" % self.name

        username, email = self._get_user(username, email)

        ret = self.wiki.gittle.commit(name=username,
                                      email=email,
                                      message=message,
                                      files=[self.filename])

        self._clear_cache()
        return ret

    def revert(self, commit_sha, message, username, email):
        """Revert page to passed commit sha1

        :param commit_sha: Commit Sha1 to revert to.
        :param message: Commit message.
        :param username: Committer name.
        :param email: Committer email.
        :return: Git commit sha1

        """
        assert self.sha == 'HEAD'
        new_page = self.wiki.get_page(self.name, commit_sha)
        if not new_page:
            raise PageNotFound('Commit not found')

        if not message:
            commit_info = gittle.utils.git.commit_info(self.wiki.gittle[commit_sha.encode('latin-1')])
            message = commit_info['message']

        return self.write(new_page.data, message=message, username=username, email=email)

    def compare(self, old_sha):
        """Compare two revisions of the same page.

        :param old_sha: Older sha.
        :return: str - Raw markup with styles

        """

        # TODO: This could be effectively done in the browser
        old = self.wiki.get_page(self.name, sha=old_sha)
        return ghdiff.diff(old.data, self.data)

    def __nonzero__(self):
        # Verify this file is in the tree for the given commit sha
        try:
            tree_lookup_path(self.wiki.repo.get_object, self.wiki.repo[self.sha].tree, self.filename)
        except KeyError:
            # We'll get a KeyError if self.sha isn't in the repo, or if self.filename isn't in the tree of our commit
            return False
        return True
