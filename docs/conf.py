import datetime
import os
import sys

from pelican import __version__

sys.path.append(os.path.abspath(os.pardir))

# -- General configuration ----------------------------------------------------
templates_path = ['_templates']
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.ifconfig",
    "sphinx.ext.extlinks",
    "sphinxext.opengraph",
]
source_suffix = '.rst'
master_doc = 'index'
project = 'Pelican'
year = datetime.datetime.now().date().year
copyright = f'2010–{year}'
exclude_patterns = ['_build']
release = __version__
version = '.'.join(release.split('.')[:1])
last_stable = __version__
rst_prolog = '''
.. |last_stable| replace:: :pelican-doc:`{}`
'''.format(last_stable)

extlinks = {
    'pelican-doc':  ('https://docs.getpelican.com/en/latest/%s.html', '%s')
}

# -- Options for HTML output --------------------------------------------------

html_theme = 'furo'
html_title = f'<strong>{project}</strong> <i>{release}</i>'
html_static_path = ['_static']
html_theme_options = {
    'light_logo': 'pelican-logo.svg',
    'dark_logo': 'pelican-logo.svg',
    'navigation_with_keys': True,
}

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
    app.add_css_file('theme_overrides.css')   # path relative to _static


# -- Options for LaTeX output -------------------------------------------------
latex_documents = [
    ('index', 'Pelican.tex', 'Pelican Documentation', 'Justin Mayer',
     'manual'),
]

# -- Options for manual page output -------------------------------------------
man_pages = [
    ('index', 'pelican', 'pelican documentation',
     ['Justin Mayer'], 1),
    ('pelican-themes', 'pelican-themes', 'A theme manager for Pelican',
     ['Mickaël Raybaud'], 1),
    ('themes', 'pelican-theming', 'How to create themes for Pelican',
     ['The Pelican contributors'], 1)
]
