import os
import re
from posixpath import join as posix_join
from unittest.mock import patch

from pelican.settings import DEFAULT_CONFIG
from pelican.tests.support import (
    TestCaseWithCLocale,
    mute,
    skipIfNoExecutable,
    temporary_folder,
    unittest,
)
from pelican.tools.pelican_import import (
    blogger2fields,
    build_header,
    build_markdown_header,
    decode_wp_content,
    download_attachments,
    fields2pelican,
    get_attachments,
    medium_slug,
    mediumpost2fields,
    mediumposts2fields,
    strip_medium_post_content,
    tumblr2fields,
    wp2fields,
)
from pelican.utils import path_to_file_url, slugify

CUR_DIR = os.path.abspath(os.path.dirname(__file__))
BLOGGER_XML_SAMPLE = os.path.join(CUR_DIR, "content", "bloggerexport.xml")
WORDPRESS_XML_SAMPLE = os.path.join(CUR_DIR, "content", "wordpressexport.xml")
WORDPRESS_ENCODED_CONTENT_SAMPLE = os.path.join(
    CUR_DIR, "content", "wordpress_content_encoded"
)
WORDPRESS_DECODED_CONTENT_SAMPLE = os.path.join(
    CUR_DIR, "content", "wordpress_content_decoded"
)

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = False

try:
    import bs4.builder._lxml as LXML
except ImportError:
    LXML = False


@skipIfNoExecutable(["pandoc", "--version"])
@unittest.skipUnless(BeautifulSoup, "Needs BeautifulSoup module")
class TestBloggerXmlImporter(TestCaseWithCLocale):
    def setUp(self):
        super().setUp()
        self.posts = blogger2fields(BLOGGER_XML_SAMPLE)

    def test_recognise_kind_and_title(self):
        """Check that importer only outputs pages, articles and comments,
        that these are correctly identified and that titles are correct.
        """
        test_posts = list(self.posts)
        kinds = {x[8] for x in test_posts}
        self.assertEqual({"page", "article", "comment"}, kinds)
        page_titles = {x[0] for x in test_posts if x[8] == "page"}
        self.assertEqual({"Test page", "Test page 2"}, page_titles)
        article_titles = {x[0] for x in test_posts if x[8] == "article"}
        self.assertEqual(
            {"Black as Egypt's Night", "The Steel Windpipe"}, article_titles
        )
        comment_titles = {x[0] for x in test_posts if x[8] == "comment"}
        self.assertEqual(
            {"Mishka, always a pleasure to read your adventures!..."}, comment_titles
        )

    def test_recognise_status_with_correct_filename(self):
        """Check that importerer outputs only statuses 'published' and 'draft',
        that these are correctly identified and that filenames are correct.
        """
        test_posts = list(self.posts)
        statuses = {x[7] for x in test_posts}
        self.assertEqual({"published", "draft"}, statuses)

        draft_filenames = {x[2] for x in test_posts if x[7] == "draft"}
        # draft filenames are id-based
        self.assertEqual(
            {"page-4386962582497458967", "post-1276418104709695660"}, draft_filenames
        )

        published_filenames = {x[2] for x in test_posts if x[7] == "published"}
        # published filenames are url-based, except comments
        self.assertEqual(
            {"the-steel-windpipe", "test-page", "post-5590533389087749201"},
            published_filenames,
        )


