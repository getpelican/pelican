# -*- coding: utf-8 -*-
"""
    Article Thumbnail Plugin for Pelican
    =======================================

    Will Hart [github: @will-hart]

    A plugin to generate thumbnail image for an article provided
    in the article's meta data. Requires Python Imaging Library (PIL)
    which you can get by typing ``pip install pil`` into the command
    line.

    You may also want to have a look around for PIL installation
    instructions as its not always simple... for instance
    ``http://jj.isgeek.net/2011/09/install-pil-with-jpeg-support-on-ubuntu-oneiric-64bits/``_

    Settings
    -----------

    To enable, add

        from pelican.plugins import article_thumbnail
        PLUGINS = [article_thumbnail]

    to your settings.py.  You can optionally customise the thumbnails in
    your settings file.  The settings and their defaults are shown below::

        THUMBNAIL_PATH = 'static/thumbs'
        THUMBNAIL_WIDTH = 100
        THUMBNAIL_HEIGHT = 100
        THUMBNAIL_PREFIX = 'thumb_'
        THUMBNAIL_DEFAULT = 'images/thumb_default.png'

    ``THUMBNAIL_DEFAULT`` is used if no thumbnail path is provided
    in the metadata.  No default image is provided - this is up to you!

    Usage
    ---------

    In your article metadata you will need (rst example)::

        :thumbnail: imagename.png

    The image path should be relative to the 'content' directory.

    To use the thumbnail in a template::

        {% if article.has_thumb %}
        <img src="{{article.thumbnail_url}}">
        {% endif %}

"""

from pelican import signals
from pelican import settings

import Image
import logging
import os
import shutil

# set up logging
logger = logging.getLogger(__name__)


def generate_thumbnail_settings(pelican):
    """
    parse the settings or use defaults
    """
    if 'THUMBNAIL_PATH' not in pelican.settings:
        pelican.settings['THUMBNAIL_PATH'] = 'static/thumbs'
    if 'THUMBNAIL_WIDTH' not in pelican.settings:
        pelican.settings['THUMBNAIL_WIDTH'] = 100
    if 'THUMBNAIL_HEIGHT' not in pelican.settings:
        pelican.settings['THUMBNAIL_HEIGHT'] = 100
    if 'THUMBNAIL_PREFIX' not in pelican.settings:
        pelican.settings['THUMBNAIL_PREFIX'] = 'thumb_'
    if 'THUMBNAIL_DEFAULT' not in pelican.settings:
        pelican.settings['THUMBNAIL_DEFAULT'] = 'images/thumb_default.png'

    pelican.settings['THUMBNAIL_DEFAULT_PATH'] = os.path.abspath(
        os.path.join('content', pelican.settings['THUMBNAIL_DEFAULT']))

    pelican.settings['THUMBNAIL_DEFAULT_FILE'] = os.path.split(
        pelican.settings['THUMBNAIL_DEFAULT'])[-1]

    # create the 'output/{{thumbs_path}}' directory
    output_dir = os.path.join('output', pelican.settings['THUMBNAIL_PATH'])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # copy the default file to the output directory
    # only copy if the thumbnail exists.
    if os.path.exists(pelican.settings['THUMBNAIL_DEFAULT_PATH']):
        shutil.copy(pelican.settings['THUMBNAIL_DEFAULT_PATH'], output_dir)
    else:
        logger.warning(u'Could not find default thumbnail at %s' %
            pelican.settings['THUMBNAIL_DEFAULT_PATH'])


def generate_article_thumb(generator, metadata):
    """
    Generates a thumbnail for the given article if a thumbnail
    path is given
    """
    if 'thumbnail' not in metadata:
        # no thumbnail given, set default
        metadata['thumbnail_url'] = os.path.join(
            generator.settings['SITEURL'],
            generator.settings['THUMBNAIL_PATH'],
            generator.settings['THUMBNAIL_DEFAULT_FILE']
        )
        metadata['has_thumb'] = False

    else:
        # get the output path
        image_name = os.path.split(metadata['thumbnail'])[-1]
        out_path = os.path.abspath(os.path.join(
            'output',
            generator.settings['THUMBNAIL_PATH'],
            generator.settings['THUMBNAIL_PREFIX'] + image_name
        ))

        # generate the thumbnail
        im = Image.open(os.path.join('content', metadata['thumbnail']))
        im.thumbnail(
            (generator.settings['THUMBNAIL_WIDTH'],
                generator.settings['THUMBNAIL_HEIGHT']),
            Image.ANTIALIAS
        )
        im.save(out_path)

        # set the metadata
        metadata['thumbnail_url'] = os.path.join(
            generator.settings['SITEURL'],
            generator.settings['THUMBNAIL_PATH'],
            generator.settings['THUMBNAIL_PREFIX'] + image_name
        )
        metadata['has_thumb'] = True


def register():
    """
    Register the plugin
    """
    signals.initialized.connect(generate_thumbnail_settings)
    signals.article_generate_context.connect(generate_article_thumb)
