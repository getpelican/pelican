Pelican internals
#################

This section describe how pelican is working internally. As you'll see, it's
quite simple, but a bit of documentation doesn't hurt :)

You can also find in :doc:`report` an excerpt of a report the original author
wrote, with some software design information.

.. _report: :doc:`report`

Overall structure
=================

What `pelican` does, is taking a list of files, and processing them, to some
sort of output. Usually, the files are restructured text and markdown files,
and the output is a blog, but it can be anything you want.

I've separated the logic in different classes and concepts:

* `writers` are responsible of all the writing process of the
  files. It's writing .html files, RSS feeds and so on. Since those operations 
  are commonly used, the object is created once, and then passed to the 
  generators.

* `readers` are used to read from various formats (Markdown, and Restructured
  Text for now, but the system is extensible). Given a file, they return
  metadata (author, tags, category etc) and content (HTML formated)

* `generators` generate the different outputs. For instance, pelican comes with
  `ArticlesGenerator` and `PageGenerator`, into others. Given
  a configurations, they can do whatever they want. Most of the time it's
  generating files from inputs.

* `pelican` also uses `templates`, so it's easy to write you own theme. The
  syntax is `jinja2`, and, trust me, really easy to learn, so don't hesitate
  a second.

How to implement a new reader ?
===============================

There is an awesome markup language you want to add to pelican ?
Well, the only thing you have to do is to create a class that have a `read`
method, that is returning an HTML content and some metadata.

Take a look to the Markdown reader::

    class MarkdownReader(Reader):
        enabled = bool(Markdown)

        def read(self, filename):
            """Parse content and metadata of markdown files"""
            text = open(filename)
            md = Markdown(extensions = ['meta', 'codehilite'])
            content = md.convert(text)
            
            metadata = {}
            for name, value in md.Meta.items():
                if name in _METADATA_FIELDS:
                    meta = _METADATA_FIELDS[name](value[0])
                else:
                    meta = value[0]
                metadata[name.lower()] = meta
            return content, metadata

Simple isn't it ?

If your new reader requires additional Python dependencies then you should wrap
their `import` statements in `try...except`.  Then inside the reader's class
set the `enabled` class attribute to mark import success or failure.  This makes
it possible for users to continue using their favourite markup method without
needing to install modules for all the additional formats they don't use.

How to implement a new generator ?
==================================

Generators have basically two important methods. You're not forced to create
both, only the existing ones will be called.

* `generate_context`, that is called in a first place, for all the generators.
  Do whatever you have to do, and update the global context if needed. This
  context is shared between all generators, and will be passed to the
  templates. For instance, the `PageGenerator` `generate_context` method find
  all the pages, transform them into objects, and populate the context with
  them. Be careful to *not* output anything using this context at this stage,
  as it is likely to change by the effect of others generators.

* `generate_output` is then called. And guess what is it made for ? Oh,
  generating the output :) That's here that you may want to look at the context
  and call the methods of the `writer` object, that is passed at the first
  argument of this function. In the `PageGenerator` example, this method will
  look at all the pages recorded in the global context, and output a file on
  the disk (using the writer method `write_file`) for each page encountered.