@skipIfNoExecutable(["pandoc", "--version"])
@unittest.skipUnless(BeautifulSoup, "Needs BeautifulSoup module")
class TestWordpressXmlImporter(TestCaseWithCLocale):
    def setUp(self):
        super().setUp()
        self.posts = wp2fields(WORDPRESS_XML_SAMPLE)
        self.custposts = wp2fields(WORDPRESS_XML_SAMPLE, True)

    def test_ignore_empty_posts(self):
        self.assertTrue(self.posts)
        for (
            title,
            _content,
            _fname,
            _date,
            _author,
            _categ,
            _tags,
            _status,
            _kind,
            _format,
        ) in self.posts:
            self.assertTrue(title.strip())

    def test_recognise_page_kind(self):
        """Check that we recognise pages in wordpress, as opposed to posts"""
        self.assertTrue(self.posts)
        # Collect (title, filename, kind) of non-empty posts recognised as page
        pages_data = []
        for (
            title,
            _content,
            fname,
            _date,
            _author,
            _categ,
            _tags,
            _status,
            kind,
            _format,
        ) in self.posts:
            if kind == "page":
                pages_data.append((title, fname))
        self.assertEqual(2, len(pages_data))
        self.assertEqual(("Page", "contact"), pages_data[0])
        self.assertEqual(("Empty Page", "empty"), pages_data[1])

    def test_dirpage_directive_for_page_kind(self):
        silent_f2p = mute(True)(fields2pelican)
        test_post = filter(lambda p: p[0].startswith("Empty Page"), self.posts)
        with temporary_folder() as temp:
            fname = next(iter(silent_f2p(test_post, "markdown", temp, dirpage=True)))
            self.assertTrue(fname.endswith(f"pages{os.path.sep}empty.md"))

    def test_dircat(self):
        silent_f2p = mute(True)(fields2pelican)
        test_posts = [
            post
            for post in self.posts
            # check post has a category
            if len(post[5]) > 0
        ]
        with temporary_folder() as temp:
            fnames = list(silent_f2p(test_posts, "markdown", temp, dircat=True))
        subs = DEFAULT_CONFIG["SLUG_REGEX_SUBSTITUTIONS"]
        index = 0
        for post in test_posts:
            name = post[2]
            category = slugify(post[5][0], regex_subs=subs, preserve_case=True)
            name += ".md"
            filename = os.path.join(category, name)
            out_name = fnames[index]
            self.assertTrue(out_name.endswith(filename))
            index += 1

    def test_unless_custom_post_all_items_should_be_pages_or_posts(self):
        self.assertTrue(self.posts)
        pages_data = []
        for (
            title,
            _content,
            fname,
            _date,
            _author,
            _categ,
            _tags,
            _status,
            kind,
            _format,
        ) in self.posts:
            if kind in {"page", "article"}:
                pass
            else:
                pages_data.append((title, fname))
        self.assertEqual(0, len(pages_data))

    def test_recognise_custom_post_type(self):
        self.assertTrue(self.custposts)
        cust_data = []
        for (
            title,
            _content,
            _fname,
            _date,
            _author,
            _categ,
            _tags,
            _status,
            kind,
            _format,
        ) in self.custposts:
            if kind in {"page", "article"}:
                pass
            else:
                cust_data.append((title, kind))
        self.assertEqual(3, len(cust_data))
        self.assertEqual(("A custom post in category 4", "custom1"), cust_data[0])
        self.assertEqual(("A custom post in category 5", "custom1"), cust_data[1])
        self.assertEqual(
            ("A 2nd custom post type also in category 5", "custom2"), cust_data[2]
        )

    def test_custom_posts_put_in_own_dir(self):
        silent_f2p = mute(True)(fields2pelican)
        test_posts = []
        for post in self.custposts:
            # check post kind
            if post[8] == "article" or post[8] == "page":
                pass
            else:
                test_posts.append(post)
        with temporary_folder() as temp:
            fnames = list(silent_f2p(test_posts, "markdown", temp, wp_custpost=True))
        index = 0
        for post in test_posts:
            name = post[2]
            kind = post[8]
            name += ".md"
            filename = os.path.join(kind, name)
            out_name = fnames[index]
            self.assertTrue(out_name.endswith(filename))
            index += 1

    def test_custom_posts_put_in_own_dir_and_catagory_sub_dir(self):
        silent_f2p = mute(True)(fields2pelican)
        test_posts = []
        for post in self.custposts:
            # check post kind
            if post[8] == "article" or post[8] == "page":
                pass
            else:
                test_posts.append(post)
        with temporary_folder() as temp:
            fnames = list(
                silent_f2p(test_posts, "markdown", temp, wp_custpost=True, dircat=True)
            )
        subs = DEFAULT_CONFIG["SLUG_REGEX_SUBSTITUTIONS"]
        index = 0
        for post in test_posts:
            name = post[2]
            kind = post[8]
            category = slugify(post[5][0], regex_subs=subs, preserve_case=True)
            name += ".md"
            filename = os.path.join(kind, category, name)
            out_name = fnames[index]
            self.assertTrue(out_name.endswith(filename))
            index += 1

    def test_wp_custpost_true_dirpage_false(self):
        # pages should only be put in their own directory when dirpage = True
        silent_f2p = mute(True)(fields2pelican)
        test_posts = [
            post
            for post in self.custposts
            # check post kind
            if post[8] == "page"
        ]
        with temporary_folder() as temp:
            fnames = list(
                silent_f2p(
                    test_posts, "markdown", temp, wp_custpost=True, dirpage=False
                )
            )
        index = 0
        for post in test_posts:
            name = post[2]
            name += ".md"
            filename = os.path.join("pages", name)
            out_name = fnames[index]
            self.assertFalse(out_name.endswith(filename))

    def test_can_toggle_raw_html_code_parsing(self):
        test_posts = list(self.posts)

        def r(f):
            with open(f, encoding="utf-8") as infile:
                return infile.read()

        silent_f2p = mute(True)(fields2pelican)

        with temporary_folder() as temp:
            rst_files = (r(f) for f in silent_f2p(test_posts, "markdown", temp))
            self.assertTrue(any("<iframe" in rst for rst in rst_files))
            rst_files = (
                r(f) for f in silent_f2p(test_posts, "markdown", temp, strip_raw=True)
            )
            self.assertFalse(any("<iframe" in rst for rst in rst_files))
            # no effect in rst
            rst_files = (r(f) for f in silent_f2p(test_posts, "rst", temp))
            self.assertFalse(any("<iframe" in rst for rst in rst_files))
            rst_files = (
                r(f) for f in silent_f2p(test_posts, "rst", temp, strip_raw=True)
            )
            self.assertFalse(any("<iframe" in rst for rst in rst_files))

    def test_decode_html_entities_in_titles(self):
        test_posts = [post for post in self.posts if post[2] == "html-entity-test"]
        self.assertEqual(len(test_posts), 1)

        post = test_posts[0]
        title = post[0]
        self.assertTrue(
            title,
            "A normal post with some <html> entities in "
            "the title. You can't miss them.",
        )
        self.assertNotIn("&", title)

    def test_decode_wp_content_returns_empty(self):
        """Check that given an empty string we return an empty string."""
        self.assertEqual(decode_wp_content(""), "")

    def test_decode_wp_content(self):
        """Check that we can decode a wordpress content string."""
        with open(WORDPRESS_ENCODED_CONTENT_SAMPLE) as encoded_file:
            encoded_content = encoded_file.read()
            with open(WORDPRESS_DECODED_CONTENT_SAMPLE) as decoded_file:
                decoded_content = decoded_file.read()
                self.assertEqual(
                    decode_wp_content(encoded_content, br=False), decoded_content
                )

    def test_preserve_verbatim_formatting(self):
        def r(f):
            with open(f, encoding="utf-8") as infile:
                return infile.read()

        silent_f2p = mute(True)(fields2pelican)
        test_post = filter(lambda p: p[0].startswith("Code in List"), self.posts)
        with temporary_folder() as temp:
            md = next(r(f) for f in silent_f2p(test_post, "markdown", temp))
            self.assertTrue(re.search(r"\s+a = \[1, 2, 3\]", md))
            self.assertTrue(re.search(r"\s+b = \[4, 5, 6\]", md))

            for_line = re.search(r"\s+for i in zip\(a, b\):", md).group(0)
            print_line = re.search(r"\s+print i", md).group(0)
            self.assertTrue(for_line.rindex("for") < print_line.rindex("print"))

    def test_code_in_list(self):
        def r(f):
            with open(f, encoding="utf-8") as infile:
                return infile.read()

        silent_f2p = mute(True)(fields2pelican)
        test_post = filter(lambda p: p[0].startswith("Code in List"), self.posts)
        with temporary_folder() as temp:
            md = next(r(f) for f in silent_f2p(test_post, "markdown", temp))
            sample_line = re.search(r"- This is a code sample", md).group(0)
            code_line = re.search(r"\s+a = \[1, 2, 3\]", md).group(0)
            self.assertTrue(sample_line.rindex("This") < code_line.rindex("a"))

    def test_dont_use_smart_quotes(self):
        def r(f):
            with open(f, encoding="utf-8") as infile:
                return infile.read()

        silent_f2p = mute(True)(fields2pelican)
        test_post = filter(lambda p: p[0].startswith("Post with raw data"), self.posts)
        with temporary_folder() as temp:
            md = next(r(f) for f in silent_f2p(test_post, "markdown", temp))
            escaped_quotes = re.search(r'\\[\'"“”‘’]', md)  # noqa: RUF001
            self.assertFalse(escaped_quotes)

    def test_convert_caption_to_figure(self):
        def r(f):
            with open(f, encoding="utf-8") as infile:
                return infile.read()

        silent_f2p = mute(True)(fields2pelican)
        test_post = filter(lambda p: p[0].startswith("Caption on image"), self.posts)
        with temporary_folder() as temp:
            md = next(r(f) for f in silent_f2p(test_post, "markdown", temp))

        caption = re.search(r"\[caption", md)
        self.assertFalse(caption)

        for occurence in [
            "/theme/img/xpelican.png.pagespeed.ic.Rjep0025-y.png",
            "/theme/img/xpelican-3.png.pagespeed.ic.m-NAIdRCOM.png",
            "/theme/img/xpelican.png.pagespeed.ic.Rjep0025-y.png",
            "This is a pelican",
            "This also a pelican",
            "Yet another pelican",
        ]:
            # pandoc 2.x converts into ![text](src)
            # pandoc 3.x converts into <figure>src<figcaption>text</figcaption></figure>
            self.assertIn(occurence, md)


