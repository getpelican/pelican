from docutils import nodes
from docutils.parsers.rst import directives, Directive
from pelican import log

"""
HTML tags for reStructuredText
==============================

Directives
----------

.. html::

    (HTML code)


Example
-------

A search engine:

.. html::
   <form action="http://seeks.fr/search" method="GET">
     <input type="text" value="Pelican v2" title="Search" maxlength="2048" name="q" autocomplete="on" />
     <input type="hidden" name="lang" value="en" />
     <input type="submit" value="Seeks !" id="search_button" />
   </form>


A contact form:

.. html::

    <form method="GET" action="mailto:some email">
      <p>
        <input type="text" placeholder="Subject" name="subject">
        <br />
        <textarea name="body" placeholder="Message">
        </textarea>
        <br />
        <input type="reset"><input type="submit">
      </p>
    </form>

"""


class RawHtml(Directive):
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True

    def run(self):
        html = u' '.join(self.content)
        node = nodes.raw('', html, format='html')
        return [node]



def register():
    directives.register_directive('html', RawHtml)

