.. _theming-pelican:

Cette page est une traduction de la documentation originale, en anglais et
disponible `ici <../themes.html>`_.

Comment créer des thèmes pour Pelican
#####################################

Pelican utlise le très bon moteur de template `jinja2 <http://jinja.pocoo.org>`_
pour produire de l'HTML. La syntaxe de jinja2 est vraiment très simple. Si vous
voulez créer votre propre thème, soyez libre de prendre inspiration sur le theme
"simple" qui est disponible `ici
<https://github.com/ametaireau/pelican/tree/master/pelican/themes/simple/templates>`_

Structure
=========

Pour réaliser votre propre thème vous devez respecter la structure suivante ::

    ├── static
    │   ├── css
    │   └── images
    └── templates
        ├── archives.html    // pour afficher les archives
        ├── article.html     // généré pour chaque article
        ├── categories.html  // doit lister toutes les catégories
        ├── category.html    // généré pour chaque catégorie
        ├── index.html       // la page d'index, affiche tous les articles
        ├── page.html        // généré pour chaque page
        ├── tag.html         // généré pour chaque tag
        └── tags.html        // doit lister tous les tags. Peut être un nuage de tag.


* `static` contient tout le contenu statique. Il sera copié dans le dossier
  `theme/static`. J'ai mis un dossier css et un image, mais ce sont juste des
  exemples. Mettez ce dont vous avez besoin ici.

* `templates` contient tous les templates qui vont être utiliser pour générer les
  pages. J'ai juste mis les templates obligatoires ici, vous pouvez définir les
  vôtres si cela vous aide à vous organiser pendant que vous réaliser le thème.
  Vous pouvez par exemple utiliser les directives {% include %} et {% extends %}
  de jinja2.
 
Templates et variables
======================

Cela utilise une syntaxe simple, que vous pouvez insérer dans vos pages HTML.
Ce document décrit les templates qui doivent exister dans un thème, et quelles
variables seront passées à chaque template, au moment de le générer.

Tous les templates recevront les variables définies dans votre fichier de
configuration, si elles sont en capitales. Vous pouvez y accéder directement.

Variables communes
------------------

Toutes ces variables seront passées à chaque template.

=============   ===================================================
Variable        Description
=============   ===================================================
articles        C'est la liste des articles, ordonnée décroissante
                par date. Tous les éléments de la liste sont des
                objets `Article`, vous pouvez donc accéder à leurs
                propriétés (exemple : title, summary, author, etc).
dates           La même liste d'articles, ordonnée croissante par
                date.
tags            Un dictionnaire contenant tous les tags (clés), et
                la liste des articles correspondants à chacun
                d'entre eux (valeur).
categories      Un dictionnaire contenant toutes les catégories
                (clés), et la liste des articles correspondants à
                chacune d'entre elles (valeur).
pages           La liste des pages.
=============   ===================================================

index.html
----------

La page d'accueil de votre blog, sera générée dans output/index.html.

Si la pagination est activée, les pages suivantes seront à l'adresse
output/index`n`.html.

===================     ===================================================
Variable                Description
===================     ===================================================
articles_paginator      Un objet paginator de la liste d'articles.
articles_page           La page actuelle d'articles.
dates_paginator         Un objet paginator de la liste d'articles, ordonné
                        par date croissante.
dates_pages             La page actuelle d'articles, ordonnée par date
                        croissante.
page_name               'index'.
===================     ===================================================

category.html
-------------

Ce template sera généré pour chaque catégorie existante, et se retrouvera
finalement à output/category/`nom de la catégorie`.html.

Si la pagination est activée, les pages suivantes seront disponibles à
l'adresse output/category/`nom de la catégorie``n`.html.

===================     ===================================================
Variable                Description
===================     ===================================================
category                La catégorie qui est en train d'être générée.
articles                Les articles dans cette catégorie.
dates                   Les articles dans cette catégorie, ordonnés par
                        date croissante.
articles_paginator      Un objet paginator de la liste d'articles.
articles_page           La page actuelle d'articles.
dates_paginator         Un objet paginator de la liste d'articles, ordonné
                        par date croissante.
dates_pages             La page actuelle d'articles, ordonnée par date
                        croissante.
page_name               'category/`nom de la catégorie`'.
===================     ===================================================

article.html
-------------

Ce template sera généré pour chaque article. Les fichiers .html seront
disponibles à output/`nom de l'article`.html.

=============   ===================================================
Variable        Description
=============   ===================================================
article         L'objet article à afficher.
category        Le nom de la catégorie de l'article actuel.
=============   ===================================================

page.html
---------

Pour chaque page ce template sera généré à l'adresse
output/`nom de la page`.html

=============   ===================================================
Variable        Description
=============   ===================================================
page            L'objet page à afficher. Vous pouvez accéder à son
                titre (title), slug, et son contenu (content).
=============   ===================================================

tag.html
--------

Ce template sera généré pour chaque tag. Cela créera des fichiers .html à
l'adresse output/tag/`nom du tag`.html.

Si la pagination est activée, les pages suivantes seront disponibles à
l'adresse output/tag/`nom du tag``n`.html

===================     ===================================================
Variable                Description
===================     ===================================================
tag                     Nom du tag à afficher.
articles                Une liste des articles contenant ce tag.
dates                   Une liste des articles contenant ce tag, ordonnée
                        par date croissante.
articles_paginator      Un objet paginator de la liste d'articles.
articles_page           La page actuelle d'articles.
dates_paginator         Un objet paginator de la liste d'articles, ordonné
                        par date croissante.
dates_pages             La page actuelle d'articles, ordonnée par date
                        croissante.
page_name               'tag/`nom du tag`'.
===================     ===================================================
