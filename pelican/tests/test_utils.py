import locale
import logging
import os
import shutil
from datetime import timezone
from sys import platform
from tempfile import mkdtemp

import watchfiles

try:
    from zoneinfo import ZoneInfo
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo

from pelican import utils
from pelican.generators import TemplatePagesGenerator
from pelican.settings import DEFAULT_CONFIG, read_settings
from pelican.tests.support import (
    LoggedTestCase,
    get_article,
    locale_available,
    unittest,
)
from pelican.writers import Writer


class ClassDeprAttr:
    _new_attribute = "new_value"

    @utils.deprecated_attribute(
        old="_old_attribute", new="_new_attribute", since=(3, 1, 0), remove=(4, 1, 3)
    )
    def _old_attribute():
        return None


class TestUtils(LoggedTestCase):
    def setUp(self):
        super().setUp()
        self.temp_output = mkdtemp(prefix="pelicantests.")

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.temp_output)

    def test_deprecated_attribute(self):
        test_class = ClassDeprAttr()
        value = test_class._old_attribute
        self.assertEqual(value, test_class._new_attribute)
        self.assertLogCountEqual(
            count=1,
            msg=(
                "_old_attribute has been deprecated since 3.1.0 and will be "
                "removed by version 4.1.3.  Use _new_attribute instead"
            ),
            level=logging.WARNING,
        )

    def test_get_date(self):
        # valid ones
        date = utils.SafeDatetime(year=2012, month=11, day=22)
        date_hour = utils.SafeDatetime(year=2012, month=11, day=22, hour=22, minute=11)
        date_hour_z = utils.SafeDatetime(
            year=2012, month=11, day=22, hour=22, minute=11, tzinfo=timezone.utc
        )
        date_hour_est = utils.SafeDatetime(
            year=2012, month=11, day=22, hour=22, minute=11, tzinfo=ZoneInfo("EST")
        )
        date_hour_sec = utils.SafeDatetime(
            year=2012, month=11, day=22, hour=22, minute=11, second=10
        )
        date_hour_sec_z = utils.SafeDatetime(
            year=2012,
            month=11,
            day=22,
            hour=22,
            minute=11,
            second=10,
            tzinfo=timezone.utc,
        )
        date_hour_sec_est = utils.SafeDatetime(
            year=2012,
            month=11,
            day=22,
            hour=22,
            minute=11,
            second=10,
            tzinfo=ZoneInfo("EST"),
        )
        date_hour_sec_frac_z = utils.SafeDatetime(
            year=2012,
            month=11,
            day=22,
            hour=22,
            minute=11,
            second=10,
            microsecond=123000,
            tzinfo=timezone.utc,
        )
        dates = {
            "2012-11-22": date,
            "2012/11/22": date,
            "2012-11-22 22:11": date_hour,
            "2012/11/22 22:11": date_hour,
            "22-11-2012": date,
            "22/11/2012": date,
            "22.11.2012": date,
            "22.11.2012 22:11": date_hour,
            "2012-11-22T22:11Z": date_hour_z,
            "2012-11-22T22:11-0500": date_hour_est,
            "2012-11-22 22:11:10": date_hour_sec,
            "2012-11-22T22:11:10Z": date_hour_sec_z,
            "2012-11-22T22:11:10-0500": date_hour_sec_est,
            "2012-11-22T22:11:10.123Z": date_hour_sec_frac_z,
        }

        # examples from http://www.w3.org/TR/NOTE-datetime
        iso_8601_date = utils.SafeDatetime(year=1997, month=7, day=16)
        iso_8601_date_hour_tz = utils.SafeDatetime(
            year=1997,
            month=7,
            day=16,
            hour=19,
            minute=20,
            tzinfo=ZoneInfo("Europe/London"),
        )
        iso_8601_date_hour_sec_tz = utils.SafeDatetime(
            year=1997,
            month=7,
            day=16,
            hour=19,
            minute=20,
            second=30,
            tzinfo=ZoneInfo("Europe/London"),
        )
        iso_8601_date_hour_sec_ms_tz = utils.SafeDatetime(
            year=1997,
            month=7,
            day=16,
            hour=19,
            minute=20,
            second=30,
            microsecond=450000,
            tzinfo=ZoneInfo("Europe/London"),
        )
        iso_8601 = {
            "1997-07-16": iso_8601_date,
            "1997-07-16T19:20+01:00": iso_8601_date_hour_tz,
            "1997-07-16T19:20:30+01:00": iso_8601_date_hour_sec_tz,
            "1997-07-16T19:20:30.45+01:00": iso_8601_date_hour_sec_ms_tz,
        }

        # invalid ones
        invalid_dates = ["2010-110-12", "yay"]

        for value, expected in dates.items():
            self.assertEqual(utils.get_date(value), expected, value)

        for value, expected in iso_8601.items():
            self.assertEqual(utils.get_date(value), expected, value)

        for item in invalid_dates:
            self.assertRaises(ValueError, utils.get_date, item)

    def test_slugify(self):
        samples = (
            ("this is a test", "this-is-a-test"),
            ("this        is a test", "this-is-a-test"),
            ("this → is ← a ↑ test", "this-is-a-test"),
            ("this--is---a test", "this-is-a-test"),
            (
                "unicode測試許功蓋，你看到了嗎？",
                "unicodece-shi-xu-gong-gai-ni-kan-dao-liao-ma",
            ),
            (
                "大飯原発４号機、１８日夜起動へ",
                "da-fan-yuan-fa-4hao-ji-18ri-ye-qi-dong-he",
            ),
        )

        settings = read_settings()
        subs = settings["SLUG_REGEX_SUBSTITUTIONS"]

        for value, expected in samples:
            self.assertEqual(utils.slugify(value, regex_subs=subs), expected)

        self.assertEqual(utils.slugify("Cat", regex_subs=subs), "cat")
        self.assertEqual(
            utils.slugify("Cat", regex_subs=subs, preserve_case=False), "cat"
        )
        self.assertEqual(
            utils.slugify("Cat", regex_subs=subs, preserve_case=True), "Cat"
        )

    def test_slugify_use_unicode(self):
        samples = (
            ("this is a test", "this-is-a-test"),
            ("this        is a test", "this-is-a-test"),
            ("this → is ← a ↑ test", "this-is-a-test"),
            ("this--is---a test", "this-is-a-test"),
            ("unicode測試許功蓋，你看到了嗎？", "unicode測試許功蓋你看到了嗎"),
            ("Çığ", "çığ"),
        )

        settings = read_settings()
        subs = settings["SLUG_REGEX_SUBSTITUTIONS"]

        for value, expected in samples:
            self.assertEqual(
                utils.slugify(value, regex_subs=subs, use_unicode=True), expected
            )

        # check with preserve case
        self.assertEqual(
            utils.slugify("Çığ", regex_subs=subs, preserve_case=True, use_unicode=True),
            "Çığ",
        )

        # check normalization
        samples = (
            ("大飯原発４号機、１８日夜起動へ", "大飯原発4号機18日夜起動へ"),
            (
                "\N{LATIN SMALL LETTER C}\N{COMBINING CEDILLA}",
                "\N{LATIN SMALL LETTER C WITH CEDILLA}",
            ),
        )
        for value, expected in samples:
            self.assertEqual(
                utils.slugify(value, regex_subs=subs, use_unicode=True), expected
            )

    def test_slugify_substitute(self):
        samples = (
            ("C++ is based on C", "cpp-is-based-on-c"),
            ("C+++ test C+ test", "cpp-test-c-test"),
            ("c++, c#, C#, C++", "cpp-c-sharp-c-sharp-cpp"),
            ("c++-streams", "cpp-streams"),
        )

        settings = read_settings()
        subs = [
            (r"C\+\+", "CPP"),
            (r"C#", "C-SHARP"),
        ] + settings["SLUG_REGEX_SUBSTITUTIONS"]
        for value, expected in samples:
            self.assertEqual(utils.slugify(value, regex_subs=subs), expected)

    def test_slugify_substitute_and_keeping_non_alphanum(self):
        samples = (
            ("Fedora QA", "fedora.qa"),
            ("C++ is used by Fedora QA", "cpp is used by fedora.qa"),
            ("C++ is based on C", "cpp is based on c"),
            ("C+++ test C+ test", "cpp+ test c+ test"),
        )

        subs = [
            (r"Fedora QA", "fedora.qa"),
            (r"c\+\+", "cpp"),
        ]
        for value, expected in samples:
            self.assertEqual(utils.slugify(value, regex_subs=subs), expected)

    def test_get_relative_path(self):
        samples = (
            (os.path.join("test", "test.html"), os.pardir),
            (
                os.path.join("test", "test", "test.html"),
                os.path.join(os.pardir, os.pardir),
            ),
            ("test.html", os.curdir),
            (os.path.join("/test", "test.html"), os.pardir),
            (
                os.path.join("/test", "test", "test.html"),
                os.path.join(os.pardir, os.pardir),
            ),
            ("/test.html", os.curdir),
        )

        for value, expected in samples:
            self.assertEqual(utils.get_relative_path(value), expected)

    def test_truncate_html_words(self):
        # Plain text.
        self.assertEqual(utils.truncate_html_words("short string", 20), "short string")
        self.assertEqual(
            utils.truncate_html_words("word " * 100, 20), "word " * 20 + "…"
        )

        # Plain text with Unicode content.
        self.assertEqual(
            utils.truncate_html_words(
                "我愿意这样，朋友——我独自远行，不但没有你，\
                 并且再没有别的影在黑暗里。",
                12,
            ),
            "我愿意这样，朋友——我独自远行" + " …",
        )
        self.assertEqual(
            utils.truncate_html_words(
                "Ты мелькнула, ты предстала, Снова сердце задрожало,", 3
            ),
            "Ты мелькнула, ты" + " …",
        )
        self.assertEqual(
            utils.truncate_html_words("Trong đầm gì đẹp bằng sen", 4),
            "Trong đầm gì đẹp" + " …",
        )

        # Words enclosed or intervaled by HTML tags.
        self.assertEqual(
            utils.truncate_html_words("<p>" + "word " * 100 + "</p>", 20),
            "<p>" + "word " * 20 + "…</p>",
        )
        self.assertEqual(
            utils.truncate_html_words(
                '<span\nstyle="\n…\n">' + "word " * 100 + "</span>", 20
            ),
            '<span\nstyle="\n…\n">' + "word " * 20 + "…</span>",
        )
        self.assertEqual(
            utils.truncate_html_words("<br>" + "word " * 100, 20),
            "<br>" + "word " * 20 + "…",
        )
        self.assertEqual(
            utils.truncate_html_words("<!-- comment -->" + "word " * 100, 20),
            "<!-- comment -->" + "word " * 20 + "…",
        )

        # Words enclosed or intervaled by HTML tags with a custom end
        # marker containing HTML tags.
        self.assertEqual(
            utils.truncate_html_words(
                "<p>" + "word " * 100 + "</p>", 20, "<span>marker</span>"
            ),
            "<p>" + "word " * 20 + "<span>marker</span></p>",
        )
        self.assertEqual(
            utils.truncate_html_words(
                '<span\nstyle="\n…\n">' + "word " * 100 + "</span>",
                20,
                "<span>marker</span>",
            ),
            '<span\nstyle="\n…\n">' + "word " * 20 + "<span>marker</span></span>",
        )
        self.assertEqual(
            utils.truncate_html_words(
                "<br>" + "word " * 100, 20, "<span>marker</span>"
            ),
            "<br>" + "word " * 20 + "<span>marker</span>",
        )
        self.assertEqual(
            utils.truncate_html_words(
                "<!-- comment -->" + "word " * 100, 20, "<span>marker</span>"
            ),
            "<!-- comment -->" + "word " * 20 + "<span>marker</span>",
        )

        # Words with hypens and apostrophes.
        self.assertEqual(utils.truncate_html_words("a-b " * 100, 20), "a-b " * 20 + "…")
        self.assertEqual(
            utils.truncate_html_words("it's " * 100, 20), "it's " * 20 + "…"
        )

        # Words with HTML entity references.
        self.assertEqual(
            utils.truncate_html_words("&eacute; " * 100, 20), "&eacute; " * 20 + "…"
        )
        self.assertEqual(
            utils.truncate_html_words("caf&eacute; " * 100, 20),
            "caf&eacute; " * 20 + "…",
        )
        self.assertEqual(
            utils.truncate_html_words("&egrave;lite " * 100, 20),
            "&egrave;lite " * 20 + "…",
        )
        self.assertEqual(
            utils.truncate_html_words("cafeti&eacute;re " * 100, 20),
            "cafeti&eacute;re " * 20 + "…",
        )
        self.assertEqual(
            utils.truncate_html_words("&int;dx " * 100, 20), "&int;dx " * 20 + "…"
        )

        # Words with HTML character references inside and outside
        # the ASCII range.
        self.assertEqual(
            utils.truncate_html_words("&#xe9; " * 100, 20), "&#xe9; " * 20 + "…"
        )
        self.assertEqual(
            utils.truncate_html_words("&#x222b;dx " * 100, 20), "&#x222b;dx " * 20 + "…"
        )

        # Words with invalid or broken HTML references.
        self.assertEqual(utils.truncate_html_words("&invalid;", 20), "&invalid;")
        self.assertEqual(
            utils.truncate_html_words("&#9999999999;", 20), "&#9999999999;"
        )
        self.assertEqual(
            utils.truncate_html_words("&#xfffffffff;", 20), "&#xfffffffff;"
        )
        self.assertEqual(utils.truncate_html_words("&mdash text", 20), "&mdash text")
        self.assertEqual(utils.truncate_html_words("&#1234 text", 20), "&#1234 text")
        self.assertEqual(utils.truncate_html_words("&#xabc text", 20), "&#xabc text")

    def test_truncate_html_paragraphs(self):
        one = "<p>one</p>"

        self.assertEqual(utils.truncate_html_paragraphs(one, 0), "")
        self.assertEqual(utils.truncate_html_paragraphs(one, 1), one)
        self.assertEqual(utils.truncate_html_paragraphs(one, 2), one)

        two = one + "<p>two</p>"
        self.assertEqual(utils.truncate_html_paragraphs(two, 1), one)
        self.assertEqual(utils.truncate_html_paragraphs(two, 2), two)

        three = two + "<p>three</p>"
        self.assertEqual(utils.truncate_html_paragraphs(three, 1), one)
        self.assertEqual(utils.truncate_html_paragraphs(three, 2), two)
        self.assertEqual(utils.truncate_html_paragraphs(three, 3), three)
        self.assertEqual(utils.truncate_html_paragraphs(three, 4), three)

    def test_process_translations(self):
        fr_articles = []
        en_articles = []

        # create a bunch of articles
        # 0: no translation metadata
        fr_articles.append(
            get_article(lang="fr", slug="yay0", title="Titre", content="en français")
        )
        en_articles.append(
            get_article(lang="en", slug="yay0", title="Title", content="in english")
        )
        # 1: translation metadata on default lang
        fr_articles.append(
            get_article(lang="fr", slug="yay1", title="Titre", content="en français")
        )
        en_articles.append(
            get_article(
                lang="en",
                slug="yay1",
                title="Title",
                content="in english",
                translation="true",
            )
        )
        # 2: translation metadata not on default lang
        fr_articles.append(
            get_article(
                lang="fr",
                slug="yay2",
                title="Titre",
                content="en français",
                translation="true",
            )
        )
        en_articles.append(
            get_article(lang="en", slug="yay2", title="Title", content="in english")
        )
        # 3: back to default language detection if all items have the
        #    translation metadata
        fr_articles.append(
            get_article(
                lang="fr",
                slug="yay3",
                title="Titre",
                content="en français",
                translation="yep",
            )
        )
        en_articles.append(
            get_article(
                lang="en",
                slug="yay3",
                title="Title",
                content="in english",
                translation="yes",
            )
        )
        # 4-5: translation pairs with the same slug but different category
        fr_articles.append(
            get_article(
                lang="fr",
                slug="yay4",
                title="Titre",
                content="en français",
                category="foo",
            )
        )
        en_articles.append(
            get_article(
                lang="en",
                slug="yay4",
                title="Title",
                content="in english",
                category="foo",
            )
        )
        fr_articles.append(
            get_article(
                lang="fr",
                slug="yay4",
                title="Titre",
                content="en français",
                category="bar",
            )
        )
        en_articles.append(
            get_article(
                lang="en",
                slug="yay4",
                title="Title",
                content="in english",
                category="bar",
            )
        )

        # try adding articles in both orders
        for lang0_articles, lang1_articles in (
            (fr_articles, en_articles),
            (en_articles, fr_articles),
        ):
            articles = lang0_articles + lang1_articles

            # test process_translations with falsy translation_id
            index, trans = utils.process_translations(articles, translation_id=None)
            for i in range(6):
                for lang_articles in [en_articles, fr_articles]:
                    self.assertIn(lang_articles[i], index)
                    self.assertNotIn(lang_articles[i], trans)

            # test process_translations with simple and complex translation_id
            for translation_id in ["slug", {"slug", "category"}]:
                index, trans = utils.process_translations(
                    articles, translation_id=translation_id
                )

                for a in [
                    en_articles[0],
                    fr_articles[1],
                    en_articles[2],
                    en_articles[3],
                    en_articles[4],
                    en_articles[5],
                ]:
                    self.assertIn(a, index)
                    self.assertNotIn(a, trans)

                for a in [
                    fr_articles[0],
                    en_articles[1],
                    fr_articles[2],
                    fr_articles[3],
                    fr_articles[4],
                    fr_articles[5],
                ]:
                    self.assertIn(a, trans)
                    self.assertNotIn(a, index)

                for i in range(6):
                    self.assertIn(en_articles[i], fr_articles[i].translations)
                    self.assertIn(fr_articles[i], en_articles[i].translations)

                for a_arts in [en_articles, fr_articles]:
                    for b_arts in [en_articles, fr_articles]:
                        if translation_id == "slug":
                            self.assertIn(a_arts[4], b_arts[5].translations)
                            self.assertIn(a_arts[5], b_arts[4].translations)
                        elif translation_id == {"slug", "category"}:
                            self.assertNotIn(a_arts[4], b_arts[5].translations)
                            self.assertNotIn(a_arts[5], b_arts[4].translations)

    def test_clean_output_dir(self):
        retention = ()
        test_directory = os.path.join(self.temp_output, "clean_output")
        content = os.path.join(os.path.dirname(__file__), "content")
        shutil.copytree(content, test_directory)
        utils.clean_output_dir(test_directory, retention)
        self.assertTrue(os.path.isdir(test_directory))
        self.assertListEqual([], os.listdir(test_directory))
        shutil.rmtree(test_directory)

    def test_clean_output_dir_not_there(self):
        retention = ()
        test_directory = os.path.join(self.temp_output, "does_not_exist")
        utils.clean_output_dir(test_directory, retention)
        self.assertFalse(os.path.exists(test_directory))

    def test_clean_output_dir_is_file(self):
        retention = ()
        test_directory = os.path.join(self.temp_output, "this_is_a_file")
        f = open(test_directory, "w")
        f.write("")
        f.close()
        utils.clean_output_dir(test_directory, retention)
        self.assertFalse(os.path.exists(test_directory))

    def test_strftime(self):
        d = utils.SafeDatetime(2012, 8, 29)

        # simple formatting
        self.assertEqual(utils.strftime(d, "%d/%m/%y"), "29/08/12")
        self.assertEqual(utils.strftime(d, "%d/%m/%Y"), "29/08/2012")

        # RFC 3339
        self.assertEqual(
            utils.strftime(d, "%Y-%m-%dT%H:%M:%SZ"), "2012-08-29T00:00:00Z"
        )

        # % escaped
        self.assertEqual(utils.strftime(d, "%d%%%m%%%y"), "29%08%12")
        self.assertEqual(utils.strftime(d, "%d %% %m %% %y"), "29 % 08 % 12")
        # not valid % formatter
        self.assertEqual(
            utils.strftime(d, "10% reduction in %Y"), "10% reduction in 2012"
        )
        self.assertEqual(
            utils.strftime(d, "%10 reduction in %Y"), "%10 reduction in 2012"
        )

        # with text
        self.assertEqual(
            utils.strftime(d, "Published in %d-%m-%Y"), "Published in 29-08-2012"
        )

        # with non-ascii text
        self.assertEqual(
            utils.strftime(d, "%d/%m/%Y Øl trinken beim Besäufnis"),
            "29/08/2012 Øl trinken beim Besäufnis",
        )

        # alternative formatting options
        self.assertEqual(utils.strftime(d, "%-d/%-m/%y"), "29/8/12")
        self.assertEqual(utils.strftime(d, "%-H:%-M:%-S"), "0:0:0")

        d = utils.SafeDatetime(2012, 8, 9)
        self.assertEqual(utils.strftime(d, "%-d/%-m/%y"), "9/8/12")

        d = utils.SafeDatetime(2021, 1, 8)
        self.assertEqual(utils.strftime(d, "%G - %-V - %u"), "2021 - 1 - 5")

    # test the output of utils.strftime in a different locale
    # Turkish locale
    @unittest.skipUnless(
        locale_available("tr_TR.UTF-8") or locale_available("Turkish"),
        "Turkish locale needed",
    )
    def test_strftime_locale_dependent_turkish(self):
        temp_locale = "Turkish" if platform == "win32" else "tr_TR.UTF-8"

        with utils.temporary_locale(temp_locale):
            d = utils.SafeDatetime(2012, 8, 29)

            # simple
            self.assertEqual(utils.strftime(d, "%d %B %Y"), "29 Ağustos 2012")
            self.assertEqual(
                utils.strftime(d, "%A, %d %B %Y"), "Çarşamba, 29 Ağustos 2012"
            )

            # with text
            self.assertEqual(
                utils.strftime(d, "Yayınlanma tarihi: %A, %d %B %Y"),
                "Yayınlanma tarihi: Çarşamba, 29 Ağustos 2012",
            )

            # non-ascii format candidate (someone might pass it… for some reason)
            self.assertEqual(
                utils.strftime(d, "%Y yılında %üretim artışı"),
                "2012 yılında %üretim artışı",
            )

    # test the output of utils.strftime in a different locale
    # French locale
    @unittest.skipUnless(
        locale_available("fr_FR.UTF-8") or locale_available("French"),
        "French locale needed",
    )
    def test_strftime_locale_dependent_french(self):
        temp_locale = "French" if platform == "win32" else "fr_FR.UTF-8"

        with utils.temporary_locale(temp_locale):
            d = utils.SafeDatetime(2012, 8, 29)

            # simple
            self.assertEqual(utils.strftime(d, "%d %B %Y"), "29 août 2012")

            # depending on OS, the first letter is m or M
            self.assertTrue(utils.strftime(d, "%A") in ("mercredi", "Mercredi"))

            # with text
            self.assertEqual(
                utils.strftime(d, "Écrit le %d %B %Y"), "Écrit le 29 août 2012"
            )

            # non-ascii format candidate (someone might pass it… for some reason)
            self.assertEqual(utils.strftime(d, "%écrits en %Y"), "%écrits en 2012")

    def test_maybe_pluralize(self):
        self.assertEqual(utils.maybe_pluralize(0, "Article", "Articles"), "0 Articles")
        self.assertEqual(utils.maybe_pluralize(1, "Article", "Articles"), "1 Article")
        self.assertEqual(utils.maybe_pluralize(2, "Article", "Articles"), "2 Articles")

    def test_temporary_locale(self):
        # test with default LC category
        orig_locale = locale.setlocale(locale.LC_ALL)

        with utils.temporary_locale("C"):
            self.assertEqual(locale.setlocale(locale.LC_ALL), "C")

        self.assertEqual(locale.setlocale(locale.LC_ALL), orig_locale)

        # test with custom LC category
        orig_locale = locale.setlocale(locale.LC_TIME)

        with utils.temporary_locale("C", locale.LC_TIME):
            self.assertEqual(locale.setlocale(locale.LC_TIME), "C")

        self.assertEqual(locale.setlocale(locale.LC_TIME), orig_locale)


