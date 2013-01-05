import os
import functools
import logging

import six

from pelican.utils import (slugify, python_2_unicode_compatible)

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
@functools.total_ordering
class URLWrapper(object):
    def __init__(self, name, settings):
        self.name = name
        self.slug = slugify(self.name)
        self.settings = settings

    def as_dict(self):
        return self.__dict__

    def __hash__(self):
        return hash(self.name)

    def _key(self):
        return self.name

    def _normalize_key(self, key):
        return six.text_type(key)

    def __eq__(self, other):
        return self._key() == self._normalize_key(other)

    def __ne__(self, other):
        return self._key() != self._normalize_key(other)

    def __lt__(self, other):
        return self._key() < self._normalize_key(other)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{} {}>'.format(type(self).__name__, str(self))

    def _from_settings(self, key, get_page_name=False):
        """Returns URL information as defined in settings.

        When get_page_name=True returns URL without anything after {slug} e.g.
        if in settings: CATEGORY_URL="cat/{slug}.html" this returns
        "cat/{slug}" Useful for pagination.

        """
        setting = "%s_%s" % (self.__class__.__name__.upper(), key)
        value = self.settings[setting]
        if not isinstance(value, six.string_types):
            logger.warning('%s is set to %s' % (setting, value))
            return value
        else:
            if get_page_name:
                return os.path.splitext(value)[0].format(**self.as_dict())
            else:
                return value.format(**self.as_dict())

    page_name = property(functools.partial(_from_settings, key='URL',
                         get_page_name=True))
    url = property(functools.partial(_from_settings, key='URL'))
    save_as = property(functools.partial(_from_settings, key='SAVE_AS'))


class Category(URLWrapper):
    pass


class Tag(URLWrapper):
    def __init__(self, name, *args, **kwargs):
        super(Tag, self).__init__(name.strip(), *args, **kwargs)


class Author(URLWrapper):
    pass
