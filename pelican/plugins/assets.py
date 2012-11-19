# -*- coding: utf-8 -*-
"""
Asset management plugin for Pelican
===================================

This plugin allows you to use the `webassets`_ module to manage assets such as
CSS and JS files.

Hint for templates: Current version of webassets seems to remove any relative
paths at the beginning of the URL. So, if ``RELATIVE_URLS`` is on,
``ASSET_URL`` will start with ``theme/``, regardless if we set ``assets_url``
here to ``./theme/`` or to ``theme/``.

However, this breaks the ``ASSET_URL`` if user navigates to a sub-URL, e.g. if
he clicks on a category. A workaround for this issue is to use::

    <link rel="stylesheet" href="{{ SITEURL }}/{{ ASSET_URL }}">

instead of::

    <link rel="stylesheet" href="{{ ASSET_URL }}">

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

    logger = logging.getLogger(__name__)

    # Let ASSET_URL honor Pelican's RELATIVE_URLS setting.
    if generator.settings.get('RELATIVE_URLS'):
        assets_url = './theme/'
    else:
        assets_url = generator.settings['SITEURL'] + '/theme/'
    assets_src = os.path.join(generator.output_path, 'theme')

    generator.env.assets_environment = Environment(assets_src, assets_url)

    if logging.getLevelName(logger.getEffectiveLevel()) == "DEBUG":
        generator.env.assets_environment.debug = True


def register():
    """Plugin registration."""

    signals.initialized.connect(add_jinja2_ext)
    signals.generator_init.connect(create_assets_env)