class TestBuildHeader(unittest.TestCase):
    def test_build_header(self):
        header = build_header("test", None, None, None, None, None)
        self.assertEqual(header, "test\n####\n\n")

    def test_build_header_with_fields(self):
        header_data = [
            "Test Post",
            "2014-11-04",
            "Alexis Métaireau",
            ["Programming"],
            ["Pelican", "Python"],
            "test-post",
        ]

        expected_docutils = "\n".join(
            [
                "Test Post",
                "#########",
                ":date: 2014-11-04",
                ":author: Alexis Métaireau",
                ":category: Programming",
                ":tags: Pelican, Python",
                ":slug: test-post",
                "\n",
            ]
        )

        expected_md = "\n".join(
            [
                "Title: Test Post",
                "Date: 2014-11-04",
                "Author: Alexis Métaireau",
                "Category: Programming",
                "Tags: Pelican, Python",
                "Slug: test-post",
                "\n",
            ]
        )

        self.assertEqual(build_header(*header_data), expected_docutils)
        self.assertEqual(build_markdown_header(*header_data), expected_md)

    def test_build_header_with_east_asian_characters(self):
        header = build_header(
            "これは広い幅の文字だけで構成されたタイトルです",
            None,
            None,
            None,
            None,
            None,
        )

        self.assertEqual(
            header,
            (
                "これは広い幅の文字だけで構成されたタイトルです\n"
                "##############################################"
                "\n\n"
            ),
        )

    def test_galleries_added_to_header(self):
        header = build_header(
            "test",
            None,
            None,
            None,
            None,
            None,
            attachments=["output/test1", "output/test2"],
        )
        self.assertEqual(
            header, ("test\n####\n:attachments: output/test1, output/test2\n\n")
        )

    def test_galleries_added_to_markdown_header(self):
        header = build_markdown_header(
            "test",
            None,
            None,
            None,
            None,
            None,
            attachments=["output/test1", "output/test2"],
        )
        self.assertEqual(
            header, "Title: test\nAttachments: output/test1, output/test2\n\n"
        )


