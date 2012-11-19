from blinker import signal

initialized = signal('pelican_initialized')
finalized = signal('pelican_finalized')
generator_init = signal('generator_init')
article_generate_context = signal('article_generate_context')
article_generator_init = signal('article_generator_init')
article_generator_finalized = signal('article_generate_finalized')
get_generators = signal('get_generators')
pages_generate_context = signal('pages_generate_context')
pages_generator_init = signal('pages_generator_init')
content_object_init = signal('content_object_init')
