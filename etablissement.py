# Classe pour représenter un établissement et ses violations
# Projet Session - INF5190 - 2026
# Yoan Desjardins - DESY77040109
from dataclasses import dataclass, field
from typing import Optional

try:
    from .violation import Violation
except ImportError:
    from violation import Violation

@dataclass(slots=True)
class Etablissement:
    nom: str
    business_id: int
    adresse: str
    proprietaire: Optional[str] = None
    ville: Optional[str] = None
    categorie: Optional[str] = None
    montantTotal: float = 0.0
    violations: list[Violation] = field(default_factory=list)
    

    def add_violation(self, violation: Violation) -> None:
        self.violations.append(violation)
        
    def delete_violation(self, id_poursuite: int) -> None:
        self.violations = [v for v in self.violations if v.id_poursuite != id_poursuite]
            
    @property
    def nombre_violations(self) -> int:
        return len(self.violations)
    
    @classmethod
    def from_db_row(cls, row):
        """Construit un etablissement a partir la db."""
        return cls(
            nom=row["etablissement"],
            proprietaire=row["proprietaire"],
            ville=row["ville"],
            categorie=row["categorie"],
            montantTotal=0.0,
            
            business_id=int(row["business_id"]),
            adresse=row["adresse"],
            violations=[],
        )
        
    @classmethod
    def from_distinct_select(cls, row):
        """Construit un etablissement a partir d'une selection distincte."""
        return cls(
            nom=row["etablissement"],
            business_id=int(row["business_id"]),
            adresse=row["adresse"],
            ville=row["ville"],
        )

    @classmethod
    def from_violations(cls, violations: list[Violation]):
        """Construit un etablissement a partir d'une liste de violations."""
        if not violations:
            raise ValueError("La liste de violations ne peut pas etre vide.")

        first_violation = violations[0]
        return cls(
            nom=first_violation.etablissement,
            proprietaire=first_violation.proprietaire,
            ville=first_violation.ville,
            categorie=first_violation.categorie,
            montantTotal=sum(v.montant for v in violations),
            business_id=first_violation.business_id,
            adresse=first_violation.adresse,
            violations=violations,
        )
        
    def to_dict(self):
        """Convertit l'etablissement en dict pour JSON."""
        return {
            "nom": self.nom,
            "business_id": self.business_id,
            "adresse": self.adresse,
            "nombre_violations": self.nombre_violations,
            "violations": [v.to_dict() for v in self.violations],
            "proprietaire": self.proprietaire,
            "ville": self.ville,
            "categorie": self.categorie,
            "montantTotal": self.montantTotal,
        }
