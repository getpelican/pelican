Sitemap
-------

The sitemap plugin generates plain-text or XML sitemaps. You can use the
``SITEMAP`` variable in your settings file to configure the behavior of the
plugin.

The ``SITEMAP`` variable must be a Python dictionary and can contain three keys:

- ``format``, which sets the output format of the plugin (``xml`` or ``txt``)

- ``priorities``, which is a dictionary with three keys:

  - ``articles``, the priority for the URLs of the articles and their
    translations

  - ``pages``, the priority for the URLs of the static pages

  - ``indexes``, the priority for the URLs of the index pages, such as tags,
     author pages, categories indexes, archives, etc...

  All the values of this dictionary must be decimal numbers between ``0`` and ``1``.

- ``changefreqs``, which is a dictionary with three items:

  - ``articles``, the update frequency of the articles

  - ``pages``, the update frequency of the pages

  - ``indexes``, the update frequency of the index pages

  Valid frequency values are ``always``, ``hourly``, ``daily``, ``weekly``, ``monthly``,
  ``yearly`` and ``never``.

If a key is missing or a value is incorrect, it will be replaced with the
default value.

The sitemap is saved in ``<output_path>/sitemap.<format>``.

.. note::
   ``priorities`` and ``changefreqs`` are information for search engines.
   They are only used in the XML sitemaps.
   For more information: <http://www.sitemaps.org/protocol.html#xmlTagDefinitions>

**Example**

Here is an example configuration (it's also the default settings):

.. code-block:: python

    PLUGINS=['pelican.plugins.sitemap',]

    SITEMAP = {
        'format': 'xml',
        'priorities': {
            'articles': 0.5,
            'indexes': 0.5,
            'pages': 0.5
        },
        'changefreqs': {
            'articles': 'monthly',
            'indexes': 'daily',
            'pages': 'monthly'
        }
    }
