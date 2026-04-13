# Contient de la logique de l'application Flask, des routes et de la configuration du scheduler
# Projet Session - INF5190 - 2026
# Yoan Desjardins - DESY77040109
import csv
import hashlib
import io
import uuid
import atexit
import os
import xml.etree.ElementTree as ET

from flask import Flask, g, redirect,render_template,request,session,url_for,jsonify, Response
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from flask_json_schema import JsonSchema, JsonValidationError
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

try:
    from .update_violations import update_violations
    from .database import Database
except ImportError:
    from update_violations import update_violations
    from database import Database


app = Flask(__name__, static_url_path="", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 

scheduler = BackgroundScheduler(timezone="America/Toronto")
schema = JsonSchema(app)


#############################
######### SCHEMA ###########
#############################
DEMANDE_INSPECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "business_id": {"type": "integer"},
        "etablissement": {"type": "string"},
        "adresse": {"type": "string"},
        "ville": {"type": "string"},
        "date_visite" : {"type": "string"},
        "nom_complet_client" : {"type": "string"},
        "description_prob" : {"type": "string"}
    },
    "required": ["business_id", "etablissement", "adresse", "ville","date_visite","nom_complet_client","description_prob"],
    "additionalProperties": False
}

USER_CREATION_SCHEMA = {
    "type": "object",
    "properties": {
        "nom": {"type": "string"},
        "prenom": {"type": "string"},
        "email": {"type": "string"},
        "avatar": {"type": "string", "format": "data-url"}, 
        "password": {"type": "string"},
        "liste_etablissements_surveiller": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "business_id": {"type": "integer"},
                    "etablissement": {"type": "string"},
                    "adresse": {"type": "string"}
                },
                "required": ["business_id", "etablissement", "adresse"],
                "additionalProperties": False
            }
        }
    },
    "required": ["nom", "prenom", "email", "password", "liste_etablissements_surveiller"],
    "additionalProperties": False
}

USER_LOGIN_SCHEMA = {
    "type": "object",
    "properties": {
        "email": {"type": "string"},
        "password": {"type": "string"}
    },
    "required": ["email", "password"],
    "additionalProperties": False
}

USER_PROFILE_UPDATE_SCHEMA = {
    "type": "object",
    "properties": {
        "nom": {"type": "string"},
        "prenom": {"type": "string"},
        "avatar": {"type": "string", "format": "data-url"},
    },
    "required": ["nom", "prenom"],
    "additionalProperties": False
}

WATCHED_BUSINESS_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "liste_etablissements_surveiller": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "business_id": {"type": "integer"},
                    "etablissement": {"type": "string"},
                    "adresse": {"type": "string"}
                },
                "required": ["business_id", "etablissement", "adresse"],
                "additionalProperties": False
            }
        }
    },
    "required": ["liste_etablissements_surveiller"],
    "additionalProperties": False
}


#############################
######### VALIDATION ########
#############################
@app.errorhandler(JsonValidationError)
def handle_validation_error(e):
    return jsonify({
        "error": "JSON invalide selon le schema",
        "errors": [err.message for err in e.errors],
    }), 400

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({
        "error": "JSON mal forme"
    }), 400

@app.errorhandler(UnsupportedMediaType)
def handle_unsupported_media_type(e):
    return jsonify({
        "error": "Le Content-Type doit etre application/json"
    }), 415


#############################
######### HELPER ############
#############################
def _get_db():
    """Pool connexion à bd."""
    db = getattr(g, "_database", None)
    if db is None:
        g._database = Database()
    return g._database

@app.teardown_appcontext
def close_connection(exception):
    """Ferme la connexion SQL ouverte pendant la requete courante."""
    db = getattr(g, "_database", None)
    if db is not None:
        db.disconnect()

def _build_password_hash(password):
    """Genere le sel et le hash SHA-512 du mot de passe."""
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512(
        str(password + salt).encode("utf-8")).hexdigest()

    return salt, hashed_password

def _is_supported_avatar_data_url(avatar_data_url):
    """Valide que l'avatar fourni est au format PNG ou JPG/JPEG."""
    if not avatar_data_url:
        return True

    return (
        avatar_data_url.startswith("data:image/png;base64,")
        or avatar_data_url.startswith("data:image/jpeg;base64,")
    )

def _get_status_violation_color(status: str):
    """Retourne une couleur CSS pour un statut de violation donné."""
    status = status.lower()
    if status == "fermé changement d'exploitant":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
    elif status == "ouvert":
        return "bg-green-100 text-green-800 border-green-200"
    elif status == "fermé":
        return "bg-red-100 text-red-800 border-red-200"
    else:
        return "bg-gray-100 text-gray-800 border-gray-200"

