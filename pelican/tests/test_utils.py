# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import logging
import shutil
import os
import datetime
import time
import locale
from sys import platform
from tempfile import mkdtemp

from pelican.generators import TemplatePagesGenerator
from pelican.writers import Writer
from pelican.settings import read_settings
from pelican import utils
from .support import get_article, LoggedTestCase, locale_available, unittest


class TestUtils(LoggedTestCase):
    _new_attribute = 'new_value'

    @utils.deprecated_attribute(
        old='_old_attribute', new='_new_attribute',
        since=(3, 1, 0), remove=(4, 1, 3))
    def _old_attribute():
        return None

    def test_deprecated_attribute(self):
        value = self._old_attribute
        self.assertEqual(value, self._new_attribute)
        self.assertLogCountEqual(
            count=1,
            msg=('_old_attribute has been deprecated since 3.1.0 and will be '
                 'removed by version 4.1.3.  Use _new_attribute instead'),
            level=logging.WARNING)

    def test_get_date(self):
        # valid ones
        date = datetime.datetime(year=2012, month=11, day=22)
        date_hour = datetime.datetime(year=2012, month=11, day=22, hour=22,
                                      minute=11)
        date_hour_sec = datetime.datetime(year=2012, month=11, day=22, hour=22,
                                          minute=11, second=10)
        dates = {'2012-11-22': date,
                 '2012/11/22': date,
                 '2012-11-22 22:11': date_hour,
                 '2012/11/22 22:11': date_hour,
                 '22-11-2012': date,
                 '22/11/2012': date,
                 '22.11.2012': date,
                 '2012-22-11': date,
                 '22.11.2012 22:11': date_hour,
                 '2012-11-22 22:11:10': date_hour_sec}

        for value, expected in dates.items():
            self.assertEqual(utils.get_date(value), expected, value)

        # invalid ones
        invalid_dates = ('2010-110-12', 'yay')
        for item in invalid_dates:
            self.assertRaises(ValueError, utils.get_date, item)

    def test_slugify(self):

        samples = (('this is a test', 'this-is-a-test'),
                   ('this        is a test', 'this-is-a-test'),
                   ('this → is ← a ↑ test', 'this-is-a-test'),
                   ('this--is---a test', 'this-is-a-test'),
                   ('unicode測試許功蓋，你看到了嗎？',
                    'unicodece-shi-xu-gong-gai-ni-kan-dao-liao-ma'),
                   ('大飯原発４号機、１８日夜起動へ',
                    'da-fan-yuan-fa-4hao-ji-18ri-ye-qi-dong-he'),)

        for value, expected in samples:
            self.assertEqual(utils.slugify(value), expected)

    def test_get_relative_path(self):

        samples = ((os.path.join('test', 'test.html'), os.pardir),
                   (os.path.join('test', 'test', 'test.html'),
                    os.path.join(os.pardir, os.pardir)),
                   ('test.html', os.curdir),
                   (os.path.join('/test', 'test.html'), os.pardir),
                   (os.path.join('/test', 'test', 'test.html'),
                    os.path.join(os.pardir, os.pardir)),
                   ('/test.html', os.curdir),)

        for value, expected in samples:
            self.assertEqual(utils.get_relative_path(value), expected)

    def test_process_translations(self):
        # create a bunch of articles
        # 1: no translation metadata
        fr_article1 = get_article(lang='fr', slug='yay', title='Un titre',
                                  content='en français')
        en_article1 = get_article(lang='en', slug='yay', title='A title',
                                  content='in english')
        # 2: reverse which one is the translation thanks to metadata
        fr_article2 = get_article(lang='fr', slug='yay2', title='Un titre',
                                  content='en français')
        en_article2 = get_article(lang='en', slug='yay2', title='A title',
                                  content='in english',
                                  extra_metadata={'translation': 'true'})
        # 3: back to default language detection if all items have the
        #    translation metadata
        fr_article3 = get_article(lang='fr', slug='yay3', title='Un titre',
                                  content='en français',
                                  extra_metadata={'translation': 'yep'})
        en_article3 = get_article(lang='en', slug='yay3', title='A title',
                                  content='in english',
                                  extra_metadata={'translation': 'yes'})

        articles = [fr_article1, en_article1, fr_article2, en_article2,
                    fr_article3, en_article3]

        index, trans = utils.process_translations(articles)

        self.assertIn(en_article1, index)
        self.assertIn(fr_article1, trans)
        self.assertNotIn(en_article1, trans)
        self.assertNotIn(fr_article1, index)

        self.assertIn(fr_article2, index)
        self.assertIn(en_article2, trans)
        self.assertNotIn(fr_article2, trans)
        self.assertNotIn(en_article2, index)

        self.assertIn(en_article3, index)
        self.assertIn(fr_article3, trans)
        self.assertNotIn(en_article3, trans)
        self.assertNotIn(fr_article3, index)

    def test_watchers(self):
        # Test if file changes are correctly detected
        # Make sure to handle not getting any files correctly.

        dirname = os.path.join(os.path.dirname(__file__), 'content')
        folder_watcher = utils.folder_watcher(dirname, ['rst'])

        path = os.path.join(dirname, 'article_with_metadata.rst')
        file_watcher = utils.file_watcher(path)

        # first check returns True
        self.assertEqual(next(folder_watcher), True)
        self.assertEqual(next(file_watcher), True)

        # next check without modification returns False
        self.assertEqual(next(folder_watcher), False)
        self.assertEqual(next(file_watcher), False)

        # after modification, returns True
        t = time.time()
        os.utime(path, (t, t))
        self.assertEqual(next(folder_watcher), True)
        self.assertEqual(next(file_watcher), True)

        # file watcher with None or empty path should return None
        self.assertEqual(next(utils.file_watcher('')), None)
        self.assertEqual(next(utils.file_watcher(None)), None)

        empty_path = os.path.join(os.path.dirname(__file__), 'empty')
        try:
            os.mkdir(empty_path)
            os.mkdir(os.path.join(empty_path, "empty_folder"))
            shutil.copy(__file__, empty_path)

            # if no files of interest, returns None
            watcher = utils.folder_watcher(empty_path, ['rst'])
            self.assertEqual(next(watcher), None)
        except OSError:
            self.fail("OSError Exception in test_files_changed test")
        finally:
            shutil.rmtree(empty_path, True)

    def test_clean_output_dir(self):
        test_directory = os.path.join(os.path.dirname(__file__),
                                      'clean_output')
        content = os.path.join(os.path.dirname(__file__), 'content')
        shutil.copytree(content, test_directory)
        utils.clean_output_dir(test_directory)
        self.assertTrue(os.path.isdir(test_directory))
        self.assertListEqual([], os.listdir(test_directory))
        shutil.rmtree(test_directory)

    def test_clean_output_dir_not_there(self):
        test_directory = os.path.join(os.path.dirname(__file__),
                                      'does_not_exist')
        utils.clean_output_dir(test_directory)
        self.assertTrue(not os.path.exists(test_directory))

    def test_clean_output_dir_is_file(self):
        test_directory = os.path.join(os.path.dirname(__file__),
                                      'this_is_a_file')
        f = open(test_directory, 'w')
        f.write('')
        f.close()
        utils.clean_output_dir(test_directory)
        self.assertTrue(not os.path.exists(test_directory))

    def test_strftime(self):
        d = datetime.date(2012, 8, 29)

        # simple formatting
        self.assertEqual(utils.strftime(d, '%d/%m/%y'), '29/08/12')
        self.assertEqual(utils.strftime(d, '%d/%m/%Y'), '29/08/2012')

        # % escaped
        self.assertEqual(utils.strftime(d, '%d%%%m%%%y'), '29%08%12')
        self.assertEqual(utils.strftime(d, '%d %% %m %% %y'), '29 % 08 % 12')
        # not valid % formatter
        self.assertEqual(utils.strftime(d, '10% reduction in %Y'),
                         '10% reduction in 2012')
        self.assertEqual(utils.strftime(d, '%10 reduction in %Y'),
                         '%10 reduction in 2012')

        # with text
        self.assertEqual(utils.strftime(d, 'Published in %d-%m-%Y'),
                         'Published in 29-08-2012')

        # with non-ascii text
        self.assertEqual(utils.strftime(d, '%d/%m/%Y Øl trinken beim Besäufnis'),
                         '29/08/2012 Øl trinken beim Besäufnis')


    # test the output of utils.strftime in a different locale
    # Turkish locale
    @unittest.skipUnless(locale_available('tr_TR.UTF-8') or
                         locale_available('Turkish'),
                         'Turkish locale needed')
    def test_strftime_locale_dependent_turkish(self):
        # store current locale
        old_locale = locale.setlocale(locale.LC_TIME)

        if platform == 'win32':
            locale.setlocale(locale.LC_TIME, str('Turkish'))
        else:
            locale.setlocale(locale.LC_TIME, str('tr_TR.UTF-8'))

        d = datetime.date(2012, 8, 29)

        # simple
        self.assertEqual(utils.strftime(d, '%d %B %Y'), '29 Ağustos 2012')
        self.assertEqual(utils.strftime(d, '%A, %d %B %Y'),
                         'Çarşamba, 29 Ağustos 2012')

        # with text
        self.assertEqual(utils.strftime(d, 'Yayınlanma tarihi: %A, %d %B %Y'),
            'Yayınlanma tarihi: Çarşamba, 29 Ağustos 2012')

        # non-ascii format candidate (someone might pass it... for some reason)
        self.assertEqual(utils.strftime(d, '%Y yılında %üretim artışı'),
            '2012 yılında %üretim artışı')

        # restore locale back
        locale.setlocale(locale.LC_TIME, old_locale)


    # test the output of utils.strftime in a different locale
    # French locale
    @unittest.skipUnless(locale_available('fr_FR.UTF-8') or
                         locale_available('French'),
                         'French locale needed')
    def test_strftime_locale_dependent_french(self):
        # store current locale
        old_locale = locale.setlocale(locale.LC_TIME)

        if platform == 'win32':
            locale.setlocale(locale.LC_TIME, str('French'))
        else:
            locale.setlocale(locale.LC_TIME, str('fr_FR.UTF-8'))

        d = datetime.date(2012, 8, 29)

        # simple
        self.assertEqual(utils.strftime(d, '%d %B %Y'), '29 août 2012')

        # depending on OS, the first letter is m or M
        self.assertTrue(utils.strftime(d, '%A') in ('mercredi', 'Mercredi'))

        # with text
        self.assertEqual(utils.strftime(d, 'Écrit le %d %B %Y'),
            'Écrit le 29 août 2012')

        # non-ascii format candidate (someone might pass it... for some reason)
        self.assertEqual(utils.strftime(d, '%écrits en %Y'),
            '%écrits en 2012')

        # restore locale back
        locale.setlocale(locale.LC_TIME, old_locale)


