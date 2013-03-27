# -*- coding: utf-8 -*-
"""
    Convert relative urls and paths into absolute urls and paths
"""

from pelican import signals
from lxml.html import fromstring, tostring
from pelican.contents import Article


def _update_content(self, content, siteurl):
    """
    `Article.content` is an immutable property, so we have to monkey-patch 
    the method that generates the content.

    """
    content = super(Article, self)._update_content(content, siteurl)
    content = fromstring(content)
    content.make_links_absolute(siteurl)

    return tostring(content)


def absolutize(sender):
    Article._update_content = _update_content


def register():
    signals.initialized.connect(absolutize)