from gittle import Gittle
import os


class Wiki():
    path = None
    base_path = '/'
    default_ref = 'master'
    default_committer_name = 'Anon'
    default_committer_email = 'anon@anon.anon'
    index_page = 'Home'
    repo = None

    def __init__(self, path, **kwargs):
        self.path = path
        self.repo = Gittle(path)

    def write_page(self, name):
        name = name.replace(" ", "-")

    def rename_page(self, page, rename, commit={}):
        pass

    def get_page(self, name):
        name = name.lower() + ".md"
        return self.repo.get_commit_files('HEAD', paths=[name]).get(name)