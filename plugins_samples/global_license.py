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
        and 'LICENSE' in self.settings.keys():
            metadatas['license'] = self.settings['LICENSE']


signal('pelican_article_generate_context').connect(add_license)
