��    %      D              l  2  m  �  �    [  
   d  �   o  
   ,  �   7  �   �  j   �  a   �  �   ]	     
     
  �   
    �
  Z   �  o        q     �    �  (   �    �  |   �    V  �   b  �     �   �  �   �  �   �  T   U  ^   �  �   	     �  �   �  =  �  �  �  {  ^     �  �   �  �   �  	   u  �        2   y   9   �   �   b   _!  W   �!  �   "     �"     �"  �   �"  3  J#  W   ~$  [   �$     2%     ?%  �   L%  /   *&  �   Z&  �   8'  �   �'  �   �(  �   /)  �   �)  �   �*  �   z+  M   h,  f   �,  �   -     �-  �   �-    �.  �  1   (The default ``Makefile`` and ``devserver.sh`` scripts use the ``python`` and ``pelican`` executables to complete its tasks. If you want to use different executables, such as ``python3``, you can set the ``PY`` and ``PELICAN`` environment variables, respectively, to override the default executable names.) A ``Makefile`` is also automatically created for you when you say "yes" to the relevant question during the ``pelican-quickstart`` process. The advantage of this method is that the ``make`` command is built into most POSIX systems and thus doesn't require installing anything else in order to use it. The downside is that non-POSIX systems (e.g., Windows) do not include ``make``, and installing it on those systems can be a non-trivial task. After you have generated your site, previewed it in your local development environment, and are ready to deploy it to production, you might first re-generate your site with any production-specific settings (e.g., analytics, feeds, etc.) that you may have defined:: Automation Because the above method may have trouble locating your CSS and other linked assets, running Pelican's simple built-in web server will often provide a more reliable previewing experience:: Deployment Following are automation tools that "wrap" the ``pelican`` command and can simplify the process of generating, previewing, and uploading your site. If during the ``pelican-quickstart`` process you answered "yes" when asked whether you want to upload your site via SSH, you can use the following command to publish your site via rsync over SSH:: If you have generated a ``publishconf.py`` using ``pelican-quickstart``, this line is included by default. If you want to use ``make`` to generate your site using the settings in ``pelicanconf.py``, run:: If you'd prefer to have Pelican automatically regenerate your site every time a change is detected (which is handy when testing locally), use the following command instead:: Invoke Make Normally you would need to run ``make regenerate`` and ``make serve`` in two separate terminal sessions, but you can run both at once via:: Once Pelican is installed and you have some content (e.g., in Markdown or reST format), you can convert your content into HTML via the ``pelican`` command, specifying the path to your content and (optionally) the path to your :doc:`settings<settings>` file:: Once the web server has been started, you can preview your site at: http://localhost:8000/ Pelican has other command-line switches available. Have a look at the help to see all the options you can use:: Publish your site Site generation Take a moment to open the ``tasks.py`` file that was generated in your project root. You will see a number of commands, any one of which can be renamed, removed, and/or customized to your liking. Using the out-of-the-box configuration, you can generate your site via:: That's it! Your site should now be live. The above command will generate your site and save it in the ``output/`` folder, using the default theme to produce a simple site. The default theme consists of very simple HTML without styling and is provided so folks may use it as a basis for creating their own themes. The above command will simultaneously run Pelican in regeneration mode as well as serve the output at http://localhost:8000. The advantage of Invoke_ is that it is written in Python and thus can be used in a wide range of environments. The downside is that it must be installed separately. Use the following command to install Invoke, prefixing with ``sudo`` if your environment requires it:: The files generated by Pelican are static files, so you don't actually need anything special to view them. You can use your browser to open the generated HTML files directly:: The steps for deploying your site will depend on where it will be hosted. If you have SSH access to a server running Nginx or Apache, you might use the ``rsync`` tool to transmit your site files:: There are many other deployment options, some of which can be configured when first setting up your site via the ``pelican-quickstart`` command. See the :doc:`Tips<tips>` page for detail on publishing via GitHub Pages. These are just a few of the commands available by default, so feel free to explore ``tasks.py`` and see what other commands are available. More importantly, don't hesitate to customize ``tasks.py`` to suit your specific needs and preferences. To base your publish configuration on top of your ``pelicanconf.py``, you can import your ``pelicanconf`` settings by including the following line in your ``publishconf.py``:: To generate the site for production, using the settings in ``publishconf.py``, run:: To serve the generated site so it can be previewed in your browser at http://localhost:8000/:: To serve the generated site with automatic browser reloading every time a change is detected, first ``python -m pip install livereload``, then use the following command:: Viewing the generated files When you're ready to publish your site, you can upload it via the method(s) you chose during the ``pelican-quickstart`` questionnaire. For this example, we'll use rsync over ssh:: While the ``pelican`` command is the canonical way to generate your site, automation tools can be used to streamline the generation and publication flow. One of the questions asked during the ``pelican-quickstart`` process pertains to whether you want to automate site generation and publication. If you answered "yes" to that question, a ``tasks.py`` and ``Makefile`` will be generated in the root of your project. These files, pre-populated with certain information gleaned from other answers provided during the ``pelican-quickstart`` process, are meant as a starting point and should be customized to fit your particular needs and usage patterns. If you find one or both of these automation tools to be of limited utility, these files can be deleted at any time and will not affect usage of the canonical ``pelican`` command. You can also tell Pelican to watch for your modifications, instead of manually re-running it every time you want to see your changes. To enable this, run the ``pelican`` command with the ``-r`` or ``--autoreload`` option. On non-Windows environments, this option can also be combined with the ``-l`` or ``--listen`` option to simultaneously both auto-regenerate *and* serve the output at http://localhost:8000:: Project-Id-Version: Pelican 4
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2023-11-19 20:08+0800
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language: zh_CN
Language-Team: zh_CN <LL@li.org>
Plural-Forms: nplurals=1; plural=0;
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.13.0
 （默认的 ``Makefile`` 和 ``devserver.sh`` 脚本执行 ``python`` 和 ``pelican`` 来完成任务。若您希望使用其他的可执行文件，例如 ``python3`` ，设置环境变量 ``PY`` 和 ``PELICAN`` 来覆盖默认的可执行文件名。） ``Makefile`` 也是自动生成的。在大多数POSIX系统中都内置了 ``make`` 命令，无需安装即可使用。但在非POSIX系统（例如Windows）中并没有 ``make`` ，在这些系统中安装 ``make`` 时非常困难的。 当您生成好站点后，可以在本地先进行预览，确认无误后，在部署前可能还需使用针对生产环境特定的配置文件重新生成站点： 自动化 事实上，上面的这种浏览方法可能会在CSS或其他链接上出点问题，可以运行Pelican自带的简易web服务器，如此可以获得可靠的预览体验： 部署 下面是一些用于包装 ``pelican`` 命令的自动化工具，可以简化生成、预览和上传站点的过程。 如果在 ``pelican-quickstart`` 过程中，对是否要通过SSH上传站点问题回答了 "yes" ，您就可以使用下面的命令借助rsync在SSH上发布站点： 如果是使用 ``pelican-quickstart`` 生成的 ``publishconf.py`` ，上面这行默认就有。 使用 ``make`` 命令是以 ``pelicanconf.py`` 作为配置文件来生成站点的： 若您希望Pelican在检测到变化时自动重新生成站点（在本地测试的时候很实用），可以使用下面的命令： Invoke Make 一般来说， ``make regenerate`` 和 ``make serve`` 需要在单独的终端会话中运行，下面的命令相当于同时运行上述两个命令： 您应该已经安装好Pelican并且已经创作了一些内容了吧（以Markdown或是reST格式），现在就可以将这些内容通过 ``pelican`` 命令转换为HTML了，在转换时需要指定创作内容存放的路径，（可选） :doc:`设置<settings>` 文件的路径也可单独指定： 当web服务器启动后，可以访问 http://localhost:8000/ 来预览您的站点。 Pelican还有一些其他的命令行选项。可以在帮助中看到所有可用选项： 发布站点 站点生成 可以打开 ``tasks.py`` 文件看看其中的代码，里面的命令可以重命名、删除，可以按照您的喜好自行修改。生成好的文件是开箱即用的，您可以通过下面的命令生成站点： OK！您的站点现在已经可以访问了。 上面的指令会在 ``output/`` 目录下生成站点，使用的是默认的主题。默认主题只使用一些简单的HTML并且不包含样式，大家往往以这个简单主题为基础来创作自己的主题。 上面的命令会让Pelican在重生成模式下持续运行，同样地，您可以通过 http://localhost:8000 访问生成的站点。 Invoke_ 工具使用Python作为书写语言，并且能够用在很多不同的环境中。它需要使用下面的命令单独安装，在某些操作系统中可能需要在前面加上 ``sudo`` ： Pelican生成的文件都是静态的，也就是说不需要使用什么特殊的手段就可以浏览。您可以直接使用浏览器打开生成的HTML文件 部署站点的方法步骤取决于网站托管的位置。对于使用SSH访问的运行着Nginx或Apache的服务器，您可能需要使用 ``rsync`` 工具来传输站点文件： 还有很多其他的部署选项，有一些在第一次通过 ``pelican-quickstart`` 命令建立站点时就已经配置。在 :doc:`小技巧<tips>` 中可以查看如何通过Github Pages部署站点。 默认就可以使用的命令远不止这些，在 ``tasks.py`` 中可以找到更多可用的命令。更重要的是，当您有特定需求和偏好时，直接修改 ``tasks.py`` 即可。 您可以基于 ``pelicanconf.py`` 进行设置文件的配置， 在``publishconf.py`` 中import ``pelicanconf`` 就可实现（译者注：配置文件其实本质上就是一些Python变量，因此import后就可以全部引入）： 使用 ``publishconf.py`` 作为配置文件来为生产环境生成站点： 下面的命令则可以让您在生成后通过浏览器访问 http://localhost:8000/ 来预览站点 在每次检测到修改重生成站点后，可以让浏览器自动进行重载。先运行 ``python -m pip install livereload`` 安装，再运行下面的这条命令就可以实现： 浏览生成的文件 当准备好发布站点时，可以使用在 ``pelican-quickstart`` 过程中选择的方法进行上传。下面的例子使用rsync在ssh上完成这一工作： ``pelican`` 命令是生成站点的标准方法，但同时也有自动化工具可以用来简化生成与发布流程。在 ``pelican-quickstart`` 的过程中，其中一个问题就是是否要自动站点生成与发布。若您选择了 "yes"，在项目的根目录中会生成``tasks.py`` and ``Makefile`` 。这些文件中预填充了一些从 ``pelican-quickstart`` 过程中收集的信息，您应该从这个生成好的文件出发来进一步根据实际需要修改。另外，如果您认为这些自动化脚本文件没什么用，完全可以将他们删除，这不会对标准命令``pelican`` 产生任何影响。 你也可以让Pelican来监听对源内容文件的修改，而不是在每次修改内容后重新手动执行命令生成站点。在执行 ``pelican`` 命令时，加上 ``-r`` 或者 ``--autoreload`` 选项就可以做到这一点。在非Windows环境下，这个选项还可以和 ``-l`` 或 ``--listen`` 搭配使用，这样就可以在自动重生成站点的基础上，同时提供在 http://localhost:8000 上的访问： 