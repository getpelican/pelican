pelican-themes
##############



Description
===========

``pelican-themes`` est un outil en lignes de commandes pour gérer les thèmes de Pelican.


Utilisation:
""""""""""""

| pelican-themes [-h] [-l] [-i *chemin d'un thème* [*chemin d'un thème* ...]]
|                      [-r *nom d'un thème* [*nom d'un thème* ...]]
|                      [-s *chemin d'un thème* [*chemin d'un thème* ...]] [-v] [--version]

Arguments:
""""""""""


-h, --help                      Afficher l'aide et quitter 

-l, --list                      Montrer les thèmes installés

-i chemin, --install chemin     Chemin(s) d'accès d'un ou plusieurs thème à installer

-r nom, --remove nom            Noms d'un ou plusieurs thèmes à installer

-s chemin, --symlink chemin     Fonctionne de la même façon que l'option ``--install``, mais crée un lien symbolique au lieu d'effectuer une copie du thème vers le répertoire des thèmes.
                                Utile pour le développement de thèmes.

-v, --verbose                   Sortie détaillée 

--version                       Affiche la version du script et quitte



Exemples
========


Lister les thèmes installés
"""""""""""""""""""""""""""

``pelican-themes`` peut afficher les thèmes disponibles.

Pour cela, vous pouvez utiliser l'option ``-l`` ou ``--list``, comme ceci:

.. code-block:: console

    $ pelican-themes -l
    notmyidea
    two-column@
    simple
    $ pelican-themes --list
    notmyidea
    two-column@
    simple

Dans cet exemple, nous voyons qu'il y a trois thèmes d'installés: ``notmyidea``, ``simple`` and ``two-column``.

``two-column`` est suivi d'un ``@`` par ce que c'est un lien symbolique (voir `Créer des liens symboliques`_).

Notez que vous pouvez combiner l'option ``--list`` avec l'option ``--verbose``, pour afficher plus de détails:

.. code-block:: console
    
    $ pelican-themes -v -l
    /usr/local/lib/python2.6/dist-packages/pelican-2.6.0-py2.6.egg/pelican/themes/notmyidea
    /usr/local/lib/python2.6/dist-packages/pelican-2.6.0-py2.6.egg/pelican/themes/two-column (symbolic link to `/home/skami/Dev/Python/pelican-themes/two-column')
    /usr/local/lib/python2.6/dist-packages/pelican-2.6.0-py2.6.egg/pelican/themes/simple


Installer des thèmes
""""""""""""""""""""

Vous pouvez installer un ou plusieurs thèmes en utilisant l'option ``-i`` ou ``--install``.

Cette option prends en argument le(s) chemin(s) d'accès du ou des thème(s) que vous voulez installer, et peut se combiner avec l'option ``--verbose``:

.. code-block:: console

    # pelican-themes --install ~/Dev/Python/pelican-themes/notmyidea-cms --verbose

.. code-block:: console

    # pelican-themes --install ~/Dev/Python/pelican-themes/notmyidea-cms\
                               ~/Dev/Python/pelican-themes/martyalchin \
                               --verbose

.. code-block:: console

    # pelican-themes -vi ~/Dev/Python/pelican-themes/two-column


Supprimer des thèmes
""""""""""""""""""""

``pelican-themes`` peut aussi supprimer des thèmes précédemment installés grâce à l'option ``-r`` ou ``--remove``.

Cette option prends en argument le ou les nom(s) des thèmes que vous voulez installer, et peux se combiner avec l'option ``--verbose``:

.. code-block:: console

    # pelican-themes --remove two-column

.. code-block:: console

    # pelican-themes -r martyachin notmyidea-cmd -v





Créer des liens symboliques
"""""""""""""""""""""""""""


L'option ``-s`` ou ``--symlink`` de ``pelican-themes`` permet de lier symboliquement un thème.

Cette option s'utilise exactement comme l'option ``--install``:

.. code-block:: console
    
    # pelican-themes --symlink ~/Dev/Python/pelican-themes/two-column

Dans l'exemple ci dessus, un lien symbolique pointant vers le thème ``two-column`` a été installé dans le répertoire des thèmes de Pelican, toute modification sur le thème ``two-column`` prendra donc effet immédiatement.

Cela peut être pratique pour le développement de thèmes

.. code-block:: console

    $ sudo pelican-themes -s ~/Dev/Python/pelican-themes/two-column
    $ pelican ~/Blog/content -o /tmp/out -t two-column
    $ firefox /tmp/out/index.html
    $ vim ~/Dev/Pelican/pelican-themes/two-coumn/static/css/main.css 
    $ pelican ~/Blog/content -o /tmp/out -t two-column
    $ cp /tmp/bg.png ~/Dev/Pelican/pelican-themes/two-coumn/static/img/bg.png
    $ pelican ~/Blog/content -o /tmp/out -t two-column
    $ vim ~/Dev/Pelican/pelican-themes/two-coumn/templates/index.html 
    $ pelican ~/Blog/content -o /tmp/out -t two-column


Notez que cette fonctionnalité nécessite d'avoir un système d'exploitation et un système de fichiers supportant les liens symboliques, elle n'est donc pas disponible sous Micro$oft®©™ Fenêtre®©™. 

Faire plusieurs choses à la fois
""""""""""""""""""""""""""""""""


Les options ``--install``, ``--remove`` et ``--symlink`` peuvent être employées en même temps, ce qui permets de réaliser plusieurs opérations en même temps:

.. code-block:: console

    # pelican-themes --remove notmyidea-cms two-column \
                     --install ~/Dev/Python/pelican-themes/notmyidea-cms-fr \
                     --symlink ~/Dev/Python/pelican-themes/two-column \
                     --verbose

Dans cette exemple, le thème ``notmyidea-cms`` sera remplacé par le thème ``notmyidea-cms-fr`` et le thème ``two-column`` sera lié symboliquement...



À voir également
================

-   http://docs.notmyidea.org/alexis/pelican/
-   ``/usr/share/doc/pelican/`` si vous avez installé Pelican par le `dépôt APT <http://skami18.github.com/pelican-packages/>`_



