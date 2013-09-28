from gittle import Gittle
import os

class Wiki():
    path = None
    base_path = '/'
    default_ref = 'master'
    default_committer_name = 'Anon'
    default_committer_email = 'anon@anon.anon'
    index_page = 'Home'

    def __init__(self, path, **kwargs):
        self.path = path

    def write_page(self, name):
        name = name.replace(" ", "-")

    def rename_page(self, page, rename, commit={}):
        pass

    def page_exists(self, name):
        return None