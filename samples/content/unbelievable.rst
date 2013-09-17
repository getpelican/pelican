Unbelievable !
##############

:date: 2010-10-15 20:30

Or completely awesome. Depends the needs.

`a root-relative link to markdown-article <|filename|/cat1/markdown-article.md>`_
`a file-relative link to markdown-article <|filename|cat1/markdown-article.md>`_

Testing sourcecode directive
----------------------------

.. sourcecode:: python
    :linenos:

    formatter = self.options and VARIANTS[self.options.keys()[0]]


Testing another case
--------------------

This will now have a line number in 'custom' since it's the default in
pelican.conf, it will have nothing in default.

.. sourcecode:: python

    formatter = self.options and VARIANTS[self.options.keys()[0]]


Lovely.

Testing more sourcecode directives
----------------------------------

.. sourcecode:: python
    :anchorlinenos:
    :classprefix: testing
    :hl_lines: 10,11,12
    :lineanchors: foo
    :linenos: inline
    :linenospecial: 2
    :linenostart: 8
    :linenostep: 2
    :lineseparator: <br>
    :linespans: foo
    :nobackground:
  
    def run(self):
        self.assert_has_content()
        try:
            lexer = get_lexer_by_name(self.arguments[0])
        except ValueError:
            # no lexer found - use the text one instead of an exception
            lexer = TextLexer()

        if ('linenos' in self.options and
                self.options['linenos'] not in ('table', 'inline')):
            self.options['linenos'] = 'table'

        for flag in ('nowrap', 'nobackground', 'anchorlinenos'):
            if flag in self.options:
                self.options[flag] = True

        # noclasses should already default to False, but just in case...
        formatter = HtmlFormatter(noclasses=False, **self.options)
        parsed = highlight('\n'.join(self.content), lexer, formatter)
        return [nodes.raw('', parsed, format='html')]


Lovely.

Testing even more sourcecode directives
---------------------------------------

.. sourcecode:: python
    :linenos: table
    :nowrap:
    
  
    formatter = self.options and VARIANTS[self.options.keys()[0]]


Lovely.

Testing overriding config defaults
----------------------------------

Even if the default is line numbers, we can override it here

.. sourcecode:: python
    :linenos: none
    
  
    formatter = self.options and VARIANTS[self.options.keys()[0]]


Lovely.
