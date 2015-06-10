from __future__ import unicode_literals

import hashlib
import logging
import os
try:
    import cPickle as pickle
except:
    import pickle

#TODO don't load pelican module, maybe have to move version definition
import pelican
from pelican.settings import settings_check_equal
from pelican.utils import mkdir_p


logger = logging.getLogger(__name__)


class FileDataCacher(object):
    """Class that can cache data contained in files"""

    def __init__(self, settings, cache_name, caching_policy, load_policy):
        """Load the specified cache within CACHE_PATH in settings

        only if *load_policy* is True,
        May use gzip if GZIP_CACHE ins settings is True.
        Sets caching policy according to *caching_policy*.
        """
        self.settings = settings
        self._cache = {}
        self._cache_path = os.path.join(self.settings['CACHE_PATH'],
                                        cache_name)
        self._cache_data_policy = caching_policy
        if self.settings['GZIP_CACHE']:
            import gzip
            self._cache_open = gzip.open
        else:
            self._cache_open = open
        if load_policy:
            try:
                self._load_cache()
            except (IOError, OSError) as err:
                logger.debug('Cannot load cache %s (this is normal on first '
                    'run). Proceeding with empty cache.\n%s',
                        self._cache_path, err)
            except pickle.PickleError as err:
                logger.warning(('Cannot unpickle cache %s, cache may be using '
                    'an incompatible protocol (see pelican caching docs). '
                    'Proceeding with empty cache.\n%s'),
                        self._cache_path, err)

    def _load_cache(self):
        '''tries loading the cache'''
        with self._cache_open(self._cache_path, 'rb') as fhandle:
            cache = pickle.load(fhandle)
            if not cache.get('__version__') == pelican.__version__:
                logger.debug('Pelican version changed. Proceeding with empty cache')
                return
            if not settings_check_equal(cache.get('__settings__'), self.settings):
                logger.debug('Settings changed. Proceeding with empty cache')
                return

            logger.debug('cache accepted')
            self._cache = cache
            return

    def cache_data(self, filename, data):
        """Cache data for given file"""
        if self._cache_data_policy:
            self._cache[filename] = data

    def get_cached_data(self, filename, default=None):
        """Get cached data for the given file

        if no data is cached, return the default object
        """
        return self._cache.get(filename, default)

    def _add_validation_data(self):
        self._cache['__version__'] = pelican.__version__
        self._cache['__settings__'] = self.settings

    def save_cache(self):
        """Save the updated cache"""
        if self._cache_data_policy:
            self._add_validation_data()
            try:
                mkdir_p(self.settings['CACHE_PATH'])
                with self._cache_open(self._cache_path, 'wb') as fhandle:
                    pickle.dump(self._cache, fhandle)
            except (IOError, OSError, pickle.PicklingError) as err:
                logger.warning('Could not save cache %s\n ... %s',
                               self._cache_path, err)


class FileStampDataCacher(FileDataCacher):
    """Subclass that also caches the stamp of the file"""

    def __init__(self, settings, cache_name, caching_policy, load_policy):
        """This sublcass additionally sets filestamp function
        and base path for filestamping operations
        """
        super(FileStampDataCacher, self).__init__(settings, cache_name,
                                                  caching_policy,
                                                  load_policy)

        method = self.settings['CHECK_MODIFIED_METHOD']
        if method == 'mtime':
            self._filestamp_func = os.path.getmtime
        else:
            try:
                hash_func = getattr(hashlib, method)

                def filestamp_func(filename):
                    """return hash of file contents"""
                    with open(filename, 'rb') as fhandle:
                        return hash_func(fhandle.read()).digest()

                self._filestamp_func = filestamp_func
            except AttributeError as err:
                logger.warning('Could not get hashing function\n\t%s', err)
                self._filestamp_func = None

    def cache_data(self, filename, data):
        """Cache stamp and data for the given file"""
        stamp = self._get_file_stamp(filename)
        super(FileStampDataCacher, self).cache_data(filename, (stamp, data))

    def _get_file_stamp(self, filename):
        """Check if the given file has been modified
        since the previous build.

        depending on CHECK_MODIFIED_METHOD
        a float may be returned for 'mtime',
        a hash for a function name in the hashlib module
        or an empty bytes string otherwise
        """
        try:
            return self._filestamp_func(filename)
        except (IOError, OSError, TypeError) as err:
            logger.warning(
                'Cannot get modification stamp for %s\n\t%s',
                filename, err)
            return ''

    def get_cached_data(self, filename, default=None):
        """Get the cached data for the given filename
        if the file has not been modified.

        If no record exists or file has been modified, return default.
        Modification is checked by comparing the cached
        and current file stamp.
        """
        stamp, data = super(FileStampDataCacher, self).get_cached_data(
            filename, (None, default))
        if stamp != self._get_file_stamp(filename):
            return default
        return data
