import calendar
import errno
import fnmatch
import logging
import os
from collections import defaultdict
from functools import partial
from itertools import chain, groupby
from operator import attrgetter
from typing import List, Optional, Set

from jinja2 import (
    BaseLoader,
    ChoiceLoader,
    Environment,
    FileSystemLoader,
    PrefixLoader,
    TemplateNotFound,
)

from pelican.cache import FileStampDataCacher
from pelican.contents import Article, Page, SkipStub, Static
from pelican.plugins import signals
from pelican.plugins._utils import plugin_enabled
from pelican.readers import Readers
from pelican.utils import (
    DateFormatter,
    copy,
    mkdir_p,
    order_content,
    posixize_path,
    process_translations,
)

logger = logging.getLogger(__name__)


class PelicanTemplateNotFound(Exception):
    pass


class Generator:
    """Baseclass generator"""

    def __init__(
        self,
        context,
        settings,
        path,
        theme,
        output_path,
        readers_cache_name="",
        **kwargs,
    ):
        self.context = context
        self.settings = settings
        self.path = path
        self.theme = theme
        self.output_path = output_path

        for arg, value in kwargs.items():
            setattr(self, arg, value)

        self.readers = Readers(self.settings, readers_cache_name)

        # templates cache
        self._templates = {}
        self._templates_path = list(self.settings["THEME_TEMPLATES_OVERRIDES"])

        theme_templates_path = os.path.expanduser(os.path.join(self.theme, "templates"))
        self._templates_path.append(theme_templates_path)
        theme_loader = FileSystemLoader(theme_templates_path)

        simple_theme_path = os.path.dirname(os.path.abspath(__file__))
        simple_loader = FileSystemLoader(
            os.path.join(simple_theme_path, "themes", "simple", "templates")
        )

        self.env = Environment(
            loader=ChoiceLoader(
                [
                    FileSystemLoader(self._templates_path),
                    simple_loader,  # implicit inheritance
                    PrefixLoader(
                        {"!simple": simple_loader, "!theme": theme_loader}
                    ),  # explicit ones
                ]
            ),
            **self.settings["JINJA_ENVIRONMENT"],
        )

        logger.debug("Template list: %s", self.env.list_templates())

        # provide utils.strftime as a jinja filter
        self.env.filters.update({"strftime": DateFormatter()})

        # get custom Jinja filters from user settings
        custom_filters = self.settings["JINJA_FILTERS"]
        self.env.filters.update(custom_filters)

        # get custom Jinja globals from user settings
        custom_globals = self.settings["JINJA_GLOBALS"]
        self.env.globals.update(custom_globals)

        # get custom Jinja tests from user settings
        custom_tests = self.settings["JINJA_TESTS"]
        self.env.tests["plugin_enabled"] = partial(
            plugin_enabled, plugin_list=self.settings["PLUGINS"]
        )
        self.env.tests.update(custom_tests)

        signals.generator_init.send(self)

    def get_template(self, name):
        """Return the template by name.
        Use self.theme to get the templates to use, and return a list of
        templates ready to use with Jinja2.
        """
        if name not in self._templates:
            for ext in self.settings["TEMPLATE_EXTENSIONS"]:
                try:
                    self._templates[name] = self.env.get_template(name + ext)
                    break
                except TemplateNotFound:
                    continue

            if name not in self._templates:
                raise PelicanTemplateNotFound(
                    "[templates] unable to load {}[{}] from {}".format(
                        name,
                        ", ".join(self.settings["TEMPLATE_EXTENSIONS"]),
                        self._templates_path,
                    )
                )

        return self._templates[name]

    def _include_path(self, path, extensions=None):
        """Inclusion logic for .get_files(), returns True/False

        :param path: the path which might be including
        :param extensions: the list of allowed extensions, or False if all
            extensions are allowed
        """
        if extensions is None:
            extensions = tuple(self.readers.extensions)
        basename = os.path.basename(path)

        # check IGNORE_FILES
        ignores = self.settings["IGNORE_FILES"]
        if any(fnmatch.fnmatch(basename, ignore) for ignore in ignores):
            return False

        ext = os.path.splitext(basename)[1][1:]
        if extensions is False or ext in extensions:
            return True

        return False

    def get_files(
        self, paths, exclude: Optional[List[str]] = None, extensions=None
    ) -> Set[str]:
        """Return a list of files to use, based on rules

        :param paths: the list pf paths to search (relative to self.path)
        :param exclude: the list of path to exclude
        :param extensions: the list of allowed extensions (if False, all
            extensions are allowed)
        """
        if exclude is None:
            exclude = []
        # backward compatibility for older generators
        if isinstance(paths, str):
            paths = [paths]

        # group the exclude dir names by parent path, for use with os.walk()
        exclusions_by_dirpath = {}
        for e in exclude:
            parent_path, subdir = os.path.split(os.path.join(self.path, e))
            exclusions_by_dirpath.setdefault(parent_path, set()).add(subdir)

        files = set()
        ignores = self.settings["IGNORE_FILES"]
        for path in paths:
            # careful: os.path.join() will add a slash when path == ''.
            root = os.path.join(self.path, path) if path else self.path

            if os.path.isdir(root):
                for dirpath, dirs, temp_files in os.walk(
                    root, topdown=True, followlinks=True
                ):
                    excl = exclusions_by_dirpath.get(dirpath, ())
                    # We copy the `dirs` list as we will modify it in the loop:
                    for d in list(dirs):
                        if d in excl or any(
                            fnmatch.fnmatch(d, ignore) for ignore in ignores
                        ):
                            if d in dirs:
                                dirs.remove(d)

                    reldir = os.path.relpath(dirpath, self.path)
                    for f in temp_files:
                        fp = os.path.join(reldir, f)
                        if self._include_path(fp, extensions):
                            files.add(fp)
            elif os.path.exists(root) and self._include_path(path, extensions):
                files.add(path)  # can't walk non-directories
        return files

    def add_source_path(self, content, static=False):
        """Record a source file path that a Generator found and processed.
        Store a reference to its Content object, for url lookups later.
        """
        location = content.get_relative_source_path()
        key = "static_content" if static else "generated_content"
        self.context[key][location] = content

    def _add_failed_source_path(self, path, static=False):
        """Record a source file path that a Generator failed to process.
        (For example, one that was missing mandatory metadata.)
        The path argument is expected to be relative to self.path.
        """
        key = "static_content" if static else "generated_content"
        self.context[key][posixize_path(os.path.normpath(path))] = None

    def _is_potential_source_path(self, path, static=False):
        """Return True if path was supposed to be used as a source file.
        (This includes all source files that have been found by generators
        before this method is called, even if they failed to process.)
        The path argument is expected to be relative to self.path.
        """
        key = "static_content" if static else "generated_content"
        return posixize_path(os.path.normpath(path)) in self.context[key]

    def add_static_links(self, content):
        """Add file links in content to context to be processed as Static
        content.
        """
        self.context["static_links"] |= content.get_static_links()

    def _update_context(self, items):
        """Update the context with the given items from the current processor.

        Note that dictionary arguments will be converted to a list of tuples.
        """
        for item in items:
            value = getattr(self, item)
            if hasattr(value, "items"):
                value = list(value.items())  # py3k safeguard for iterators
            self.context[item] = value

    def __str__(self):
        # return the name of the class for logging purposes
        return self.__class__.__name__

    def _check_disabled_readers(self, paths, exclude: Optional[List[str]]) -> None:
        """Log warnings for files that would have been processed by disabled readers."""
        for fil in self.get_files(
            paths, exclude=exclude, extensions=self.readers.disabled_extensions
        ):
            self.readers.check_file(fil)