@unittest.skipUnless(BeautifulSoup, "Needs BeautifulSoup module")
@unittest.skipUnless(LXML, "Needs lxml module")
class TestWordpressXMLAttachements(TestCaseWithCLocale):
    def setUp(self):
        super().setUp()
        self.attachments = get_attachments(WORDPRESS_XML_SAMPLE)

    def test_recognise_attachments(self):
        self.assertTrue(self.attachments)
        self.assertEqual(3, len(self.attachments.keys()))

    def test_attachments_associated_with_correct_post(self):
        self.assertTrue(self.attachments)
        for post in self.attachments.keys():
            if post is None:
                expected = {
                    (
                        "https://upload.wikimedia.org/wikipedia/commons/"
                        "thumb/2/2c/Pelican_lakes_entrance02.jpg/"
                        "240px-Pelican_lakes_entrance02.jpg"
                    )
                }
                self.assertEqual(self.attachments[post], expected)
            elif post == "with-excerpt":
                expected_invalid = (
                    "http://thisurlisinvalid.notarealdomain/not_an_image.jpg"
                )
                expected_pelikan = (
                    "http://en.wikipedia.org/wiki/File:Pelikan_Walvis_Bay.jpg"
                )
                self.assertEqual(
                    self.attachments[post], {expected_invalid, expected_pelikan}
                )
            elif post == "with-tags":
                expected_invalid = "http://thisurlisinvalid.notarealdomain"
                self.assertEqual(self.attachments[post], {expected_invalid})
            else:
                self.fail(f"all attachments should match to a filename or None, {post}")

    def test_download_attachments(self):
        real_file = os.path.join(CUR_DIR, "content/article.rst")
        good_url = path_to_file_url(real_file)
        bad_url = "http://localhost:1/not_a_file.txt"
        silent_da = mute()(download_attachments)
        with temporary_folder() as temp:
            locations = list(silent_da(temp, [good_url, bad_url]))
            self.assertEqual(1, len(locations))
            directory = locations[0]
            self.assertTrue(
                directory.endswith(posix_join("content", "article.rst")), directory
            )


