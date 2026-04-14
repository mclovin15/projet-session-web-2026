# Fichier pour la configuration de Flask en respectant les exigences du projet
# Projet Session - INF5190 - 2026
# Yoan Desjardins - DESY77040109
import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "GHgQgYj2Yl1HD/WvFawstsVdlNJsNYSa")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
