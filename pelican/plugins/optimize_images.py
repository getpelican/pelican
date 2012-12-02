# -*- coding: utf-8 -*-

"""
Optimized images (jpg and png)
Assumes that jpegtran and optipng are isntalled on path.
http://jpegclub.org/jpegtran/
http://optipng.sourceforge.net/
Copyright (c) 2012 Irfan Ahmad (http://i.com.pk)
"""

import logging
import os
from subprocess import call

from pelican import signals

logger = logging.getLogger(__name__)

# A list of file types with their respective commands
COMMANDS = [
    ('.jpg', 'jpegtran -copy none -optimize "{0}" "{0}"'),
    ('.png', 'optipng "{0}"'),
]

def optimize_images(pelican):
    """
    Optimized jpg and png images

    :param pelican: The Pelican instance
    """
    for dirpath, _, filenames in os.walk(pelican.settings['OUTPUT_PATH']):
        for name in filenames:
            optimize(dirpath, name)

def optimize(dirpath, filename):
    """
    Check if the name is a type of file that should be optimized.
    And optimizes it if required.

    :param dirpath: Path of the file to be optimzed
    :param name: A file name to be optimized
    """
    for extension, command in COMMANDS:
        if filename.endswith(extension):
            filepath = os.path.join(dirpath, filename)
            command = command.format(filepath)
            call( command )


def register():
    signals.finalized.connect(optimize_images)

