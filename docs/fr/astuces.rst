Trucs et astuces pour Pelican
#############################

Personnaliser l'url d'un article pour Pelican
=============================================

Par défaut, quand vous créez un article ayant pour titre *Mon article pour Pelican*,
l'url par défaut devient *mon-article-pour-pelican.html*. Cependant, il est possible 
de modifier cela en utilisant la technique utilisée pour les traductions d'article,
c'est à dire le paramètre *:slug:* ::

	Mon article pour Pelican
	########################

	:date: 2011-01-31 11:05
	:slug: super-article-pour-pelican

	bla, bla, bla …

En prenant cet exemple ci dessus, votre url deviendra *super-article-pour-pelican.html*
