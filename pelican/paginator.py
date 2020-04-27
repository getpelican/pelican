import functools
import logging
import os
from collections import namedtuple
from math import ceil

logger = logging.getLogger(__name__)
PaginationRule = namedtuple(
    'PaginationRule',
    'min_page URL SAVE_AS',
)


class Paginator:
    def __init__(self, name, url, object_list, settings, per_page=None):
        self.name = name
        self.url = url
        self.object_list = object_list
        self.settings = settings
        if per_page:
            self.per_page = per_page
            self.orphans = settings['DEFAULT_ORPHANS']
        else:
            self.per_page = len(object_list)
            self.orphans = 0

        self._num_pages = self._count = None

    def page(self, number):
        "Returns a Page object for the given 1-based page number."
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return Page(self.name, self.url, self.object_list[bottom:top], number,
                    self, self.settings)

    def _get_count(self):
        "Returns the total number of objects, across all pages."
        if self._count is None:
            self._count = len(self.object_list)
        return self._count
    count = property(_get_count)

    def _get_num_pages(self):
        "Returns the total number of pages."
        if self._num_pages is None:
            hits = max(1, self.count - self.orphans)
            self._num_pages = int(ceil(hits / (float(self.per_page) or 1)))
        return self._num_pages
    num_pages = property(_get_num_pages)

    def _get_page_range(self):
        """
        Returns a 1-based range of pages for iterating through within
        a template for loop.
        """
        return list(range(1, self.num_pages + 1))
    page_range = property(_get_page_range)


class Page:
    def __init__(self, name, url, object_list, number, paginator, settings):
        self.full_name = name
        self.name, self.extension = os.path.splitext(name)
        dn, fn = os.path.split(name)
        self.base_name = dn if fn in ('index.htm', 'index.html') else self.name
        self.base_url = url
        self.object_list = object_list
        self.number = number
        self.paginator = paginator
        self.settings = settings

    def __repr__(self):
        return '<Page {} of {}>'.format(self.number, self.paginator.num_pages)

    def has_next(self):
        return self.number < self.paginator.num_pages

    def has_previous(self):
        return self.number > 1

    def has_other_pages(self):
        return self.has_previous() or self.has_next()

    def next_page_number(self):
        return self.number + 1

    def previous_page_number(self):
        return self.number - 1

    def start_index(self):
        """
        Returns the 1-based index of the first object on this page,
        relative to total objects in the paginator.
        """
        # Special case, return zero if no items.
        if self.paginator.count == 0:
            return 0
        return (self.paginator.per_page * (self.number - 1)) + 1

    def end_index(self):
        """
        Returns the 1-based index of the last object on this page,
        relative to total objects found (hits).
        """
        # Special case for the last page because there can be orphans.
        if self.number == self.paginator.num_pages:
            return self.paginator.count
        return self.number * self.paginator.per_page

    def _from_settings(self, key):
        """Returns URL information as defined in settings. Similar to
        URLWrapper._from_settings, but specialized to deal with pagination
        logic."""

        rule = None

        # find the last matching pagination rule
        for p in self.settings['PAGINATION_PATTERNS']:
            if p.min_page <= self.number:
                rule = p

        if not rule:
            return ''

        prop_value = getattr(rule, key)

        if not isinstance(prop_value, str):
            logger.warning('%s is set to %s', key, prop_value)
            return prop_value

        # URL or SAVE_AS is a string, format it with a controlled context
        context = {
            'save_as': self.full_name,
            'url': self.base_url,
            'name': self.name,
            'base_name': self.base_name,
            'extension': self.extension,
            'number': self.number,
        }

        ret = prop_value.format(**context)
        # Remove a single leading slash, if any. This is done for backwards
        # compatibility reasons. If a leading slash is needed (for URLs
        # relative to server root or absolute URLs without the scheme such as
        # //blog.my.site/), it can be worked around by prefixing the pagination
        # pattern by an additional slash (which then gets removed, preserving
        # the other slashes). This also means the following code *can't* be
        # changed to lstrip() because that would remove all leading slashes and
        # thus make the workaround impossible. See
        # test_custom_pagination_pattern() for a verification of this.
        if ret[0] == '/':
            ret = ret[1:]
        return ret

    url = property(functools.partial(_from_settings, key='URL'))
    save_as = property(functools.partial(_from_settings, key='SAVE_AS'))
