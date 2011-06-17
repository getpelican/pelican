import hashlib

from blinker import signal
"""
Gravata plugin for Pelican
==========================

Simply add author_gravatar variable in article's context, which contain 
the gravatar url.

Settings:
---------

Add AUTHOR_EMAIL to your settings file to define default author email

Article metadata:
------------------

:email:  article's author email

If one of them are defined the author_gravatar variable is added to 
article's context.
"""

def add_gravatar(generator, metadata):
    
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
    signal('pelican_article_generate_context').connect(add_gravatar)