class TestCopy(unittest.TestCase):
    """Tests the copy utility"""

    def setUp(self):
        self.root_dir = mkdtemp(prefix="pelicantests.")
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, "C")

    def tearDown(self):
        shutil.rmtree(self.root_dir)
        locale.setlocale(locale.LC_ALL, self.old_locale)

    def _create_file(self, *path):
        with open(os.path.join(self.root_dir, *path), "w") as f:
            f.write("42\n")

    def _create_dir(self, *path):
        os.makedirs(os.path.join(self.root_dir, *path))

    def _exist_file(self, *path):
        path = os.path.join(self.root_dir, *path)
        self.assertTrue(os.path.isfile(path), f"File does not exist: {path}")

    def _exist_dir(self, *path):
        path = os.path.join(self.root_dir, *path)
        self.assertTrue(os.path.exists(path), f"Directory does not exist: {path}")

    def test_copy_file_same_path(self):
        self._create_file("a.txt")
        utils.copy(
            os.path.join(self.root_dir, "a.txt"), os.path.join(self.root_dir, "b.txt")
        )
        self._exist_file("b.txt")

    def test_copy_file_different_path(self):
        self._create_dir("a")
        self._create_dir("b")
        self._create_file("a", "a.txt")
        utils.copy(
            os.path.join(self.root_dir, "a", "a.txt"),
            os.path.join(self.root_dir, "b", "b.txt"),
        )
        self._exist_dir("b")
        self._exist_file("b", "b.txt")

    def test_copy_file_create_dirs(self):
        self._create_file("a.txt")
        utils.copy(
            os.path.join(self.root_dir, "a.txt"),
            os.path.join(self.root_dir, "b0", "b1", "b2", "b3", "b.txt"),
        )
        self._exist_dir("b0")
        self._exist_dir("b0", "b1")
        self._exist_dir("b0", "b1", "b2")
        self._exist_dir("b0", "b1", "b2", "b3")
        self._exist_file("b0", "b1", "b2", "b3", "b.txt")

    def test_copy_dir_same_path(self):
        self._create_dir("a")
        self._create_file("a", "a.txt")
        utils.copy(os.path.join(self.root_dir, "a"), os.path.join(self.root_dir, "b"))
        self._exist_dir("b")
        self._exist_file("b", "a.txt")

    def test_copy_dir_different_path(self):
        self._create_dir("a0")
        self._create_dir("a0", "a1")
        self._create_file("a0", "a1", "a.txt")
        self._create_dir("b0")
        utils.copy(
            os.path.join(self.root_dir, "a0", "a1"),
            os.path.join(self.root_dir, "b0", "b1"),
        )
        self._exist_dir("b0", "b1")
        self._exist_file("b0", "b1", "a.txt")

    def test_copy_dir_create_dirs(self):
        self._create_dir("a")
        self._create_file("a", "a.txt")
        utils.copy(
            os.path.join(self.root_dir, "a"),
            os.path.join(self.root_dir, "b0", "b1", "b2", "b3", "b"),
        )
        self._exist_dir("b0")
        self._exist_dir("b0", "b1")
        self._exist_dir("b0", "b1", "b2")
        self._exist_dir("b0", "b1", "b2", "b3")
        self._exist_dir("b0", "b1", "b2", "b3", "b")
        self._exist_file("b0", "b1", "b2", "b3", "b", "a.txt")


