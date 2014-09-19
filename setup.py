from setuptools import setup, find_packages

DESCRIPTION = "Simple git based wiki"

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

VERSION = '0.1.8'

CLASSIFIERS = [
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GPLv2 License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules']

setup(name='realms-wiki',
      version=VERSION,
      packages=find_packages(),
      install_requires=required,
      scripts=['realms-wiki'],
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