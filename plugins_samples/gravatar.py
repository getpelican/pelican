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

Article metadatas:
------------------

:email:  article's author email

If one of them are defined the author_gravatar variable is added to 
article's context.
"""

def add_gravatar(generator, metadatas):
    
    #first check email
    if 'email' not in metadatas.keys()\
        and 'AUTHOR_EMAIL' in generator.settings.keys():
            metadatas['email'] = generator.settings['AUTHOR_EMAIL']
            
    #then add gravatar url
    if 'email' in metadatas.keys():
        gravatar_url = "http://www.gravatar.com/avatar/" + \
                        hashlib.md5(metadatas['email'].lower()).hexdigest()
        metadatas["author_gravatar"] = gravatar_url
    
    
signal('pelican_article_generate_context').connect(add_gravatar)
