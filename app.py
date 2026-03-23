# Projet Session - INF5190 - 2026
# Yoan Desjardins - DESY77040109
import base64
import hashlib
import uuid

from flask import Flask
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session

try:
    from .database import Database
except ImportError:
    from database import Database

app = Flask(__name__, static_url_path="", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB upload limit

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


# @app.context_processor
# def inject_auth_state():
#     """Fonction utile pour le front-end"""
#     return {
#         "current_email": (
#             _get_db().get_session_email(session.get("id"))
#             if "id" in session
#             else None
#         ),
#         "is_logged_in": _get_db().user_is_log_in(session.get("id")),
#         "connected_user_id": (
#             _get_db().get_user_id_from_email(
#                 _get_db().get_session_email(session.get("id"))
#             )
#             if "id" in session
#             else None
#         ),
#         "avatar": _get_db().get_avatar_by_userid(session.get("user_id")),
#         "get_avatar_by_userid": _get_db().get_avatar_by_userid,
#         "get_author_name_by_userid": _get_db().get_author_name_by_userid,
#     }


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

app.secret_key = "GHgQgYj2Yl1HD/WvFawstsVdlNJsNYSa"
