AUTHOR = "Alexis Métaireau"
SITENAME = "Alexis' log"
SITEURL = "http://blog.notmyidea.org"
TIMEZONE = "UTC"

GITHUB_URL = "http://github.com/ametaireau/"
DISQUS_SITENAME = "blog-notmyidea"
PDF_GENERATOR = False
REVERSE_CATEGORY_ORDER = True
DEFAULT_PAGINATION = 2

FEED_RSS = "feeds/all.rss.xml"
CATEGORY_FEED_RSS = "feeds/{slug}.rss.xml"

LINKS = (
    ("Biologeek", "http://biologeek.org"),
    ("Filyb", "http://filyb.info/"),
    ("Libert-fr", "http://www.libert-fr.com"),
    ("N1k0", "http://prendreuncafe.com/blog/"),
    ("Tarek Ziadé", "http://ziade.org/blog"),
    ("Zubin Mithra", "http://zubin71.wordpress.com/"),
)

SOCIAL = (
    ("twitter", "http://twitter.com/ametaireau"),
    ("lastfm", "http://lastfm.com/user/akounet"),
    ("github", "http://github.com/ametaireau"),
)

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

FORMATTED_FIELDS = ["summary", "custom_formatted_field"]

# foobar will not be used, because it's not in caps. All configuration keys
# have to be in caps
foobar = "barbaz"