class CachingGenerator(Generator, FileStampDataCacher):
    """Subclass of Generator and FileStampDataCacher classes

    enables content caching, either at the generator or reader level
    """

    def __init__(self, *args, **kwargs):
        """Initialize the generator, then set up caching

        note the multiple inheritance structure
        """
        cls_name = self.__class__.__name__
        Generator.__init__(
            self, *args, readers_cache_name=(cls_name + "-Readers"), **kwargs
        )

        cache_this_level = self.settings["CONTENT_CACHING_LAYER"] == "generator"
        caching_policy = cache_this_level and self.settings["CACHE_CONTENT"]
        load_policy = cache_this_level and self.settings["LOAD_CONTENT_CACHE"]
        FileStampDataCacher.__init__(
            self, self.settings, cls_name, caching_policy, load_policy
        )

    def _get_file_stamp(self, filename):
        """Get filestamp for path relative to generator.path"""
        filename = os.path.join(self.path, filename)
        return super()._get_file_stamp(filename)


class _FileLoader(BaseLoader):
    def __init__(self, path, basedir):
        self.path = path
        self.fullpath = os.path.join(basedir, path)

    def get_source(self, environment, template):
        if template != self.path or not os.path.exists(self.fullpath):
            raise TemplateNotFound(template)
        mtime = os.path.getmtime(self.fullpath)
        with open(self.fullpath, encoding="utf-8") as f:
            source = f.read()
        return (source, self.fullpath, lambda: mtime == os.path.getmtime(self.fullpath))


