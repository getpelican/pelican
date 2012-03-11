#!/usr/bin/env python
import os
from setuptools import setup

VERSION = "3.0" # find a better way to do so.

requires = ['feedgenerator', 'jinja2', 'pygments', 'docutils', 'pytz']

try:
    import argparse
except ImportError:
    requires.append('argparse')

entry_points = {
    'console_scripts': [
        'pelican = pelican:main',
        'pelican-import = pelican.tools.pelican_import:main',
        'pelican-quickstart = pelican.tools.pelican_quickstart:main',
        'pelican-themes = pelican.tools.pelican_themes:main'
   ]     
}

def find_packages(toplevel):
    return [directory.replace(os.path.sep, '.') for directory, subdirs, files in os.walk(toplevel) if '__init__.py' in files]

setup(
    name = "pelican",
    version = VERSION,
    url = 'http://pelican.notmyidea.org/',
    author = 'Alexis Metaireau',
    author_email = 'alexis@notmyidea.org',
    description = "A tool to generate a static blog from reStructuredText or Markdown input files.",
    long_description=open('README.rst').read(),
    packages = find_packages('pelican'),
    include_package_data = True,
    install_requires = requires,
    entry_points = entry_points,
    classifiers = ['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'License :: OSI Approved :: GNU Affero General Public License v3',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   ],
)
