from blinker import signal

initialized = signal('pelican_initialized')
article_generate_context = signal('article_generate_context')
github_activity = signal('github_activity')