class TestTumblrImporter(TestCaseWithCLocale):
    @patch("pelican.tools.pelican_import._get_tumblr_posts")
    def test_posts(self, get):
        def get_posts(api_key, blogname, offset=0):
            if offset > 0:
                return []

            return [
                {
                    "type": "photo",
                    "blog_name": "testy",
                    "date": "2019-11-07 21:26:40 UTC",
                    "timestamp": 1573162000,
                    "format": "html",
                    "slug": "a-slug",
                    "tags": ["economics"],
                    "state": "published",
                    "photos": [
                        {
                            "caption": "",
                            "original_size": {
                                "url": "https://..fccdc2360ba7182a.jpg",
                                "width": 634,
                                "height": 789,
                            },
                        }
                    ],
                }
            ]

        get.side_effect = get_posts

        posts = list(tumblr2fields("api_key", "blogname"))
        self.assertEqual(
            [
                (
                    "Photo",
                    '<img alt="" src="https://..fccdc2360ba7182a.jpg" />\n',
                    "2019-11-07-a-slug",
                    "2019-11-07 21:26:40+0000",
                    "testy",
                    ["photo"],
                    ["economics"],
                    "published",
                    "article",
                    "html",
                )
            ],
            posts,
            posts,
        )

    @patch("pelican.tools.pelican_import._get_tumblr_posts")
    def test_video_embed(self, get):
        def get_posts(api_key, blogname, offset=0):
            if offset > 0:
                return []

            return [
                {
                    "type": "video",
                    "blog_name": "testy",
                    "slug": "the-slug",
                    "date": "2017-07-07 20:31:41 UTC",
                    "timestamp": 1499459501,
                    "state": "published",
                    "format": "html",
                    "tags": [],
                    "source_url": "https://href.li/?https://www.youtube.com/a",
                    "source_title": "youtube.com",
                    "caption": "<p>Caption</p>",
                    "player": [
                        {"width": 250, "embed_code": "<iframe>1</iframe>"},
                        {"width": 400, "embed_code": "<iframe>2</iframe>"},
                        {"width": 500, "embed_code": "<iframe>3</iframe>"},
                    ],
                    "video_type": "youtube",
                }
            ]

        get.side_effect = get_posts

        posts = list(tumblr2fields("api_key", "blogname"))
        self.assertEqual(
            [
                (
                    "youtube.com",
                    '<p><a href="https://href.li/?'
                    'https://www.youtube.com/a">via</a></p>\n<p>Caption</p>'
                    "<iframe>1</iframe>\n"
                    "<iframe>2</iframe>\n"
                    "<iframe>3</iframe>\n",
                    "2017-07-07-the-slug",
                    "2017-07-07 20:31:41+0000",
                    "testy",
                    ["video"],
                    [],
                    "published",
                    "article",
                    "html",
                )
            ],
            posts,
            posts,
        )

    @patch("pelican.tools.pelican_import._get_tumblr_posts")
    def test_broken_video_embed(self, get):
        def get_posts(api_key, blogname, offset=0):
            if offset > 0:
                return []

            return [
                {
                    "type": "video",
                    "blog_name": "testy",
                    "slug": "the-slug",
                    "date": "2016-08-14 16:37:35 UTC",
                    "timestamp": 1471192655,
                    "state": "published",
                    "format": "html",
                    "tags": ["interviews"],
                    "source_url": "https://href.li/?https://www.youtube.com/watch?v=b",
                    "source_title": "youtube.com",
                    "caption": "<p>Caption</p>",
                    "player": [
                        {
                            "width": 250,
                            # If video is gone, embed_code is False
                            "embed_code": False,
                        },
                        {"width": 400, "embed_code": False},
                        {"width": 500, "embed_code": False},
                    ],
                    "video_type": "youtube",
                }
            ]

        get.side_effect = get_posts

        posts = list(tumblr2fields("api_key", "blogname"))
        self.assertEqual(
            [
                (
                    "youtube.com",
                    '<p><a href="https://href.li/?https://www.youtube.com/watch?'
                    'v=b">via</a></p>\n<p>Caption</p>'
                    "<p>(This video isn't available anymore.)</p>\n",
                    "2016-08-14-the-slug",
                    "2016-08-14 16:37:35+0000",
                    "testy",
                    ["video"],
                    ["interviews"],
                    "published",
                    "article",
                    "html",
                )
            ],
            posts,
            posts,
        )


