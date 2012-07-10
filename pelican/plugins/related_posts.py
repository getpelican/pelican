from pelican import signals

"""
Related posts plugin for Pelican
================================

Adds related_posts variable to article's context
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
        ranked_related.reverse()
        
        metadata["related_posts"] = ranked_related[:5]

    else:
        return

def register():
    signals.article_generate_context.connect(add_related_posts)
