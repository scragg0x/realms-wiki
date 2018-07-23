from __future__ import absolute_import

import os
import posixpath
import re

import ghdiff
import yaml
from dulwich.object_store import tree_lookup_path
from dulwich.repo import Repo, NotGitRepository
from six import text_type

from realms import cache
from realms.lib.hook import HookMixin
from realms.lib.util import cname_to_filename, filename_to_cname


class PageNotFound(Exception):
    pass


class Wiki(HookMixin):
    path = None
    base_path = '/'
    default_ref = 'master'
    default_committer_name = 'Anon'
    default_committer_email = 'anon@anon.anon'
    index_page = 'home'
    repo = None

    def __init__(self, path):
        try:
            self.repo = Repo(path)
        except NotGitRepository:
            self.repo = Repo.init(path, mkdir=True)
            # TODO add first commit here

        self.path = path

    def __repr__(self):
        return "Wiki: {0}".format(self.path)

    def commit(self, name, email, message, files):
        """Commit to the underlying git repo.

        :param name: Committer name
        :param email: Committer email
        :param message: Commit message
        :param files: list of file names that will be staged for commit
        :return:
        """
        if isinstance(name, text_type):
            name = name.encode('utf-8')
        if isinstance(email, text_type):
            email = email.encode('utf-8')
        if isinstance(message, text_type):
            message = message.encode('utf-8')
        author = committer = "{0} <{1}>".format(name, email).encode()
        self.repo.stage(files)
        return self.repo.do_commit(message=message,
                                   committer=committer,
                                   author=author)

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


