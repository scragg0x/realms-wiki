from __future__ import absolute_import

import os
import sys

from .models import Wiki


def init(app):
    # Init Wiki
    Wiki(app.config['WIKI_PATH'])

    # Check paths
    for mode in [os.W_OK, os.R_OK]:
        for dir_ in [app.config['WIKI_PATH'], os.path.join(app.config['WIKI_PATH'], '.git')]:
            if not os.access(dir_, mode):
                sys.exit('Read and write access to WIKI_PATH is required (%s)' % dir_)
