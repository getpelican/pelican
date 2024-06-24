��    �      D              l
  ^  m
     �     �     �  w     H   �  ,   �  I  �  &   G  (   n  ,   �  9   �  *   �  7   )  !   a     �     �     �  Z   �  ^     �   w  >   8  J   w     �  �   B  �     m  �  K        N  (   [    �  >   �  �   �  .   n  ?   �  &   �  =     c   B  �   �  �   Q  �     �   �  l   �  �     %  �  �   !     �!    �!  8   �"     #  f   �#     $  �   $  �   �$  h  R%  1  �&     �'  .   (     <(     X(  �   p(     e)  ?   n)  #   �)  .   �)     *  ?   *  �  E*  �   �,  �  �-  j   �/     ?0     F0  �   L0  �   "1  �   2  s   �2  �   3  �   �3  y   �4  b  5     o6  -   �6     �6  �   �6  '   �7  �   �7  M   T8  �  �8  �  G:  �  <     �=  �  �=  &   �?  7   �?  5   �?     )@     =@  �   S@  �   �@  �   �A  ,   ZB     �B    �B  t   �C    0D     PF      ]F     ~F  �   �F  �   �G  ^   H  �   nH  4   cI  >   �I     �I  �  �I  �   �K  �   oL  F   fM  �   �M    <N  �   \O  
   �O     P  r   P     �P     �P     �P     �P     �P  "  �P  "   �Q     �Q     R  
   R     R     +R     4R     AR     ]R  	   }R     �R     �R     �R     �R     �R  '   �R     �R     S     S     'S     /S     =S  
   IS     TS  	   bS     lS     yS     �S     �S     �S     �S     �S  {  �S    (U     *Y     =Y     MY  �   iY  ?   �Y  -   .Z  0  \Z  3   �[  0   �[  E   �[  F   8\  A   \  =   �\  -   �\     -]     L]     S]  I   c]  |   �]  �   *^  7   �^  7   �^  �   4_  �   �_  u   �`  6  a  N   <b     �b  $   �b  >  �b  q   �c  �   nd  )   &e  -   Pe  '   ~e  9   �e  �   �e  �   rf  �   g  �   h  �  �h  n   1j  �   �j    lk  �   yl      m  �  3m  9   �n  �   �n  p   �o     p  �   p  r   �p  @  &q  �   gr     ^s  *   ts     �s     �s  �   �s     }t  >   �t  0   �t  @   �t     >u  f   Bu  [  �u  �   x  �  �x  �   {z     {     {  �   {    �{  s   �|  ^   F}     �}  �   %~  W   �~  *       F�  :   _�     ��  �   ��  -   n�  �   ��  0   i�  [  ��  �  ��  �  ��     e�  9  r�  <   ��  >   �  *   (�     S�     `�  �   v�  �   �  �   ��  -   ��     ��  �   ɋ  u   ��    4�     <�  '   C�  	   k�  '  u�  �   ��  W   &�  \  ~�  M   ے  J   )�     t�  L  ��  �   Δ  �   ��  X   ��  �   �  �   ��     o�  
   �     ��  �   �     ��     ��     ��     ��     ��    Ǚ  /   �     �     #�  
   ,�     7�     C�     L�  "   Y�  "   |�  	   ��     ��     ��     ��  #   ϛ     �      ��      �     :�     C�     O�     W�     e�  
   q�     |�  	   ��     ��     ��     ��     ��     ��     ��     ǜ   **Be careful when linking to a file from multiple documents:** Since the first link to a file finalizes its location and Pelican does not define the order in which documents are processed, using ``{attach}`` on a file linked by multiple documents can cause its location to change from one site build to the next. (Whether this happens in practice will depend on the operating system, file system, version of Pelican, and documents being added, modified, or removed from the project.) Any external sites linking to the file's old location might then find their links broken. **It is therefore advisable to use {attach} only if you use it in all links to a file, and only if the linking documents share a single directory.** Under these conditions, the file's output location will not change in future builds. In cases where these precautions are not possible, consider using ``{static}`` links instead of ``{attach}``, and letting the file's location be determined by the project's ``STATIC_SAVE_AS`` and ``STATIC_URL`` settings. (Per-file ``save_as`` and ``url`` overrides can still be set in ``EXTRA_PATH_METADATA``.) And the French version:: Articles and pages Attaching static files Author and tag lists may be semicolon-separated instead, which allows you to write authors and tags containing commas:: Both Markdown and reStructuredText syntaxes provide mechanisms for this. Brief description of content for index pages By default, Pelican uses the article's URL "slug" to determine if two or more articles are translations of one another. (This can be changed with the ``ARTICLE_TRANSLATION_ID`` setting.) The slug can be set manually in the file's metadata; if not set explicitly, Pelican will auto-generate the slug from the title of the article. Content author, when there is only one Content authors, when there are multiple Content category (one only — not multiple) Content keywords, separated by commas (HTML content only) Content language ID (``en``, ``fr``, etc.) Content status: ``draft``, ``hidden``, or ``published`` Content tags, separated by commas Deprecated internal link syntax Description File metadata Following below are some examples for **reStructuredText** using `the include directive`_: For **Markdown**, one must rely on an extension. For example, using the `mdx_include plugin`_: For Markdown, which utilizes the `CodeHilite extension`_ to provide syntax highlighting, include the language identifier just above the code block, indenting both the identifier and the code:: For example, a Pelican project might be structured like this:: For example, a project's content directory might be structured like this:: For example, if you want to have line numbers displayed for every code block and a CSS prefix, you would set this variable to:: For example, the following code block enables line numbers, starting at 153, and prefixes the Pygments CSS classes with *pgcss* to make the names more unique and avoid possible CSS conflicts:: For reStructuredText, use the ``code-block`` directive to specify the type of code to be highlighted (in these examples, we'll use ``python``):: From Pelican 3.1 onwards, it is now possible to specify intra-site links to files in the *source content* hierarchy instead of files in the *generated* hierarchy. This makes it easier to link from the current post to other content that may be sitting alongside that post (instead of having to determine where the other content will be placed after site generation). Here is an example of two articles, one in English and the other in French. Hidden Posts Identifier used in URLs and translations If a static file is linked multiple times, the relocating feature of ``{attach}`` will only work in the first of those links to be processed. After the first link, Pelican will treat ``{attach}`` like ``{static}``. This avoids breaking the already-processed links. If content is a translation of another (``true`` or ``false``) If present or set to "table", output line numbers in a table; if set to "inline", output them inline. "none" means do not output the line numbers for this table. If present, wrap line numbers in ``<a>`` tags. If set, do not output background color for the wrapping element If set, do not wrap the tokens at all. If set, every nth line will be given the 'special' CSS class. If specified, settings for individual code blocks will override the defaults in your settings file. If you are writing your content in reStructuredText format, you can provide this metadata in text files via the following syntax (give your file the ``.rst`` extension):: If you create a folder named ``pages`` inside the content folder, all the files in it will be used to generate static pages, such as **About** or **Contact** pages. (See example filesystem layout below.) If you do not explicitly specify summary metadata for a given post, the ``SUMMARY_MAX_LENGTH`` setting can be used to specify how many words from the beginning of an article are used as the summary. If you do not want the original version of one specific article to be detected by the ``DEFAULT_LANG`` setting, use the ``translation`` metadata to specify which posts are translations:: If you use ``{static}`` to link to an article or a page, this will be turned into a link to its source code. If you want to exclude any pages from being linked to or listed in the menu, then add a ``status: hidden`` attribute to its metadata. This is useful for things like making error pages that fit the generated theme of your site. If you want to publish an article or a page as a draft (for friends to review before publishing, for example), you can add a ``Status: draft`` attribute to its metadata. That article will then be output to the ``drafts`` folder and not listed on the index page nor on any category or tag page. If your articles should be automatically published as a draft (to not accidentally publish an article before it is finished), include the status in the ``DEFAULT_METADATA``:: Importing an existing site In the default configuration, all files with a valid content file suffix (``.html``, ``.rst``, ``.md``, ...) get processed by the article and page generators *before* the static generator. This is avoided by altering the ``*_EXCLUDE`` settings appropriately. In this example, ``article1.rst`` could look like this:: Include a fragment of a file delimited by two identifiers, highlighted as C++ (slicing based on line numbers is also possible): Include a raw HTML file (or an inline SVG) and put it directly into the output without any processing: Including other files It is also possible to specify the ``PYGMENTS_RST_OPTIONS`` variable in your Pelican settings file to include options that will be automatically applied to every code block. It is possible to import your site from several other blogging sites (like WordPress, Tumblr, ..) using a simple script. See :ref:`import`. It is possible to translate articles. To do so, you need to add a ``lang`` meta attribute to your articles/pages and set a ``DEFAULT_LANG`` setting (which is English [en] by default). With those settings in place, only articles with the default language will be listed, and each article will be accompanied by a list of available translations for that article. Like pages, posts can also be marked as ``hidden`` with the ``Status: hidden`` attribute. Hidden posts will be output to ``ARTICLE_SAVE_AS`` as expected, but are not included by default in tag, category, and author indexes, nor in the main article feed. This has the effect of creating an "unlisted" post. Line number for the first line. Linking to authors, categories, index and tags Linking to internal content Linking to static files List of lines to be highlighted, where line numbers to highlight are separated by a space. This is similar to ``emphasize-lines`` in Sphinx, but it does not support a range of line numbers separated by a hyphen, or comma-separated line numbers. Metadata Metadata syntax for Markdown posts should follow this pattern:: Mixed content in the same directory Modification date (e.g., ``YYYY-MM-DD HH:SS``) N/A Name of template to use to generate content (without extension) Note that, aside from the title, none of this content metadata is mandatory: if the date is not specified and ``DEFAULT_DATE`` is set to ``'fs'``, Pelican will rely on the file's "mtime" timestamp, and the category can be determined by the directory in which the file resides. For example, a file located at ``python/foobar/myfoobar.rst`` will have a category of ``foobar``. If you would like to organize your files in other ways where the name of the subfolder would not be a good category name, you can set the setting ``USE_FOLDER_AS_CATEGORY`` to ``False``.  When parsing dates given in the page metadata, Pelican supports the W3C's `suggested subset ISO 8601`__. Note that, depending on the version, your Pygments module might not have all of these options available. Refer to the *HtmlFormatter* section of the `Pygments documentation <https://pygments.org/docs/formatters/>`_ for more details on each of the options. Note: Placing static and content source files together in the same source directory does not guarantee that they will end up in the same place in the generated site. The easiest way to do this is by using the ``{attach}`` link syntax (described below). Alternatively, the ``STATIC_SAVE_AS``, ``PAGE_SAVE_AS``, and ``ARTICLE_SAVE_AS`` settings (and the corresponding ``*_URL`` settings) can be configured to place files of different types together, just as they could in earlier versions of Pelican. Notice that all the files linked using ``{attach}`` ended up in or beneath the article's output directory. Option Pages Pelican also supports `Markdown Extensions`_, which might have to be installed separately if they are not included in the default ``Markdown`` package and can be configured and loaded via the ``MARKDOWN`` setting. Pelican can also process HTML files ending in ``.html`` and ``.htm``. Pelican interprets the HTML in a very straightforward manner, reading metadata from ``meta`` tags, the title from the ``title`` tag, and the body out from the ``body`` tag:: Pelican can provide colorized syntax highlighting for your code blocks. To do so, you must use the following conventions inside your content files. Pelican considers "articles" to be chronological content, such as posts on a blog, and thus associated with a date. Pelican implements an extension to reStructuredText to enable support for the ``abbr`` HTML tag. To use it, write something like this in your post:: Pelican tries to be smart enough to get the information it needs from the file system (for instance, about the category of your articles), but some information you need to provide in the form of metadata inside your files. Please note that the metadata available inside your files takes precedence over the metadata extracted from the filename. Post content quality notwithstanding, you can see that only item in common between the two articles is the slug, which is functioning here as an identifier. If you'd rather not explicitly define the slug this way, you must then instead ensure that the translated article titles are identical, since the slug will be auto-generated from the article title. Print every nth line number. Publication date (e.g., ``YYYY-MM-DD HH:SS``) Publishing drafts Readers for additional formats (such as AsciiDoc_) are available via plugins, which you can find via the `Pelican Plugins`_ collection as well as the legacy `pelican-plugins`_ repository. Save content to this relative file path Site generation would then copy ``han.jpg`` to ``output/images/han.jpg``, ``menu.pdf`` to ``output/pdfs/menu.pdf``, and write the appropriate links in ``test.md``. Site generation would then produce an output directory structured like this:: So the title is the only required metadata. If that bothers you, worry not. Instead of manually specifying a title in your metadata each time, you can use the source content file name as the title. For example, a Markdown source file named ``Publishing via Pelican.md`` would automatically be assigned a title of *Publishing via Pelican*. If you would prefer this behavior, add the following line to your settings file:: Starting with Pelican 3.5, static files can be "attached" to a page or article using this syntax for the link target: ``{attach}path/to/file``. This works like the ``{static}`` syntax, but also relocates the static file into the linking document's output directory. If the static file originates from a subdirectory beneath the linking document's source, that relationship will be preserved on output. Otherwise, it will become a sibling of the linking document. Starting with Pelican 3.5, static files can safely share a source directory with page source files, without exposing the page sources in the generated site. Any such directory must be added to both ``STATIC_PATHS`` and ``PAGE_PATHS`` (or ``STATIC_PATHS`` and ``ARTICLE_PATHS``). Pelican will identify and process the page source files normally, and copy the remaining files as if they lived in a separate directory reserved for static files. Static content Static files are files other than articles and pages that are copied to the output folder as-is, without processing. You can control which static files are copied over with the ``STATIC_PATHS`` setting of the project's ``pelicanconf.py`` file. Pelican's default configuration includes the ``images`` directory for this, but others must be added manually. In addition, static files that are explicitly linked to are included (see below). String to prepend to token class names String to print between lines of code, '\n' by default. Support for the old syntax may eventually be removed. Syntax highlighting The English article:: The idea behind "pages" is that they are usually not temporal in nature and are used for content that does not change very often (e.g., "About" or "Contact" pages). The specified identifier (e.g. ``python``, ``ruby``) should be one that appears on the `list of available lexers <https://pygments.org/docs/lexers/>`_. This core Pelican functionality does not create sub-sites (e.g. ``example.com/de``) with translated templates for each language. For such advanced functionality the `i18n_subsites plugin`_ can be used. This only works for linking to static files. Title of the article or page To link to internal content (files in the ``content`` directory), use the following syntax for the link target: ``{filename}path/to/file``. Note: forward slashes, ``/``, are the required path separator in the ``{filename}`` directive on all operating systems, including Windows. To publish a post when the default status is ``draft``, update the post's metadata to include ``Status: published``. To remain compatible with earlier versions, Pelican still supports vertical bars (``||``) in addition to curly braces (``{}``) for internal links. For example: ``|filename|an_article.rst``, ``|tag|tagname``, ``|category|foobar``. The syntax was changed from ``||`` to ``{}`` to avoid collision with Markdown extensions or reST directives. Similarly, Pelican also still supports linking to static content with ``{filename}``. The syntax was changed to ``{static}`` to allow linking to both generated articles and pages and their static sources. Translations URL to use for this article/page Valid values When experimenting with different settings (especially the metadata ones) caching may interfere and the changes may not be visible. In such cases disable caching with ``LOAD_CONTENT_CACHE = False`` or use the ``--ignore-cache`` command-line switch. When using ``{attach}``, any parent directory in ``*_URL`` / ``*_SAVE_AS`` settings should match each other. See also: :ref:`url-settings` When using reStructuredText the following options are available in the `code-block` directive: With HTML, there is one simple exception to the standard metadata: tags can be specified either via the ``tags`` metadata, as is standard in Pelican, or via the ``keywords`` metadata, as is standard in HTML. The two can be used interchangeably. Wrap each line in a span using this and -linenumber. Wrap each line in an anchor using this string and -linenumber. Writing content You can also extract any metadata from the filename through a regular expression to be set in the ``FILENAME_METADATA`` setting. All named groups that are matched will be set in the metadata object. The default value for the ``FILENAME_METADATA`` setting will only extract the date from the filename. For example, if you would like to extract both the date and the slug, you could set something like: ``'(?P<date>\d{4}-\d{2}-\d{2})_(?P<slug>.*)'`` You can also have your own metadata keys (so long as they don't conflict with reserved metadata keywords) for use in your templates. The following table contains a list of reserved metadata keywords: You can also use Markdown syntax (with a file ending in ``.md``, ``.markdown``, ``.mkd``, or ``.mdown``). Markdown generation requires that you first explicitly install the Python-Markdown_ package, which can be done via ``pip install Markdown``. You can find sample content in the repository at ``samples/content/``. You can link to authors, categories, index and tags using the ``{author}name``, ``{category}foobar``, ``{index}`` and ``{tag}tagname`` syntax. You can link to static content using ``{static}path/to/file``. Files linked to with this syntax will automatically be copied to the output directory, even if the source directories containing them are not included in the ``STATIC_PATHS`` setting of the project's ``pelicanconf.py`` file. You can use the ``DISPLAY_PAGES_ON_MENU`` setting to control whether all those pages are displayed in the primary navigation menu. (Default is ``True``.) ``author`` ``authors`` ``authors`` is a comma-separated list of article authors. If there's only one author you can use ``author`` field. ``category`` ``date`` ``keywords`` ``lang`` ``modified`` ``modified`` should be last time you updated the article, and defaults to ``date`` if not specified. Besides you can show ``modified`` in the templates, feed entries in feed readers will be updated automatically when you set ``modified`` to the current date after you modified your article. ``pelicanconf.py`` would include:: ``save_as`` ``slug`` ``status`` ``summary`` ``tags`` ``template`` ``test.md`` would include:: ``testpost.md`` would include:: ``title`` ``translation`` ``url`` anchorlinenos and ``article2.md``:: classprefix ctags file to use for name definitions. format for the ctag links. hl_lines lineanchors linenos linenospecial linenostart linenostep lineseparator linespans nobackground nowrap number numbers string tagsfile tagurlformat Project-Id-Version: Pelican 4
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2024-03-13 10:21+0800
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language: zh_CN
Language-Team: zh_CN <LL@li.org>
Plural-Forms: nplurals=1; plural=0;
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.13.0
 **当有多个文档链接到同一文件时需要尤其小心：** 第一次链接到文件时Pelican就会确定其最终位置，而Pelican处理文档的顺序是不能确定的，因此多个文档使用 ``{attach}`` 链接到同一文件时，每一次站点生成后该文件的最终位置是无法确定的。（这种情况是否会发生取决于操作系统、文件系统、Pelican的版本、文档从项目中的添加修改移除）外站中到文件旧位置的链接就会损坏。**因此，建议只有当文件只有一个链接，并且链接到某文件的文档都在同一目录下时才使用 {attach}**。在这种情况下，文件的输出位置在未来的站点构建中不会变化。如果无法保证上述条件来预防链接损坏，可以考虑使用 ``{static}`` 来替换 ``{attach}`` 。如此，文件的最终位置就由 ``STATIC_SAVE_AS`` 和 ``STATIC_URL`` 来决定。（每个文件的 ``save_as`` 和 ``url`` 仍然可以通过更改 ``EXTRA_PATH_METADATA`` 设置来覆盖） 法语版本为： 文章和页面 将静态文件作为附件 如果有多个作者或多个文章标签，需要将他们以分号分隔，这样就可以在作者或标签中包含逗号了： Markdown和reStructuredText的语法中都提供了这种机制 内容的简短概要，会显示在首页上 默认情况下，Pelican会使用文章的URL  "slug" 来判断当前文档是否是同一篇文章的不同翻译版本。（这一点可以通过 ``ARTICLE_TRANSLATION_ID`` 设置来改变）slug可以通过元数据手动指定，若没有，Pelican会根据文章的标题title来自动生成slug。 当只有一个作者时可以使用这个元数据 当有多个作者时需要使用这个元数据 内容的分类（只能归属到一个分类中，不支持多个） 内容的关键字，以逗号分隔（只能在HTML内容中使用） 内容的语言ID（例如 ``en`` 、 ``fr`` 、 ``zh-cn`` 等） 内容的状态： ``draft``、 ``hidden`` 或 ``published``  内容的标签，多个标签以逗号分隔 已弃用的内部链接语法 描述 文件元数据 下面是 **reStructuredText** 使用 `include指令`_ 的一些例子： 对于 **Markdown** ，若要进行文件引入，就必须使用扩展插件。例如可以使用 `mdx_include plugin`_ ： Markdown则使用 `CodeHilite extension`_ 扩展插件来完成语法高亮。在代码上方标记所用语言，同时将其与代码都进行缩进： 例如，某Pelican项目的文件结构组织如下： 例如，某Pelican项目的文件结构组织如下： 举个例子，若您希望每个代码块都显示行号，并且在CSS类名前都加上前缀pgcss，就可以像这样设置 ``PYGMENTS_RST_OPTIONS`` ： 举个例子，下面的代码块开启了行号显示，从153行开始输出，并且指定Pygments的CSS类以 *pgcss* 为前缀，使得类名更为独特并避免可能的CSS冲突： 对于reStructuredText，使用 ``code-block`` 指令指定代码所使用的语言（此处以``python``为例）： 从Pelican 3.1开始，站内链接可以在 *源内容* 层次下指定，而不是只能在 *生成站点* 的层次下指定。当需要在当前推文链接到邻近位置的内容时，可以直接从源内容文件的位置开始链接（而不需要考虑在站点生成后文件会被放在哪儿）。 以下的例子是一篇文章有英语和法语两个翻译版本的情况。 隐藏推文 作为URL和翻译的唯一标识符 若一个静态文件被多次链接， ``{attach}`` 只会在该静态文件第一次被链接时进行重定位处理（即按照上面的规则复制到对应目录）。之后使用 ``{attach}`` 进行的链接的效果就和 ``{static}`` 一模一样了。这样子就可以避免破坏已经生成好的链接。 手动指定当前内容是否是某一个的翻译版本（该元数据的值只能是 ``true`` 或 ``false``） 开启此选项或将此选项设为“table”时，输出表格时会带上行号；如果设为“inline”，则内联输出行号；如果设为“none”，则不输出行号。 指定行号是否显示在 <a> 标签中 若设置，则不为元素输出背景颜色 若设置，则不包裹代码符号。 是否每隔几行就设置一行特殊的css样式类。 若同时在 ``PYGMENTS_RST_OPTIONS`` 和某些代码块中单独指定了一些选项，单独指定的会将 ``PYGMENTS_RST_OPTIONS`` 覆盖。 如果您用reStructuredText的格式进行内容创作，您可以按照下面的语法在文本文件中提供元数据（请给文本文件加上 ``.rst`` 的后缀） 如果您在content文件夹下创建了一个 ``pages`` 文件夹，那么Pelican会为其中的每个文件都生成一个静态页面例如 **关于** 、 **联系我们** 这样的页面。（具体可以看下面项目文件组织的例子） 若您没有指定summary元数据，Pelican会自动从推文开头截取由 ``SUMMARY_MAX_LENGTH`` 指定长度的内容作为summary。 如果您不希望某篇文章的原始版本被视为是 ``DEFAULT_LANG`` 设置指定的翻译版本，可以使用 ``translation`` 元数据来指出本推文是一个非源语言的翻译版本。（译者注：例如，设置的默认语言为[zh-cn]，如果某篇推文的原始版本是英文而不是中文，那么对于中文翻译版本的就可以指定其translations元数据为true） 如果您使用 ``{static}`` 链接到文章或页面，会链接到源文件而不是文章或页面本身。 如果您希望让某些页面不会被链接并且也不列在任何菜单中，可以为它加上元数据属性 ``status: hidden`` 。这对于制作符合网站生成主题的错误页面很有用。 如果您想要以草稿的形式发布文章或页面（例如在正式发布前给朋友预览），可以添加元数据属性 ``Status: draft`` 。如此，文章就会输出到 ``drafts`` 文件夹中，并且不会被列在首页、分类或是标签页面中。 若您希望文章默认以草稿形式发布（可以防止在完成文章前不小心将其正式发布），可以将status属性加在 ``DEFAULT_METADATA`` 中： 导入已有站点 在默认配置下，所有后缀名有效的文件（ ``.html`` 、 ``.rst`` 、 ``.md`` , ...）都会由文章页面生成器处理，这个处理是在静态文件生成器之前完成的。当您需要将一些会被认为是文章或页面的文件作为静态文件时，可以合理使用 ``*_EXCLUDE`` 设置（例如 ``ARTICLE_EXCLUDES`` 、 ``PAGE_EXCLUDES``）将他们排除。 在这个例子中， ``article1.rst`` 的内容如下： 下面的例子，引入了一段用一对标识符分隔的文件片段，并指定以C++语法进行高亮显示。（基于行号的片段指定也是可以的） 将一HTML文件（或者一个行内SVG）直接引入，并且不进行任何处理直接将其作为输出： 引入其他文件 您也可以在Pelican的设置文件中指定 ``PYGMENTS_RST_OPTIONS`` ，如此就可以让Pelican自动在每个代码块上使用指定的选项 您可以使用一个简单的脚本导入已有的站点（例如WordPress、Tumblr）。详见 :ref:`import` 。 一篇文章可以有多个翻译版本。对于这类文章，您需要加上元数据属性 ``lang`` ，并且在设置中指定 ``DEFAULT_LANG`` （默认为[en]）。完成上述设置后，列表中只会列出默认语言版本的文章，并且这些文章中会列出所有可用的翻译版本供读者选择。 和页面一样，推文也能通过 ``Status: hidden`` 标记为隐藏状态。隐藏的推文会输出到 ``ARTICLE_SAVE_AS`` 指定的目录中，这些推文“不会被列出”，即不会在标签、分类、作者主页、feed中出现。 起始行的行号。 链接到作者、分类、索引、标签 文章或页面的内部链接 链接到静态文件 需要高亮的行号列表，行号之间以空格隔开。这与Sphinx中的 ``emphasize-lines`` 类似，但是不支持使用连字符和逗号指定行号范围。 元数据类型 Markdown中的元数据语法需要按照下面的格式书写 在同一个目录下存放不同类型的内容 最后修改日期（需要以 ``YYYY-MM-DD HH:SS`` 的格式） N/A 用于指定要使用的生成模板，只需要写模板的名字，不需要模板文件的后缀名 需要注意的是，除了title外，其他所有元数据都是可以缺省的。若未指定日期元数据并且将 ``DEFAULT_DATE`` 设置为了 ``'fs'``，Pelican就会从文件的 "mtime" 时间戳中获取日期信息；category会从文件所在的子目录的名称中提取。例如 ``python/foobar/myfoobar.rst`` 的category元数据值就会被设为 ``foobar``。如果您不希望子目录的名称成为category的值，则需要在设置中将 ``USE_FOLDER_AS_CATEGORY`` 设为 ``False`` 。进行日期元数据的解析时，Pelican支持W3C的 `suggested subset ISO 8601`__ 标准。 请注意，由于版本的不同，Pygments模块可能不完全支持上述选项。请参考 `Pygments 文档 <https://pygments.org/docs/formatters/>`_ 中的 *HtmlFormatter* 一节获取每个选项的详细信息。 请注意：Pelican不保证放在同一个源目录下的静态文件和内容文件在站点生成完后最终出现在同一个地方。要让他们出现在一个地方，可以使用 ``{attach}`` 链接语法（下面会提到）。要么还可以通过设置 ``STATIC_SAVE_AS`` 、 ``PAGE_SAVE_AS`` 和 ``ARTICLE_SAVE_AS`` (还有相应的 ``*_URL`` 设置)让不同类型的文件最终放在一起。 可以注意到，使用 ``{attach}`` 链接的文件要么和文章输出处于同级目录，要么就是在文章所在位置的子目录下。 选项 页面 Pelican也支持 `Markdown扩展`_ ，可以是 ``Markdown`` 包自带的扩展，也可以是另外安装的，可以通过 ``MARKDOWN`` 设置这些扩展。 Pelican还能处理后缀名为 ``.html`` 和 ``.htm`` 的HTML文件Pelican在解释转换HTML文件时用的方法非常直接，会从 ``meta`` HTML标签中获取元数据信息，从 ``title`` HTML标签中获取标题，从 ``body`` 标签中获取文章的正文内容： 您可以按照下面的约定在文件内容中添加代码块，Pelican可以完成五彩缤纷的语法高亮。 Pelican将“文章”视为有时间顺序的内容，例如博客上的博文就是文章。 Pelican在reStructuredText上实现了 ``abbr`` HTML标签的使用支持。在正文部分按照下面的形式书写即可。 Pelican可以从文件系统中自动地获取一些信息（例如文章的分类），但是有些信息需要您以元数据的形式在文件中提供。 请注意，您在文件中指定的元数据优先级大于从文件名中提取的。 不谈推文的内容质量，你可以发现上面两篇文章的共同点在于它们的slug是相同的，slug在这里作为标识符存在。若您没有手动指定slug，那么请保证同一篇文章的不同翻译版本的标题是相同的，如此slug会根据文章标题自动生成。 每隔几行输出一次 发布日期（需要以 ``YYYY-MM-DD HH:SS`` 的格式） 发布草稿 对其他格式的支持（例如 AsciiDoc_ ）可以通过插件实现，在 `Pelican Plugins`_ 集合中可以查看所有插件。当然，在老的 `pelican-plugins`_ 仓库中也可以查看。 将内容保存到指定的相对文件路径 站点生成时会将 ``han.jpg`` 拷贝到 ``output/images/han.jpg`` 、将 ``menu.pdf`` 拷贝到 ``output/pdfs/menu.pdf`` ，同时也会自动把 ``test.md`` 中的相关链接都替换为正确的。 对应的生成站点输出目录结构如下： 所以说标题是唯一必须指定的元数据。如果您甚至懒得写标题，也不用担心。Pelican会自动将文件名作为内容的标题。例如，Markdown源文件 ``Publishing via Pelican.md`` 的标题会自动设为 *Publishing via Pelican*。如果您希望启用这个特性，请在设置文件中添加下面这么一行： 从Pelican 3.5开始，静态文件可以使用下述语法 “附” 在页面或文章上： ``{attach}path/to/file`` 。这和 ``{static}`` 语法很像，也会将静态文件重定位到文章或页面的对应输出目录中。当文档所链接的静态文件处于其源文件位置的子目录下时，这种父子关系在输出目录中会得以保留。否则，默认情况下，静态文件会和对应的文档处于同一输出目录下。 从Pelican 3.5开始，静态文件就可以和页面源文件安全地放在同一个目录下了。这些包含了不同类型的内容文件的目录需要添加到 ``STATIC_PATHS`` 和 ``PAGE_PATHS`` 中（或者 ``STATIC_PATHS`` 和 ``ARTICLE_PATHS`` 中）Pelican会正常地识别和处理文章和页面源文件，然后再把静态文件复制，和处理处于单独一个文件夹的静态文件行为一致。 静态内容 静态文件与文章、页面不同，会原模原样地复制到输出文件夹中。当然，您也通过设置 ``STATIC_PATHS`` 更改复制的目标文件夹。Pelican的默认配置只包含了一个 ``images`` 文件夹，其他的需要手动添加。另外静态文件也包含那些被显式链接的。 要添加到用于语法高亮的css类名前面的字符串 每行输出代码之间的输出字符串，默认为 '\n'。 对旧语法地支持最终会被移除。 语法高亮 英语文章如下： “页面”指的是本质上通常不是临时的内容这些内容不会经常改变（例如“关于”“联系我们”这样的，就可以看成“页面”） 指定语言的标识符（例如 ``python``、``ruby``）必须是在 `可用列表 <https://pygments.org/docs/lexers/>`_ 中列出的。 Pelican的这个核心功能并不会给同一文章的不同语言版本创建子站点（例如 ``example.com/de`` ）。但是如果需要创建子站点的话，可以使用扩展插件  `i18n_subsites plugin`_  这只在链接到静态文件时起作用。 文章或页面的标题 要链接到站内（即在 ``content`` 目录下的文件），使用下述的目标链接语法： ``{filename}path/to/file`` 。注意，在所有操作系统（当然也包括Windows）上，路径的分隔符都要使用正斜杠 ``/`` 。 要发布当前处于 ``draft`` 状态的推文，更新推文的元数据，使其中包括 ``Status: published``。 为了保持和早期版本的兼容，在内部链接中除了使用花括号（ ``{}`` ）外，还支持在内部链接中使用竖线（ ``||`` ）。例如， ``|filename|an_article.rst`` 、  ``|tag|tagname`` 、 ``|category|foobar`` 。将语法中的 ``||`` 改到 ``{}`` 是为了避免和Markdown或reST的语法和指令相冲突。类似地， ``{filename}`` 虽然仍能使用，但是其语法已经改为了 ``{static}`` 。 ``{static}`` 既可以链接到文章或页面，也可以链接到静态资源 翻译 指定本篇文章或页面使用的URL 有效值 在您尝试不同的设置时（特别是在设置元数据时），缓存可能会造成干扰，导致设置更改不起作用。若您遇到了这种问题，可以在设置中加上 ``LOAD_CONTENT_CACHE = False`` ，或是在使用命令行生成站点时加上 ``--ignore-cache`` 参数。 当使用{attach}时， ``*_URL`` / ``*_SAVE_AS`` 设置中的任何父目录都应该相互匹配。具体请参见 :ref:`url-settings` 对于reStructuredText，下面列出的选项可以在 `code-block` 命令中使用： 当使用HTML文件时，上述的众多元数据中有一个比较特殊的存在：tags。这个元数据在HTML文档中有两种方式可以指定，一种是Pelican中定义的 ``tags`` （上面的例子中用的就是这种）；另一种是使用HTML中定义的 ``keywords`` 元数据名（将name属性的“tags”换成“keywords”。 使用指定的字符串和“-行号”将每一行包装在一个span中。 用此处指定的字符串和 “-行号”给每一行都加上锚点。 创作内容 您可以通过 ``FILENAME_METADATA`` 设置来使用正则表达式从文件名中提取元数据。正则匹配到的每个命名分组都被看成一个元数据。 ``FILENAME_METADATA`` 的默认值只会从文件名中提取date和slug。例如，可以使用 ``'(?P<date>\d{4}-\d{2}-\d{2})_(?P<slug>.*)'`` 提取date和slug。 您也可以定义自己的元数据类型（只要和保留的元数据关键字不冲突），这些自定义的元数据关键字可以用在自定义的模板中。下面的列出了所有保留的元数据关键字。 Markdown的语法也是支持的（文件的扩展名需要为 ``.md`` 、``.markdown``、``.mkd``或``.mdown``）要让Pelican进行Markdown的生成，需要先通过 ``pip install Markdown`` 安装 Python的Markdown包_ 。 在代码仓库的 ``samples/content/`` 文件夹下有一些内容示例供您查看。 您可以通过 ``{author}name`` 、 ``{category}foobar`` 、 ``{index}`` 和 ``{tag}tagname`` 这样的语法链接到作者、分类、索引和标签 您可以通过 ``{static}path/to/file`` 链接到静态内容。使用这个指令链接的文件都会被自动复制到输出目录中，即使是没有包含在 ``STATIC_PATHS`` 设置指定目录中的静态内容也会被复制。 您可以通过 ``DISPLAY_PAGES_ON_MENU`` 设置来决定页面是否被列在主导航菜单中（默认值为 ``True`` ）。 ``author`` ``authors`` ``authors`` 元数据中是文章作者的列表，各个作者之间用逗号分隔。若只有一个作者，可以使用 ``author``  ``category`` ``date`` ``keywords`` ``lang`` ``modified`` ``modified`` 元数据中应该为文章最后一次的修改时间，若没有指定，会自动与 ``date`` 设为一样的。在您修改文章并将 ``modified`` 设为当前日期后，除了在模板中显示 ``modified`` 之外，feed阅读器中的feed条目也会自动更新。 例如对于某设置文件 ``pelicanconf.py``  ``save_as`` ``slug`` ``status`` ``summary`` ``tags`` ``template``  ``test.md`` 文件内容如下： ``testpost.md`` 的内容如下： ``title`` ``translation`` ``url`` anchorlinenos 下面则是 ``article2.md`` 的： classprefix 用于命名定义的ctags文件 用于ctag链接的格式 hl_lines lineanchors linenos linenospecial linenostart linenostep lineseparator linespans nobackground nowrap number numbers string tagsfile tagurlformat 