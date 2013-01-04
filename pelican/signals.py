# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from blinker import signal

# Run-level signals:

initialized = signal('pelican_initialized')
get_generators = signal('get_generators')
finalized = signal('pelican_finalized')

# Generator-level signals

generator_init = signal('generator_init')

article_generator_init = signal('article_generator_init')
article_generator_finalized = signal('article_generate_finalized')

pages_generator_init = signal('pages_generator_init')

# Page-level signals

article_generate_preread = signal('article_generate_preread')
article_generate_context = signal('article_generate_context')

pages_generate_context = signal('pages_generate_context')

content_object_init = signal('content_object_init')
