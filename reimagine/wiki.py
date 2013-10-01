from gittle import Gittle
from util import to_canonical
from lxml.html.clean import clean_html


class Wiki():
    path = None
    base_path = '/'
    default_ref = 'master'
    default_committer_name = 'Anon'
    default_committer_email = 'anon@anon.anon'
    index_page = 'Home'
    repo = None

    def __init__(self, path):
        try:
            self.repo = Gittle.init(path)
        except OSError:
            # Repo already exists
            self.repo = Gittle(path)

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

    def get_page(self, name):
        name = name.lower() + ".md"
        try:
            return self.repo.get_commit_files('HEAD', paths=[name]).get(name)
        except KeyError:
            # HEAD doesn't exist yet
            return None