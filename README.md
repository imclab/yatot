# YATOT

## Description

YATOT est une expérimentation sur le réseau lexico-sémantique JeuxDeMots.

Il s'agit de faire deviner un mot au programme.

## Installation

Avant de commencer l'installation, il faut disposer des programmes suivants :
* python 2.7
* networkx 1.8
* sqlite 3

### Récuperer les données

Pour commencer, rendez-vous [ici](http://www2.lirmm.fr/~lafourcade/JDM-LEXICALNET-FR/LAST_OUTPUT_NOHTML.txt).

L'url s'y trouvant est la dernière version de JeuxDeMots.

Sauvegardez la dans le répertoire data.

YATOT fonctionnant avec de l'UTF-8, il nous faut convertir le .txt :

`$ iconv -f ISO-8859-15 -t UTF-8 data/<fichier-txt> --output data/<fichier-txt>`

### Créer la base de données

Il faut maintenant créer la base de données avec SQLite3 :

`$ sqlite3 -init data/createDB.sql data/<bdd.sqlite3>`

Tapez ensuite :

`.exit`

pour quiter SQLite.

### Remplir la base de données

Chargons les données dans la BDD :

`$ src/sqliteImporter/sqliteImporter.py data/<fichier-txt> data/<bdd.sqlite3>`

Le chargement prend un certain temps, et des erreurs peuvent apparaître.

Celles-ci devraient être corrigées sous peu.

### Lancer YATOT

Tout devrait être correctement chargé maintenant.
Pour vérifier :

`$ src/yatot/ data/<bdd.sqlite3>`

## Documentation

Une documentation, en cours de rédaction est disponible : doc/TALN.pdf

## Auteurs & contacts

* Kevin Cousot
* Rider Carrion
