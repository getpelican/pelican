AUTHOR = "Alexis Métaireau"
SITENAME = "Alexis' log"
SITEURL = "http://blog.notmyidea.org"
TIMEZONE = "Europe/Paris"

# can be useful in development, but set to False when you're ready to publish
RELATIVE_URLS = True

GITHUB_URL = "http://github.com/ametaireau/"
DISQUS_SITENAME = "blog-notmyidea"
PDF_GENERATOR = False
REVERSE_CATEGORY_ORDER = True
LOCALE = "fr_FR.UTF-8"
DEFAULT_PAGINATION = 4
DEFAULT_DATE = (2012, 3, 2, 14, 1, 1)
DEFAULT_DATE_FORMAT = "%d %B %Y"

ARTICLE_URL = "posts/{date:%Y}/{date:%B}/{date:%d}/{slug}/"
ARTICLE_SAVE_AS = ARTICLE_URL + "index.html"

FEED_ALL_RSS = "feeds/all.rss.xml"
CATEGORY_FEED_RSS = "feeds/{slug}.rss.xml"

LINKS = [
    ("Biologeek", "http://biologeek.org"),
    ("Filyb", "http://filyb.info/"),
    ("Libert-fr", "http://www.libert-fr.com"),
    ("N1k0", "http://prendreuncafe.com/blog/"),
    ("Tarek Ziadé", "http://ziade.org/blog"),
    ("Zubin Mithra", "http://zubin71.wordpress.com/"),
]

SOCIAL = [
    ("twitter", "http://twitter.com/ametaireau"),
    ("lastfm", "http://lastfm.com/user/akounet"),
    ("github", "http://github.com/ametaireau"),
]

# global metadata to all the contents
DEFAULT_METADATA = {"yeah": "it is"}

# path-specific metadata
EXTRA_PATH_METADATA = {
    "extra/robots.txt": {"path": "robots.txt"},
}

# static paths will be copied without parsing their contents
STATIC_PATHS = [
    "pictures",
    "extra/robots.txt",
]

# custom page generated with a jinja2 template
TEMPLATE_PAGES = {"pages/jinja2_template.html": "jinja2_template.html"}

# code blocks with line numbers
PYGMENTS_RST_OPTIONS = {"linenos": "table"}

# foobar will not be used, because it's not in caps. All configuration keys
# have to be in caps
foobar = "barbaz"