class TestDateFormatter(unittest.TestCase):
    '''Tests that the output of DateFormatter jinja filter is same as
    utils.strftime'''

    def setUp(self):
        # prepare a temp content and output folder
        self.temp_content = mkdtemp(prefix='pelicantests.')
        self.temp_output = mkdtemp(prefix='pelicantests.')

        # prepare a template file
        template_dir = os.path.join(self.temp_content, 'template')
        template_path = os.path.join(template_dir, 'source.html')
        os.makedirs(template_dir)
        with open(template_path, 'w') as template_file:
            template_file.write('date = {{ date|strftime("%A, %d %B %Y") }}')
        self.date = datetime.date(2012, 8, 29)


    def tearDown(self):
        shutil.rmtree(self.temp_content)
        shutil.rmtree(self.temp_output)
        # reset locale to default
        locale.setlocale(locale.LC_ALL, '')


    @unittest.skipUnless(locale_available('fr_FR.UTF-8') or
                         locale_available('French'),
                         'French locale needed')
    def test_french_locale(self):
        settings = read_settings(
            override = {'LOCALE': locale.normalize('fr_FR.UTF-8'),
                        'TEMPLATE_PAGES': {'template/source.html':
                                           'generated/file.html'}})

        generator = TemplatePagesGenerator({'date': self.date}, settings,
                self.temp_content, '', self.temp_output, None)
        generator.env.filters.update({'strftime': utils.DateFormatter()})

        writer = Writer(self.temp_output, settings=settings)
        generator.generate_output(writer)

        output_path = os.path.join(
                self.temp_output, 'generated', 'file.html')

        # output file has been generated
        self.assertTrue(os.path.exists(output_path))

        # output content is correct
        with utils.pelican_open(output_path) as output_file:
            self.assertEqual(output_file,
                             utils.strftime(self.date, 'date = %A, %d %B %Y'))


    @unittest.skipUnless(locale_available('tr_TR.UTF-8') or
                         locale_available('Turkish'),
                         'Turkish locale needed')
    def test_turkish_locale(self):
        settings = read_settings(
            override = {'LOCALE': locale.normalize('tr_TR.UTF-8'),
                        'TEMPLATE_PAGES': {'template/source.html':
                                           'generated/file.html'}})

        generator = TemplatePagesGenerator({'date': self.date}, settings,
                self.temp_content, '', self.temp_output, None)
        generator.env.filters.update({'strftime': utils.DateFormatter()})

        writer = Writer(self.temp_output, settings=settings)
        generator.generate_output(writer)

        output_path = os.path.join(
                self.temp_output, 'generated', 'file.html')

        # output file has been generated
        self.assertTrue(os.path.exists(output_path))

        # output content is correct
        with utils.pelican_open(output_path) as output_file:
            self.assertEqual(output_file,
                             utils.strftime(self.date, 'date = %A, %d %B %Y'))
