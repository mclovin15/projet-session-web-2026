# Encapsule l'acces SQLite pour ..
# Projet Session - INF5190 - 2026
# Yoan Desjardins - DESY77040109
import datetime
import sqlite3
import uuid
import json

try:
    from .violation import Violation
    from .etablissement import Etablissement
except ImportError:
    from violation import Violation
    from etablissement import Etablissement


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


    ### VIOLATIONS ###
    
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
                SELECT DISTINCT business_id, etablissement, adresse, ville
                 from violations ORDER by etablissement;
            """
        )
        return [Etablissement.from_distinct_select(row) for row in cursor.fetchall()]
    
    def return_etablissement_details(self, business_id: int):
        """Retourne les details d'un établissement par son business_id"""
        connection = self.get_connection()
        cursor = connection.execute(
            """
            SELECT * FROM violations
            WHERE business_id = ?
            """,
            (business_id,),
        )
        rows = cursor.fetchall()
        if not rows:
            return None

        violations = [Violation.from_db_row(row) for row in rows]
        return Etablissement.from_violations(violations)
    
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

    def return_all_etablissement_with_nb_violations(self):
        """Recherche des violations avec un range donnée"""
        connection = self.get_connection()
        cursor = connection.execute(
        """SELECT
            business_id,
            etablissement,
            adresse,
            COUNT(*) AS nombre_violations
        FROM violations
        GROUP BY business_id, etablissement, adresse
        ORDER BY nombre_violations DESC;
        """)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    # TODO: voir si j'utilise cette meta
    def etablissement_exists_by_id(self, business_id: int):
        """Verifie si un etablissement existe deja par son business_id"""
        connection = self.get_connection()
        cursor = connection.execute(
            "SELECT 1 FROM violations WHERE business_id = ?", (business_id,)
        )
        return cursor.fetchone() is not None
    
    def etablissement_exists_by_infos(self, nom: str,adresse: str, ville: str):
        """Verifie si un etablissement existe deja par son nom, adresse et ville"""
        connection = self.get_connection()
        cursor = connection.execute(
            "SELECT 1 FROM violations WHERE etablissement = ? AND adresse = ? AND ville = ?",
            (nom, adresse, ville)
        )
        return cursor.fetchone() is not None
    
    ### INSPECTION ###

    def insert_inspection(self, inspection: dict):
        """Insere une nouvelle demande d'inspection"""

        connection = self.get_connection()
        connection.execute(
            """
            INSERT INTO inspections (
                adresse, etablissement, ville, date_visite,
                nom_complet_client, description_prob
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                # inspection["business_id"], # TODO: voir si on veut garder business_id dans table inspections
                inspection["adresse"],
                inspection["etablissement"],
                inspection["ville"],
                inspection["date_visite"],
                inspection["nom_complet_client"],
                inspection["description_prob"],
            ),
        )
        connection.commit()

    def get_inspection_by_id(self, id_inspection: int):
        """Retourne une demande d'inspection par son identifiant."""
        connection = self.get_connection()
        cursor = connection.execute(
            "SELECT * FROM inspections WHERE id_inspection = ?",
            (id_inspection,),
        )
        row = cursor.fetchone()
        return dict(row) if row is not None else None

    def delete_inspection(self, id_inspection: int):
        """Supprime une demande d'inspection."""
        connection = self.get_connection()
        connection.execute(
            "DELETE FROM inspections WHERE id_inspection = ?",
            (id_inspection,),
        )
        connection.commit()
        
    def return_all_inspections(self):
        """Retourne toutes les demandes d'inspection ordonnees par date de visite decroissante"""
        connection = self.get_connection()
        cursor = connection.execute(
            """
            SELECT * FROM inspections
            ORDER BY id_inspection ASC
            """
            # TODO: voir si on veut ordonner par date_visite ou id_inspection (qui est auto-increment) 
        )
        return [dict(row) for row in cursor.fetchall()]
    
    ### USER ###

    def insert_user(self, user: dict,salt,hashed_password):
        """Insere un nouveau user"""
        liste_etablissements_json = json.dumps(user["liste_etablissements_surveiller"])

        connection = self.get_connection()
        connection.execute(
            """
            INSERT INTO users (
                nom, prenom, email, hash, salt,
                avatar, liste_etablissements_surveiller
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user["nom"],
                user["prenom"],
                user["email"],
                hashed_password,
                salt,
                user["avatar"],
                liste_etablissements_json,
                
            ),
        )
        connection.commit()
        
        
    def email_already_exist(self, email: str) -> bool:
        """Determine si email deja existant"""
        connection = self.get_connection()
        cursor = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        )
        row = cursor.fetchone()
        return  row is not None
    
    def get_user_id_from_email(self, email):
        """Retourne l'identifiant utilisateur associe a un courriel."""
        cursor = self.get_connection().cursor()
        cursor.execute(("select id from users where email=?"), (email,))
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]

    def get_user_login_info(self, email):
        """Retourne le salt, le hash et l'id pour l'authentification."""
        cursor = self.get_connection().cursor()
        cursor.execute(
            ("select salt, hash,id from users where email=?"),
            (email,),
        )
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user[0], user[1], user[2]

    def get_user_profile_by_id(self, user_id):
        """Recupere les informations de profil d'un utilisateur."""
        cursor = self.get_connection().cursor()
        cursor.execute(
            ("select nom, prenom,email,avatar,status,liste_etablissements_surveiller from users where id=?"),
            (user_id,),
        )
        user_info = cursor.fetchone()
        if user_info is None:
            return None
        else:
            return user_info

    
    ### SESSIONS ###
    
    def user_is_log_in(self, id_session):
        """Indique si un id de session correspond a une session valide."""
        return self.get_session_email(id_session) is not None
    
    def save_session(self, id_session, email):
        """Enregistre une nouvelle session pour un utilisateur."""
        connection = self.get_connection()
        connection.execute(
            (
                "insert into sessions(id_session, email) "
                "values(?, ?)"
            ),
            (id_session, email),
        )
        connection.commit()

    def delete_session(self, id_session):
        """Supprime une session a partir de son identifiant."""
        connection = self.get_connection()
        connection.execute(
            ("delete from sessions where id_session=?"),
            (id_session,),
        )
        connection.commit()
