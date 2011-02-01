Les paramètres des articles dans Pelican
########################################

Les catégories
==============

Nous avons vu que pour affecter un article à une catégorie, nous avions le paramètre *:category:*.
Il y a cependant plus simple, affecter un répertoire à une catégorie. 
  
Dans le répertoire ou vous avez vos articles, créez le repertoire **GNU-Linux** et déplacez y le fichier
**premier_article.rst**. Bien évidemment nous ne verront pas la différence, car jusqu'ici *GNU-Linux*
est notre catégorie par défaut.
  
Nous allons faire un autre exemple d'article avec la catégorie Pelican. Créez le répertoire **Pelican**
et collez cette exemple d'article ::

	Préparation de la documentation
	###############################

	:date: 2011-01-27 15:28
	:tags: documentation
	
	Il y a quand même pas mal de boulot pour faire une documentation !

Et lancez la compilation du blog. Vous voyez que la catégorie est affectée automatiquement. 

Les tags
========

Pour les tags, il n'y a rien de compliqué. il suffit de mettre le(s) tags séparés si besoin d'une virgule. ::

	Préparation de la documentation
	###############################

	:date: 2011-01-27 15:28
	:tags: documentation, pelican

Par contre, par soucis de clarté au niveau des url je vous conseille de mettre les expression de plusieurs 
mots séparées par des tirets ::

	:tags: mise-a-jour

et non ::

	:tags: mise a jour


Les auteurs
===========

Par défaut, vous pouvez indiqué votre nom en tant qu'auteur dans le fichier de configuration.
S'il y a plusieurs auteurs pour le site, vous pouvez le définir manuellement dans
l'article avec la méta-donnée ::

	:author: Guillaume

La date
=======

La date se met au format anglophone : **YYYY-MM-DD hh:mm** ::

	:date: 2011-01-31 14:12


Les traductions
===============

Pelican permet de générer un blog multilingue assez facilement. Pour cela nous devons :

* Définir la langue de base du blog ;
* Donner une référence à l'article initial ;
* Définir la langue du fichier traduit et y reporter la référence.

Pour définir la langue de base nous allons modifier le fichier **settings.py** et y rajouter la ligne suivante ::

	DEFAULT_LANG = "fr"

Puis ajouter la référence dans notre article d'origine qui deviendra ::

	Préparation de la documentation
        ###############################

        :date: 2011-01-27 15:28
        :tags: documentation
	:slug: preparation-de-la-documentation

        Il y a quand même pas mal de boulot pour faire une documentation !

Nous n'avons plus qu'à créer l'article en anglais ::

	Start of documentation
	######################

	:slug: preparation-de-la-documention
	:lang: en

	There are still a lot of work to documentation !

**Il est important de comprendre que la valeur de :slug: deviendra votre url. Ne mettez donc pas un diminutif pour 
identifier l'article**

Rien de plus à savoir pour traduire efficacement des articles.	


Maintenant que vous avez toutes les clés en main pour créer un article, nous allons passer à la personnalisation 
du fichier de configuration.
