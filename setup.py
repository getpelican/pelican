#!/usr/bin/env python
from setuptools import setup

execfile('version.py')

requires = ['feedgenerator', 'jinja2', 'pygments', 'docutils', 'pytz']

try:
    import argparse
except ImportError:
    requires.append('argparse')

entry_points = {
    'console_scripts': [
        'pelican = pelican:main',
        'pelican-import = tools.pelican_import:main',
        'pelican-quickstart = tools.pelican_quickstart:main',
        'pelican-themes = tools.pelican_themes:main'
   ]     
}

setup(
    name = "pelican",
    version = VERSION,
    url = 'http://pelican.notmyidea.org/',
    author = 'Alexis Metaireau',
    author_email = 'alexis@notmyidea.org',
    description = "A tool to generate a static blog from reStructuredText or Markdown input files.",
    long_description=open('README.rst').read(),
    packages = ['pelican'],
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
