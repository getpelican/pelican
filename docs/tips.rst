Tips
####

Here are some tips about pelican, which you might find useful.

Publishing to github
====================

Github comes with an interesting "pages" feature: you can upload things there
and it will be available directly from their servers. As pelican is a static
file generator, we can take advantage of this.

The excellent `ghp-import <https://github.com/davisp/ghp-import>`_ makes this
eally easy. You would have to install it::

    $ pip install ghp-import

Then, considering a repository containing your articles, you would simply have
to run pelican and upload the output to github::

    $ pelican -s pelican.conf.py .
    $ ghp-import output
    $ git push origin gh-pages

And that's it.

If you want you can put that directly into a post commit hook, so each time you
commit, your blog is up to date on github!

Put the following into `.git/hooks/post-commit`::

    pelican -s pelican.conf.py . && ghp-import output && git push origin
    gh-pages
