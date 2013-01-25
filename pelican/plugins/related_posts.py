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

to your pelicanconf.py.

Control the number of entries with in the config file with:

RELATED_POSTS = {
   'numentries': 6,
}


Usage
-----
    {% if article.related_posts %}
        <ul>
        {% for related_post in article.related_posts %}
            <li><a href="{{ related_post.url }}">{{ related_post.title }}</a></li>
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
        
        metadata["related_posts"] = sorted(set(related_posts))

        relation_score = dict(zip(set(related_posts), map(related_posts.count,
                              set(related_posts))))
        ranked_related = sorted(relation_score, key=relation_score.get)
        
        #Load the confg file and get the number of entries specified there
        settings =  generator.settings
        config = settings.get('RELATED_POSTS', {})

        #check if the related_posts var is set in the pythonconfig.py
        if not isinstance(config, dict):
            info("realted_links plugin: Using default number of related links ("+numentries+")")
        else:
            numentries = config.get('numentries', 5)
        
        metadata["related_posts"] = ranked_related[:numentries]


def register():
    signals.article_generate_context.connect(add_related_posts)
