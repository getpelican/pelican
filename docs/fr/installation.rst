Installation et mise à jour de Pelican
######################################

Installation
============

Il y a deux façons d’installer Pelican sur son système. La première est via l’utilitaire
pip, l’autre façon est de télécharger Pelican via Github. Ici nous allons voir les deux
façons de procéder.

Via pip
-------

Pour installer Pelican via pip, vous aurez besoin du paquet python-pip. puis installez Pelican ::

	# apt-get install python-pip
	# pip install pelican


Via Github
----------

Pour installer Pelican en reprenant le code via Github, nous aurons besoin du paquet 
git-core pour récupérez les sources de Pelican. Puis nous procédons à l’installation ::

	# apt-get install git-core
	$ git clone https://github.com/ametaireau/pelican.git
	$ cd pelican
	# python setup.py install

Mises à jour
============

Via pip
-------

Rien de bien compliqué pour mettre à jour via pip ::

	$ cd votreRepertoireSource
	$ pip install --upgrade pelican


Via Github
----------

C'est un peu plus long avec Github par contre ::

	$ cd votreRepertoireSource
	$ git pull origin master
	$ cd pelican
	# python setup.py install

Vous aurez un message d’erreur si le module setuptools de python n’est pas installé. 
La manipulation est la suivante ::

	# apt-get install python-setuptools

Alors, quelle méthode choisir ?
===============================

Vous avez le choix entre deux méthodes, mais aussi entre deux concepts. La méthode 
de Github est la version de développement, où les modifications arrivent assez
fréquemment sans être testées à fond. La version de pip est une version arrêtée avec un
numéro de version dans laquelle vous aurez moins de bug. N’oubliez cependant pas
que le projet est très jeune et manque donc de maturité. Si vous aimez avoir les toutes
dernières versions utilisez Github, sinon penchez vous sur pip.

