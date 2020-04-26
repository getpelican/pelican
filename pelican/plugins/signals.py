from blinker import signal

# Run-level signals:

initialized = signal('pelican_initialized')
get_generators = signal('get_generators')
all_generators_finalized = signal('all_generators_finalized')
get_writer = signal('get_writer')
finalized = signal('pelican_finalized')

# Reader-level signals

readers_init = signal('readers_init')

# Generator-level signals

generator_init = signal('generator_init')

article_generator_init = signal('article_generator_init')
article_generator_pretaxonomy = signal('article_generator_pretaxonomy')
article_generator_finalized = signal('article_generator_finalized')
article_generator_write_article = signal('article_generator_write_article')
article_writer_finalized = signal('article_writer_finalized')

page_generator_init = signal('page_generator_init')
page_generator_finalized = signal('page_generator_finalized')
page_generator_write_page = signal('page_generator_write_page')
page_writer_finalized = signal('page_writer_finalized')

static_generator_init = signal('static_generator_init')
static_generator_finalized = signal('static_generator_finalized')

# Page-level signals

article_generator_preread = signal('article_generator_preread')
article_generator_context = signal('article_generator_context')

page_generator_preread = signal('page_generator_preread')
page_generator_context = signal('page_generator_context')

static_generator_preread = signal('static_generator_preread')
static_generator_context = signal('static_generator_context')

content_object_init = signal('content_object_init')

# Writers signals
content_written = signal('content_written')
feed_generated = signal('feed_generated')
feed_written = signal('feed_written')
