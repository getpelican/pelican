Pelican |正式版|
=================


.. ifconfig:: release.endswith('.dev')

    .. warning::

		这份文档是关于Pelican当前正在开发的版本的。

		您是否在寻找 |last_stable| 版本的文档呢？


Pelican是一个静态页面生成器，用 Python_ 开发。

* 用你喜欢的编辑器（比如vim）以下列格式写内容： reStructuredText_, Markdown_ 或 AsciiDoc_
* 包含一个简单的CLI工具（重）生成你的站点
* 很容易通过版本控制系统和web hooks发布
* 完全地静态输出可以在用任何机器做主机
  
特性
--------

Pelican 当前 |版本| 支持:

* 文章 （例如博客）和页面（例如“关于”，“项目”，“联系我”）
* 通过一个附加服务（Disqus）评论 . (请注意，尽管评论功能很有用，Disqus是一个附加服务，并且
  评论数据会被放在某些您控制不了的位置，并且有可能有会丢失。）
* 主题支持 (主题通过 Jinja2_ 主题创建)
* 在多种语言下发布内容
* Atom/RSS 支持
* 代码高亮功能
* 导入 WordPress，Dotclear，或RSS feeds
* 与其他附加工具写作：比如Twitter，Google Analytics等。 (可选)

为什么叫做"Pelican"?
-----------------------

"Pelican"是法语 *calepin* 单词拼写混乱形成的，意思是笔记本。 ;)

源代码
-----------

您可以在Github上访问源代码： https://github.com/getpelican/pelican

反馈/联系我们
---------------------

如果您希望看到新特性在Pelican被实现，不要犹豫，请提供建议、克隆这个仓库或做其他的贡献。
有许多贡献的方法： :doc:`contribute<contribute>`.
它是开源的，小子！

将反馈发消息到 "authors at getpelican dot com". 若想得到更快的回复, 您也可以通过IRC参加
团队： `#pelican on Freenode`_ 。 如果您手头没有IRC客户端, 请用 webchat_ 进行快速反馈。
如果您在IRC上提问却没有立即得到回答，请不要离开这个频道。 由于失去差异将需要等几个小时，但如果您
有足够的耐心留在频道，基本上一定会有人回应你的提问。

文档
-------------

欲看一个法语的版本请点击 :doc:`fr/index` 。

.. toctree::
   :maxdepth: 2

   入门
   设置
   主题
   插件
   内部构架
   Pelican主题
   导入工具
   Faq
   提示
   贡献
   报告错误
   更新记录

.. Links

.. _Python: http://www.python.org/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Markdown: http://daringfireball.net/projects/markdown/
.. _AsciiDoc: http://www.methods.co.nz/asciidoc/index.html
.. _Jinja2: http://jinja.pocoo.org/
.. _`Pelican documentation`: http://docs.getpelican.com/latest/
.. _`Pelican's internals`: http://docs.getpelican.com/en/latest/internals.html
.. _`#pelican on Freenode`: irc://irc.freenode.net/pelican
.. _webchat: http://webchat.freenode.net/?channels=pelican&uio=d4