class TestDateFormatter(unittest.TestCase):
    """Tests that the output of DateFormatter jinja filter is same as
    utils.strftime"""

    def setUp(self):
        # prepare a temp content and output folder
        self.temp_content = mkdtemp(prefix="pelicantests.")
        self.temp_output = mkdtemp(prefix="pelicantests.")

        # prepare a template file
        template_dir = os.path.join(self.temp_content, "template")
        template_path = os.path.join(template_dir, "source.html")
        os.makedirs(template_dir)
        with open(template_path, "w") as template_file:
            template_file.write('date = {{ date|strftime("%A, %d %B %Y") }}')
        self.date = utils.SafeDatetime(2012, 8, 29)

    def tearDown(self):
        shutil.rmtree(self.temp_content)
        shutil.rmtree(self.temp_output)
        # reset locale to default
        locale.setlocale(locale.LC_ALL, "")

    @unittest.skipUnless(
        locale_available("fr_FR.UTF-8") or locale_available("French"),
        "French locale needed",
    )
    def test_french_strftime(self):
        # This test tries to reproduce an issue that
        # occurred with python3.3 under macos10 only
        temp_locale = "French" if platform == "win32" else "fr_FR.UTF-8"

        with utils.temporary_locale(temp_locale):
            date = utils.SafeDatetime(2014, 8, 14)
            # we compare the lower() dates since macos10 returns
            # "Jeudi" for %A whereas linux reports "jeudi"
            self.assertEqual(
                "jeudi, 14 août 2014",
                utils.strftime(date, date_format="%A, %d %B %Y").lower(),
            )
            df = utils.DateFormatter()
            self.assertEqual(
                "jeudi, 14 août 2014", df(date, date_format="%A, %d %B %Y").lower()
            )

        # Let us now set the global locale to C:
        with utils.temporary_locale("C"):
            # DateFormatter should still work as expected
            # since it is the whole point of DateFormatter
            # (This is where pre-2014/4/15 code fails on macos10)
            df_date = df(date, date_format="%A, %d %B %Y").lower()
            self.assertEqual("jeudi, 14 août 2014", df_date)

    @unittest.skipUnless(
        locale_available("fr_FR.UTF-8") or locale_available("French"),
        "French locale needed",
    )
    def test_french_locale(self):
        if platform == "win32":
            locale_string = "French"
        else:
            locale_string = "fr_FR.UTF-8"
        settings = read_settings(
            override={
                "LOCALE": locale_string,
                "TEMPLATE_PAGES": {"template/source.html": "generated/file.html"},
            }
        )

        generator = TemplatePagesGenerator(
            {"date": self.date}, settings, self.temp_content, "", self.temp_output
        )
        generator.env.filters.update({"strftime": utils.DateFormatter()})

        writer = Writer(self.temp_output, settings=settings)
        generator.generate_output(writer)

        output_path = os.path.join(self.temp_output, "generated", "file.html")

        # output file has been generated
        self.assertTrue(os.path.exists(output_path))

        # output content is correct
        with utils.pelican_open(output_path) as output_file:
            self.assertEqual(
                output_file, utils.strftime(self.date, "date = %A, %d %B %Y")
            )

    @unittest.skipUnless(
        locale_available("tr_TR.UTF-8") or locale_available("Turkish"),
        "Turkish locale needed",
    )
    def test_turkish_locale(self):
        if platform == "win32":
            locale_string = "Turkish"
        else:
            locale_string = "tr_TR.UTF-8"
        settings = read_settings(
            override={
                "LOCALE": locale_string,
                "TEMPLATE_PAGES": {"template/source.html": "generated/file.html"},
            }
        )

        generator = TemplatePagesGenerator(
            {"date": self.date}, settings, self.temp_content, "", self.temp_output
        )
        generator.env.filters.update({"strftime": utils.DateFormatter()})

        writer = Writer(self.temp_output, settings=settings)
        generator.generate_output(writer)

        output_path = os.path.join(self.temp_output, "generated", "file.html")

        # output file has been generated
        self.assertTrue(os.path.exists(output_path))

        # output content is correct
        with utils.pelican_open(output_path) as output_file:
            self.assertEqual(
                output_file, utils.strftime(self.date, "date = %A, %d %B %Y")
            )