def _get_categorie_violation_icon(categorie: str):
    """Retourne une icone pour une categorie de violation donné."""
    categorie = categorie.lower()
    if categorie == "restaurant service rapide":
        return '<i class="fa-solid fa-burger"></i>'
    elif categorie == "restaurant":
        return '<i class="fa-solid fa-utensils"></i>'
    elif categorie == "brasserie":
        return '<i class="fa-solid fa-beer-mug-empty"></i>'
    else:
        return '<i class="fa-solid fa-shop"></i>'
    
def is_iso_extended_date(date_str: str) -> bool:
    """ Permet savoir si format est YYYY-MM-DD """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
    
def iso_date_to_basic(date_str: str) -> str:
    """Convertit YYYY-MM-DD en YYYYMMDD."""
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y%m%d")

def _start_session(user_id, email):
    """Démarre une session pour un utilisateur donné."""    
    id_session = uuid.uuid4().hex
    
    _get_db().save_session(id_session, email)

    session["id"] = id_session
    session["user_id"] = user_id
    session["email"] = email

def _end_session(id_session):
    """Termine une session pour un utilisateur donné."""
    
    _get_db().delete_session(id_session)
    
    session.pop("id", None)
    session.pop("user_id", None)
    session.pop("email", None)

@app.context_processor
def inject_auth_state():
    """Fonction utile pour le front-end"""
    is_logged_in = _get_db().user_is_log_in(session.get("id"),session.get("email"))
    connected_user_id = session.get("user_id") if is_logged_in else None
    avatar = _get_db().get_avatar_by_userid(connected_user_id) if connected_user_id else None
    connected_user_name = (
        _get_db().get_author_name_by_userid(connected_user_id)
        if connected_user_id else None
    )

    return {
        "get_categorie_violation_icon": _get_categorie_violation_icon,
        "get_status_violation_color": _get_status_violation_color,
        "is_logged_in": is_logged_in,
        "connected_user_id": connected_user_id,
        "avatar": avatar,
        "connected_user_name": connected_user_name,
        "connected_user_email": session.get("email") if is_logged_in else None,
        "get_avatar_by_userid": _get_db().get_avatar_by_userid,
        "get_author_name_by_userid": _get_db().get_author_name_by_userid,

    }



#############################
######### ROUTES ############
#############################
@app.route("/", methods=["GET"])
def index():
    """Affiche page accueil avec formulaire de recherche."""
    query = request.args.get("query", "").strip()
    mode = request.args.get("mode", "1")

    if query and mode == "1":
        violations = _get_db().search_violations(query)
        return render_template(
            "default_search_results.html",
            violations=violations,
            query=query,
            mode=mode,
        )
    elif mode == "3":
        # sert à remplir la liste deroulante
        liste_etablissement = _get_db().return_all_etablissements()
        return render_template("index.html", mode=mode,liste_etablissement=liste_etablissement)
        
    return render_template("index.html", mode=mode)

@app.route("/etablissement_details/<int:business_id>", methods=["GET"])
def etablissement_details_page(business_id: int):
    """Remplis la page pour les details d'un établissement."""
    etablissement_summary = _get_db().return_business_summary(business_id)
    
    if not etablissement_summary:
        return render_template("404.html", message="Établissement non trouvé.")
    violation_list = _get_db().return_all_violations_of_etablissement(business_id)
    
    if not violation_list:
        return render_template("404.html", message="Aucune violation trouvée pour cet établissement.")
    
    return render_template("business_details.html", etablissement_details=etablissement_summary[0], violations=violation_list)

@app.route("/doc", methods=["GET"])
def doc():
    """Redirige vers la documentation de l'API."""
    return redirect(url_for("static", filename="doc/api.html"))

@app.route("/inspections", methods=["GET"])
def inspections():
    """Affiche la page de tout les demandes d\'inspections inspections."""
    plaintes = _get_db().return_all_inspections()
    return render_template("inspections.html",plaintes=plaintes)

@app.route("/demande-inspection", methods=["GET"])
def demande_inspection():
    """Affiche la page de formulaire de demande d\'inspection."""
    liste_etablissement = _get_db().return_all_etablissements()
    
    return render_template("form_demande_inspection.html",liste_etablissement=liste_etablissement)

@app.route("/login", methods=["GET"])
def login_page():
    """Affiche la page login."""
    if _get_db().user_is_log_in(session.get("id"),email=session.get("email")):
        return redirect(url_for("index"))

    return render_template("login.html")

