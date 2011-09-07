from blinker import signal

initialized = signal('pelican_initialized')
article_generate_context = signal('article_generate_context')
article_generator_init = signal('article_generator_init')
