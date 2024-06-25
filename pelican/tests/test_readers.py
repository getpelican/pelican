import os
from unittest.mock import PropertyMock, patch

from pelican import readers
from pelican.tests.support import get_settings, unittest
from pelican.utils import SafeDatetime

CUR_DIR = os.path.dirname(__file__)
CONTENT_PATH = os.path.join(CUR_DIR, "content")


def _path(*args):
    return os.path.join(CONTENT_PATH, *args)


class ReaderTest(unittest.TestCase):
    def read_file(self, path, **kwargs):
        # Isolate from future API changes to readers.read_file

        r = readers.Readers(settings=get_settings(**kwargs))
        return r.read_file(base_path=CONTENT_PATH, path=path)

    def assertDictHasSubset(self, dictionary, subset):
        for key, value in subset.items():
            if key in dictionary:
                real_value = dictionary.get(key)
                self.assertEqual(
                    value,
                    real_value,
                    f"Expected {key} to have value {value}, but was {real_value}",
                )
            else:
                self.fail(f"Expected {key} to have value {value}, but was not in Dict")

    def test_markdown_disabled(self):
        with patch.object(
            readers.MarkdownReader, "enabled", new_callable=PropertyMock
        ) as attr_mock:
            attr_mock.return_value = False
            readrs = readers.Readers(settings=get_settings())
            self.assertEqual(
                set(readers.MarkdownReader.file_extensions),
                readrs.disabled_readers.keys(),
            )
            for val in readrs.disabled_readers.values():
                self.assertEqual(readers.MarkdownReader, val.__class__)


class TestAssertDictHasSubset(ReaderTest):
    def setUp(self):
        self.dictionary = {"key-a": "val-a", "key-b": "val-b"}

    def tearDown(self):
        self.dictionary = None

    def test_subset(self):
        self.assertDictHasSubset(self.dictionary, {"key-a": "val-a"})

    def test_equal(self):
        self.assertDictHasSubset(self.dictionary, self.dictionary)

    def test_fail_not_set(self):
        self.assertRaisesRegex(
            AssertionError,
            r"Expected.*key-c.*to have value.*val-c.*but was not in Dict",
            self.assertDictHasSubset,
            self.dictionary,
            {"key-c": "val-c"},
        )

    def test_fail_wrong_val(self):
        self.assertRaisesRegex(
            AssertionError,
            r"Expected .*key-a.* to have value .*val-b.* but was .*val-a.*",
            self.assertDictHasSubset,
            self.dictionary,
            {"key-a": "val-b"},
        )


class DefaultReaderTest(ReaderTest):
    def test_readfile_unknown_extension(self):
        with self.assertRaises(TypeError):
            self.read_file(path="article_with_metadata.unknownextension")

    def test_readfile_path_metadata_implicit_dates(self):
        test_file = "article_with_metadata_implicit_dates.html"
        page = self.read_file(path=test_file, DEFAULT_DATE="fs")
        expected = {
            "date": SafeDatetime.fromtimestamp(os.stat(_path(test_file)).st_mtime),
            "modified": SafeDatetime.fromtimestamp(os.stat(_path(test_file)).st_mtime),
        }

        self.assertDictHasSubset(page.metadata, expected)

    def test_readfile_path_metadata_explicit_dates(self):
        test_file = "article_with_metadata_explicit_dates.html"
        page = self.read_file(path=test_file, DEFAULT_DATE="fs")
        expected = {
            "date": SafeDatetime(2010, 12, 2, 10, 14),
            "modified": SafeDatetime(2010, 12, 31, 23, 59),
        }

        self.assertDictHasSubset(page.metadata, expected)

    def test_readfile_path_metadata_implicit_date_explicit_modified(self):
        test_file = "article_with_metadata_implicit_date_explicit_modified.html"
        page = self.read_file(path=test_file, DEFAULT_DATE="fs")
        expected = {
            "date": SafeDatetime.fromtimestamp(os.stat(_path(test_file)).st_mtime),
            "modified": SafeDatetime(2010, 12, 2, 10, 14),
        }

        self.assertDictHasSubset(page.metadata, expected)

    def test_readfile_path_metadata_explicit_date_implicit_modified(self):
        test_file = "article_with_metadata_explicit_date_implicit_modified.html"
        page = self.read_file(path=test_file, DEFAULT_DATE="fs")
        expected = {
            "date": SafeDatetime(2010, 12, 2, 10, 14),
            "modified": SafeDatetime.fromtimestamp(os.stat(_path(test_file)).st_mtime),
        }

        self.assertDictHasSubset(page.metadata, expected)

    def test_find_empty_alt(self):
        with patch("pelican.readers.logger") as log_mock:
            content = [
                '<img alt="" src="test-image.png" width="300px" />',
                '<img src="test-image.png"  width="300px" alt="" />',
            ]

            for tag in content:
                readers.find_empty_alt(tag, "/test/path")
                log_mock.warning.assert_called_with(
                    "Empty alt attribute for image %s in %s",
                    "test-image.png",
                    "/test/path",
                    extra={"limit_msg": "Other images have empty alt attributes"},
                )


