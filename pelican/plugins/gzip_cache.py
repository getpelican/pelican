# Copyright (c) 2012 Matt Layman
'''A plugin to create .gz cache files for optimization.'''

import gzip
import logging
import os

from pelican import signals

logger = logging.getLogger(__name__)

# A list of file types to exclude from possible compression
EXCLUDE_TYPES = [
    # Compressed types
    '.bz2',
    '.gz',

    # Audio types
    '.aac',
    '.flac',
    '.mp3',
    '.wma',

    # Image types
    '.gif',
    '.jpg',
    '.jpeg',
    '.png',

    # Video types
    '.avi',
    '.mov',
    '.mp4',
]

def create_gzip_cache(pelican):
    '''Create a gzip cache file for every file that a webserver would
    reasonably want to cache (e.g., text type files).

    :param pelican: The Pelican instance
    '''
    for dirpath, _, filenames in os.walk(pelican.settings['OUTPUT_PATH']):
        for name in filenames:
            if should_compress(name):
                filepath = os.path.join(dirpath, name)
                create_gzip_file(filepath)

def should_compress(filename):
    '''Check if the filename is a type of file that should be compressed.

    :param filename: A file name to check against
    '''
    for extension in EXCLUDE_TYPES:
        if filename.endswith(extension):
            return False

    return True

def create_gzip_file(filepath):
    '''Create a gzipped file in the same directory with a filepath.gz name.

    :param filepath: A file to compress
    '''
    compressed_path = filepath + '.gz'

    with open(filepath, 'rb') as uncompressed:
        try:
            logger.debug('Compressing: %s' % filepath)
            compressed = gzip.open(compressed_path, 'wb')
            compressed.writelines(uncompressed)
        except Exception, ex:
            logger.critical('Gzip compression failed: %s' % ex)
        finally:
            compressed.close()

def register():
    signals.finalized.connect(create_gzip_cache)

