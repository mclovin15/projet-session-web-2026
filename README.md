# INF5190 - Programmation web avancée : Projet de session (Hiver 2026)

## Description
Le projet consiste à récupérer un ensemble de données provenant de la ville de Montréal et d'offrir des services à partir de ces données. Il s'agit de données ouvertes à propos d'établissements ayant reçu des constats d'infraction lors d'inspections alimentaires. 

## Architecture et Fonctionnalités (Système d'XP)
Ce projet est construit sur un modèle de progression par points d'expérience (XP), où les diverses fonctionnalités offrent un certain nombre de points et ouvrent le chemin vers d'autres fonctionnalités à développer. Le point de départ obligatoire est la fonctionnalité de base permettant d'obtenir la liste des contraventions en format CSV et de la stocker dans une base de données SQLite.

* **Extraction et Stockage :** Téléchargement des données via une requête HTTP et insertion dans la base de données via un script Python.
* **Interface et Recherche :** Application Flask offrant un outil de recherche par nom d'établissement, propriétaire ou rue.
* **Fonctionnalités avancées :** Le projet inclut potentiellement des services REST, des synchronisations quotidiennes de données, des envois de courriels automatiques, ou encore des requêtes Ajax pour la recherche rapide.

*(Note : Consulter le fichier `correction.md` pour la liste exacte des fonctionnalités complétées et les instructions de test de chacune.)*

## Technologies Imposées
* **Python 3** et **Flask 3**.
* **SQLite 3** pour la gestion de la base de données.
* Librairies **Javascript/Python** et templates **HTML/CSS** libres de choix, dans le respect des licences.

## Exigences de Qualité et Déploiement
* **Qualité du code :** L'exécution de `pycodestyle` sur le code source ne doit soulever aucune erreur et aucun avertissement.
* **Structure de la base de données :** Le répertoire de base contient un dossier `/db` incluant le script de création `db.sql` ainsi qu'une base de données vide pour les tests.

## Auteur
* **Yoan Desjardins**
