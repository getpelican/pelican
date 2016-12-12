# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys

from pelican import __version__

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

sys.path.append(os.path.abspath(os.pardir))

# -- General configuration ----------------------------------------------------
templates_path = ['_templates']
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.ifconfig',
              'sphinx.ext.extlinks']
source_suffix = '.rst'
master_doc = 'index'
project = 'Pelican'
copyright = '2015, Alexis Metaireau and contributors'
exclude_patterns = ['_build']
release = __version__
version = '.'.join(release.split('.')[:1])
last_stable = '3.7.0'
rst_prolog = '''
.. |last_stable| replace:: :pelican-doc:`{0}`
'''.format(last_stable)

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

extlinks = {
    'pelican-doc':  ('http://docs.getpelican.com/%s/', '')
}

# -- Options for HTML output --------------------------------------------------

html_theme = 'default'
if not on_rtd:
    try:
        import sphinx_rtd_theme
        html_theme = 'sphinx_rtd_theme'
        html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
    except ImportError:
        pass

html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'Pelicandoc'

html_use_smartypants = True

# If false, no module index is generated.
html_use_modindex = False

# If false, no index is generated.
html_use_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False


def setup(app):
    # overrides for wide tables in RTD theme
    app.add_stylesheet('theme_overrides.css')   # path relative to _static


# -- Options for LaTeX output -------------------------------------------------
latex_documents = [
    ('index', 'Pelican.tex', 'Pelican Documentation', 'Alexis Métaireau',
     'manual'),
]

# -- Options for manual page output -------------------------------------------
man_pages = [
    ('index', 'pelican', 'pelican documentation',
     ['Alexis Métaireau'], 1),
    ('pelican-themes', 'pelican-themes', 'A theme manager for Pelican',
     ['Mickaël Raybaud'], 1),
    ('themes', 'pelican-theming', 'How to create themes for Pelican',
     ['The Pelican contributors'], 1)
]
