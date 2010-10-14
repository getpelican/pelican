Pelican
#######

Pelican is a simple weblog generator, writen in python.
.
* Write your weblog entries directly with your editor of choice (vim!) and
  directly in restructured text.
* A simple cli-tool to (re)generate the weblog.
* Easy to interface with DVCSes and web hooks
* Completely static output, so easy to host anywhere !

Source code
-----------

Get the source code from http://alexis.notmyidea.org/pelican/

Getting started
---------------

Yeah? You're ready? Let's go !::

    $ pip install pelican
    $ pelican -p /path/to/your/content/
    ...

And… that's all! You can see your weblog generated on the content/ folder.


Metadata
---------

Pelican tries to be smart enough to get the informations he needs from the
filesystem (for instance, about date of creation of the files), but it seems to
be less reliable than static metadata.

You could provide the metadata in the restructured text files, using the
following syntax::

    My super title
    ##############

    .. date: 2010-10-03 10:20
    .. tags: thats, awesome
    .. category: yeah
    .. author: Alexis Metaireau

Why the name "Pelican" ?
------------------------

Heh, you didnt noticed? "Pelican" is an anagram for "Calepin" ;)

Feedback !
----------

If you want to see new features in Pelican, dont hesitate to tell me, to clone
the repository, etc. That's open source, dude!
