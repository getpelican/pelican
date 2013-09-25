import os.path
import hashlib
import pickle
import logging

logger = logging.getLogger(__name__)


class CachedReader(object):

    def __init__(self, reader, cache_path):
        self._reader = reader
        self._cache_path = cache_path

    def process_metadata(self, *args, **kwargs):
        return self._reader.process_metadata(*args, **kwargs)

    def read(self, path):
        mtime = os.stat(path).st_mtime

        m = hashlib.md5()
        # We want to hash path + mtime
        m.update(path)
        m.update(str(mtime))
        hash_ = m.hexdigest()

        cache_file = os.path.join(self._cache_path, hash_)
        if os.path.exists(cache_file):
            logger.debug('reading {0} from cache'.format(path))
            with open(cache_file) as f:
                content, metadata = pickle.load(f)
        else:
            content, metadata = self._reader.read(path)
            with open(cache_file, 'w+') as f:
                pickle.dump((content, metadata), f)
            logger.debug('stored {0} in the cache'.format(path))
        return content, metadata
