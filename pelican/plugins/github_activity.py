from pelican import signals
from pelican.utils import singleton

@singleton
class GitHubActivity():
    def __init__(self, generator):
        try:
            import feedparser
            self.ga = feedparser.parse(
                generator.settings['GITHUB_ACTIVITY_FEED'])
        except ImportError:
            raise Exception("unable to find feedparser")

    def fetch(self):
        return [activity['content'][0]['value'].strip()
            for activity in self.ga['entries']]

def add_github_activity(generator, metadata):
    if 'GITHUB_ACTIVITY_FEED' in generator.settings.keys():

        ga = GitHubActivity(generator)

        ga_html_snippets = ga.fetch()
        generator.context['github_activity'] = ga_html_snippets

def register():
    signals.article_generate_context.connect(add_github_activity)
