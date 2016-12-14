#!/usr/bin/env python
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

README = open('README.rst').read()
CHANGELOG = open('docs/changelog.rst').read()

setup(
    name='pelican',
    version='3.7.1.dev0',
    url='http://getpelican.com/',
    author='Alexis Metaireau',
    maintainer='Justin Mayer',
    author_email='authors@getpelican.com',
    description="Static site generator supporting reStructuredText and "
                "Markdown source content.",
    long_description=README + '\n' + CHANGELOG,
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
         'License :: OSI Approved :: GNU Affero General Public License v3',
         'Operating System :: OS Independent',
         'Programming Language :: Python :: 2',
         'Programming Language :: Python :: 2.7',
         'Programming Language :: Python :: 3',
         'Programming Language :: Python :: 3.3',
         'Programming Language :: Python :: 3.4',
         'Programming Language :: Python :: 3.5',
         'Topic :: Internet :: WWW/HTTP',
         'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='pelican.tests',
)