class TestSanitisedJoin(unittest.TestCase):
    def test_detect_parent_breakout(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "Attempted to break out of output directory to (.*?:)?/foo/test",
        ):  # (.*?:)? accounts for Windows root
            utils.sanitised_join("/foo/bar", "../test")

    def test_detect_root_breakout(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "Attempted to break out of output directory to (.*?:)?/test",
        ):  # (.*?:)? accounts for Windows root
            utils.sanitised_join("/foo/bar", "/test")

    def test_pass_deep_subpaths(self):
        self.assertEqual(
            utils.sanitised_join("/foo/bar", "test"),
            utils.posixize_path(os.path.abspath(os.path.join("/foo/bar", "test"))),
        )


class TestMemoized(unittest.TestCase):
    def test_memoized(self):
        class Container:
            def _get(self, key):
                pass

            @utils.memoized
            def get(self, key):
                return self._get(key)

        container = Container()

        with unittest.mock.patch.object(
            container, "_get", side_effect=lambda x: x
        ) as get_mock:
            self.assertEqual("foo", container.get("foo"))
            get_mock.assert_called_once_with("foo")

            get_mock.reset_mock()
            self.assertEqual("foo", container.get("foo"))
            get_mock.assert_not_called()

            self.assertEqual("bar", container.get("bar"))
            get_mock.assert_called_once_with("bar")

            get_mock.reset_mock()
            container.get.cache.clear()
            self.assertEqual("bar", container.get("bar"))
            get_mock.assert_called_once_with("bar")