class TemplatePagesGenerator(Generator):
    def generate_output(self, writer):
        for source, dest in self.settings["TEMPLATE_PAGES"].items():
            self.env.loader.loaders.insert(0, _FileLoader(source, self.path))
            try:
                template = self.env.get_template(source)
                rurls = self.settings["RELATIVE_URLS"]
                writer.write_file(
                    dest, template, self.context, rurls, override_output=True, url=""
                )
            finally:
                del self.env.loader.loaders[0]


class ArticlesGenerator(CachingGenerator):
    """Generate blog articles"""

    def __init__(self, *args, **kwargs):
        """initialize properties"""
        # Published, listed articles
        self.articles = []  # only articles in default language
        self.translations = []
        # Published, unlisted articles
        self.hidden_articles = []
        self.hidden_translations = []
        # Draft articles
        self.drafts = []  # only drafts in default language
        self.drafts_translations = []
        self.dates = {}
        self.period_archives = defaultdict(list)
        self.tags = defaultdict(list)
        self.categories = defaultdict(list)
        self.related_posts = []
        self.authors = defaultdict(list)
        super().__init__(*args, **kwargs)
        signals.article_generator_init.send(self)

    def generate_feeds(self, writer):
        """Generate the feeds from the current context, and output files."""

        if self.settings.get("FEED_ATOM"):
            writer.write_feed(
                self.articles,
                self.context,
                self.settings["FEED_ATOM"],
                self.settings.get("FEED_ATOM_URL", self.settings["FEED_ATOM"]),
            )

        if self.settings.get("FEED_RSS"):
            writer.write_feed(
                self.articles,
                self.context,
                self.settings["FEED_RSS"],
                self.settings.get("FEED_RSS_URL", self.settings["FEED_RSS"]),
                feed_type="rss",
            )

        if self.settings.get("FEED_ALL_ATOM") or self.settings.get("FEED_ALL_RSS"):
            all_articles = list(self.articles)
            for article in self.articles:
                all_articles.extend(article.translations)
            order_content(all_articles, order_by=self.settings["ARTICLE_ORDER_BY"])

            if self.settings.get("FEED_ALL_ATOM"):
                writer.write_feed(
                    all_articles,
                    self.context,
                    self.settings["FEED_ALL_ATOM"],
                    self.settings.get(
                        "FEED_ALL_ATOM_URL", self.settings["FEED_ALL_ATOM"]
                    ),
                )

            if self.settings.get("FEED_ALL_RSS"):
                writer.write_feed(
                    all_articles,
                    self.context,
                    self.settings["FEED_ALL_RSS"],
                    self.settings.get(
                        "FEED_ALL_RSS_URL", self.settings["FEED_ALL_RSS"]
                    ),
                    feed_type="rss",
                )

        for cat, arts in self.categories:
            if self.settings.get("CATEGORY_FEED_ATOM"):
                writer.write_feed(
                    arts,
                    self.context,
                    str(self.settings["CATEGORY_FEED_ATOM"]).format(slug=cat.slug),
                    self.settings.get(
                        "CATEGORY_FEED_ATOM_URL",
                        str(self.settings["CATEGORY_FEED_ATOM"]),
                    ).format(slug=cat.slug),
                    feed_title=cat.name,
                )

            if self.settings.get("CATEGORY_FEED_RSS"):
                writer.write_feed(
                    arts,
                    self.context,
                    str(self.settings["CATEGORY_FEED_RSS"]).format(slug=cat.slug),
                    self.settings.get(
                        "CATEGORY_FEED_RSS_URL",
                        str(self.settings["CATEGORY_FEED_RSS"]),
                    ).format(slug=cat.slug),
                    feed_title=cat.name,
                    feed_type="rss",
                )

        for auth, arts in self.authors:
            if self.settings.get("AUTHOR_FEED_ATOM"):
                writer.write_feed(
                    arts,
                    self.context,
                    str(self.settings["AUTHOR_FEED_ATOM"]).format(slug=auth.slug),
                    self.settings.get(
                        "AUTHOR_FEED_ATOM_URL",
                        str(self.settings["AUTHOR_FEED_ATOM"]),
                    ).format(slug=auth.slug),
                    feed_title=auth.name,
                )

            if self.settings.get("AUTHOR_FEED_RSS"):
                writer.write_feed(
                    arts,
                    self.context,
                    str(self.settings["AUTHOR_FEED_RSS"]).format(slug=auth.slug),
                    self.settings.get(
                        "AUTHOR_FEED_RSS_URL",
                        str(self.settings["AUTHOR_FEED_RSS"]),
                    ).format(slug=auth.slug),
                    feed_title=auth.name,
                    feed_type="rss",
                )

        if self.settings.get("TAG_FEED_ATOM") or self.settings.get("TAG_FEED_RSS"):
            for tag, arts in self.tags.items():
                if self.settings.get("TAG_FEED_ATOM"):
                    writer.write_feed(
                        arts,
                        self.context,
                        str(self.settings["TAG_FEED_ATOM"]).format(slug=tag.slug),
                        self.settings.get(
                            "TAG_FEED_ATOM_URL",
                            str(self.settings["TAG_FEED_ATOM"]),
                        ).format(slug=tag.slug),
                        feed_title=tag.name,
                    )

                if self.settings.get("TAG_FEED_RSS"):
                    writer.write_feed(
                        arts,
                        self.context,
                        str(self.settings["TAG_FEED_RSS"]).format(slug=tag.slug),
                        self.settings.get(
                            "TAG_FEED_RSS_URL",
                            str(self.settings["TAG_FEED_RSS"]),
                        ).format(slug=tag.slug),
                        feed_title=tag.name,
                        feed_type="rss",
                    )

        if self.settings.get("TRANSLATION_FEED_ATOM") or self.settings.get(
            "TRANSLATION_FEED_RSS"
        ):
            translations_feeds = defaultdict(list)
            for article in chain(self.articles, self.translations):
                translations_feeds[article.lang].append(article)

            for lang, items in translations_feeds.items():
                items = order_content(items, order_by=self.settings["ARTICLE_ORDER_BY"])
                if self.settings.get("TRANSLATION_FEED_ATOM"):
                    writer.write_feed(
                        items,
                        self.context,
                        str(self.settings["TRANSLATION_FEED_ATOM"]).format(lang=lang),
                        self.settings.get(
                            "TRANSLATION_FEED_ATOM_URL",
                            str(self.settings["TRANSLATION_FEED_ATOM"]),
                        ).format(lang=lang),
                    )
                if self.settings.get("TRANSLATION_FEED_RSS"):
                    writer.write_feed(
                        items,
                        self.context,
                        str(self.settings["TRANSLATION_FEED_RSS"]).format(lang=lang),
                        self.settings.get(
                            "TRANSLATION_FEED_RSS_URL",
                            str(self.settings["TRANSLATION_FEED_RSS"]),
                        ).format(lang=lang),
                        feed_type="rss",
                    )

    def generate_articles(self, write):
        """Generate the articles."""
        for article in chain(
            self.translations,
            self.articles,
            self.hidden_translations,
            self.hidden_articles,
        ):
            signals.article_generator_write_article.send(self, content=article)
            write(
                article.save_as,
                self.get_template(article.template),
                self.context,
                article=article,
                category=article.category,
                override_output=hasattr(article, "override_save_as"),
                url=article.url,
                blog=True,
            )

    def generate_period_archives(self, write):
        """Generate per-year, per-month, and per-day archives."""
        try:
            template = self.get_template("period_archives")
        except PelicanTemplateNotFound:
            template = self.get_template("archives")

        for granularity in self.period_archives:
            for period in self.period_archives[granularity]:
                context = self.context.copy()
                context["period"] = period["period"]
                context["period_num"] = period["period_num"]

                write(
                    period["save_as"],
                    template,
                    context,
                    articles=period["articles"],
                    dates=period["dates"],
                    template_name="period_archives",
                    blog=True,
                    url=period["url"],
                    all_articles=self.articles,
                )

    def generate_direct_templates(self, write):
        """Generate direct templates pages"""
        for template in self.settings["DIRECT_TEMPLATES"]:
            save_as = self.settings.get(
                f"{template.upper()}_SAVE_AS", f"{template}.html"
            )
            url = self.settings.get(f"{template.upper()}_URL", f"{template}.html")
            if not save_as:
                continue

            write(
                save_as,
                self.get_template(template),
                self.context,
                articles=self.articles,
                dates=self.dates,
                blog=True,
                template_name=template,
                page_name=os.path.splitext(save_as)[0],
                url=url,
            )

    def generate_tags(self, write):
        """Generate Tags pages."""
        tag_template = self.get_template("tag")
        for tag, articles in self.tags.items():
            dates = [article for article in self.dates if article in articles]
            write(
                tag.save_as,
                tag_template,
                self.context,
                tag=tag,
                url=tag.url,
                articles=articles,
                dates=dates,
                template_name="tag",
                blog=True,
                page_name=tag.page_name,
                all_articles=self.articles,
            )

    def generate_categories(self, write):
        """Generate category pages."""
        category_template = self.get_template("category")
        for cat, articles in self.categories:
            dates = [article for article in self.dates if article in articles]
            write(
                cat.save_as,
                category_template,
                self.context,
                url=cat.url,
                category=cat,
                articles=articles,
                dates=dates,
                template_name="category",
                blog=True,
                page_name=cat.page_name,
                all_articles=self.articles,
            )

    def generate_authors(self, write):
        """Generate Author pages."""
        author_template = self.get_template("author")
        for aut, articles in self.authors:
            dates = [article for article in self.dates if article in articles]
            write(
                aut.save_as,
                author_template,
                self.context,
                url=aut.url,
                author=aut,
                articles=articles,
                dates=dates,
                template_name="author",
                blog=True,
                page_name=aut.page_name,
                all_articles=self.articles,
            )

    def generate_drafts(self, write):
        """Generate drafts pages."""
        for draft in chain(self.drafts_translations, self.drafts):
            write(
                draft.save_as,
                self.get_template(draft.template),
                self.context,
                article=draft,
                category=draft.category,
                override_output=hasattr(draft, "override_save_as"),
                blog=True,
                all_articles=self.articles,
                url=draft.url,
            )

    def generate_pages(self, writer):
        """Generate the pages on the disk"""
        write = partial(writer.write_file, relative_urls=self.settings["RELATIVE_URLS"])

        # to minimize the number of relative path stuff modification
        # in writer, articles pass first
        self.generate_articles(write)
        self.generate_period_archives(write)
        self.generate_direct_templates(write)

        # and subfolders after that
        self.generate_tags(write)
        self.generate_categories(write)
        self.generate_authors(write)
        self.generate_drafts(write)

    def check_disabled_readers(self) -> None:
        self._check_disabled_readers(
            self.settings["ARTICLE_PATHS"], exclude=self.settings["ARTICLE_EXCLUDES"]
        )

    def generate_context(self):
        """Add the articles into the shared context"""

        all_articles = []
        all_drafts = []
        hidden_articles = []
        for f in self.get_files(
            self.settings["ARTICLE_PATHS"], exclude=self.settings["ARTICLE_EXCLUDES"]
        ):
            article = self.get_cached_data(f, None)
            if article is None:
                try:
                    article = self.readers.read_file(
                        base_path=self.path,
                        path=f,
                        content_class=Article,
                        context=self.context,
                        preread_signal=signals.article_generator_preread,
                        preread_sender=self,
                        context_signal=signals.article_generator_context,
                        context_sender=self,
                    )
                except Exception as e:
                    logger.error(
                        "Could not process %s\n%s",
                        f,
                        e,
                        exc_info=self.settings.get("DEBUG", False),
                    )
                    self._add_failed_source_path(f)
                    continue

                if isinstance(article, SkipStub):
                    logger.debug("Safely skipping %s", f)
                    continue

                if not article.is_valid():
                    self._add_failed_source_path(f)
                    continue

                self.cache_data(f, article)

            if article.status == "published":
                all_articles.append(article)
            elif article.status == "draft":
                all_drafts.append(article)
            elif article.status == "hidden":
                hidden_articles.append(article)
            elif article.status == "skip":
                raise AssertionError("Documents with 'skip' status should be skipped")

            self.add_source_path(article)
            self.add_static_links(article)

        def _process(arts):
            origs, translations = process_translations(
                arts, translation_id=self.settings["ARTICLE_TRANSLATION_ID"]
            )
            origs = order_content(origs, self.settings["ARTICLE_ORDER_BY"])
            return origs, translations

        self.articles, self.translations = _process(all_articles)
        self.hidden_articles, self.hidden_translations = _process(hidden_articles)
        self.drafts, self.drafts_translations = _process(all_drafts)

        signals.article_generator_pretaxonomy.send(self)

        for article in self.articles:
            # only main articles are listed in categories and tags
            # not translations or hidden articles
            self.categories[article.category].append(article)
            if hasattr(article, "tags"):
                for tag in article.tags:
                    self.tags[tag].append(article)
            for author in getattr(article, "authors", []):
                self.authors[author].append(article)

        self.dates = list(self.articles)
        self.dates.sort(
            key=attrgetter("date"), reverse=self.context["NEWEST_FIRST_ARCHIVES"]
        )

        self.period_archives = self._build_period_archives(
            self.dates, self.articles, self.settings
        )

        # and generate the output :)

        # order the categories per name
        self.categories = list(self.categories.items())
        self.categories.sort(reverse=self.settings["REVERSE_CATEGORY_ORDER"])

        self.authors = list(self.authors.items())
        self.authors.sort()

        self._update_context(
            (
                "articles",
                "drafts",
                "hidden_articles",
                "dates",
                "tags",
                "categories",
                "authors",
                "related_posts",
            )
        )
        # _update_context flattens dicts, which should not happen to
        # period_archives, so we update the context directly for it:
        self.context["period_archives"] = self.period_archives
        self.save_cache()
        self.readers.save_cache()
        signals.article_generator_finalized.send(self)

    def _build_period_archives(self, sorted_articles, articles, settings):
        """
        Compute the groupings of articles, with related attributes, for
        per-year, per-month, and per-day archives.
        """

        period_archives = defaultdict(list)

        period_archives_settings = {
            "year": {
                "save_as": settings["YEAR_ARCHIVE_SAVE_AS"],
                "url": settings["YEAR_ARCHIVE_URL"],
            },
            "month": {
                "save_as": settings["MONTH_ARCHIVE_SAVE_AS"],
                "url": settings["MONTH_ARCHIVE_URL"],
            },
            "day": {
                "save_as": settings["DAY_ARCHIVE_SAVE_AS"],
                "url": settings["DAY_ARCHIVE_URL"],
            },
        }

        granularity_key_func = {
            "year": attrgetter("date.year"),
            "month": attrgetter("date.year", "date.month"),
            "day": attrgetter("date.year", "date.month", "date.day"),
        }

        for granularity in "year", "month", "day":
            save_as_fmt = period_archives_settings[granularity]["save_as"]
            url_fmt = period_archives_settings[granularity]["url"]
            key_func = granularity_key_func[granularity]

            if not save_as_fmt:
                # the archives for this period granularity are not needed
                continue

            for period, group in groupby(sorted_articles, key=key_func):
                archive = {}

                dates = list(group)
                archive["dates"] = dates
                archive["articles"] = [a for a in articles if a in dates]

                # use the first date to specify the period archive URL
                # and save_as; the specific date used does not matter as
                # they all belong to the same period
                d = dates[0].date
                archive["save_as"] = save_as_fmt.format(date=d)
                archive["url"] = url_fmt.format(date=d)

                if granularity == "year":
                    archive["period"] = (period,)
                    archive["period_num"] = (period,)
                else:
                    month_name = calendar.month_name[period[1]]
                    if granularity == "month":
                        archive["period"] = (period[0], month_name)
                    else:
                        archive["period"] = (period[0], month_name, period[2])
                    archive["period_num"] = tuple(period)

                period_archives[granularity].append(archive)

        return period_archives

    def generate_output(self, writer):
        self.generate_feeds(writer)
        self.generate_pages(writer)
        signals.article_writer_finalized.send(self, writer=writer)

    def refresh_metadata_intersite_links(self):
        for e in chain(
            self.articles,
            self.translations,
            self.drafts,
            self.drafts_translations,
            self.hidden_articles,
            self.hidden_translations,
        ):
            if hasattr(e, "refresh_metadata_intersite_links"):
                e.refresh_metadata_intersite_links()


