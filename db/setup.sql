CREATE TABLE violations (
    id_poursuite INTEGER PRIMARY KEY,
    business_id INTEGER NOT NULL,
    date_violation DATE NOT NULL, /*date*/
    descr TEXT NOT NULL, /*description*/
    adresse TEXT NOT NULL,
    date_jugement DATE NOT NULL,
    etablissement TEXT NOT NULL,
    montant DECIMAL(10,2) NOT NULL,
    proprietaire TEXT NOT NULL,
    ville TEXT NOT NULL,
    statut TEXT NOT NULL,
    date_statut DATE NOT NULL,
    categorie TEXT NOT NULL
);

CREATE TABLE inspections (
    id_inspection INTEGER PRIMARY KEY,
    business_id INTEGER NOT NULL,
    adresse TEXT NOT NULL,
    etablissement TEXT NOT NULL,
    ville TEXT NOT NULL,
    date_visite DATE NOT NULL,
    nom_complet_client TEXT NOT NULL,
    description_prob TEXT NOT NULL
);

create table users (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   nom TEXT,
   prenom TEXT,
   email TEXT UNIQUE NOT NULL,
   avatar TEXT,
   createdDate DATETIME DEFAULT CURRENT_TIMESTAMP, 
   liste_etablissements_surveiller TEXT NOT NULL,
   salt TEXT,
   hash TEXT,
   status BOOLEAN NOT NULL DEFAULT TRUE
);

create table sessions (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   id_session TEXT,
   email TEXT
);
