from pelican import signals

"""
Related posts plugin for Pelican
================================

Adds related_posts variable to article's context

Settings
--------
To enable, add 
    
    from pelican.plugins import related_posts
    PLUGINS = [related_posts]

to your settings.py.

Usage
-----
    {% if article.related_posts %}
        <ul>
        {% for related_post in article.related_posts %}
            <li>{{ related_post }}</li>
        {% endfor %}
        </ul>
    {% endif %}


"""

related_posts = []
def add_related_posts(generator, metadata):
    if 'tags' in metadata:
        for tag in metadata['tags']:
            #print tag
            for related_article in generator.tags[tag]:
                related_posts.append(related_article)
        
        if len(related_posts) < 1:
            return
        
        relation_score = dict( \
                zip(set(related_posts), \
                map(related_posts.count, \
                set(related_posts))))
        ranked_related = sorted(relation_score, key=relation_score.get)
        
        metadata["related_posts"] = ranked_related[:5]

def register():
    signals.article_generate_context.connect(add_related_posts)