class RstReaderTest(ReaderTest):
    def test_article_with_metadata(self):
        page = self.read_file(path="article_with_metadata.rst")
        expected = {
            "category": "yeah",
            "author": "Alexis Métaireau",
            "title": "This is a super article !",
            "summary": '<p class="first last">Multi-line metadata should be'
            " supported\nas well as <strong>inline"
            " markup</strong> and stuff to &quot;typogrify"
            "&quot;...</p>\n",
            "date": SafeDatetime(2010, 12, 2, 10, 14),
            "modified": SafeDatetime(2010, 12, 2, 10, 20),
            "tags": ["foo", "bar", "foobar"],
            "custom_field": "http://notmyidea.org",
        }

        self.assertDictHasSubset(page.metadata, expected)

    def test_article_with_capitalized_metadata(self):
        page = self.read_file(path="article_with_capitalized_metadata.rst")
        expected = {
            "category": "yeah",
            "author": "Alexis Métaireau",
            "title": "This is a super article !",
            "summary": '<p class="first last">Multi-line metadata should be'
            " supported\nas well as <strong>inline"
            " markup</strong> and stuff to &quot;typogrify"
            "&quot;...</p>\n",
            "date": SafeDatetime(2010, 12, 2, 10, 14),
            "modified": SafeDatetime(2010, 12, 2, 10, 20),
            "tags": ["foo", "bar", "foobar"],
            "custom_field": "http://notmyidea.org",
        }

        self.assertDictHasSubset(page.metadata, expected)

    def test_article_with_filename_metadata(self):
        page = self.read_file(
            path="2012-11-29_rst_w_filename_meta#foo-bar.rst", FILENAME_METADATA=None
        )
        expected = {
            "category": "yeah",
            "author": "Alexis Métaireau",
            "title": "Rst with filename metadata",
            "reader": "rst",
        }
        self.assertDictHasSubset(page.metadata, expected)

        page = self.read_file(
            path="2012-11-29_rst_w_filename_meta#foo-bar.rst",
            FILENAME_METADATA=r"(?P<date>\d{4}-\d{2}-\d{2}).*",
        )
        expected = {
            "category": "yeah",
            "author": "Alexis Métaireau",
            "title": "Rst with filename metadata",
            "date": SafeDatetime(2012, 11, 29),
            "reader": "rst",
        }
        self.assertDictHasSubset(page.metadata, expected)

        page = self.read_file(
            path="2012-11-29_rst_w_filename_meta#foo-bar.rst",
            FILENAME_METADATA=(
                r"(?P<date>\d{4}-\d{2}-\d{2})"
                r"_(?P<Slug>.*)"
                r"#(?P<MyMeta>.*)-(?P<author>.*)"
            ),
        )
        expected = {
            "category": "yeah",
            "author": "Alexis Métaireau",
            "title": "Rst with filename metadata",
            "date": SafeDatetime(2012, 11, 29),
            "slug": "rst_w_filename_meta",
            "mymeta": "foo",
            "reader": "rst",
        }
        self.assertDictHasSubset(page.metadata, expected)

    def test_article_with_optional_filename_metadata(self):
        page = self.read_file(
            path="2012-11-29_rst_w_filename_meta#foo-bar.rst",
            FILENAME_METADATA=r"(?P<date>\d{4}-\d{2}-\d{2})?",
        )
        expected = {
            "date": SafeDatetime(2012, 11, 29),
            "reader": "rst",
        }
        self.assertDictHasSubset(page.metadata, expected)

        page = self.read_file(
            path="article.rst", FILENAME_METADATA=r"(?P<date>\d{4}-\d{2}-\d{2})?"
        )
        expected = {
            "reader": "rst",
        }
        self.assertDictHasSubset(page.metadata, expected)
        self.assertNotIn("date", page.metadata, "Date should not be set.")

    def test_article_metadata_key_lowercase(self):
        # Keys of metadata should be lowercase.
        reader = readers.RstReader(settings=get_settings())
        content, metadata = reader.read(_path("article_with_uppercase_metadata.rst"))

        self.assertIn("category", metadata, "Key should be lowercase.")
        self.assertEqual("Yeah", metadata.get("category"), "Value keeps case.")

    def test_article_extra_path_metadata(self):
        input_with_metadata = "2012-11-29_rst_w_filename_meta#foo-bar.rst"
        page_metadata = self.read_file(
            path=input_with_metadata,
            FILENAME_METADATA=(
                r"(?P<date>\d{4}-\d{2}-\d{2})"
                r"_(?P<Slug>.*)"
                r"#(?P<MyMeta>.*)-(?P<author>.*)"
            ),
            EXTRA_PATH_METADATA={
                input_with_metadata: {"key-1a": "value-1a", "key-1b": "value-1b"}
            },
        )
        expected_metadata = {
            "category": "yeah",
            "author": "Alexis Métaireau",
            "title": "Rst with filename metadata",
            "date": SafeDatetime(2012, 11, 29),
            "slug": "rst_w_filename_meta",
            "mymeta": "foo",
            "reader": "rst",
            "key-1a": "value-1a",
            "key-1b": "value-1b",
        }
        self.assertDictHasSubset(page_metadata.metadata, expected_metadata)

        input_file_path_without_metadata = "article.rst"
        page_without_metadata = self.read_file(
            path=input_file_path_without_metadata,
            EXTRA_PATH_METADATA={
                input_file_path_without_metadata: {"author": "Charlès Overwrite"}
            },
        )
        expected_without_metadata = {
            "category": "misc",
            "author": "Charlès Overwrite",
            "title": "Article title",
            "reader": "rst",
        }
        self.assertDictHasSubset(
            page_without_metadata.metadata, expected_without_metadata
        )

    def test_article_extra_path_metadata_dont_overwrite(self):
        # EXTRA_PATH_METADATA['author'] should get ignored
        # since we don't overwrite already set values
        input_file_path = "2012-11-29_rst_w_filename_meta#foo-bar.rst"
        page = self.read_file(
            path=input_file_path,
            FILENAME_METADATA=(
                r"(?P<date>\d{4}-\d{2}-\d{2})"
                r"_(?P<Slug>.*)"
                r"#(?P<MyMeta>.*)-(?P<orginalauthor>.*)"
            ),
            EXTRA_PATH_METADATA={
                input_file_path: {"author": "Charlès Overwrite", "key-1b": "value-1b"}
            },
        )
        expected = {
            "category": "yeah",
            "author": "Alexis Métaireau",
            "title": "Rst with filename metadata",
            "date": SafeDatetime(2012, 11, 29),
            "slug": "rst_w_filename_meta",
            "mymeta": "foo",
            "reader": "rst",
            "key-1b": "value-1b",
        }
        self.assertDictHasSubset(page.metadata, expected)

    def test_article_extra_path_metadata_recurse(self):
        parent = "TestCategory"
        notparent = "TestCategory/article"
        path = "TestCategory/article_without_category.rst"

        epm = {
            parent: {
                "epmr_inherit": parent,
                "epmr_override": parent,
            },
            notparent: {"epmr_bogus": notparent},
            path: {
                "epmr_override": path,
            },
        }
        expected_metadata = {
            "epmr_inherit": parent,
            "epmr_override": path,
        }

        page = self.read_file(path=path, EXTRA_PATH_METADATA=epm)
        self.assertDictHasSubset(page.metadata, expected_metadata)

        # Make sure vars aren't getting "inherited" by mistake...
        path = "article.rst"
        page = self.read_file(path=path, EXTRA_PATH_METADATA=epm)
        for k in expected_metadata.keys():
            self.assertNotIn(k, page.metadata)

        # Same, but for edge cases where one file's name is a prefix of
        # another.
        path = "TestCategory/article_without_category.rst"
        page = self.read_file(path=path, EXTRA_PATH_METADATA=epm)
        for k in epm[notparent].keys():
            self.assertNotIn(k, page.metadata)

    def test_typogrify(self):
        # if nothing is specified in the settings, the content should be
        # unmodified
        page = self.read_file(path="article.rst")
        expected = (
            "<p>THIS is some content. With some stuff to "
            "&quot;typogrify&quot;...</p>\n<p>Now with added "
            'support for <abbr title="three letter acronym">'
            "TLA</abbr>.</p>\n"
        )

        self.assertEqual(page.content, expected)

        try:
            # otherwise, typogrify should be applied
            page = self.read_file(path="article.rst", TYPOGRIFY=True)
            expected = (
                '<p><span class="caps">THIS</span> is some content. '
                "With some stuff to&nbsp;&#8220;typogrify&#8221;&#8230;</p>\n"
                '<p>Now with added support for <abbr title="three letter '
                'acronym"><span class="caps">TLA</span></abbr>.</p>\n'
            )

            self.assertEqual(page.content, expected)
        except ImportError:
            return unittest.skip("need the typogrify distribution")

    def test_typogrify_summary(self):
        # if nothing is specified in the settings, the summary should be
        # unmodified
        page = self.read_file(path="article_with_metadata.rst")
        expected = (
            '<p class="first last">Multi-line metadata should be'
            " supported\nas well as <strong>inline"
            " markup</strong> and stuff to &quot;typogrify"
            "&quot;...</p>\n"
        )

        self.assertEqual(page.metadata["summary"], expected)

        try:
            # otherwise, typogrify should be applied
            page = self.read_file(path="article_with_metadata.rst", TYPOGRIFY=True)
            expected = (
                '<p class="first last">Multi-line metadata should be'
                " supported\nas well as <strong>inline"
                " markup</strong> and stuff to&nbsp;&#8220;typogrify"
                "&#8221;&#8230;</p>\n"
            )

            self.assertEqual(page.metadata["summary"], expected)
        except ImportError:
            return unittest.skip("need the typogrify distribution")

    def test_typogrify_ignore_tags(self):
        try:
            # typogrify should be able to ignore user specified tags,
            # but tries to be clever with widont extension
            page = self.read_file(
                path="article.rst", TYPOGRIFY=True, TYPOGRIFY_IGNORE_TAGS=["p"]
            )
            expected = (
                "<p>THIS is some content. With some stuff to&nbsp;"
                "&quot;typogrify&quot;...</p>\n<p>Now with added "
                'support for <abbr title="three letter acronym">'
                "TLA</abbr>.</p>\n"
            )

            self.assertEqual(page.content, expected)

            # typogrify should ignore code blocks by default because
            # code blocks are composed inside the pre tag
            page = self.read_file(path="article_with_code_block.rst", TYPOGRIFY=True)

            expected = (
                "<p>An article with some&nbsp;code</p>\n"
                '<div class="highlight"><pre><span></span>'
                '<span class="n">x</span>'
                ' <span class="o">&amp;</span>'
                ' <span class="n">y</span>\n</pre></div>\n'
                "<p>A block&nbsp;quote:</p>\n<blockquote>\nx "
                '<span class="amp">&amp;</span> y</blockquote>\n'
                "<p>Normal:\nx"
                ' <span class="amp">&amp;</span>'
                "&nbsp;y"
                "</p>\n"
            )

            self.assertEqual(page.content, expected)

            # instruct typogrify to also ignore blockquotes
            page = self.read_file(
                path="article_with_code_block.rst",
                TYPOGRIFY=True,
                TYPOGRIFY_IGNORE_TAGS=["blockquote"],
            )

            expected = (
                "<p>An article with some&nbsp;code</p>\n"
                '<div class="highlight"><pre><span>'
                '</span><span class="n">x</span>'
                ' <span class="o">&amp;</span>'
                ' <span class="n">y</span>\n</pre></div>\n'
                "<p>A block&nbsp;quote:</p>\n<blockquote>\nx "
                "&amp; y</blockquote>\n"
                "<p>Normal:\nx"
                ' <span class="amp">&amp;</span>'
                "&nbsp;y"
                "</p>\n"
            )

            self.assertEqual(page.content, expected)
        except ImportError:
            return unittest.skip("need the typogrify distribution")
        except TypeError:
            return unittest.skip("need typogrify version 2.0.4 or later")

    def test_article_with_multiple_authors(self):
        page = self.read_file(path="article_with_multiple_authors.rst")
        expected = {"authors": ["First Author", "Second Author"]}

        self.assertDictHasSubset(page.metadata, expected)

    def test_article_with_multiple_authors_semicolon(self):
        page = self.read_file(path="article_with_multiple_authors_semicolon.rst")
        expected = {"authors": ["Author, First", "Author, Second"]}

        self.assertDictHasSubset(page.metadata, expected)

    def test_article_with_multiple_authors_list(self):
        page = self.read_file(path="article_with_multiple_authors_list.rst")
        expected = {"authors": ["Author, First", "Author, Second"]}

        self.assertDictHasSubset(page.metadata, expected)

    def test_default_date_formats(self):
        tuple_date = self.read_file(path="article.rst", DEFAULT_DATE=(2012, 5, 1))
        string_date = self.read_file(path="article.rst", DEFAULT_DATE="2012-05-01")

        self.assertEqual(tuple_date.metadata["date"], string_date.metadata["date"])

    def test_parse_error(self):
        # Verify that it raises an Exception, not nothing and not SystemExit or
        # some such
        with self.assertRaisesRegex(Exception, "underline too short"):
            self.read_file(path="../parse_error/parse_error.rst")

    def test_typogrify_dashes_config(self):
        # Test default config
        page = self.read_file(
            path="article_with_typogrify_dashes.rst",
            TYPOGRIFY=True,
            TYPOGRIFY_DASHES="default",
        )
        expected = "<p>One: -; Two: &#8212;; Three:&nbsp;&#8212;-</p>\n"
        expected_title = "One -, two &#8212;, three &#8212;-&nbsp;dashes!"

        self.assertEqual(page.content, expected)
        self.assertEqual(page.title, expected_title)

        # Test 'oldschool' variant
        page = self.read_file(
            path="article_with_typogrify_dashes.rst",
            TYPOGRIFY=True,
            TYPOGRIFY_DASHES="oldschool",
        )
        expected = "<p>One: -; Two: &#8211;; Three:&nbsp;&#8212;</p>\n"
        expected_title = "One -, two &#8211;, three &#8212;&nbsp;dashes!"

        self.assertEqual(page.content, expected)
        self.assertEqual(page.title, expected_title)

        # Test 'oldschool_inverted' variant
        page = self.read_file(
            path="article_with_typogrify_dashes.rst",
            TYPOGRIFY=True,
            TYPOGRIFY_DASHES="oldschool_inverted",
        )
        expected = "<p>One: -; Two: &#8212;; Three:&nbsp;&#8211;</p>\n"
        expected_title = "One -, two &#8212;, three &#8211;&nbsp;dashes!"

        self.assertEqual(page.content, expected)
        self.assertEqual(page.title, expected_title)


