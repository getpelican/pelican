Fichier de configuration
************************

On va créer un fichier de configuration que l’on va appeler **settings.py**. On peut
utiliser Pelican sans faire ce fichier, mais il faudrait à chaque fois passer les paramètres
en ligne de commande. Et comme il va nous servir à faire d’autres choses bien utile,
autant l’appréhender de suite. Cependant, nous n’allons voir que la base pour l’instant.

Paramètres de base
==================

AUTHOR :
	Désigne l’auteur par défaut ;

DEFAULT_CATEGORY :
        La catégorie par défaut des articles. Si ce paramètre n’est
	pas documenté, il prendra la valeur misc — pour miscellaneous (divers en français) ;

SITENAME :
	Le nom de votre site ;

OUTPUT_PATH : 
	Le répertoire de sortie du blog.

Quand je dis qu’on va faire simple, on fait simple !
Passons donc à ce quoi doit ressembler le fichier de configuration ::

	# -*- coding: utf-8 -*-
	AUTHOR = "Guillaume"
	DEFAULT_CATEGORY = "GNU-Linux"
	SITENAME = "Free Culture"


Si vous avez un serveur comme Apache de configuré pour votre machine, vous
pouvez paramétrer le répertoire de sortie vers **/var/www/blog** par exemple ::

	OUTPUT_PATH = "/var/www/blog"

Une remarque importante. Si vous avez besoin de passer un caractère accentué, il
faut le préciser que la chaine est en unicode en faisant par exemple
*AUTHOR = u"Guillaume LAMÉ"*

Pour bien vérifier que les paramètres sont bien pris en compte, nous allons enlever les lignes *:author: Guillaume* et *:category: GNU-Linux* de notre fichier
**premier_article.rst** et regénérer le blog.

Rafraichissez votre page, ce devrait être bon.

Nous allons maintenant passer en revue les différents paramètres de Pelican. Je les
ai regroupé par thème. Cependant, c’est surtout un listing avant de rentrer dans les
détails au prochain chapitre.

Flux de syndication
===================

CATEGORY_FEED_ATOM :
	Chemin d’écriture des flux Atom liés aux catégories ;

CATEGORY_FEED_RSS : 
	Idem pour les flux rss (Optionnel);

FEED_ATOM :
	Chemin du flux Atom global;

FEED_RSS :
	Chemin du flux Rss global (Optionnel);

FEED_ALL_ATOM :
	Chemin du flux Atom global qui inclut la totalité des posts, indépendamment de la langue;

FEED_ALL_RSS :
	Chemin du flux Rss global  qui inclut la totalité des posts, indépendamment de la langue (Optionnel);

TAG_FEED_ATOM :
	Chemin des flux Atom pour les tags (Optionnel);

TAG_FEED_RSS :
	Chemin des flux Rss pour les tags (Optionnel).


Traductions
===========

DEFAULT_LANG :
	Le langage par défaut à utiliser. «*en*» par défaut ;

TRANSLATION_FEED_ATOM :
	Chemin du flux Atom pour les traductions.

TRANSLATION_FEED_RSS :
	Chemin du flux RSS pour les traductions.


Thèmes
======

CSS_FILE :
	Fichier css à utiliser si celui-ci est différent du fichier par défaut (*main.css*) ;

DISPLAY_PAGES_ON_MENU :
	Affiche ou non les pages statiques sur le menu du thème ; 

DISQUS_SITENAME :
	Indiquer le nom du site spécifié sur Disqus ;

GITHUB_URL :
	Indiquez votre url Github ;

GOOGLE_ANALYTICS :
	'UA-XXXX-YYYY' pour activer Google analytics ;
	
GOSQUARED_SITENAME :
	'XXX-YYYYYY-X' pour activer GoSquared ;

JINJA_EXTENSIONS :
	Liste d'extension Jinja2 que vous souhaitez utiliser ;

LINKS :
	Une liste de tuples (Titre, url) pour afficher la liste de lien ;

PDF_PROCESSOR :
	Génère ou non les articles et pages au format pdf ;

NEWEST_FIRST_ARCHIVES :
	Met les articles plus récent en tête de l'archive ;

SOCIAL :
	Une liste de tuples (Titre, url) pour afficher la liste de lien dans la section "Social" ;

STATIC_THEME_PATHS :
	Répertoire du thème que vous souhaitez importer dans l'arborescence finale ;
 
THEME :
	Thème à utiliser:

TWITTER_USERNAME :
	Permet d'afficher un bouton permettant le tweet des articles. 

Pelican est fournit avec :doc:`pelican-themes`, un script permettant de gérer les thèmes



Paramètres divers
=================

DEFAULT_DATE:
    Date par défaut à utiliser si l'information de date n'est pas spécifiée
    dans les metadonnées de l'article.
    Si 'fs', Pelican se basera sur le *mtime* du fichier.
    Si c'est un tuple, il sera passé au constructeur datetime.datetime pour
    générer l'objet datetime utilisé par défaut.

KEEP_OUTPUT DIRECTORY :
	Ne génère que les fichiers modifiés et n'efface pas le repertoire de sortie ;

MARKUP :
	Langage de balisage à utiliser ;

PATH :
	Répertoire à suivre pour les fichiers inclus ;

SITEURL :
	URL de base de votre site ;

STATIC_PATHS :
	Les chemins statiques que vous voulez avoir accès sur le chemin de sortie "statique" ;
