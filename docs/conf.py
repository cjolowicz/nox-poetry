"""Sphinx configuration."""
project = "nox-poetry"
author = "Claudio Jolowicz"
copyright = "2020, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
]
autodoc_typehints = "description"
html_theme = "furo"
html_favicon = "images/favicon.png"
html_logo = "images/logo.png"
intersphinx_mapping = {
    "nox": ("https://nox.thea.codes/en/stable", None),
    "pip": ("https://pip.pypa.io/en/stable", None),
}
