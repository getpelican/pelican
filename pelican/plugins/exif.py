#coding=utf-8
"""
    Copyright (c) Jonathan Gonse <jonathan.gonse@gmail.com>

Photo blog plugin for Pelican
==========================

This plugin allows you to define an Album variable to the article's context,
making the photos in that folder and their exif info available to use from
within your theme's templates.

Settings:
---------

You do not need to add anything in your settings file.

Article metadata:
------------------

for rst file:

:album: pictures/lol

for markdown file:

Album: pictures/lol

Usage
-----
    in your template just write a for in jinja2 syntax against the
    article.pic_exif variable.

      {% if article.pic_exif %}

      <div id="album_container">
          <div id="slide_container">
              {% for fn in article.pic_exif %}
                  <img src="{{ fn }}">
                  <pre>
                      {% for exif_str in article.pic_exif[fn] %}
                      <li>{{ exif_str }}</li>
                      {% endfor %}
                  </pre>
              {% endfor %}
          </div>
      </div>
      {% endif %}
"""

import logging
import os
import lib_exif_py as exif
#get it from https://github.com/ianare/exif-py
from pelican import signals

logger = logging.getLogger(__name__)


def add_pic_info(generator, metadata):
    """
    Add a dict of file_path : file_exif_info to metadata['pic_exif']
    """

    if 'album' in metadata.keys():
        abspath = os.path.join(generator.path, metadata['album'])
        metadata['pic_paths'] = get_files(abspath)
        metadata['pic_exif'] = {}
        for filename in metadata['pic_paths']:
            file_path = os.path.join('static',
                                     metadata['album'],
                                     os.path.basename(filename))
            metadata['pic_exif'][file_path] = ""
            try:
                file = open(filename, 'rb')
            except:
                logger.debug("'%s' is unreadable\n" % filename)
                continue
            # get the tags
            data = exif.process_file(file)
            if not data:
                logger.debug('No EXIF information found')
                continue
            x = data.keys()
            x.sort()
            tmp_str = []
            for i in x:
                if i in ('JPEGThumbnail', 'TIFFThumbnail'):
                    continue
                try:
                    if i in ('Image Make',
                             'Image Model',
                             'Image Software',
                             'EXIF ApertureValue',
                             'EXIF DateTimeOriginal',
                             'EXIF DateTimeDigitized',
                             'EXIF ExposureTime',
                             'EXIF FNumber',
                             'EXIF ISOSpeedRatings',
                             'EXIF ExposureMode',
                             'EXIF ExposureBiasValue',
                             'EXIF Flash'):
                        i_strip = i.replace("EXIF ", "").replace("Image ", "")
                        logger.debug('%s: %s' %
                                     (i_strip, data[i].printable))
                        tmp_str.append(('%s: %s' %
                                        (i_strip, data[i].printable)))
                except:
                    logger.debug('error', i, '"', data[i], '"')
            file_path = os.path.join('static',
                                     metadata['album'],
                                     os.path.basename(filename))
            metadata['pic_exif'][file_path] = tmp_str
        logger.debug(metadata['pic_exif'])


def get_files(path):
    """Return a list of files to use, based on rules

    :param path: the path to search the file on
    :param exclude: the list of path to exclude
    """
    files = []

    try:
        iter = os.walk(path, followlinks=True)
    except TypeError:  # python 2.5 does not support followlinks
        iter = os.walk(path)

    for root, dirs, temp_files in iter:
        files.extend([os.sep.join((root, f)) for f in temp_files])
    return files


def register():
    signals.article_generate_context.connect(add_pic_info)
