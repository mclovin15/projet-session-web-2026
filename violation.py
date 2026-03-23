# Classe pour représenter une violation et faciliter la manipulation des données
# Projet Session - INF5190 - 2026
# Yoan Desjardins - DESY77040109
from dataclasses import dataclass


@dataclass(slots=True)
class Violation:
    id_poursuite: int
    business_id: int
    date_violation: str
    descr: str
    adresse: str
    date_jugement: str
    etablissement: str
    montant: float
    proprietaire: str
    ville: str
    statut: str
    date_statut: str
    categorie: str

    @classmethod
    def from_csv_row(cls, row):
        """Crée une instance de Violation à partir d'une ligne de CSV."""
        return cls(
            id_poursuite=int(row["id_poursuite"]),
            business_id=int(row["business_id"]),
            date_violation=row["date"],
            descr=row["description"],
            adresse=row["adresse"],
            date_jugement=row["date_jugement"],
            etablissement=row["etablissement"],
            montant=float(row["montant"]),
            proprietaire=row["proprietaire"],
            ville=row["ville"],
            statut=row["statut"],
            date_statut=row["date_statut"],
            categorie=row["categorie"],
        )

    def to_db_tuple(self):
        """Convertit l'instance de Violation en un tuple pour insertion dans la base de données."""
        return (
            self.id_poursuite,
            self.business_id,
            self.date_violation,
            self.descr,
            self.adresse,
            self.date_jugement,
            self.etablissement,
            self.montant,
            self.proprietaire,
            self.ville,
            self.statut,
            self.date_statut,
            self.categorie,
        )
