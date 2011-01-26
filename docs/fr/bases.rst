Les bases de Pelican
####################

Créer son premier article
=========================

Pour créer notre premier article, nous allons éditer un fichier, par exemple premier_article.rst ::

	Premier article pour Pelican
	############################
	:author: Guillaume
	:date: 2011-01-08 10:20
	:category: GNU-Linux
	:tags: tutoriel, git
	Ceci est un tutoriel pour configurer git.
	Bla, bla, bla ....

Maintenant que ce fichier est créé, on va lancer la création du blog ::

	pelican .

Vous aller obtenir une sortie comme celle ci — $PATH représente le dossier où vous
avez créé votre article ::

	[ok] writing $PATH/output/feeds/all.atom.xml
	[ok] writing $PATH/output/feeds/GNU/Linux.atom.xml
	[ok] writing $PATH/output/feeds/all-en.atom.xml
	[ok] writing $PATH/output/premier-article-pour-pelican.html
	[ok] writing $PATH/output/index.html
	[ok] writing $PATH/output/tags.html
	[ok] writing $PATH/output/categories.html
	[ok] writing $PATH/output/archives.html
	[ok] writing $PATH/output/tag/tutoriel.html
	[ok] writing $PATH/output/tag/git.html
	[ok] writing $PATH/output/category/GNU-Linux.html


Première analyse
================

Nous allons décortiquer un peu tout ça ensemble.

* Un dossier output/ a été créé pour y mettre le fichiers xml et html du blog.
* Dans le dossier feeds/, nous retrouvons les différents flux de syndication.
* Le fichier de l’article et la page principale du blog a été généré.
* Le répertoire tag/ propose une page par tag.
* La page correspondant à la catégorie est générée dans le répertoire category/

Si vous ouvrez le fichier index.html — ou un autre — avec votre navigateur, vous
remarquerez que :

* Le thème utilisé par défaut est notmyidea
* Le nom du blog est A Pelican Blog.
  
Bien évidemment, il y a des paramètres de base que l’on peut modifier pour mettre
un peu tout ça à sa sauce. C’est ce que nous allons voir au travers du fichier de configuration.