@unittest.skipUnless(readers.Markdown, "markdown isn't installed")
class MdReaderTest(ReaderTest):
    def test_article_with_metadata(self):
        reader = readers.MarkdownReader(settings=get_settings())
        content, metadata = reader.read(_path("article_with_md_extension.md"))
        expected = {
            "category": "test",
            "title": "Test md File",
            "summary": "<p>I have a lot to test</p>",
            "date": SafeDatetime(2010, 12, 2, 10, 14),
            "modified": SafeDatetime(2010, 12, 2, 10, 20),
            "tags": ["foo", "bar", "foobar"],
        }
        self.assertDictHasSubset(metadata, expected)

        content, metadata = reader.read(
            _path("article_with_markdown_and_nonascii_summary.md")
        )
        expected = {
            "title": "マックOS X 10.8でパイソンとVirtualenvをインストールと設定",
            "summary": "<p>パイソンとVirtualenvをまっくでインストールする方法について明確に説明します。</p>",
            "category": "指導書",
            "date": SafeDatetime(2012, 12, 20),
            "modified": SafeDatetime(2012, 12, 22),
            "tags": ["パイソン", "マック"],
            "slug": "python-virtualenv-on-mac-osx-mountain-lion-10.8",
        }
        self.assertDictHasSubset(metadata, expected)

    def test_article_with_footnote(self):
        settings = get_settings()
        ec = settings["MARKDOWN"]["extension_configs"]
        ec["markdown.extensions.footnotes"] = {"SEPARATOR": "-"}
        reader = readers.MarkdownReader(settings)
        content, metadata = reader.read(_path("article_with_markdown_and_footnote.md"))
        expected_content = (
            "<p>This is some content"
            '<sup id="fnref-1"><a class="footnote-ref" href="#fn-1"'
            ">1</a></sup>"
            " with some footnotes"
            '<sup id="fnref-footnote"><a class="footnote-ref" '
            'href="#fn-footnote">2</a></sup></p>\n'
            '<div class="footnote">\n'
            '<hr>\n<ol>\n<li id="fn-1">\n'
            "<p>Numbered footnote&#160;"
            '<a class="footnote-backref" href="#fnref-1" '
            'title="Jump back to footnote 1 in the text">&#8617;</a></p>\n'
            '</li>\n<li id="fn-footnote">\n'
            "<p>Named footnote&#160;"
            '<a class="footnote-backref" href="#fnref-footnote"'
            ' title="Jump back to footnote 2 in the text">&#8617;</a></p>\n'
            "</li>\n</ol>\n</div>"
        )
        expected_metadata = {
            "title": "Article with markdown containing footnotes",
            "summary": (
                "<p>Summary with <strong>inline</strong> markup "
                "<em>should</em> be supported.</p>"
            ),
            "date": SafeDatetime(2012, 10, 31),
            "modified": SafeDatetime(2012, 11, 1),
            "multiline": [
                "Line Metadata should be handle properly.",
                "See syntax of Meta-Data extension of Python Markdown package:",
                "If a line is indented by 4 or more spaces,",
                "that line is assumed to be an additional line of the value",
                "for the previous keyword.",
                "A keyword may have as many lines as desired.",
            ],
        }
        self.assertEqual(content, expected_content)
        self.assertDictHasSubset(metadata, expected_metadata)

    def test_article_with_file_extensions(self):
        reader = readers.MarkdownReader(settings=get_settings())
        # test to ensure the md file extension is being processed by the
        # correct reader
        content, metadata = reader.read(_path("article_with_md_extension.md"))
        expected = (
            "<h1>Test Markdown File Header</h1>\n"
            "<h2>Used for pelican test</h2>\n"
            "<p>The quick brown fox jumped over the lazy dog's back.</p>"
        )
        self.assertEqual(content, expected)
        # test to ensure the mkd file extension is being processed by the
        # correct reader
        content, metadata = reader.read(_path("article_with_mkd_extension.mkd"))
        expected = (
            "<h1>Test Markdown File Header</h1>\n<h2>Used for pelican"
            " test</h2>\n<p>This is another markdown test file.  Uses"
            " the mkd extension.</p>"
        )
        self.assertEqual(content, expected)
        # test to ensure the markdown file extension is being processed by the
        # correct reader
        content, metadata = reader.read(
            _path("article_with_markdown_extension.markdown")
        )
        expected = (
            "<h1>Test Markdown File Header</h1>\n<h2>Used for pelican"
            " test</h2>\n<p>This is another markdown test file.  Uses"
            " the markdown extension.</p>"
        )
        self.assertEqual(content, expected)
        # test to ensure the mdown file extension is being processed by the
        # correct reader
        content, metadata = reader.read(_path("article_with_mdown_extension.mdown"))
        expected = (
            "<h1>Test Markdown File Header</h1>\n<h2>Used for pelican"
            " test</h2>\n<p>This is another markdown test file.  Uses"
            " the mdown extension.</p>"
        )
        self.assertEqual(content, expected)

    def test_article_with_markdown_markup_extension(self):
        # test to ensure the markdown markup extension is being processed as
        # expected
        page = self.read_file(
            path="article_with_markdown_markup_extensions.md",
            MARKDOWN={
                "extension_configs": {
                    "markdown.extensions.toc": {},
                    "markdown.extensions.codehilite": {},
                    "markdown.extensions.extra": {},
                }
            },
        )
        expected = (
            '<div class="toc">\n'
            "<ul>\n"
            '<li><a href="#level1">Level1</a><ul>\n'
            '<li><a href="#level2">Level2</a></li>\n'
            "</ul>\n"
            "</li>\n"
            "</ul>\n"
            "</div>\n"
            '<h2 id="level1">Level1</h2>\n'
            '<h3 id="level2">Level2</h3>'
        )

        self.assertEqual(page.content, expected)

    def test_article_with_filename_metadata(self):
        page = self.read_file(
            path="2012-11-30_md_w_filename_meta#foo-bar.md", FILENAME_METADATA=None
        )
        expected = {
            "category": "yeah",
            "author": "Alexis Métaireau",
        }
        self.assertDictHasSubset(page.metadata, expected)

        page = self.read_file(
            path="2012-11-30_md_w_filename_meta#foo-bar.md",
            FILENAME_METADATA=r"(?P<date>\d{4}-\d{2}-\d{2}).*",
        )
        expected = {
            "category": "yeah",
            "author": "Alexis Métaireau",
            "date": SafeDatetime(2012, 11, 30),
        }
        self.assertDictHasSubset(page.metadata, expected)

        page = self.read_file(
            path="2012-11-30_md_w_filename_meta#foo-bar.md",
            FILENAME_METADATA=(
                r"(?P<date>\d{4}-\d{2}-\d{2})"
                r"_(?P<Slug>.*)"
                r"#(?P<MyMeta>.*)-(?P<author>.*)"
            ),
        )
        expected = {
            "category": "yeah",
            "author": "Alexis Métaireau",
            "date": SafeDatetime(2012, 11, 30),
            "slug": "md_w_filename_meta",
            "mymeta": "foo",
        }
        self.assertDictHasSubset(page.metadata, expected)

    def test_article_with_optional_filename_metadata(self):
        page = self.read_file(
            path="2012-11-30_md_w_filename_meta#foo-bar.md",
            FILENAME_METADATA=r"(?P<date>\d{4}-\d{2}-\d{2})?",
        )
        expected = {
            "date": SafeDatetime(2012, 11, 30),
            "reader": "markdown",
        }
        self.assertDictHasSubset(page.metadata, expected)

        page = self.read_file(
            path="empty.md", FILENAME_METADATA=r"(?P<date>\d{4}-\d{2}-\d{2})?"
        )
        expected = {
            "reader": "markdown",
        }
        self.assertDictHasSubset(page.metadata, expected)
        self.assertNotIn("date", page.metadata, "Date should not be set.")

    def test_duplicate_tags_or_authors_are_removed(self):
        reader = readers.MarkdownReader(settings=get_settings())
        content, metadata = reader.read(_path("article_with_duplicate_tags_authors.md"))
        expected = {
            "tags": ["foo", "bar", "foobar"],
            "authors": ["Author, First", "Author, Second"],
        }
        self.assertDictHasSubset(metadata, expected)

    def test_metadata_not_parsed_for_metadata(self):
        settings = get_settings()
        settings["FORMATTED_FIELDS"] = ["summary"]

        reader = readers.MarkdownReader(settings=settings)
        content, metadata = reader.read(
            _path("article_with_markdown_and_nested_metadata.md")
        )
        expected = {
            "title": "Article with markdown and nested summary metadata",
            "summary": "<p>Test: This metadata value looks like metadata</p>",
        }
        self.assertDictHasSubset(metadata, expected)

    def test_empty_file(self):
        reader = readers.MarkdownReader(settings=get_settings())
        content, metadata = reader.read(_path("empty.md"))

        self.assertEqual(metadata, {})
        self.assertEqual(content, "")

    def test_empty_file_with_bom(self):
        reader = readers.MarkdownReader(settings=get_settings())
        content, metadata = reader.read(_path("empty_with_bom.md"))

        self.assertEqual(metadata, {})
        self.assertEqual(content, "")

    def test_typogrify_dashes_config(self):
        # Test default config
        page = self.read_file(
            path="article_with_typogrify_dashes.md",
            TYPOGRIFY=True,
            TYPOGRIFY_DASHES="default",
        )
        expected = "<p>One: -; Two: &#8212;; Three:&nbsp;&#8212;-</p>"
        expected_title = "One -, two &#8212;, three &#8212;-&nbsp;dashes!"

        self.assertEqual(page.content, expected)
        self.assertEqual(page.title, expected_title)

        # Test 'oldschool' variant
        page = self.read_file(
            path="article_with_typogrify_dashes.md",
            TYPOGRIFY=True,
            TYPOGRIFY_DASHES="oldschool",
        )
        expected = "<p>One: -; Two: &#8211;; Three:&nbsp;&#8212;</p>"
        expected_title = "One -, two &#8211;, three &#8212;&nbsp;dashes!"

        self.assertEqual(page.content, expected)
        self.assertEqual(page.title, expected_title)

        # Test 'oldschool_inverted' variant
        page = self.read_file(
            path="article_with_typogrify_dashes.md",
            TYPOGRIFY=True,
            TYPOGRIFY_DASHES="oldschool_inverted",
        )
        expected = "<p>One: -; Two: &#8212;; Three:&nbsp;&#8211;</p>"
        expected_title = "One -, two &#8212;, three &#8211;&nbsp;dashes!"

        self.assertEqual(page.content, expected)
        self.assertEqual(page.title, expected_title)

    def test_metadata_has_no_discarded_data(self):
        md_filename = "article_with_markdown_and_empty_tags.md"

        r = readers.Readers(
            cache_name="cache", settings=get_settings(CACHE_CONTENT=True)
        )
        page = r.read_file(base_path=CONTENT_PATH, path=md_filename)

        __, cached_metadata = r.get_cached_data(_path(md_filename), (None, None))

        expected = {"title": "Article with markdown and empty tags"}
        self.assertEqual(cached_metadata, expected)
        self.assertNotIn("tags", page.metadata)
        self.assertDictHasSubset(page.metadata, expected)


