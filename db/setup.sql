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
