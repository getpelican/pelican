# coding: utf-8
import unittest2
import os
import datetime
import tempfile
from pelican import Pelican
from pelican.settings import read_settings

CUR_DIR = os.path.dirname(__file__)
SETTINGS_PATH = os.path.join(CUR_DIR, 'default_conf.py')
CONTENT_PATH = os.path.join(CUR_DIR, 'content')
OUTPUT_PATH = tempfile.mkdtemp()

class OutputTest(unittest2.TestCase):

    def setUp(self):
        self.pelican = Pelican(settings=read_settings(SETTINGS_PATH), 
                               path=CONTENT_PATH, output_path=OUTPUT_PATH, 
                               delete_outputdir=True)

    def test_output(self):
        self.pelican.run()
        self.assertListEqual(os.listdir(self.pelican.output_path), 
                             ['archives.html',
                              'author',
                              'categories.html',
                              'category',
                              'feeds',
                              'index.html',
                              'tag',
                              'tags.html',
                              'theme',
                              'this-is-a-super-article.html',
                              'this-is-a-super-article.txt'])
        self.assertEqual(open(os.path.join(OUTPUT_PATH, 'this-is-a-super-article.txt')).read(),
                         open(os.path.join(CUR_DIR, 'content', 'article_with_metadata.rst')).read())
