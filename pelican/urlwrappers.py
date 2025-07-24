import functools
import logging
import os
import pathlib

from pelican.utils import slugify

logger = logging.getLogger(__name__)


@functools.total_ordering
class URLWrapper:
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
            class_key = f"{self.__class__.__name__.upper()}_REGEX_SUBSTITUTIONS"
            regex_subs = self.settings.get(
                class_key, self.settings.get("SLUG_REGEX_SUBSTITUTIONS", [])
            )
            preserve_case = self.settings.get("SLUGIFY_PRESERVE_CASE", False)
            self._slug = slugify(
                self.name,
                regex_subs=regex_subs,
                preserve_case=preserve_case,
                use_unicode=self.settings.get("SLUGIFY_USE_UNICODE", False),
            )
            if not self._slug:
                logger.warning(
                    'Unable to generate valid slug for %s "%s".',
                    self.__class__.__name__,
                    self.name,
                    extra={"limit_msg": "Other invalid slugs."},
                )
        return self._slug

    @slug.setter
    def slug(self, slug):
        # if slug is explicitly set, changing name won't alter slug
        self._slug_from_name = False
        self._slug = slug

    def as_dict(self):
        d = self.__dict__
        d["name"] = self.name
        d["slug"] = self.slug
        return d

    def __hash__(self):
        return hash(self.slug)

    def _normalize_key(self, key):
        class_key = f"{self.__class__.__name__.upper()}_REGEX_SUBSTITUTIONS"
        regex_subs = self.settings.get(
            class_key, self.settings.get("SLUG_REGEX_SUBSTITUTIONS", [])
        )
        use_unicode = self.settings.get("SLUGIFY_USE_UNICODE", False)
        preserve_case = self.settings.get("SLUGIFY_PRESERVE_CASE", False)
        return slugify(
            key,
            regex_subs=regex_subs,
            preserve_case=preserve_case,
            use_unicode=use_unicode,
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.slug == other.slug
        if isinstance(other, str):
            return self.slug == self._normalize_key(other)
        return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.slug != other.slug
        if isinstance(other, str):
            return self.slug != self._normalize_key(other)
        return True

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.slug < other.slug
        if isinstance(other, str):
            return self.slug < self._normalize_key(other)
        return False

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{type(self).__name__} {self._name!r}>"

    def _from_settings(self, key, get_page_name=False):
        """Returns URL information as defined in settings.

        When get_page_name=True returns URL without anything after {slug} e.g.
        if in settings: CATEGORY_URL="cat/{slug}.html" this returns
        "cat/{slug}" Useful for pagination.

        """
        setting = f"{self.__class__.__name__.upper()}_{key}"
        value = self.settings[setting]
        if isinstance(value, pathlib.Path):
            value = str(value)
        if not isinstance(value, str):
            logger.warning("%s is set to %s", setting, value)
            return value
        elif get_page_name:
            return os.path.splitext(value)[0].format(**self.as_dict())
        else:
            return value.format(**self.as_dict())

    page_name = property(
        functools.partial(_from_settings, key="URL", get_page_name=True)
    )
    url = property(functools.partial(_from_settings, key="URL"))
    save_as = property(functools.partial(_from_settings, key="SAVE_AS"))


class Category(URLWrapper):
    pass


class Tag(URLWrapper):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name.strip(), *args, **kwargs)


class Author(URLWrapper):
    pass
