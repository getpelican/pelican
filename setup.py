#!/usr/bin/env python
from setuptools import setup

requires = ['feedgenerator', 'jinja2 >= 2.6', 'pygments', 'docutils', 'pytz',
            'blinker', 'unidecode']

try:
    import argparse  # NOQA
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


README = open('README.rst').read()
CHANGELOG = open('docs/changelog.rst').read()


setup(
    name="pelican",
    version="3.2",
    url='http://getpelican.com/',
    author='Alexis Metaireau',
    author_email='authors@getpelican.com',
    description="A tool to generate a static blog from reStructuredText or "
                "Markdown input files.",
    long_description=README + '\n' + CHANGELOG,
    packages=['pelican', 'pelican.tools', 'pelican.plugins'],
    include_package_data=True,
    install_requires=requires,
    entry_points=entry_points,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
         'Environment :: Console',
         'License :: OSI Approved :: GNU Affero General Public License v3',
         'Operating System :: OS Independent',
         'Programming Language :: Python :: 2.6',
         'Programming Language :: Python :: 2.7',
         'Topic :: Internet :: WWW/HTTP',
         'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='tests',
)
