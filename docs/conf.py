# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys, os

sys.path.append(os.path.abspath(os.pardir))

from pelican import __version__

# -- General configuration -----------------------------------------------------
templates_path = ['_templates']
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.ifconfig', 'sphinx.ext.extlinks']
source_suffix = '.rst'
master_doc = 'index'
project = 'Pelican'
copyright = '2014, Alexis Metaireau and contributors'
exclude_patterns = ['_build']
release = __version__
version = '.'.join(release.split('.')[:1])
last_stable = '3.3.0'
rst_prolog = '''
.. |last_stable| replace:: :pelican-doc:`{0}`
'''.format(last_stable)

extlinks = {
    'pelican-doc':  ('http://docs.getpelican.com/%s/', '')
}

# -- Options for HTML output ---------------------------------------------------

html_theme_path = ['_themes']
html_theme = 'pelican'

html_theme_options = {
    'nosidebar': True,
    'index_logo': 'pelican.png',
    'github_fork': 'getpelican/pelican',
}

html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'Pelicandoc'

# -- Options for LaTeX output --------------------------------------------------
latex_documents = [
  ('index', 'Pelican.tex', 'Pelican Documentation',
   'Alexis Métaireau', 'manual'),
]

# -- Options for manual page output --------------------------------------------
man_pages = [
    ('index', 'pelican', 'pelican documentation',
     ['Alexis Métaireau'], 1),
    ('pelican-themes', 'pelican-themes', 'A theme manager for Pelican',
     ['Mickaël Raybaud'], 1),
    ('themes', 'pelican-theming', 'How to create themes for Pelican',
     ['The Pelican contributors'], 1)
]
