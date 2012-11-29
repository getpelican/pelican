# -*- coding: utf-8 -*-
import shutil
import os
import datetime
import time

from pelican import utils
from .support import get_article, unittest
from pelican.utils import NoFilesError


class TestUtils(unittest.TestCase):

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
            self.assertEquals(utils.get_date(value), expected, value)

        # invalid ones
        invalid_dates = ('2010-110-12', 'yay')
        for item in invalid_dates:
            self.assertRaises(ValueError, utils.get_date, item)

    def test_slugify(self):

        samples = (('this is a test', 'this-is-a-test'),
                   ('this        is a test', 'this-is-a-test'),
                   (u'this → is ← a ↑ test', 'this-is-a-test'),
                   ('this--is---a test', 'this-is-a-test'),
                   (u'unicode測試許功蓋，你看到了嗎？', 'unicodece-shi-xu-gong-gai-ni-kan-dao-liao-ma'),
                   (u'大飯原発４号機、１８日夜起動へ', 'da-fan-yuan-fa-4hao-ji-18ri-ye-qi-dong-he'),)

        for value, expected in samples:
            self.assertEquals(utils.slugify(value), expected)

    def test_get_relative_path(self):

        samples = (('test/test.html', '..'),
                   ('test/test/test.html', '../..'),
                   ('test.html', '.'))

        for value, expected in samples:
            self.assertEquals(utils.get_relative_path(value), expected)

    def test_process_translations(self):
        # create a bunch of articles
        fr_article1 = get_article(lang='fr', slug='yay', title='Un titre',
                                  content='en français')
        en_article1 = get_article(lang='en', slug='yay', title='A title',
                                  content='in english')

        articles = [fr_article1, en_article1]

        index, trans = utils.process_translations(articles)

        self.assertIn(en_article1, index)
        self.assertIn(fr_article1, trans)
        self.assertNotIn(en_article1, trans)
        self.assertNotIn(fr_article1, index)

    def test_files_changed(self):
        """Test if file changes are correctly detected
        Make sure to handle not getting any files correctly"""

        path = os.path.join(os.path.dirname(__file__), 'content')
        filename = os.path.join(path, 'article_with_metadata.rst')
        changed = utils.files_changed(path, 'rst')
        self.assertEquals(changed, True)

        changed = utils.files_changed(path, 'rst')
        self.assertEquals(changed, False)

        t = time.time()
        os.utime(filename, (t, t))
        changed = utils.files_changed(path, 'rst')
        self.assertEquals(changed, True)
        self.assertAlmostEqual(utils.LAST_MTIME, t, delta=1)

        empty_path = os.path.join(os.path.dirname(__file__), 'empty')
        try:
            os.mkdir(empty_path)
            os.mkdir(os.path.join(empty_path, "empty_folder"))
            shutil.copy(__file__, empty_path)
            with self.assertRaises(NoFilesError):
                utils.files_changed(empty_path, 'rst')
        except OSError:
            self.fail("OSError Exception in test_files_changed test")
        finally:
            shutil.rmtree(empty_path, True)

    def test_clean_output_dir(self):
        test_directory = os.path.join(os.path.dirname(__file__), 'clean_output')
        content = os.path.join(os.path.dirname(__file__), 'content')
        shutil.copytree(content, test_directory)
        utils.clean_output_dir(test_directory)
        self.assertTrue(os.path.isdir(test_directory))
        self.assertListEqual([], os.listdir(test_directory))
        shutil.rmtree(test_directory)

    def test_clean_output_dir_not_there(self):
        test_directory = os.path.join(os.path.dirname(__file__), 'does_not_exist')
        utils.clean_output_dir(test_directory)
        self.assertTrue(not os.path.exists(test_directory))

    def test_clean_output_dir_is_file(self):
        test_directory = os.path.join(os.path.dirname(__file__), 'this_is_a_file')
        f = open(test_directory, 'w')
        f.write('')
        f.close()
        utils.clean_output_dir(test_directory)
        self.assertTrue(not os.path.exists(test_directory))
