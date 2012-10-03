from blinker import signal

initialized = signal('pelican_initialized')
finalized = signal('pelican_finalized')
article_generate_context = signal('article_generate_context')
article_generator_init = signal('article_generator_init')
get_generators = signal('get_generators')
pages_generate_context = signal('pages_generate_context')
pages_generator_init = signal('pages_generator_init')