class TestMediumImporter(TestCaseWithCLocale):
    def setUp(self):
        super().setUp()
        self.test_content_root = "pelican/tests/content"
        # The content coming out of parsing is similar, but not the same.
        # Beautiful soup rearranges the order of attributes, for example.
        # So, we keep a copy of the content for the test.
        content_filename = f"{self.test_content_root}/medium_post_content.txt"
        with open(content_filename, encoding="utf-8") as the_content_file:
            # Many editors and scripts add a final newline, so live with that
            # in our test
            the_content = the_content_file.read()
            assert the_content[-1] == "\n"
            the_content = the_content[:-1]
        self.post_tuple = (
            "A title",
            the_content,
            # slug:
            "2017-04-21-medium-post",
            "2017-04-21 17:11",
            "User Name",
            None,
            (),
            "published",
            "article",
            "html",
        )

    def test_mediumpost2field(self):
        """Parse one post"""
        post_filename = f"{self.test_content_root}/medium_posts/2017-04-21_-medium-post--d1bf01d62ba3.html"
        val = mediumpost2fields(post_filename)
        self.assertEqual(self.post_tuple, val, val)

    def test_mediumposts2field(self):
        """Parse all posts in an export directory"""
        posts = list(mediumposts2fields(f"{self.test_content_root}/medium_posts"))
        self.assertEqual(1, len(posts))
        self.assertEqual(self.post_tuple, posts[0])

    def test_strip_content(self):
        """Strip out unhelpful tags"""
        html_doc = (
            "<section>This keeps <i>lots</i> of <b>tags</b>, but not "
            "the <section>section</section> tags</section>"
        )
        soup = BeautifulSoup(html_doc, "html.parser")
        self.assertEqual(
            "This keeps <i>lots</i> of <b>tags</b>, but not the section tags",
            strip_medium_post_content(soup),
        )

    def test_medium_slug(self):
        # Remove hex stuff at the end
        self.assertEqual(
            "2017-04-27_A-long-title",
            medium_slug(
                "medium-export/posts/2017-04-27_A-long-title--2971442227dd.html"
            ),
        )
        # Remove "--DRAFT" at the end
        self.assertEqual(
            "2017-04-27_A-long-title",
            medium_slug("medium-export/posts/2017-04-27_A-long-title--DRAFT.html"),
        )
        # Remove both (which happens)
        self.assertEqual(
            "draft_How-to-do", medium_slug("draft_How-to-do--DRAFT--87225c81dddd.html")
        )
        # If no hex stuff, leave it alone
        self.assertEqual(
            "2017-04-27_A-long-title",
            medium_slug("medium-export/posts/2017-04-27_A-long-title.html"),
        )
