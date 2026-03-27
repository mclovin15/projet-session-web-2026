# Checklist des exigences - Projet INF5190

## Exigences generales

- [ ] Accumuler au minimum 100 XP si travail individuel
- [ ] Respecter les dependances entre fonctionnalites
- [ ] Realiser chaque fonctionnalite choisie au complet

## Contraintes techniques

- [ ] Utiliser Python 3
- [ ] Utiliser Flask 3
- [ ] Utiliser SQLite 3
- [ ] Respecter les exigences de qualite du logiciel
- [ ] Avoir un code conforme a `pycodestyle` sans erreur ni avertissement

## Base de donnees

- [x] Modeliser soi-meme la base de donnees
- [x] Creer un dossier `db/`
- [x] Fournir un script SQL de creation nomme `db/db.sql`
- [x] Fournir une base de donnees deja creee mais vide pour les tests

## Fonctionnalites

### A1 - Importation CSV vers SQLite - 10 XP

- [x] Telecharger la liste des contraventions en format CSV par requete HTTP
- [x] Stocker le contenu du CSV dans une base de donnees SQLite
- [x] Faire un script Python qui telecharge et insere les donnees
- [x] Ne pas creer la base de donnees dans le script
- [x] Ne pas vider la base de donnees dans le script
- [x] Assumer que la base existe deja lors de l'execution du script
- [x] Fournir le script SQL de creation de la base
- [x] Fournir une base de donnees deja creee mais vide

### A2 - Application Flask et recherche - 10 XP

- [x] Construire une application Flask pour acceder aux donnees
- [x] Ajouter une page d'accueil avec un outil de recherche
- [x] Permettre la recherche par nom d'etablissement
- [x] Permettre la recherche par proprietaire
- [x] Permettre la recherche par rue
- [x] Afficher les resultats sur une nouvelle page
- [x] Afficher toutes les donnees disponibles pour chaque contravention
- [x] Permettre qu'un restaurant apparaisse plusieurs fois s'il a plusieurs sanctions

### A3 - Synchronisation quotidienne - 10 XP

- [x] Mettre en place un `BackgroundScheduler` dans l'application Flask
- [x] Extraire les donnees de la ville de Montreal chaque jour a minuit
- [x] Mettre a jour les donnees de la base de donnees
- [x] Synchroniser quotidiennement les donnees locales avec celles de la ville

### A4 - Service REST par plage de dates - 10 XP

- [x] Offrir un service REST pour obtenir les contraventions entre deux dates
- [x] Recevoir les dates via parametres
- [ ] Utiliser le format ISO 8601 pour les dates --> revoir ceci vérif pas complète
- [x] Retourner les donnees en format JSON
- [x] Implementer la route du type `GET /contrevenants?du=YYYY-MM-DD&au=YYYY-MM-DD`
- [x] Rendre disponible une route `/doc`
- [x] Afficher sur `/doc` la representation HTML de la documentation RAML

### A5 - Recherche Ajax par dates - 10 XP

- [x] Ajouter un formulaire de recherche rapide sur la page d'accueil
- [x] Permettre la saisie de deux dates
- [x] Envoyer une requete Ajax vers la route de A4
- [x] Afficher les resultats dans un tableau apres la reponse Ajax
- [x] Afficher une colonne avec le nom de l'etablissement
- [x] Afficher une colonne avec le nombre de contraventions durant la periode

### A6 - Recherche Ajax par restaurant - 10 XP

- [ ] Ajouter un mode de recherche par nom du restaurant dans l'application de A5
- [x] Predeterminer la liste de tous les contrevenants dans une liste deroulante
- [x] Permettre a l'utilisateur de choisir un restaurant dans la liste
- [x] Envoyer une requete Ajax vers un service REST dedie
- [x] Afficher les differentes infractions du restaurant apres la reponse Ajax

### B1 - Detection des nouvelles contraventions par courriel - 5 XP

- [ ] Detecter les nouvelles contraventions depuis la derniere importation
- [ ] Dresser une liste sans doublon des nouvelles contraventions
- [ ] Envoyer automatiquement cette liste par courriel
- [ ] Stocker l'adresse du destinataire dans un fichier YAML

### B2 - Publication Twitter - 10 XP

- [ ] Publier automatiquement les noms d'etablissements des nouvelles contraventions sur un compte Twitter

### C1 - Service REST etablissements et nombre d'infractions - 10 XP

- [x] Offrir un service REST listant les etablissements ayant commis une ou plusieurs infractions
- [x] Indiquer pour chaque etablissement le nombre d'infractions connues
- [x] Trier la liste en ordre decroissant du nombre d'infractions
- [x] Documenter le service avec RAML
- [x] Rendre la documentation disponible sur `/doc`

### C2 - Meme service en XML - 5 XP