@app.route("/signin", methods=["GET"])
def signin_page():
    """Affiche la page d\'inscription."""
    if _get_db().user_is_log_in(session.get("id"),email=session.get("email")):
        return redirect(url_for("index"))

    liste_etablissement = _get_db().return_all_etablissements()
    return render_template("signin.html", liste_etablissement=liste_etablissement)

@app.route("/edit_profile", methods=["GET"])
def edit_profile_page():
    """Affiche la page de modification du profil."""
    if not _get_db().user_is_log_in(session.get("id"),email=session.get("email")):
        # Non connecte
        return render_template("login.html"),403

    user_profile = _get_db().get_user_profile_by_id(session.get("user_id"))
    return render_template("edit_profile.html", user_profile=user_profile)

@app.route("/edit_user_watch_list", methods=["GET"])
def render_form_user_watch_list():
    """Affiche la page de modification de la liste d'établissements surveillés."""
    if not _get_db().user_is_log_in(session.get("id"),email=session.get("email")):
        # Non connecte
        return render_template("login.html"),403
    liste_etablissement = _get_db().return_all_etablissements()
    watched_businesses = _get_db().get_business_watchlist_user(session.get("user_id"))
    return render_template(
        "form_user_watched_businesses.html",
        liste_etablissement=liste_etablissement,
        watched_businesses=watched_businesses,
    )

@app.route("/user_watch_list", methods=["GET"])
def user_watch_list():
    """Affiche la page de gestion des établissements surveillés."""
    if not _get_db().user_is_log_in(session.get("id"),email=session.get("email")):
        # Non connecte
        return render_template("login.html"),403
    watched_businesses = _get_db().get_business_watchlist_user(session.get("user_id"))
    return render_template("user_watch_list.html", watched_businesses=watched_businesses)


#############################
###### API SERVICES #########
#############################
@app.route("/etablissement/<int:business_id>", methods=["GET"])
def etablissement_details(business_id: int):
    """API retourne en JSON les details d'un établissement."""
    etablissement = _get_db().return_etablissement_details(business_id)
    if not etablissement:
        return jsonify({"error": "Établissement non trouvé."}), 404

    return jsonify(etablissement.to_dict()), 200

@app.route("/contrevenants", methods=["GET"])
def contrevenants():
    """API retourne en JSON les contrenvations entre les dates données."""
    date_du = request.args.get("du")
    date_au = request.args.get("au")
    
    if not date_du or not date_au:
        return jsonify({
            "error": "Les parametres 'du' et 'au' sont obligatoires."
        }), 400    
        
    try: 
        if(is_iso_extended_date(date_au)):
            date_au = iso_date_to_basic(date_au)
        else:
            raise ValueError("Date au invalide")
            
        if(is_iso_extended_date(date_du)):
            date_du = iso_date_to_basic(date_du)
        else:
            raise ValueError("Date du  invalide") 
        
    except ValueError:
        return jsonify({
            "error": "Les dates doivent etre au format ISO 8601 YYYY-MM-DD."
        }), 400   
        
    if date_du > date_au:
        return jsonify({
            "error": "La date 'du' doit etre anterieure ou egale a la date 'au'."
        }), 400

    violations_in_range = _get_db().search_violations_by_date_range(date_du,date_au)
    
    return jsonify([violation.to_dict() for violation in violations_in_range]), 200

@app.route("/violations_par_etablissement", methods=["GET"])
def violations_par_etablissement():
    """API retourne en JSON les violations par établissement."""
    violations = _get_db().return_all_etablissement_with_nb_violations()
    return jsonify(violations),200

@app.route("/violations_par_etablissement.xml", methods=["GET"])
def violations_par_etablissement_xml():
    """API retourne en XML les violations par établissement."""
    violations = _get_db().return_all_etablissement_with_nb_violations()

    root = ET.Element("etablissements")

    for item in violations:
        etab = ET.SubElement(root, "etablissement")
        ET.SubElement(etab, "business_id").text = str(item["business_id"])
        ET.SubElement(etab, "nom").text = item["etablissement"]
        ET.SubElement(etab, "adresse").text = item["adresse"]
        ET.SubElement(etab, "nombre_violations").text = str(item["nombre_violations"])

    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    return Response(
        xml_bytes,
        mimetype="application/xml; charset=utf-8",
    )