class PagesGenerator(CachingGenerator):
    """Generate pages"""

    def __init__(self, *args, **kwargs):
        self.pages = []
        self.translations = []
        self.hidden_pages = []
        self.hidden_translations = []
        self.draft_pages = []
        self.draft_translations = []
        super().__init__(*args, **kwargs)
        signals.page_generator_init.send(self)

    def check_disabled_readers(self) -> None:
        self._check_disabled_readers(
            self.settings["PAGE_PATHS"], exclude=self.settings["PAGE_EXCLUDES"]
        )

    def generate_context(self):
        all_pages = []
        hidden_pages = []
        draft_pages = []
        for f in self.get_files(
            self.settings["PAGE_PATHS"], exclude=self.settings["PAGE_EXCLUDES"]
        ):
            page = self.get_cached_data(f, None)
            if page is None:
                try:
                    page = self.readers.read_file(
                        base_path=self.path,
                        path=f,
                        content_class=Page,
                        context=self.context,
                        preread_signal=signals.page_generator_preread,
                        preread_sender=self,
                        context_signal=signals.page_generator_context,
                        context_sender=self,
                    )
                except Exception as e:
                    logger.error(
                        "Could not process %s\n%s",
                        f,
                        e,
                        exc_info=self.settings.get("DEBUG", False),
                    )
                    self._add_failed_source_path(f)
                    continue

                if isinstance(page, SkipStub):
                    logger.debug("Safely skipping %s", f)
                    continue

                if not page.is_valid():
                    self._add_failed_source_path(f)
                    continue

                self.cache_data(f, page)

            if page.status == "published":
                all_pages.append(page)
            elif page.status == "hidden":
                hidden_pages.append(page)
            elif page.status == "draft":
                draft_pages.append(page)
            elif page.status == "skip":
                raise AssertionError("Documents with 'skip' status should be skipped")

            self.add_source_path(page)
            self.add_static_links(page)

        def _process(pages):
            origs, translations = process_translations(
                pages, translation_id=self.settings["PAGE_TRANSLATION_ID"]
            )
            origs = order_content(origs, self.settings["PAGE_ORDER_BY"])
            return origs, translations

        self.pages, self.translations = _process(all_pages)
        self.hidden_pages, self.hidden_translations = _process(hidden_pages)
        self.draft_pages, self.draft_translations = _process(draft_pages)

        self._update_context(("pages", "hidden_pages", "draft_pages"))

        self.save_cache()
        self.readers.save_cache()
        signals.page_generator_finalized.send(self)

    def generate_output(self, writer):
        for page in chain(
            self.translations,
            self.pages,
            self.hidden_translations,
            self.hidden_pages,
            self.draft_translations,
            self.draft_pages,
        ):
            signals.page_generator_write_page.send(self, content=page)
            writer.write_file(
                page.save_as,
                self.get_template(page.template),
                self.context,
                page=page,
                relative_urls=self.settings["RELATIVE_URLS"],
                override_output=hasattr(page, "override_save_as"),
                url=page.url,
            )
        signals.page_writer_finalized.send(self, writer=writer)

    def refresh_metadata_intersite_links(self):
        for e in chain(
            self.pages,
            self.hidden_pages,
            self.hidden_translations,
            self.draft_pages,
            self.draft_translations,
        ):
            if hasattr(e, "refresh_metadata_intersite_links"):
                e.refresh_metadata_intersite_links()


