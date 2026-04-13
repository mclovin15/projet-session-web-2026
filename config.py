import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "GHgQgYj2Yl1HD/WvFawstsVdlNJsNYSa")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
