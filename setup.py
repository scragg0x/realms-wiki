from setuptools import setup, find_packages
import os

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
      install_requires=[
          'Flask==0.10.1',
          'Flask-Assets==0.10',
          'Flask-Cache==0.13.1',
          'Flask-Elastic==0.2',
          'Flask-Login==0.2.11',
          'Flask-OAuthlib==0.9.1',
          'Flask-SQLAlchemy==2.0',
          'Flask-WTF==0.10.2',
          'PyYAML==3.11',
          'bcrypt==1.0.2',
          'beautifulsoup4==4.3.2',
          'click==3.3',
          'flask-ldap-login==0.3.0',
          'gevent==1.0.2',
          'ghdiff==0.4',
          'gittle==0.5.0',
          'gunicorn==19.3',
          'itsdangerous==0.24',
          'markdown2==2.3.0',
          'python-ldap==2.4.22',
          'simplejson==3.6.3'
      ],
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
