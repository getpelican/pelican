# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import functools
import logging
import os
import six

from pelican.utils import (slugify, python_2_unicode_compatible)

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
@functools.total_ordering
class URLWrapper(object):
    def __init__(self, name, settings):
        self.settings = settings
        self._name = name
        self._slug = None
        self._slug_from_name = True

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        # if slug wasn't explicitly set, it needs to be regenerated from name
        # so, changing name should reset slug for slugification
        if self._slug_from_name:
            self._slug = None

    @property
    def slug(self):
        if self._slug is None:
            self._slug = slugify(self.name,
                                 self.settings.get('SLUG_SUBSTITUTIONS', ()))
        return self._slug

    @slug.setter
    def slug(self, slug):
        # if slug is expliticly set, changing name won't alter slug
        self._slug_from_name = False
        self._slug = slug

    def as_dict(self):
        d = self.__dict__
        d['name'] = self.name
        d['slug'] = self.slug
        return d

    def __hash__(self):
        return hash(self.slug)

    def _normalize_key(self, key):
        subs = self.settings.get('SLUG_SUBSTITUTIONS', ())
        return six.text_type(slugify(key, subs))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.slug == other.slug
        if isinstance(other, six.text_type):
            return self.slug == self._normalize_key(other)
        return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.slug != other.slug
        if isinstance(other, six.text_type):
            return self.slug != self._normalize_key(other)
        return True

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.slug < other.slug
        if isinstance(other, six.text_type):
            return self.slug < self._normalize_key(other)
        return False

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{} {}>'.format(type(self).__name__, repr(self._name))

    def _from_settings(self, key, get_page_name=False):
        """Returns URL information as defined in settings.

        When get_page_name=True returns URL without anything after {slug} e.g.
        if in settings: CATEGORY_URL="cat/{slug}.html" this returns
        "cat/{slug}" Useful for pagination.

        """
        setting = "%s_%s" % (self.__class__.__name__.upper(), key)
        value = self.settings[setting]
        if not isinstance(value, six.string_types):
            logger.warning('%s is set to %s', setting, value)
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