@app.route("/violations_par_etablissement.csv", methods=["GET"])
def violations_par_etablissement_csv():
    """ API retourne en CSV les violations par établissement."""
    
    violations = _get_db().return_all_etablissement_with_nb_violations()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["business_id", "etablissement", "adresse", "nombre_violations"])
    for item in violations:
        writer.writerow([
            item["business_id"],
            item["etablissement"],
            item["adresse"],
            item["nombre_violations"],
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
    )

@app.route("/demande-inspection", methods=["POST"])
@schema.validate(DEMANDE_INSPECTION_SCHEMA)
def creer_demande_inspection():
    """API pour creer une demande inspection. Validation date et existence de l'établissement."""
    
    demande_inspection = request.get_json()
    if not is_iso_extended_date(demande_inspection.get("date_visite")):
        return jsonify({
            "error": "La date doit etre au format ISO 8601 YYYY-MM-DD."
        }), 400
    
    if not _get_db().etablissement_exists_by_id(demande_inspection.get("business_id")):
        return jsonify({
            "error": "Aucun établissement ne correspond au business_id fourni."
        }), 400
    
    _get_db().insert_inspection(demande_inspection)
    
    return jsonify({"success": True,"message": "Demande d'inspection créée avec succès."}), 201

@app.route("/demande-inspection/<int:id_inspection>", methods=["DELETE"])
def supprimer_demande_inspection(id_inspection):
    """API pour supprimer une demande d'inspection."""
    
    if not id_inspection:
        return jsonify({
            "error": "Le parametre 'id_inspection' est obligatoire."
        }), 400
    
    try:
        id_inspection = int(id_inspection)
    except ValueError:
        return jsonify({
            "error": "Le parametre 'id_inspection' doit etre un entier."
        }), 400
    
    if  _get_db().get_inspection_by_id(id_inspection) is None:
        return jsonify({
            "error": f"Aucune demande d'inspection trouvee avec l'id {id_inspection}."
        }), 404
    
    _get_db().delete_inspection(id_inspection)
    
    return jsonify({"success": True,"message": f"Demande d'inspection avec l'id {id_inspection} supprimee avec succes."}), 200


@app.route("/login", methods=["POST"])
@schema.validate(USER_LOGIN_SCHEMA)
def connect_user():
    """API pour connecter un utilisateur."""
    
    credentials = request.get_json()
    email = credentials.get("email")
    password = credentials.get("password")
    
    user_login_info = _get_db().get_user_login_info(email)
    if user_login_info is None:
        return jsonify({
            "error": f"Aucun utilisateur trouvee avec le courriel {email}."
        }), 404

    salt, stored_hash, user_id = user_login_info
    # Verif du mdp
    hashed_password = hashlib.sha512(
        str(password + salt).encode("utf-8")).hexdigest()

    if hashed_password != stored_hash:
        return jsonify({
            "error": "Mots de passe invalide."
        }), 404

    if _get_db().get_user_status(user_id) == 0:
        return jsonify({
            "error": "Compte désactiver veuillez contacter un administrateur !"
        }), 403
    
    # Creation de la session
    _start_session(user_id, email)

    return jsonify({"success": True,"message": "Connexion réussie.","session_id": session.get("id")}), 200

@app.route("/logout", methods=["DELETE"])
def logout_user():
    """API pour deconnecter un utilisateur."""
    
    id_session = session.get("id")
    if not id_session:
        return jsonify({
            "error": "Aucune session active trouvee."
        }), 404
    
    # Terminer la session
    _end_session(id_session)

    return jsonify({"success": True,"message": "Déconnexion réussie."}), 200


@app.route("/user", methods=["POST"])
@schema.validate(USER_CREATION_SCHEMA)
def creer_new_user():
    """ API pour creer un nouvel utilisateur."""
    
    new_user = request.get_json()
    email = new_user.get("email")
    if _get_db().email_already_exist(email):
        return jsonify({
            "error": f"Le courriel {email} est deja pris."
        }), 404   
        
    liste_etablissements_surveiller = new_user.get("liste_etablissements_surveiller")

    for etablissement in liste_etablissements_surveiller:
        business_id = etablissement["business_id"]
        nom = etablissement["etablissement"]
        if not _get_db().etablissement_exists_by_id(business_id):
            return jsonify({
            "error": f"L'établissement {nom} n'existe pas."
            }), 404
        
    password = new_user.get("password")
    salt, hashed_password = _build_password_hash(password)
    
    if new_user.get("avatar"):
        avatar = new_user.get("avatar")
    else:
        avatar = None

    if not _is_supported_avatar_data_url(avatar):
        return jsonify({
            "error": "L'avatar doit etre au format JPG ou PNG."
        }), 400
        
    _get_db().insert_user(new_user,salt,hashed_password,avatar)
    user_id = _get_db().get_user_id_from_email(email)
    _start_session(user_id, email)
    
    return jsonify({"success": True,"message": f"L'utilisateur {email} a été créer avec succes."}), 201

@app.route("/user/<int:user_id>", methods=["PATCH"])
@schema.validate(USER_PROFILE_UPDATE_SCHEMA)
def edit_user_profile(user_id):
    """API pour modifier le profil d'un utilisateur connecté."""
    user = _get_db().get_user_profile_by_id(user_id)
    if user is None:
        return jsonify({
            "error": f"Aucun utilisateur trouvee avec l'id {user_id}."
        }), 404

    if not _get_db().user_is_log_in(session.get("id"), email=user["email"]):
        return jsonify({
            "error": "Vous devez etre connecter pour faire cela."
        }), 404

    data = request.get_json()
    nom = data.get("nom", "").strip()
    prenom = data.get("prenom", "").strip()

    if not nom or not prenom:
        return jsonify({
            "error": "Le nom et le prénom sont obligatoires."
        }), 400

    avatar = data["avatar"] if "avatar" in data else user["avatar"]

    if not _is_supported_avatar_data_url(avatar):
        return jsonify({
            "error": "L'avatar doit etre au format JPG ou PNG."
        }), 400

    _get_db().update_user_profile(user_id, nom, prenom, avatar)

    return jsonify({
        "success": True,
        "message": "Profil mis à jour avec succès."
    }), 200

@app.route("/user_watch_list/<int:user_id>", methods=["PATCH"])
@schema.validate(WATCHED_BUSINESS_LIST_SCHEMA)
def edit_user_watch_list(user_id):
    """API pour modifier la liste de surveillance d'un utilisateur."""
    user = _get_db().get_user_profile_by_id(user_id)
    if user is None:
        return jsonify({
            "error": f"Aucun utilisateur trouvee avec l'id {user_id}."
        }), 404
    if not _get_db().user_is_log_in(session.get("id"),email=user["email"]):
        # Non connecte
        return jsonify({
            "error": f"Vous devez etre connecter pour faire cela."
            }), 404

    new_watch_list = request.get_json().get("liste_etablissements_surveiller", [])
    current_watch_list = _get_db().get_business_watchlist_user(user_id)

    # On transformes les listes en dict avec le business_id comme key
    current_by_id = {
        etablissement["business_id"]: etablissement
        for etablissement in current_watch_list
    }
    new_by_id = {
        etablissement["business_id"]: etablissement
        for etablissement in new_watch_list
    }

    # On verifie si etablissement existe bien
    for etablissement in new_watch_list:
        business_id = etablissement["business_id"]
        nom = etablissement["etablissement"]
        if not _get_db().etablissement_exists_by_id(business_id):
            return jsonify({
                "error": f"L'établissement {nom} n'existe pas."
            }), 404
    # on compare pour voir les changements
    added_ids = sorted(set(new_by_id) - set(current_by_id))
    removed_ids = sorted(set(current_by_id) - set(new_by_id))

    # on verifie si les infos des établissements qui sont dans les deux listes ont changé
    updated_ids = sorted(
        business_id for business_id in (set(new_by_id) & set(current_by_id))
        if new_by_id[business_id] != current_by_id[business_id]
    )

    if not added_ids and not removed_ids and not updated_ids:
        return jsonify({
            "success": True,
            "message": "Aucune modification à enregistrer.",
            "added_ids": [],
            "removed_ids": [],
            "updated_ids": [],
        }), 200

    _get_db().update_business_watchlist_user(user_id, new_watch_list)

    return jsonify({
        "success": True,
        "message": "La liste de surveillance a été modifiée avec succès.",
        "added_ids": added_ids,
        "removed_ids": removed_ids,
        "updated_ids": updated_ids,
    }), 200


#############################
######## SCHEDULER ##########
#############################
def sync_violations_job():
    """Synchroniser les violations. """
    with app.app_context():
        app.logger.info("Debut de la synchronisation")
        result = update_violations()
        app.logger.info(
            "Synchronisation terminee: %s insertions, %s mises a jour",
            result["inserted"],
            result["updated"],
        )    
    
scheduler.add_job(
    func=sync_violations_job,
    trigger="cron",
    hour=0,
    minute=0,
    id="daily_violation_sync",
    replace_existing=True,
    misfire_grace_time=3600, # autoriser une execution jusqu'à 1h après l'heure
)
# TODO: revoir à la remise si on l'enlève
# Evite de lancer deux schedulers avec le reloader de Flask en debug
if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

# TODO: ai ->  garde la secret_key en dur dans le code.
# Le document demande que les éléments de configuration soient dans un fichier de configuration documenté. Ici, ce n’est pas respecté.
app.secret_key = "GHgQgYj2Yl1HD/WvFawstsVdlNJsNYSa"
