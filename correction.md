# Fonctionnalités complétées

### Yoan Desjardins (DESY77040109)

#### Doc des services [API](http://127.0.0.1:5000/doc)

---

- **A1** : On peut tester cette fonctionnalité en exécutant la commande :  ```python3 import_data.py```.
- **A2** : On peut tester cette fonctionnalité en utilisant la barre de recherche à la page d'accueil à cette [URL](http://127.0.0.1:5000/?mode=1).
- **A3** : On peut tester la fonctionnalité de synchronisation avec le script suivant en exécutant cette commande :  ```python3 update_violations.py```.
- **A4** :  On peut tester cette fonctionnalité en utilisant cette [URL](http://127.0.0.1:5000/contrevenants?du=2025-04-15&au=2026-03-30).
- **A5** : On peut tester cette fonctionnalité en utilisant la barre de recherche à la page d'accueil à cette [URL](http://127.0.0.1:5000/?mode=2).
- **A6** : On peut tester cette fonctionnalité en utilisant la barre de recherche à la page d'accueil à cette [URL](http://127.0.0.1:5000/?mode=3).
- **C1** : On peut tester cette fonctionnalité en utilisant cette [URL](http://127.0.0.1:5000/violations_par_etablissement).
- **C2** : On peut tester cette fonctionnalité en utilisant cette [URL](http://127.0.0.1:5000/violations_par_etablissement.xml).
- **C3** : On peut tester cette fonctionnalité en utilisant cette [URL](http://127.0.0.1:5000/violations_par_etablissement.csv).
- **D1** : On peut tester cette fonctionnalité en utilisant la page des plaintes et en cliquant le bouton "Nouvelle Plainte" ou avec cette [URL]([http://127.0.0.1:5000/?mode=2](http://127.0.0.1:5000/demande-inspection)). Il faut ensuite remplir le formulaire.
- **D2** : Il faut tout d'abord avoir des plaintes existantes et on peut supprimer une plainte en cliquant sur le bouton supprimer à cette [URL](http://127.0.0.1:5000/inspections).
- **E1** : On peut tester ce service API avec cette [URL](http://127.0.0.1:5000/user)  (POST) avec Postman ou autres. Pour connaître la requête attendu consulter la [doc](http://127.0.0.1:5000/doc/api.html#user_post).
