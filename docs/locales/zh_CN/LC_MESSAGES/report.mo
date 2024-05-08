��          �               �    �  �   �  �   �  i   �          +  7   �  �   �  M  �     	  ?  
     F  .   U  =   �  �  �  e  l  �   �     ~  R   �  �   �  T   q  
  �  l   �  �   >  l   �  /   M     }  {  �  �     �   �  �   �  U   �       f     +   �  �   �  �  �  �   �    k     �   *   �   6   �   Y  �   U  Y"  �   �$     e%  P   |%  �   �%  L   g&  �   �&  b   �'  �   (  g   �(  +   )     4)   *generators* generate the different outputs. For instance, Pelican comes with an ArticlesGenerator and PagesGenerator, into others. Given a configuration, they can do whatever you want them to do. Most of the time it's generating files from inputs (user inputs and files). *readers* are used to read from various formats (Markdown and reStructuredText for now, but the system is extensible). Given a file, they return metadata (author, tags, category, etc) and content (HTML formatted). *writers* are responsible of all the writing process of the files. They are responsible of writing .html files, RSS feeds and so on. Since those operations are commonly used, the object is created once, and then passed to the generators. A ``context`` is created. It contains the settings from the command line and a settings file if provided. Design process First of all, the command line is parsed, and some content from the user is used to initialize the different generator objects. Here is an overview of the classes involved in Pelican. I also deal with contents objects. They can be ``Articles``, ``Pages``, ``Quotes``, or whatever you want. They are defined in the ``contents.py`` module and represent some content to be used by the program. I have been facing different problems all over the time and wanted to add features to Pelican while using it. The first change I have done was to add the support of a settings file. It is possible to pass the options to the command line, but can be tedious if there is a lot of them. In the same way, I have added the support of different things over time: Atom feeds, multiple themes, multiple markup support, etc. At some point, it appears that the "only one file" mantra was not good enough for Pelican, so I decided to rework a bit all that, and split this in multiple different files. I make two calls because it is important that when the output is generated by the generators, the context will not change. In other words, the first method ``generate_context`` should modify the context, whereas the second ``generate_output`` method should not. I was previously using WordPress, a solution you can host on a web server to manage your blog. Most of the time, I prefer using markup languages such as Markdown or reStructuredText to type my articles. To do so, I use vim. I think it is important to let the people choose the tool they want to write the articles. In my opinion, a blog manager should just allow you to take any kind of input and transform it to a weblog. That's what Pelican does. You can write your articles using the tool you want, and the markup language you want, and then generate a static HTML weblog. In more detail Internally, the following process is followed: I’ve separated the logic in different classes and concepts: Pelican came from a need I have. I started by creating a single file application, and I have make it grow to support what it does by now. To start, I wrote a piece of documentation about what I wanted to do. Then, I created the content I wanted to parse (the reStructuredText files) and started experimenting with the code. Pelican was 200 lines long and contained almost ten functions and one class when it was first usable. Pelican is a simple static blog generator. It parses markup files (Markdown or reStructuredText for now) and generates an HTML folder with all the files in it. I've chosen to use Python to implement Pelican because it seemed to be simple and to fit to my needs. I did not wanted to define a class for each thing, but still wanted to keep my things loosely coupled. It turns out that it was exactly what I wanted. From time to time, thanks to the feedback of some users, it took me a very few time to provide fixes on it. So far, I've re-factored the Pelican code by two times; each time took less than 30 minutes. Read the folder “path”, looking for restructured text files, load each of them, and construct a content object (``Article``) with it. To do so, use ``Reader`` objects. Some history about Pelican The ``generate_context`` method of each generator is called, updating the context. The interface does not really exist, and I have added it only to clarify the whole picture. I do use duck typing and not interfaces. The writer is created and given to the ``generate_output`` method of each generator. Then, it is up to the generators to do what the want, in the ``generate_context`` and ``generate_content`` method. Taking the ``ArticlesGenerator`` class will help to understand some others concepts. Here is what happens when calling the ``generate_context`` method: Then, the ``generate_content`` method uses the ``context`` and the ``writer`` to generate the wanted output. This page comes from a report the original author (Alexis Métaireau) wrote right after writing Pelican, in December 2010. The information may not be up-to-date. To be flexible enough, Pelican has template support, so you can easily write your own themes if you want to. Update the ``context`` with all those articles. Use case Project-Id-Version: Pelican 4
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2023-04-29 21:43+0800
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language: zh_CN
Language-Team: zh_CN <LL@li.org>
Plural-Forms: nplurals=1; plural=0;
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.13.0
 **Generators** 用以生成不同的输出，Pelican自带了 ``ArticlesGenerator`` 和 ``PageGenerator`` 。给定一套配置信息， **Generators** 可以做几乎任何事。但大多数情况下，它的工作就是从输入生成文件。 **Readers** 用于读取不同格式的文件（目前支持Markdown、reStructuredText，但可以继续扩展）。向**Readers**输入一个文件，它会返回文档的元数据（作者、标签、分类等等）与HTML格式的文档正文内容。 **Writers** 负责文件的写入工作，即负责完成 html文件、RSS订阅源等内容因为这些操作都是比较常用的，这个类只会被创建一次，然后再传给Generators。 创建一个 ``context`` ，其中包含了来自命令行和文件的配置信息。 设计过程 首先，解析命令行，并根据用户给入的一些内容来初始化不同的generator对象。 以下是Pelican中涉及的类的概述。 同样，还要处理正文对象。正文对象可以是 ``Articles`` 、 ``Pages`` 、 ``Quotes`` 或者其他你想要的类型。这些对象在 ``contents.py`` 模块中完成定义，同时代表了应用中使用到的内容。 我不断遇到各种问题，在使用过程中还想要往Pelican中添加功能。在对代码的第一次修改中，添加了对配置文件的支持。虽然可以在命令行中往里传入选项，但当配置项多起来后，就会变得异常冗长。同样地，Pelican支持了越来越多的功能：Atom订阅源、多主体支持、多标记语言支持等等。在某一时刻，单文件应用已经不适合Pelican了，因此我决定多做些工作，将应用分离到多个文件中。 由于当generator生成输出时并不会改变上下文，我进行了两次调用。换句话说，第一个方法 ``generate_context`` 会修改上下文，而第二个方法 ``generate_output`` 不会。 我之前使用的是WordPress，你可以将它部署在Web服务器上来管理博客。大多数时候，我更喜欢使用Markdown或reStructuredText等标记语言来撰写文章。为此，我一般用vim来写这些文章。我认为让大家自行选择用于写文章的工具是很重要的。在我看来，博客管理器应该能够接受任何类型的输入并将其转换为博客站。Pelican就采取这一思想。您可以选择自己喜欢的工具以及标记语言来撰写文章，然后生成静态的HTML博客站。 更细节的内容 应用内部按以下流程进行处理： 我将系统整体逻辑分为如下几个类和概念 Pelican来源于我的需求。从单文件应用程序出发，不断成长为现在功能丰富的应用。首先，我写了一份需求文档；然后创建了我想要解析的内容（reStructuredText文件），并开始实验性的编写代码。Pelican的第一个能够使用的版本包含了200行代码、10个函数以及1个类。 Pelican是一个简单的静态博客生成器。它解析标记文件（目前主要是Markdown和reStructuredText），并生成一个文件夹，其中包含了对应于标记文件的HTML。由于Python很简单并且符合需求，我选择使用Python来实现Pelican。我不想为每个东西定义一个类，但同时又想要各部件之间低耦合。事实证明，这正是我想要的。在发展过程中，多亏了用户给的反馈，我花了些时间修复了一些问题。到目前为止，我已经将Pelican的代码重构了两次，每次重构都不会超过30分钟。 读取文件夹路径，查找并加载每个restructured文件，并为每个文件构建一个正文内容对象（ ``Article`` ）。此工作是由 ``Reader`` 对象完成的。 Pelican的一些历史 调用各generator对象的 ``generate_context`` 方法来更新 ``context`` 。 上图中的接口事实上并不存在，我是为了整张图的完整性才加上去的。在实际实现中，使用了鸭子类型而不是接口。 创建 **Writers** 并将其给入generator的 ``generate_output`` 方法。 然后，事情就取决于各generator在 ``generate_context`` 和 ``generate_content`` 中做的操作了。拿 ``ArticlesGenerator`` 举例可以帮助理解其他的一些概念。下面是调用 ``generate_context`` 方法后会发生的事情： 然后， ``generate_content`` 方法使用 ``context`` 和 ``writer`` 来生成想要的输出。 此页面来自原作者 Alexis Métaireau 在2010年12月完成Pelican后作的一篇报告，因此其中的内容可能不是最新的。 为了足够的灵活性，Pelican中支持使用模板，这样你就可以编写自己的主题了。 根据所有的文章更新 ``context`` 。 使用场景 