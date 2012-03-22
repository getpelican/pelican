import sys

from setuptools import setup

requires = ['feedgenerator', 'Jinja2', 'Pygments', 'docutils', 'pytz']

tests_require = ['mock', 'nose']

if sys.version < '2.7':
    tests_require.append('unittest2')

entry_points = {
    'console_scripts': [
        'pelican = pelican:main',
        'pelican-import = pelican.tools.pelican_import:main',
        'pelican-quickstart = pelican.tools.pelican_quickstart:main',
        'pelican-themes = pelican.tools.pelican_themes:main'
   ]
}

setup(
    name = "pelican",
    version = "3.0",
    url = 'http://pelican.notmyidea.org/',
    author = 'Alexis Metaireau',
    author_email = 'alexis@notmyidea.org',
    description = "A tool to generate a static blog from reStructuredText or Markdown input files.",
    long_description=open('README.rst').read(),
    packages = ['pelican', 'pelican.tools'],
    include_package_data = True,
    install_requires = requires,
    tests_require = tests_require,
    test_suite = 'nose.collector',
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
