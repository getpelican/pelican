#!/usr/bin/env python
import sys
from io import open
from os import walk
from os.path import join, relpath

from setuptools import setup

requires = ['feedgenerator >= 1.9', 'jinja2 >= 2.7', 'pygments', 'docutils',
            'pytz >= 0a', 'blinker', 'unidecode', 'six >= 1.4',
            'python-dateutil']

entry_points = {
    'console_scripts': [
        'pelican = pelican:main',
        'pelican-import = pelican.tools.pelican_import:main',
        'pelican-quickstart = pelican.tools.pelican_quickstart:main',
        'pelican-themes = pelican.tools.pelican_themes:main'
    ]
}

README = open('README.rst', encoding='utf-8').read()
CHANGELOG = open('docs/changelog.rst', encoding='utf-8').read()

description = u'\n'.join([README, CHANGELOG])
if sys.version_info.major < 3:
    description = description.encode('utf-8')

setup(
    name='pelican',
    version='3.7.2.dev0',
    url='https://getpelican.com/',
    author='Alexis Metaireau',
    maintainer='Justin Mayer',
    author_email='authors@getpelican.com',
    description="Static site generator supporting reStructuredText and "
                "Markdown source content.",
    license='AGPLv3',
    long_description=description,
    packages=['pelican', 'pelican.tools'],
    package_data={
        # we manually collect the package data, as opposed to using,
        # include_package_data=True because we don't want the tests to be
        # included automatically as package data (MANIFEST.in is too greedy)
        'pelican': [relpath(join(root, name), 'pelican')
                    for root, _, names in walk(join('pelican', 'themes'))
                    for name in names],
        'pelican.tools': [relpath(join(root, name), join('pelican', 'tools'))
                          for root, _, names in walk(join('pelican',
                                                          'tools',
                                                          'templates'))
                          for name in names],
    },
    install_requires=requires,
    entry_points=entry_points,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Framework :: Pelican',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='pelican.tests',
)
