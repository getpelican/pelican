__author__ = 'flaviocaetano'

import os
import gettext
import pprint

from pelican import signals

class Translations(gettext.GNUTranslations, object):
    """Class taken from Babel and adapted to Pelican.

    An extended translation catalog class."""

    DEFAULT_DOMAIN = 'messages'

    def __init__(self, fileobj=None, domain=DEFAULT_DOMAIN):
        """Initialize the translations catalog.

        :param fileobj: the file-like object the translation should be read
                        from
        """
        gettext.GNUTranslations.__init__(self, fp=fileobj)
        self.files = filter(None, [getattr(fileobj, 'name', None)])
        self.domain = domain
        self._domains = {}

    def load(cls, dirname=None, locales=None, domain=DEFAULT_DOMAIN):
        """Load translations from the given directory.

        :param dirname: the directory containing the ``MO`` files
        :param locales: the list of locales in order of preference (items in
                        this list can be either `Locale` objects or locale
                        strings)
        :param domain: the message domain
        :return: the loaded catalog, or a ``NullTranslations`` instance if no
                 matching translations were found
        :rtype: `Translations`
        """
        if locales is not None:
            if not isinstance(locales, (list, tuple)):
                locales = [locales]
            locales = [str(locale) for locale in locales]
        if not domain:
            domain = cls.DEFAULT_DOMAIN
        filename = gettext.find(domain, dirname, locales)
        if not filename:
            return gettext.NullTranslations()
        return cls(fileobj=open(filename, 'rb'), domain=domain)
    load = classmethod(load)

    def __repr__(self):
        return '<%s: "%s">' % (type(self).__name__,
                               self._info.get('project-id-version'))

    def add(self, translations, merge=True):
        """Add the given translations to the catalog.

        If the domain of the translations is different than that of the
        current catalog, they are added as a catalog that is only accessible
        by the various ``d*gettext`` functions.

        :param translations: the `Translations` instance with the messages to
                             add
        :param merge: whether translations for message domains that have
                      already been added should be merged with the existing
                      translations
        :return: the `Translations` instance (``self``) so that `merge` calls
                 can be easily chained
        :rtype: `Translations`
        """
        domain = getattr(translations, 'domain', self.DEFAULT_DOMAIN)
        if merge and domain == self.domain:
            return self.merge(translations)

        existing = self._domains.get(domain)
        if merge and existing is not None:
            existing.merge(translations)
        else:
            translations.add_fallback(self)
            self._domains[domain] = translations

        return self

    def merge(self, translations):
        """Merge the given translations into the catalog.

        Message translations in the specified catalog override any messages
        with the same identifier in the existing catalog.

        :param translations: the `Translations` instance with the messages to
                             merge
        :return: the `Translations` instance (``self``) so that `merge` calls
                 can be easily chained
        :rtype: `Translations`
        """
        if isinstance(translations, gettext.GNUTranslations):
            self._catalog.update(translations._catalog)
            if isinstance(translations, Translations):
                self.files.extend(translations.files)

        return self

    def dgettext(self, domain, message):
        """Like ``gettext()``, but look the message up in the specified
        domain.
        """
        return self._domains.get(domain, self).gettext(message)

    def ldgettext(self, domain, message):
        """Like ``lgettext()``, but look the message up in the specified
        domain.
        """
        return self._domains.get(domain, self).lgettext(message)

    def dugettext(self, domain, message):
        """Like ``ugettext()``, but look the message up in the specified
        domain.
        """
        return self._domains.get(domain, self).ugettext(message)

    def dngettext(self, domain, singular, plural, num):
        """Like ``ngettext()``, but look the message up in the specified
        domain.
        """
        return self._domains.get(domain, self).ngettext(singular, plural, num)

    def ldngettext(self, domain, singular, plural, num):
        """Like ``lngettext()``, but look the message up in the specified
        domain.
        """
        return self._domains.get(domain, self).lngettext(singular, plural, num)

    def dungettext(self, domain, singular, plural, num):
        """Like ``ungettext()`` but look the message up in the specified
        domain.
        """
        return self._domains.get(domain, self).ungettext(singular, plural, num)

class PelicanTranslations(object):
    """Pelican plugin for translation."""

    DEFAULT_DOMAIN = 'messages'

    def __init__(self, generator):
        self.theme = generator.theme
        self.settings = generator.settings

        generator.env.install_gettext_translations(self)

    def gettext(self, string, **variables):
        """Method took from Flask-Babel and adapted.

        Translates a string with the current locale and passes in the
        given keyword arguments as mapping to a string formatting string.

        ::

            gettext(u'Hello World!')
            gettext(u'Hello %(name)s!', name='World')
        """

        dirname = os.path.join(self.theme, 'locale')
        t = Translations.load(dirname, [self.settings.get('DEFAULT_LANG', 'en_US')])
        if t is None:
            return string % variables

        return t.ugettext(string) % variables


    def ngettext(self, singular, plural, num, **variables):
        """Method took from Flask-Babel and adapted.

        Translates a string with the current locale and passes in the
        given keyword arguments as mapping to a string formatting string.
        The `num` parameter is used to dispatch between singular and various
        plural forms of the message.  It is available in the format string
        as ``%(num)d`` or ``%(num)s``.  The source language should be
        English or a similar language which only has one plural form.

        ::

            ngettext(u'%(num)d Apple', u'%(num)d Apples', num=len(apples))
        """
        variables.setdefault('num', num)
        dirname = os.path.join(self.theme, 'translations')
        t = Translations.load(dirname, [self.settings.get('DEFAULT_LANG', 'en_US')])
        if t is None:
            return (singular if num == 1 else plural) % variables
        return t.ungettext(singular, plural, num) % variables


def callback(articles_gen):
    PelicanTranslations(articles_gen)

def register():
    signals.article_generator_init.connect(callback)