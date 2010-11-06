from setuptools import setup
import sys

requires = ['feedgenerator', 'jinja2', 'pygments', 'docutils', 'Markdown',
            'rst2pdf']
if sys.version_info < (2,7):
    requires.append('argparse')

setup(
    name = "pelican",
    version = '2.4.2',
    url = 'http://alexis.notmyidea.org/pelican/',
    author = 'Alexis Metaireau',
    author_email = 'alexis@notmyidea.org',
    description = "A tool to generate a static blog, with restructured text (or markdown) input files.",
    long_description=open('README.rst').read(),
    packages = ['pelican'],
    include_package_data = True,
    install_requires = requires, 
    scripts = ['bin/pelican'],
    classifiers = ['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'License :: OSI Approved :: GNU Affero General Public License v3',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   ],
)
