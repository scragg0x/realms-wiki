import os
from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip
from setuptools import setup, find_packages

pipfile = Project().parsed_pipfile
requirements = convert_deps_to_pip(pipfile['packages'], r=False)

if os.environ.get('USER', '') == 'vagrant':
    del os.link

DESCRIPTION = "Simple git based wiki"

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

__version__ = None
exec(open('realms/version.py').read())

CLASSIFIERS = [
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content']

setup(name='realms-wiki',
      version=__version__,
      packages=find_packages(),
      install_requires=requirements,
      entry_points={
          'console_scripts': [
              'realms-wiki = realms.commands:cli'
          ]},
      author='Matthew Scragg',
      author_email='scragg@gmail.com',
      maintainer='Matthew Scragg',
      maintainer_email='scragg@gmail.com',
      url='https://github.com/scragg0x/realms-wiki',
      license='GPLv2',
      include_package_data=True,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      platforms=['any'],
      classifiers=CLASSIFIERS)
