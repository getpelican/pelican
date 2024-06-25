import datetime
import os
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


sys.path.append(os.path.abspath(os.pardir))


with open("../pyproject.toml", "rb") as f:
    project_data = tomllib.load(f).get("project")
    if project_data is None:
        raise KeyError("project data is not found")


# -- General configuration ----------------------------------------------------
templates_path = ["_templates"]
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinxext.opengraph",
]
source_suffix = ".rst"
master_doc = "index"
project = project_data.get("name").upper()
year = datetime.datetime.now().date().year
copyright = f"2010–{year}"  # noqa: RUF001
exclude_patterns = ["_build"]
release = project_data.get("version")
version = ".".join(release.split(".")[:1])
last_stable = project_data.get("version")
rst_prolog = f"""
.. |last_stable| replace:: :pelican-doc:`{last_stable}`
.. |min_python| replace:: {project_data.get('requires-python').split(",")[0]}
"""

extlinks = {"pelican-doc": ("https://docs.getpelican.com/en/latest/%s.html", "%s")}

# -- Options for HTML output --------------------------------------------------

html_theme = "furo"
html_title = f"<strong>{project}</strong> <i>{release}</i>"
html_static_path = ["_static"]
html_theme_options = {
    "light_logo": "pelican-logo.svg",
    "dark_logo": "pelican-logo.svg",
    "navigation_with_keys": True,
}

# Output file base name for HTML help builder.
htmlhelp_basename = "Pelicandoc"

html_use_smartypants = True

# If false, no module index is generated.
html_use_modindex = False

# If false, no index is generated.
html_use_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False


def setup(app):
    # overrides for wide tables in RTD theme
    app.add_css_file("theme_overrides.css")  # path relative to _static


# -- Options for LaTeX output -------------------------------------------------
latex_documents = [
    ("index", "Pelican.tex", "Pelican Documentation", "Justin Mayer", "manual"),
]

# -- Options for manual page output -------------------------------------------
man_pages = [
    ("index", "pelican", "pelican documentation", ["Justin Mayer"], 1),
    (
        "pelican-themes",
        "pelican-themes",
        "A theme manager for Pelican",
        ["Mickaël Raybaud"],
        1,
    ),
    (
        "themes",
        "pelican-theming",
        "How to create themes for Pelican",
        ["The Pelican contributors"],
        1,
    ),
]
