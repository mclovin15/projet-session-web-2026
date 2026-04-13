# Projet Session - INF5190 - 2026
# Yoan Desjardins - DESY77040109
import base64
import csv
import hashlib
import io
import uuid
import json
import atexit
import os
import xml.etree.ElementTree as ET

from flask import Flask,abort,flash, g, redirect,render_template,request,session,url_for,jsonify, Response
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from flask_json_schema import JsonSchema, JsonValidationError
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

try:
    from .update_violations import update_violations
except ImportError:
    from update_violations import update_violations


try:
    from .database import Database
except ImportError:
    from database import Database

app = Flask(__name__, static_url_path="", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB upload limit

scheduler = BackgroundScheduler(timezone="America/Toronto")
schema = JsonSchema(app)

#############################
######### SCHEMA ###########
#############################
DEMANDE_INSPECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "etablissement": {"type": "string"},
        "adresse": {"type": "string"},
        "ville": {"type": "string"},
        "date_visite" : {"type": "string"},
        "nom_complet_client" : {"type": "string"},
        "description_prob" : {"type": "string"}
    },
    "required": ["etablissement", "adresse", "ville","date_visite","nom_complet_client","description_prob"],
    "additionalProperties": False
}
# TODO: vérifier si je mets avatar
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
def is_date_iso(date_str: str) -> bool:
    """ Permet savoir si format est YYYYMMDD """
    try:
        datetime.strptime(date_str, "%Y%m%d")
        return True
    except ValueError:
        if(is_iso_extended_date(date_str)):
            return True
        return False

def iso_date_to_basic(date_str: str) -> str:
    """Convertit YYYY-MM-DD en YYYYMMDD."""
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y%m%d")

@app.context_processor
def inject_auth_state():
    """Fonction utile pour le front-end"""
    return {
        "get_categorie_violation_icon": _get_categorie_violation_icon,
        "get_status_violation_color": _get_status_violation_color,
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
            "search_results.html",
            violations=violations,
            query=query,
            mode=mode,
        )
    elif mode == "3":
        # sert à remplir la liste deroulante
        liste_etablissement = _get_db().return_all_etablissements()
        return render_template("index.html", mode=mode,liste_etablissement=liste_etablissement)
        
    return render_template("index.html", mode=mode)

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
        # TODO: faire meilleur verif format date
        # on check si on recoit format YYYY-MM-DD,si oui on convertit
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

# TODO: revoir comment je fais mon post
@app.route("/demande-inspection", methods=["POST"])
@schema.validate(DEMANDE_INSPECTION_SCHEMA)
def creer_demande_inspection():
    """API pour creer une demande inspection. Validation date et existence de l'établissement."""
    
    demande_inspection = request.get_json()
    if not is_date_iso(demande_inspection.get("date_visite")):
        return jsonify({
            "error": "La date doit etre au format ISO 8601 YYYYMMDD ou YYYY-MM-DD."
        }), 400
    
    if(not _get_db().etablissement_exists_by_infos(demande_inspection.get("etablissement"),demande_inspection.get("adresse"),demande_inspection.get("ville"))):
        return jsonify({
            "error": "Aucun établissement ne correspond aux informations fournies."
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
        adresse = etablissement["adresse"]   
        # TODO: voir si on vérifie tout les champs
        if not _get_db().etablissement_exists_by_id(business_id):
            return jsonify({
            "error": f"L'établissement {nom} n'existe pas."
            }), 404
        
    # TODO: voir si j'intégre avatar
    password = new_user.get("password")
    salt, hashed_password = _build_password_hash(password)
    _get_db().insert_user(new_user,salt,hashed_password)
    return jsonify({"success": True,"message": f"L'utilisateur {email} a été créer avec succes."}), 201


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
# TODO: enlever 
# scheduler.add_job(
#     func=sync_violations_job,
#     trigger="interval",
#     minutes=1,
#     id="daily_violation_sync",
#     replace_existing=True,
# )

# TODO: revoir à la remise si on l'enlève
# Evite de lancer deux schedulers avec le reloader de Flask en debug
if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

app.secret_key = "GHgQgYj2Yl1HD/WvFawstsVdlNJsNYSa"
