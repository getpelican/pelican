# -*- coding: utf-8 -*-
"""
Asset management plugin for Pelican
===================================

This plugin allows you to use the `webassets`_ module to manage assets such as
CSS and JS files.

The ASSET_URL is set to a relative url to honor Pelican's RELATIVE_URLS
setting. This requires the use of SITEURL in the templates::

    <link rel="stylesheet" href="{{ SITEURL }}/{{ ASSET_URL }}">

.. _webassets: https://webassets.readthedocs.org/

"""

import os
import logging

from pelican import signals
from webassets import Environment
from webassets.ext.jinja2 import AssetsExtension


def add_jinja2_ext(pelican):
    """Add Webassets to Jinja2 extensions in Pelican settings."""

    pelican.settings['JINJA_EXTENSIONS'].append(AssetsExtension)


def create_assets_env(generator):
    """Define the assets environment and pass it to the generator."""

    assets_url = 'theme/'
    assets_src = os.path.join(generator.output_path, 'theme')
    generator.env.assets_environment = Environment(assets_src, assets_url)

    logger = logging.getLogger(__name__)
    if logging.getLevelName(logger.getEffectiveLevel()) == "DEBUG":
        generator.env.assets_environment.debug = True


def register():
    """Plugin registration."""

    signals.initialized.connect(add_jinja2_ext)
    signals.generator_init.connect(create_assets_env)
