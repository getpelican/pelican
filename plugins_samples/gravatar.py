import hashlib

from blinker import signal


def add_gravatar(generator, metadatas):
    
    #first check email
    if 'email' not in metadatas.keys()\
        and 'AUTHOR_EMAIL' in generator.settings.keys():
            metadatas['email'] = generator.settings['AUTHOR_EMAIL']
            
    #then add gravatar url
    if 'email' in metadatas.keys():
        gravatar_url = "http://www.gravatar.com/avatar/" + \
                        hashlib.md5(metadatas['email'].lower()).hexdigest()
        metadatas["author_gravatar"] = gravatar_url
    
    
signal('pelican_generate_context').connect(add_gravatar)
