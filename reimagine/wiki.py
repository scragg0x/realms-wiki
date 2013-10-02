from gittle import Gittle
from util import to_canonical
from lxml.html.clean import clean_html


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
            self.repo = MyGittle.init(path)
        except OSError:
            # Repo already exists
            self.repo = MyGittle(path)

        self.path = path

    def write_page(self, name, content, message=None, create=False):
        name = to_canonical(name)
        #content = clean_html(content)
        filename = name.lower() + ".md"
        f = open(self.path + "/" + filename, 'w')
        f.write(content)
        f.close()

        if create:
            self.repo.add(filename)

        return self.repo.commit(name=self.default_committer_name,
                                email=self.default_committer_email,
                                message=message,
                                files=[filename])

    def rename_page(self, old_name, new_name):
        self.repo.mv([old_name, new_name])

    def get_page(self, name, sha='HEAD'):
        name = name.lower() + ".md"
        try:
            return self.repo.get_commit_files(sha, paths=[name]).get(name)
        except KeyError:
            # HEAD doesn't exist yet
            return None

    def get_history(self, name):
        name = name.lower() + ".md"
        return self.repo.file_history(name)