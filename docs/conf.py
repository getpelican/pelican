# -*- coding: utf-8 -*-
import sys, os

# -- General configuration -----------------------------------------------------
templates_path = ['_templates']
extensions = ['sphinx.ext.autodoc',]
source_suffix = '.rst'
master_doc = 'index'
project = u'Pelican'
copyright = u'2010, Alexis Metaireau and contributors'
exclude_patterns = ['_build']
version = "2"
release = version

# -- Options for HTML output ---------------------------------------------------

sys.path.append(os.path.abspath('_themes'))
html_theme_path = ['_themes']
html_theme = 'pelican'

html_theme_options = {
    'nosidebar': True,
    'index_logo': 'pelican.png',
    'github_fork': 'ametaireau/pelican',
}

html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'Pelicandoc'

# -- Options for LaTeX output --------------------------------------------------
latex_documents = [
  ('index', 'Pelican.tex', u'Pelican Documentation',
   u'Alexis Métaireau', 'manual'),
]

# -- Options for manual page output --------------------------------------------
man_pages = [
    ('index', 'pelican', u'pelican documentation',
     [u'Alexis Métaireau'], 1),
    ('pelican-themes', 'pelican-themes', u'A theme manager for Pelican',
     [u'Mickaël Raybaud'], 'en.1'),
    ('fr/pelican-themes', 'pelican-themes', u'Un gestionnaire de thèmes pour Pelican',
     [u'Mickaël Raybaud'], 'fr.1')
]
