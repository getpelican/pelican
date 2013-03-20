import hashlib

from pelican import signals
"""
Gravatar plugin for Pelican
===========================

This plugin assigns the ``author_gravatar`` variable to the Gravatar URL and
makes the variable available within the article's context.

Settings:
---------

Add AUTHOR_EMAIL to your settings file to define the default author's email
address. Obviously, that email address must be associated with a Gravatar
account.

Article metadata:
------------------

:email:  article's author email

If one of them are defined, the author_gravatar variable is added to the
article's context.
"""

def add_gravatar(generator, metadata, **kwargs):

    #first check email
    if 'email' not in metadata.keys()\
        and 'AUTHOR_EMAIL' in generator.settings.keys():
            metadata['email'] = generator.settings['AUTHOR_EMAIL']

    #then add gravatar url
    if 'email' in metadata.keys():
        gravatar_url = "http://www.gravatar.com/avatar/" + \
                        hashlib.md5(metadata['email'].lower()).hexdigest()
        metadata["author_gravatar"] = gravatar_url


def register():
    signals.article_generate_context.connect(add_gravatar)
