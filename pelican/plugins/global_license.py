from pelican import signals

"""
License plugin for Pelican
==========================

Simply add license variable in article's context, which contain 
the license text.

Settings:
---------

Add LICENSE to your settings file to define default license.

"""

def add_license(generator, metadata):
    if 'license' not in metadata.keys()\
        and 'LICENSE' in generator.settings.keys():
            metadata['license'] = generator.settings['LICENSE']

def register():
    signals.article_generate_context.connect(add_license)