class StaticGenerator(Generator):
    """copy static paths (what you want to copy, like images, medias etc.
    to output"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fallback_to_symlinks = False
        signals.static_generator_init.send(self)

    def check_disabled_readers(self) -> None:
        self._check_disabled_readers(
            self.settings["STATIC_PATHS"], exclude=self.settings["STATIC_EXCLUDES"]
        )

    def generate_context(self):
        self.staticfiles = []
        linked_files = set(self.context["static_links"])
        found_files = self.get_files(
            self.settings["STATIC_PATHS"],
            exclude=self.settings["STATIC_EXCLUDES"],
            extensions=False,
        )
        for f in linked_files | found_files:
            # skip content source files unless the user explicitly wants them
            if self.settings["STATIC_EXCLUDE_SOURCES"]:
                if self._is_potential_source_path(f):
                    continue

            static = self.readers.read_file(
                base_path=self.path,
                path=f,
                content_class=Static,
                fmt="static",
                context=self.context,
                preread_signal=signals.static_generator_preread,
                preread_sender=self,
                context_signal=signals.static_generator_context,
                context_sender=self,
            )
            self.staticfiles.append(static)
            self.add_source_path(static, static=True)
        self._update_context(("staticfiles",))
        signals.static_generator_finalized.send(self)

    def generate_output(self, writer):
        self._copy_paths(
            self.settings["THEME_STATIC_PATHS"],
            self.theme,
            self.settings["THEME_STATIC_DIR"],
            self.output_path,
            os.curdir,
        )
        for sc in self.context["staticfiles"]:
            if self._file_update_required(sc):
                self._link_or_copy_staticfile(sc)
            else:
                logger.debug("%s is up to date, not copying", sc.source_path)

    def _copy_paths(self, paths, source, destination, output_path, final_path=None):
        """Copy all the paths from source to destination"""
        for path in paths:
            source_path = os.path.join(source, path)

            if final_path:
                if os.path.isfile(source_path):
                    destination_path = os.path.join(
                        output_path, destination, final_path, os.path.basename(path)
                    )
                else:
                    destination_path = os.path.join(
                        output_path, destination, final_path
                    )
            else:
                destination_path = os.path.join(output_path, destination, path)

            copy(source_path, destination_path, self.settings["IGNORE_FILES"])

    def _file_update_required(self, staticfile):
        source_path = os.path.join(self.path, staticfile.source_path)
        save_as = os.path.join(self.output_path, staticfile.save_as)
        if not os.path.exists(save_as):
            return True
        elif self.settings["STATIC_CREATE_LINKS"] and os.path.samefile(
            source_path, save_as
        ):
            return False
        elif (
            self.settings["STATIC_CREATE_LINKS"]
            and os.path.realpath(save_as) == source_path
        ):
            return False
        elif not self.settings["STATIC_CHECK_IF_MODIFIED"]:
            return True
        else:
            return self._source_is_newer(staticfile)

    def _source_is_newer(self, staticfile):
        source_path = os.path.join(self.path, staticfile.source_path)
        save_as = os.path.join(self.output_path, staticfile.save_as)
        s_mtime = os.path.getmtime(source_path)
        d_mtime = os.path.getmtime(save_as)
        return s_mtime - d_mtime > 0.000001  # noqa: PLR2004

    def _link_or_copy_staticfile(self, sc):
        if self.settings["STATIC_CREATE_LINKS"]:
            self._link_staticfile(sc)
        else:
            self._copy_staticfile(sc)

    def _copy_staticfile(self, sc):
        source_path = os.path.join(self.path, sc.source_path)
        save_as = os.path.join(self.output_path, sc.save_as)
        self._mkdir(os.path.dirname(save_as))
        copy(source_path, save_as)
        logger.info("Copying %s to %s", sc.source_path, sc.save_as)

    def _link_staticfile(self, sc):
        source_path = os.path.join(self.path, sc.source_path)
        save_as = os.path.join(self.output_path, sc.save_as)
        self._mkdir(os.path.dirname(save_as))
        try:
            if os.path.lexists(save_as):
                os.unlink(save_as)
            logger.info("Linking %s and %s", sc.source_path, sc.save_as)
            if self.fallback_to_symlinks:
                os.symlink(source_path, save_as)
            else:
                os.link(source_path, save_as)
        except OSError as err:
            if err.errno == errno.EXDEV:  # 18: Invalid cross-device link
                logger.debug(
                    "Cross-device links not valid. Creating symbolic links instead."
                )
                self.fallback_to_symlinks = True
                self._link_staticfile(sc)
            else:
                raise err

    def _mkdir(self, path):
        if os.path.lexists(path) and not os.path.isdir(path):
            os.unlink(path)
        mkdir_p(path)


class SourceFileGenerator(Generator):
    def generate_context(self):
        self.output_extension = self.settings["OUTPUT_SOURCES_EXTENSION"]

    def _create_source(self, obj):
        output_path, _ = os.path.splitext(obj.save_as)
        dest = os.path.join(self.output_path, output_path + self.output_extension)
        copy(obj.source_path, dest)

    def generate_output(self, writer=None):
        logger.info("Generating source files...")
        for obj in chain(self.context["articles"], self.context["pages"]):
            self._create_source(obj)
            for obj_trans in obj.translations:
                self._create_source(obj_trans)
