# Encapsule l'acces SQLite pour ..
# Projet Session - INF5190 - 2026
# Yoan Desjardins - DESY77040109
import datetime
import sqlite3
import uuid

try:
    from .violation import Violation
except ImportError:
    from violation import Violation


class Database:
    """Encapsule l'acces SQLite pour les utilisateurs, sessions et articles."""

    def __init__(self):
        """Initialise l'etat interne de la connexion SQL."""
        self.connection = None

    def get_connection(self):
        """Retourne une connexion SQLite active avec row_factory configuree."""
        if self.connection is None:
            self.connection = sqlite3.connect("db/violations.db")
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def disconnect(self):
        """Ferme la connexion SQL si elle est ouverte."""
        if self.connection is not None:
            self.connection.close()

    def insert_violation(self, violation: Violation):
        """Insere une nouvelle violation"""

        connection = self.get_connection()
        connection.execute(
            """
            INSERT INTO violations (
                id_poursuite, business_id, date_violation, descr, adresse,
                date_jugement, etablissement, montant, proprietaire,
                ville, statut, date_statut, categorie
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            violation.to_db_tuple(),
        )
        connection.commit()
        
    def update_violation(self, violation: Violation):
        """Met à jour une violation existante"""

        connection = self.get_connection()
        connection.execute(
            """
            UPDATE violations SET
                business_id = ?,
                date_violation = ?,
                descr = ?,
                adresse = ?,
                date_jugement = ?,
                etablissement = ?,
                montant = ?,
                proprietaire = ?,
                ville = ?,
                statut = ?,
                date_statut = ?,
                categorie = ?
            WHERE id_poursuite = ?
            """,
            violation.to_update_tuple(),
        )
        connection.commit()
    
    def is_violation_updated(self, id_poursuite: int, csv_row: dict):
        """Verifie si une ligne CSV differe de la ligne en base."""
        connection = self.get_connection()
        cursor = connection.execute(
            "SELECT * FROM violations WHERE id_poursuite = ?", (id_poursuite,)
        )
        db_row = cursor.fetchone()
        if db_row is None:
            return False

        csv_to_db_fields = {
            "business_id": "business_id",
            "date": "date_violation",
            "description": "descr",
            "adresse": "adresse",
            "date_jugement": "date_jugement",
            "etablissement": "etablissement",
            "montant": "montant",
            "proprietaire": "proprietaire",
            "ville": "ville",
            "statut": "statut",
            "date_statut": "date_statut",
            "categorie": "categorie",
        }

        for csv_field, db_field in csv_to_db_fields.items():
            if str(db_row[db_field]) != str(csv_row[csv_field]):
                return True

        return False
    
    def violation_exists(self, id_poursuite: int):
        """Verifie si la violation existe deja"""
        connection = self.get_connection()
        cursor = connection.execute(
            "SELECT 1 FROM violations WHERE id_poursuite = ?", (id_poursuite,)
        )
        return cursor.fetchone() is not None
    
    def search_violations(self, query: str):
        """Recherche des violations par etablissement, proprietaire ou adresse"""
        connection = self.get_connection()
        search_input = f"%{query}%"
        cursor = connection.execute(
            """
            SELECT * FROM violations
            WHERE etablissement LIKE ? OR proprietaire LIKE ? OR adresse LIKE ?
            """,
            (search_input, search_input, search_input),
        )
        return [Violation.from_db_row(row) for row in cursor.fetchall()]
    
    def return_all_etablissements(self):
        """Retourne tous les établissements"""
        connection = self.get_connection()
        cursor = connection.execute(
            """
            select DISTINCT etablissement,adresse,business_id from violations ORDER by etablissement;
            """
        )
        return cursor.fetchall()
    
    def search_violations_by_date_range(self, from_date, to_date):
        """Recherche des violations avec un range donnée"""
        connection = self.get_connection()
        cursor = connection.execute(
            """
            SELECT * FROM violations
            WHERE date_violation BETWEEN ? AND ?
            """,
            (from_date, to_date),
        )
        return [Violation.from_db_row(row) for row in cursor.fetchall()]