class WikiPage(HookMixin):
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

        mode, sha = tree_lookup_path(self.wiki.repo.get_object, self.wiki.repo[self.sha].tree, self.filename.encode())
        data = self.wiki.repo[sha].data
        cache.set(cache_key, data)
        return data

    @property
    def history(self):
        """Get page history.

        History can take a long time to generate for repositories with many commits.
        This returns an iterator to avoid having to load them all at once, and caches
        as it goes.

        :return: iter -- Iterator over dicts

        """
        cache_head = []
        cache_tail = cache.get(self._cache_key('history')) or [{'_cache_missing': True}]
        while True:
            if not cache_tail:
                return
            index = 0
            for index, cached_rev in enumerate(cache_tail):
                if cached_rev.get("_cache_missing"):
                    break
                else:
                    cache_head.append(cached_rev)
                    yield cached_rev
            cache_tail = cache_tail[index+1:]

            start_sha = cached_rev.get('sha')
            end_sha = cache_tail[0].get('sha') if cache_tail else None
            for rev in self._iter_revs(start_sha=start_sha, end_sha=end_sha, filename=cached_rev.get('filename')):
                cache_head.append(rev)
                placeholder = {
                    '_cache_missing': True,
                    'sha': rev['sha'],
                    'filename': rev['new_filename']
                }
                cache.set(self._cache_key('history'), cache_head + [placeholder] + cache_tail)
                yield rev
            cache.set(self._cache_key('history'), cache_head + cache_tail)

    def _iter_revs(self, start_sha=None, end_sha=None, filename=None):
        if end_sha:
            end_sha = [end_sha]
        if not len(self.wiki.repo.open_index()):
            # Index is empty, no commits
            return
        filename = filename or self.filename
        filename = filename.encode('utf-8')
        walker = iter(self.wiki.repo.get_walker(paths=[filename],
                                                include=start_sha,
                                                exclude=end_sha,
                                                follow=True))
        if start_sha:
            # If we are not starting from HEAD, we already have the start commit
            next(walker)
        filename = self.filename
        for entry in walker:
            change_type = None
            for change in entry.changes():
                if change.new.path == filename:
                    filename = change.old.path
                    change_type = change.type
                    break

            author_name, author_email = entry.commit.author.rstrip(b'>').split(b'<')
            r = dict(author=author_name.strip(),
                     author_email=author_email,
                     time=entry.commit.author_time,
                     message=entry.commit.message,
                     sha=entry.commit.id,
                     type=change_type,
                     new_filename=change.new.path,
                     old_filename=change.old.path)
            yield r

    @property
    def history_cache(self):
        """Get info about the history cache.

        :return: tuple -- (cached items, cache complete?)
        """
        cached_revs = cache.get(self._cache_key('history'))
        if not cached_revs:
            return 0, False
        elif any(rev.get('_cache_missing') for rev in cached_revs):
            return len(cached_revs) - 1, False
        return len(cached_revs), True

    @property
    def imports(self):
        """Names"""
        meta = self._get_meta(self.data) or {}
        return meta.get('import', [])
    
    def get_front_matter(self):
        return self._get_meta(self.data) or {}

    @staticmethod
    def update_front_matter(content, obj):
        frontmatter_text = "---" + "\n"
        frontmatter_text += yaml.safe_dump(obj, default_flow_style=False)
        frontmatter_text += "---"
        
        if not content.startswith(b"---"):
            content = frontmatter_text + "\n\n" + content
        else:
            meta_end = re.search("\n(\.{3}|\-{3})", content)

            if not meta_end:
                content = frontmatter_text + content
            else:
                content = frontmatter_text + content[meta_end.end():]

        return content

    @staticmethod
    def _get_meta(content):
        """Get metadata from page if any.

        :param content: Page content
        :return: dict

        """
        if not content.startswith(b"---"):
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

    def _invalidate_cache(self, save_history=None):
        cache.delete(self._cache_key('data'))
        if save_history:
            if not save_history[0].get('_cache_missing'):
                save_history = [{'_cache_missing': True}] + save_history
            cache.set(self._cache_key('history'), save_history)
        else:
            cache.delete(self._cache_key('history'))

    def delete(self, username=None, email=None, message=None):
        """Delete page.
        :param username: Committer name
        :param email: Committer email
        :return: str -- Commit sha1

        """
        username, email = self._get_user(username, email)

        if not message:
            message = "Deleted %s" % self.name

        os.remove(os.path.join(self.wiki.path, self.filename))
        commit = self.wiki.commit(name=username,
                                  email=email,
                                  message=message,
                                  files=[self.filename])
        self._invalidate_cache()
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
        if old_filename not in self.wiki.repo.open_index():
            # old doesn't exist
            return None
        elif old_filename == new_filename:
            return None
        else:
            # file is being overwritten, but that is ok, it's git!
            pass

        username, email = self._get_user(username, email)

        if not message:
            message = "Moved {0} to {1}".format(self.name, new_name)

        os.rename(os.path.join(self.wiki.path, old_filename), os.path.join(self.wiki.path, new_filename))
        commit = self.wiki.commit(name=username,
                                  email=email,
                                  message=message,
                                  files=[old_filename, new_filename])

        old_history = cache.get(self._cache_key('history'))
        self._invalidate_cache()
        self.name = new_name
        self.filename = new_filename
        # We need to clear the cache for the new name as well as the old
        self._invalidate_cache(save_history=old_history)

        return commit

    def write(self, content, message=None, username=None, email=None):
        """Write page to git repo

        :param content: Content of page.
        :param message: Commit message.
        :param username: Commit Name.
        :param email: Commit Email.
        :return: Git commit sha1.
        """
        assert self.sha == b'HEAD'
        dirname = posixpath.join(self.wiki.path, posixpath.dirname(self.filename))

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(self.wiki.path + "/" + self.filename, 'w') as f:
            f.write(content)

        if not message:
            message = "Updated %s" % self.name

        username, email = self._get_user(username, email)

        ret = self.wiki.commit(name=username,
                               email=email,
                               message=message,
                               files=[self.filename])

        old_history = cache.get(self._cache_key('history'))
        self._invalidate_cache(save_history=old_history)
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
            message = "Revert '{0}' to {1}".format(self.name, commit_sha[:7])

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
