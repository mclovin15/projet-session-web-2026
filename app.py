# Projet Session - INF5190 - 2026
# Yoan Desjardins - DESY77040109
import base64
import hashlib
import uuid
import atexit
import os

from flask import Flask
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from apscheduler.schedulers.background import BackgroundScheduler

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

def _get_db():
    """Pool connexion à bd."""
    db = getattr(g, "_database", None)
    if db is None:
        g._database = Database()
    return g._database

def sync_violations_job():
    with app.app_context():
        app.logger.info("Debut de la synchronisation")
        result = update_violations()
        app.logger.info(
            "Synchronisation terminee: %s insertions, %s mises a jour",
            result["inserted"],
            result["updated"],
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

@app.teardown_appcontext
def close_connection(exception):
    """Ferme la connexion SQL ouverte pendant la requete courante."""
    db = getattr(g, "_database", None)
    if db is not None:
        db.disconnect()


@app.context_processor
def inject_auth_state():
    """Fonction utile pour le front-end"""
    return {
        # "current_email": (
        #     _get_db().get_session_email(session.get("id"))
        #     if "id" in session
        #     else None
        # ),
        # "is_logged_in": _get_db().user_is_log_in(session.get("id")),
        # "connected_user_id": (
        #     _get_db().get_user_id_from_email(
        #         _get_db().get_session_email(session.get("id"))
        #     )
        #     if "id" in session
        #     else None
        # ),
        # "avatar": _get_db().get_avatar_by_userid(session.get("user_id")),
        # "get_avatar_by_userid": _get_db().get_avatar_by_userid,
        "get_categorie_violation_icon": _get_categorie_violation_icon,
        "get_status_violation_color": _get_status_violation_color,
    }


@app.route("/", methods=["GET"])
def index():
    """Affiche page accueil avec formulaire de recherche."""
    query = request.args.get("query", "").strip()
    if query:
        violations = _get_db().search_violations(query)
        return render_template(
            "search_results.html",
            violations=violations,
            query=query,
        )
    return render_template("index.html")

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