class TestStringUtils(unittest.TestCase):
    def test_file_suffix(self):
        self.assertEqual("", utils.file_suffix(""))
        self.assertEqual("", utils.file_suffix("foo"))
        self.assertEqual("md", utils.file_suffix("foo.md"))


class TestFileChangeFilter(unittest.TestCase):
    ignore_file_patterns = DEFAULT_CONFIG["IGNORE_FILES"]

    def test_regular_files_not_filtered(self):
        filter = utils.FileChangeFilter(ignore_file_patterns=self.ignore_file_patterns)
        basename = "article.rst"
        full_path = os.path.join(os.path.dirname(__file__), "content", basename)

        for change in watchfiles.Change:
            self.assertTrue(filter(change=change, path=basename))
            self.assertTrue(filter(change=change, path=full_path))

    def test_dotfiles_filtered(self):
        filter = utils.FileChangeFilter(ignore_file_patterns=self.ignore_file_patterns)
        basename = ".config"
        full_path = os.path.join(os.path.dirname(__file__), "content", basename)

        # Testing with just the hidden file name and the full file path to the hidden file
        for change in watchfiles.Change:
            self.assertFalse(filter(change=change, path=basename))
            self.assertFalse(filter(change=change, path=full_path))

    def test_default_filters(self):
        # Testing a subset of the default filters
        # For reference: https://watchfiles.helpmanual.io/api/filters/#watchfiles.DefaultFilter.ignore_dirs
        filter = utils.FileChangeFilter(ignore_file_patterns=[])
        test_basenames = [
            "__pycache__",
            ".git",
            ".hg",
            ".svn",
            ".tox",
            ".venv",
            ".idea",
            "node_modules",
            ".mypy_cache",
            ".pytest_cache",
            ".hypothesis",
            ".DS_Store",
            "flycheck_file",
            "test_file~",
        ]

        for basename in test_basenames:
            full_path = os.path.join(os.path.dirname(__file__), basename)
            for change in watchfiles.Change:
                self.assertFalse(filter(change=change, path=basename))
                self.assertFalse(filter(change=change, path=full_path))

    def test_custom_ignore_pattern(self):
        filter = utils.FileChangeFilter(ignore_file_patterns=["*.rst"])
        basename = "article.rst"
        full_path = os.path.join(os.path.dirname(__file__), basename)
        for change in watchfiles.Change:
            self.assertFalse(filter(change=change, path=basename))
            self.assertFalse(filter(change=change, path=full_path))

        # If the user changes `IGNORE_FILES` to only contain ['*.rst'], then dotfiles would not be filtered anymore
        basename = ".config"
        full_path = os.path.join(os.path.dirname(__file__), basename)
        for change in watchfiles.Change:
            self.assertTrue(filter(change=change, path=basename))
            self.assertTrue(filter(change=change, path=full_path))