- [x] Offrir exactement les memes donnees que C1 en format XML
- [x] Utiliser l'encodage UTF-8
- [x] Documenter le service avec RAML
- [x] Rendre la documentation disponible sur `/doc`

### C3 - Meme service en CSV - 5 XP

- [x] Offrir exactement les memes donnees que C1 en format CSV
- [x] Utiliser l'encodage UTF-8
- [x] Documenter le service avec RAML
- [x] Rendre la documentation disponible sur `/doc`

### D1 - Demande d'inspection et page de plainte - 15 XP

- [x] Offrir un service REST permettant de faire une demande d'inspection a la ville
- [x] Valider le document JSON avec `json-schema`
- [x] Recevoir le nom de l'etablissement
- [x] Recevoir l'adresse
- [x] Recevoir la ville
- [x] Recevoir la date de la visite du client
- [x] Recevoir le nom et prenom du client faisant la plainte
- [x] Recevoir une description du probleme observe
- [x] Documenter le service avec RAML
- [x] Rendre la documentation disponible sur `/doc`
- [x] Creer une page HTML de plainte avec formulaire
- [x] Faire invoquer le service REST par Javascript

### D2 - Suppression d'une demande d'inspection - 5 XP

- [x] Offrir un service REST permettant de supprimer une demande d'inspection
- [x] Documenter le service avec RAML
- [x] Rendre la documentation disponible sur `/doc`

### D3 - Modification et suppression de contrevenants - 15 XP

- [ ] Modifier l'application de A5 pour permettre la suppression des contrevenants retournes
- [ ] Modifier l'application de A5 pour permettre la modification des contrevenants retournes
- [ ] Invoquer des services via appels Ajax
- [ ] Afficher une confirmation en cas de succes
- [ ] Afficher un message d'erreur en cas d'erreur
- [ ] Preserver les changements en tout temps
- [ ] Preserver les changements meme lors d'une synchronisation quotidienne
- [ ] Documenter les services avec RAML
- [ ] Rendre la documentation disponible sur `/doc`
- [ ] Lorsqu'un contrevenant est modifie, modifier toutes ses contraventions en meme temps
- [ ] Lorsqu'un contrevenant est supprime, supprimer toutes ses contraventions

### D4 - Basic Auth pour proteger D3 - 15 XP

- [ ] Offrir une procedure d'authentification de type Basic Auth
- [ ] Restreindre les fonctionnalites de modification et suppression de D3 a un utilisateur predefini
- [ ] Specifier clairement les donnees d'authentification pour la correction

### E1 - Creation de profil utilisateur - 15 XP

- [x] Offrir un service REST pour creer un profil utilisateur
- [x] Valider le document JSON avec `json-schema`
- [x] Recevoir le nom complet de l'utilisateur
- [x] Recevoir l'adresse courriel de l'utilisateur
- [x] Recevoir une liste de noms d'etablissements a surveiller
- [x] Recevoir le mot de passe
- [x] Documenter le service avec RAML
- [x] Rendre la documentation disponible sur `/doc`

### E2 - Interface profil, auth et photo - 15 XP

- [ ] Offrir une page web pour invoquer le service de E1
- [ ] Offrir une option d'authentification
- [ ] Apres authentification, offrir une page pour modifier la liste des etablissements a surveiller
- [ ] Permettre le televersement d'une photo de profil
- [ ] Sauvegarder la photo dans la base de donnees
- [ ] Accepter uniquement les formats `jpg` et `png`

### E3 - Courriel automatique aux utilisateurs interesses - 5 XP

- [ ] Envoyer automatiquement un courriel a tous les utilisateurs qui surveillent un etablissement lorsqu'un nouveau contrevenant est detecte

### E4 - Desabonnement via lien dans le courriel - 10 XP

- [ ] Inclure dans le courriel de E3 un lien pour se desabonner du restaurant
- [ ] Rediriger ce lien vers une page HTML de confirmation
- [ ] Si l'utilisateur confirme, envoyer une requete Ajax
- [ ] Invoquer un service REST pour supprimer le restaurant du profil utilisateur

### F1 - Deploiement infonuagique - 15 XP

- [ ] Deployer completement le systeme sur une plateforme infonuagique
- [ ] Fournir l'URL de l'application pour la correction

## Remise et correction

- [ ] Archiver le repertoire de travail dans un fichier zip
- [ ] Nommer l'archive selon les codes permanents des auteurs
- [ ] Remettre l'archive sur Moodle
- [ ] Si travail en equipe, utiliser un depot git prive
- [ ] Donner un acces en lecture a l'enseignant si travail en equipe
- [ ] S'assurer que chaque membre contribue a au moins 100 XP si travail en equipe
- [ ] Ajouter un fichier `correction.md` a la racine du projet
- [ ] Indiquer dans `correction.md` tous les points developpes
- [ ] Expliquer dans `correction.md` comment tester chaque point
- [ ] Fournir l'URL de l'application dans `correction.md` pour F1 si applicable
