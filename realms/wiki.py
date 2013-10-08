import os
import re
from lxml.html.clean import clean_html
import ghdiff

from gittle import Gittle
from dulwich.repo import NotGitRepository

from util import to_canonical
from models import Site


class MyGittle(Gittle):

    def file_history(self, path):
        """Returns all commits where given file was modified
        """
        versions = []
        commits_info = self.commit_info()
        seen_shas = set()

        for commit in commits_info:
            try:
                files = self.get_commit_files(commit['sha'], paths=[path])
                file_path, file_data = files.items()[0]
            except IndexError:
                continue

            file_sha = file_data['sha']

            if file_sha in seen_shas:
                continue
            else:
                seen_shas.add(file_sha)

            versions.append(dict(author=commit['author']['name'],
                                 time=commit['time'],
                                 file_sha=file_sha,
                                 sha=commit['sha'],
                                 message=commit['message']))
        return versions

    def mv_fs(self, file_pair):
        old_name, new_name = file_pair
        os.rename(self.path + "/" + old_name, self.path + "/" + new_name)


class Wiki():
    path = None
    base_path = '/'
    default_ref = 'master'
    default_committer_name = 'Anon'
    default_committer_email = 'anon@anon.anon'
    index_page = 'home'
    repo = None

    def __init__(self, path):
        try:
            self.repo = MyGittle(path)
        except NotGitRepository:
            self.repo = MyGittle.init(path)

        self.path = path

    @staticmethod
    def is_registered(name):
        s = Site()
        return True if s.get_by_name(name) else False

    def write_page(self, name, content, message=None, create=False, username=None, email=None):
        # adding the div wrapper apparently fixes anomalies with the lxml parser with certain markdown
        content = clean_html('<div>' + content + '</div>')
        content = content[5:-6]
        content = re.sub(r"(\n&gt;)", "\n>", content)
        content = re.sub(r"(^&gt;)", ">", content)

        filename = self.cname_to_filename(to_canonical(name))
        f = open(self.path + "/" + filename, 'w')
        f.write(content)
        f.close()

        if create:
            self.repo.add(filename)

        if not message:
            message = "Updated %s" % name

        if not username:
            username = self.default_committer_name

        if not email:
            email = "%s@realms.io" % username

        return self.repo.commit(name=username,
                                email=email,
                                message=message,
                                files=[filename])

    def rename_page(self, old_name, new_name):
        old_name, new_name = map(self.cname_to_filename, [old_name, new_name])
        self.repo.mv([(old_name, new_name)])
        self.repo.commit(name=self.default_committer_name,
                         email=self.default_committer_email,
                         message="Moving %s to %s" % (old_name, new_name),
                         files=[old_name])

    def get_page(self, name, sha='HEAD'):
        name = self.cname_to_filename(name)
        try:
            return self.repo.get_commit_files(sha, paths=[name]).get(name)
        except KeyError:
            # HEAD doesn't exist yet
            return None

    def compare(self, name, new_sha, old_sha):
        old = self.get_page(name, sha=old_sha)
        new = self.get_page(name, sha=new_sha)

        return ghdiff.diff(old['data'], new['data'])

    def get_history(self, name):
        return self.repo.file_history(self.cname_to_filename(name))

    def cname_to_filename(self, cname):
        return cname.lower() + ".md"