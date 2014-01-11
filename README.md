YATOT
*****

Description
===========

Installation
============

Avant de commencer l'installation, il faut disposer des programmes suivants :

  * python 2.7
  * networkx 1.8
  * sqlite 3

1. Récuperer les données
------------------------

Pour commencer, rendez-vous à l'url suivante :
  http://www2.lirmm.fr/~lafourcade/JDM-LEXICALNET-FR/LAST_OUTPUT_NOHTML.txt

L'url s'y trouvant est la dernière version de JeuxDeMots.
Sauvegardez la dans le repertoire data.

YATOT fonctionnant avec de l'UTF-8, il nous faut convertir le .txt :
  $ iconv -f ISO-8859-15 -t UTF-8 data/<fichier-txt> --output data/<fichier-txt>

2. Créer la base de données
---------------------------

Il faut maintenant créer la base de données avec SQLite3 :
  $ sqlite3 -init data/createDB.sql data/<bdd.sqlite3>

3. Remplir la base de données
-----------------------------

Chargons les données dans la BDD :
  $ src/sqliteImporter/sqliteImporter.py data/<fichier-txt> data/<bdd.sqlite3>
Tapez ensuite :
  .exit
pour quiter SQLite.

Le chargement prend un certain temps, et des erreurs peuvent apparaitre.
Celles-ci devraient être corrigées sous peu.

4. Lancer YATOT
---------------

Tout devrait être correctement chargé maintenant.
Pour vérifier :
  $ src/yatot/ data/<bdd.sqlite3>

Documentation
=============

Une documentation, en cours de redaction est disponible :
  doc/TALN.pdf

Organisation
============

./
+--data/		données
+--doc/			documentation
|  +--img/		images & figures
|  +--raw/		version brute des images & figures
|  +--tex/		tex
+--src/			source
   +--sqliteImporter/	importeur txt -> sqlite
   +--yatot/		jeu yatot

Auteurs & contacts
==================

Kevin Cousot	<kevin.cousot @ gmail.com>
Rider Carrion	<rider.carrion @ gmail.com>
