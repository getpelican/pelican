from blinker import signal

"""
License plugin for Pelican
==========================

Simply add license variable in article's context, which contain 
the license text.

Settings:
---------

Add LICENSE to your settings file to define default license.

"""

def add_license(generator, metadatas):
    if 'license' not in metadatas.keys()\
        and 'LICENSE' in generator.settings.keys():
            metadatas['license'] = generator.settings['LICENSE']


signal('pelican_article_generate_context').connect(add_license)
