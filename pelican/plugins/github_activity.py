# -*- coding: utf-8 -*-
"""
    Copyright (c) Marco Milanesi <kpanic@gnufunk.org>

    A plugin to list your Github Activity
    To enable it set in your pelican config file the GITHUB_ACTIVITY_FEED
    parameter pointing to your github activity feed.

    for example my personal activity feed is:

        https://github.com/kpanic.atom

    in your template just write a for in jinja2 syntax against the
    github_activity variable.

    github_activity is a list containing raw html from github so you can
    include it directly in your template

"""

from pelican import signals


class GitHubActivity():
    """
        A class created to fetch github activity with feedparser
    """
    def __init__(self, generator):
        try:
            import feedparser
            self.activities = feedparser.parse(
                generator.settings['GITHUB_ACTIVITY_FEED'])
        except ImportError:
            raise Exception("unable to find feedparser")

    def fetch(self):
        """
            returns a list of html snippets fetched from github actitivy feed
        """
        return [activity['content'][0]['value'].strip()
            for activity in self.activities['entries']]


def fetch_github_activity(gen, metadata):
    """
        registered handler for the github activity plugin
        it puts in generator.context the html needed to be displayed on a
        template
    """

    if 'GITHUB_ACTIVITY_FEED' in gen.settings.keys():
        gen.context['github_activity'] = gen.plugin_instance.fetch()


def feed_parser_initialization(generator):
    """
        Initialization of feed parser
    """

    generator.plugin_instance = GitHubActivity(generator)


def register():
    """
        Plugin registration
    """
    signals.article_generator_init.connect(feed_parser_initialization)
    signals.article_generate_context.connect(fetch_github_activity)
