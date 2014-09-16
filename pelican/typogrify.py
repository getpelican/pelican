# -*- coding: utf-8 -*-

import re
import sys
import six

from six.moves.html_parser import HTMLParser
from six.moves.html_entities import name2codepoint

# Used to represent any tag
class any_tag:
    pass

class Typogrify(object):
    
    # class variables 
    __ignores = None
    __default_ignores = ['pre', 'code', 'script', 'kbd']
    __filters = ['smartypants','widont','caps','amp','initial_quotes']
   
    class _HTMLParser(HTMLParser):
        """Typogrify HTML Parser: A very simple parser, it determines when
        HTML text is being processed (as opposed to HTML tags) and applies
        the typogrify filters to the text"""

        current_pos = 0
        filtering = True  # default is to filter everything
        intermediate_tags = 0
        data_buffer = ''
        new_line_pos = dict()
        filtered_data_length = 0

        def __init__(self, typogrify, html_doc):
            self.html_doc = html_doc.strip()
            try:
                # Python 3.4+
                HTMLParser.__init__(self, convert_charrefs=False)
            except TypeError:
                HTMLParser.__init__(self)
            
            # Mark the new line positions - needed to
            # determine the position within the input string
            new_line = 1
            self.new_line_pos[new_line] = 0
            for index, char in enumerate(self.html_doc):
                if char == "\n":
                    new_line += 1
                    # Add one due to index being zero based
                    self.new_line_pos[new_line] = index + 1
            
            self.typogrify = typogrify
            self.feed(self.html_doc)  # start parsing

        def handle_starttag(self, tag, attrs):
            """Records the current tag and determines if
            filters should be applied. If intermediate_tags > 0
            then this tag is already being ignored (not
            filtered) because a parent was specified to be
            ignored"""
            
            if self.intermediate_tags > 0:
                self.intermediate_tags += 1
                return
            
            self.filtering = self.typogrify._should_be_filtered(tag, attrs)
            self.intermediate_tags = 1 if not self.filtering else 0

        def handle_data(self, data):
            """Filters the content of a html text node if
            it is not being ignored"""
            
            line_num, offset = self.getpos()
            new_pos = self.new_line_pos[line_num] + offset
            self.data_buffer += self.html_doc[self.current_pos:new_pos]

            content = data
            content = self.typogrify._apply_filters(content, self.lasttag)
            self.data_buffer += content

            self.current_pos = new_pos + len(data)
            self.filtered_data_length = len(content)

        def handle_endtag(self, tag):
            """Used to determine when a tag that is not
            being filtered has ended"""

            if self.intermediate_tags > 0:
                self.intermediate_tags -= 1
            
            # Widont filter needs to be handled here
            if self.filtering:
                content = self.data_buffer[-self.filtered_data_length:]
                content = self.typogrify.widont(tag, content)
                self.data_buffer = self.data_buffer[:-self.filtered_data_length] + content

        def get_output(self):
            """If current_pos has not reached to the end of the
            document, then it gets appended here"""

            if self.current_pos < len(self.html_doc):
                self.data_buffer += self.html_doc[self.current_pos:]
                self.current_pos = len(self.html_doc)

            return self.data_buffer

    def __init__(self):
        """Class constructor"""

        # Set default variables
        self.ignores = []  # sets ignores to defaults

    @property
    def ignores(self):
        """Exposes ignores as a list containing
        items to be ignored"""
        pass  # make ignore_tags unaccessible

    @ignores.setter
    def ignores(self, value):
        """The setter of the ignore list, the format is
        as follows: ['div','span.test','#test'] would
        ignore: the tag div, the tag span if it has
        a class of test, all id's set to test"""
        value += self.__default_ignores
        tags, attributes = self._process_ignores(value)
        self.__ignores = list([tags, attributes])

    def _process_ignores(self, ignores):
        """User specified HTML tags or attributes can be ignored. This
        method classifies the different ignores into three categories:
          1) Tags to be ignored (e.g. span, div)
          2) Attributes to be ignored, with # representing an id, and .
             representing a class (e.g. #test - ignore all id's that
             are set to test)
          3) Attributes on tags, using the same attribute format as
             mentioned above (e.g. span.test - ignore all span elements
             that have class set to test)"""

        ignores = set(map(lambda ign: ign.strip(), ignores))  # strip ws and make unique
        ignored_tags = set()  # contains tags that will be ignored
        ignored_attributes = dict()  # contains attributes (classes or ids) to be ignored

        # classify ignores into categories
        tags = set(filter(lambda x: '.' not in x and '#' not in x, ignores))
        generic_filters = set(filter(lambda x: x.startswith(('.','#')), ignores))
        tag_filters = ignores - (tags | generic_filters)

        # tags that are to be ignored
        for item in tags:
            ignored_tags.add(item)

        # attributes that are to be ignored
        ignored_attributes[any_tag] = set()

        for item in generic_filters:
            ignored_attributes[any_tag].add(item)

        for item in tag_filters:
            tag_attr = re.split(r'([.#])', item, 1)

            # Do not process if tag is already being ignored
            if tag_attr[0] not in tags:
                attr = ignored_attributes.get(tag_attr[0], set())
                attr.add(tag_attr[1]+tag_attr[2])
                ignored_attributes[tag_attr[0]] = attr

        return (ignored_tags, ignored_attributes)

    def _should_be_filtered(self, tag, attrs):
        """Determines if the current html node should be filtered.
        A node should be filtered if it's tag or its class or id
        attribute was not specified to be ignored by the user"""
       
        # Test if the node's tag should be filtered
        if self.__ignores[0] and tag in self.__ignores[0]:
            return False
        
        # Test if the node's attributes should be filtered
        filters = self.__ignores[1][any_tag]
        if tag in self.__ignores[1]:
            filters |= self.__ignores[1][tag]

        try:
            if any('.%s' % attr[1] in filters for attr in attrs if attr[0] == 'class'):
                return False
        except KeyError:
            pass

        try:
            if any('#%s' % attr[1] in filters for attr in attrs if attr[0] == 'id'):
                return False
        except KeyError:
            pass

        return True

    #
    # Typogrify Filters
    #
    def amp(self, text):
        """Wraps apersands in HTML with ``<span class="amp">`` so they can be
        styled with CSS. Apersands are also normalized to ``&amp;``. Requires
        ampersands to have whitespace or an ``&nbsp;`` on both sides."""

        amp_finder = re.compile(r"""
                (\s|&nbsp;)         # Group 1: prefixed whitespace
                (?:&|&amp;|&\#38;)  # The actual ampersand (non capturing group)
                (\s|&nbsp;)         # Group 2: suffixed whitespace
            """, re.VERBOSE)

        replace_function = lambda match: """%s<span class="amp">&amp;</span>%s""" % match.group(1,2)
        text = amp_finder.sub(replace_function, text)

        return text

    def caps(self, text):
        """Wraps multiple capital letters in ``<span class="caps">``
        so they can be styled with CSS."""

        cap_finder = re.compile(r"""
                (                     # Start group capture
                (?=(:?\d*[A-Z]){2})   # Positive look ahead: At least two caps interspersed with any amount of digits must exist
                (?:[A-Z\d']*)         # Any amount of caps, digits or dumb apostrophes
                |                     # Or
                (?:[A-Z]+\.\s??){2,}  # Caps followed by '.' must be present at least twice (note \s?? which is non-greedy)
                )                     # End group capture
            """, re.VERBOSE)
        
        replace_function = lambda match: """<span class="caps">%s</span>""" % match.group(1)
        text = cap_finder.sub(replace_function, text)

        return text

    def widont(self, tag, text):
        """Replaces the space between the last two words in a string with ``&nbsp;``
        Works in these block tags ``(h1-h6, p, li, dd, dt)`` and also accounts for
        potential closing inline elements ``a, em, strong, span, b, i``"""

        approved_tags = ['a','em','span','strong','i','b','p','h1',
                         'h2','h3','h4','h5','h6','li','dt','dd']
        
        # Must be inside an approved tag
        if tag not in approved_tags:
            return text
        
        widont_finder = re.compile(r"""
                    (.*)  # Group 1: captures everything except the final whitespace before a word
                    \s+   # The final whitespace before the word
                    (\S)  # The actual word
                    \s*   # Optional whitespace (which is removed if present)
                """, re.VERBOSE)

        replace_function = lambda match: '%s&nbsp;%s' % match.group(1, 2)
        text = widont_finder.sub(replace_function, text)

        return text

    def initial_quotes(self, text):
        """Wraps initial quotes in ``class="dquo"`` for double quotes or
        ``class="quo"`` for single quotes"""

        quote_finder = re.compile(r"""
                    (                     # Start group capture
                    ("|&ldquo;|&\#8220;)  # A double quote
                    |                     # Or
                    ('|&lsquo;|&\#8216;)  # A single quote
                    )                     # End group capture
                """, re.VERBOSE)

        replace_function = lambda match: """<span class="%s">%s</span>"""\
                % ('dquo' if match.group(2) else 'quo', match.group(1))
        text = quote_finder.sub(replace_function, text, 1) 
        
        return text

    def smarty_pants(self, text):
        """Applies smarty pants to html text"""

        # Try to load smartypants
        try:
            import smartypants
            return smartypants.smartypants(text)
        except ImportError:
            pass  # this should be logged maybe??? Right now, silently ignored

        return text

    def _apply_filters(self, text, tag):
        """Applies the above filters to the text nodes of the HTML doc"""

        # The order of the filters below is important
        # and should not be changed

        # intial_quotes needs to happen at this point so that
        # attribute values introduced later on do not get affected
        text = self.initial_quotes(text)
        text = self.smarty_pants(text)
        text = self.amp(text)
        text = self.caps(text)

        return text

    def filter(self, html_doc, tags=None, session_ignores=None, session_filters=None):
        """Produces Typogryfied html for the Pelican static project"""
        parser = self._HTMLParser(self, html_doc)
        
        return parser.get_output()
