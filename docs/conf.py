# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys, os

sys.path.append(os.path.abspath('..'))

from pelican import __version__, __major__

# -- General configuration -----------------------------------------------------
templates_path = ['_templates']
extensions = ['sphinx.ext.autodoc',]
source_suffix = '.rst'
master_doc = 'index'
project = 'Pelican'
copyright = '2010, Alexis Metaireau and contributors'
exclude_patterns = ['_build']
version = __version__
release = __major__

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
