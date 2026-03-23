# Encapsule l'acces SQLite pour ..
# Projet Session - INF5190 - 2026
# Yoan Desjardins - DESY77040109
import datetime
import sqlite3
import uuid
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
    
    def violation_exists(self, id_poursuite: int):
        """Verifie si la violation existe deja"""
        connection = self.get_connection()
        cursor = connection.execute(
            "SELECT 1 FROM violations WHERE id_poursuite = ?", (id_poursuite,)
        )
        return cursor.fetchone() is not None
