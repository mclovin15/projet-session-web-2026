# Classe pour représenter une violation et faciliter la manipulation des données
# Projet Session - INF5190 - 2026
# Yoan Desjardins - DESY77040109
from dataclasses import dataclass
from datetime import datetime


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

    @staticmethod
    def _format_date(date_value: str) -> str:
        """Convertit une date YYYYMMDD en YYYY-MM-DD pour l'affichage."""
        return datetime.strptime(str(date_value), "%Y%m%d").strftime("%Y-%m-%d")

    @classmethod
    def from_db_row(cls, row):
        """Cree une instance de Violation a partir d'une ligne de la base."""
        return cls(
            id_poursuite=int(row["id_poursuite"]),
            business_id=int(row["business_id"]),
            date_violation=row["date_violation"],
            descr=row["descr"],
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

    @classmethod
    def from_csv_row(cls, row):
        """Cree une instance de Violation a partir d'une ligne de CSV."""
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
        """Convertit l'instance de Violation en tuple pour insertion en base."""
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

    def to_update_tuple(self):
        """Retourne les valeurs dans l'ordre attendu par la requete UPDATE."""
        return (
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
            self.id_poursuite,
        )

    @property
    def formatted_date_violation(self) -> str:
        """Retourne la date de violation au format YYYY-MM-DD."""
        return self._format_date(self.date_violation)

    @property
    def formatted_date_jugement(self) -> str:
        """Retourne la date de jugement au format YYYY-MM-DD."""
        return self._format_date(self.date_jugement)

    @property
    def formatted_date_statut(self) -> str:
        """Retourne la date du statut au format YYYY-MM-DD."""
        return self._format_date(self.date_statut)