class HTMLReaderTest(ReaderTest):
    def test_article_with_comments(self):
        page = self.read_file(path="article_with_comments.html")

        self.assertEqual(
            """
        Body content
        <!--  This comment is included (including extra whitespace)   -->
    """,
            page.content,
        )

    def test_article_with_keywords(self):
        page = self.read_file(path="article_with_keywords.html")
        expected = {
            "tags": ["foo", "bar", "foobar"],
        }

        self.assertDictHasSubset(page.metadata, expected)

    def test_article_with_metadata(self):
        page = self.read_file(path="article_with_metadata.html")
        expected = {
            "category": "yeah",
            "author": "Alexis Métaireau",
            "title": "This is a super article !",
            "summary": "Summary and stuff",
            "date": SafeDatetime(2010, 12, 2, 10, 14),
            "tags": ["foo", "bar", "foobar"],
            "custom_field": "http://notmyidea.org",
        }

        self.assertDictHasSubset(page.metadata, expected)

    def test_article_with_multiple_similar_metadata_tags(self):
        page = self.read_file(path="article_with_multiple_metadata_tags.html")
        expected = {
            "custom_field": ["https://getpelican.com", "https://www.eff.org"],
        }

        self.assertDictHasSubset(page.metadata, expected)

    def test_article_with_multiple_authors(self):
        page = self.read_file(path="article_with_multiple_authors.html")
        expected = {"authors": ["First Author", "Second Author"]}

        self.assertDictHasSubset(page.metadata, expected)

    def test_article_with_metadata_and_contents_attrib(self):
        page = self.read_file(path="article_with_metadata_and_contents.html")
        expected = {
            "category": "yeah",
            "author": "Alexis Métaireau",
            "title": "This is a super article !",
            "summary": "Summary and stuff",
            "date": SafeDatetime(2010, 12, 2, 10, 14),
            "tags": ["foo", "bar", "foobar"],
            "custom_field": "http://notmyidea.org",
        }
        self.assertDictHasSubset(page.metadata, expected)

    def test_article_with_null_attributes(self):
        page = self.read_file(path="article_with_null_attributes.html")

        self.assertEqual(
            """
        Ensure that empty attributes are copied properly.
        <input name="test" disabled style="" />
    """,
            page.content,
        )

    def test_article_with_attributes_containing_double_quotes(self):
        page = self.read_file(
            path="article_with_attributes_containing_" + "double_quotes.html"
        )
        self.assertEqual(
            """
        Ensure that if an attribute value contains a double quote, it is
        surrounded with single quotes, otherwise with double quotes.
        <span data-test="'single quoted string'">Span content</span>
        <span data-test='"double quoted string"'>Span content</span>
        <span data-test="string without quotes">Span content</span>
    """,
            page.content,
        )

    def test_article_metadata_key_lowercase(self):
        # Keys of metadata should be lowercase.
        page = self.read_file(path="article_with_uppercase_metadata.html")

        # Key should be lowercase
        self.assertIn("category", page.metadata, "Key should be lowercase.")

        # Value should keep cases
        self.assertEqual("Yeah", page.metadata.get("category"))

    def test_article_with_nonconformant_meta_tags(self):
        page = self.read_file(path="article_with_nonconformant_meta_tags.html")
        expected = {
            "summary": "Summary and stuff",
            "title": "Article with Nonconformant HTML meta tags",
        }

        self.assertDictHasSubset(page.metadata, expected)

    def test_article_with_inline_svg(self):
        page = self.read_file(path="article_with_inline_svg.html")
        expected = {
            "title": "Article with an inline SVG",
        }
        self.assertDictHasSubset(page.metadata, expected)
