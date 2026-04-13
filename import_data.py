# Script Python pour importer les contraventions depuis un fichier CSV dans une base de données SQLite
# Sert à peupler la base de données avec les données initiales
# Projet Session - INF5190 - 2026
# Yoan Desjardins - DESY77040109
from database import Database
from violation import Violation
import csv
from urllib.request import Request,urlopen

db = Database()
connection = db.get_connection()

URL = (
    "https://data.montreal.ca/dataset/"
    "05a9e718-6810-4e73-8bb9-5955efeb91a0/resource/"
    "7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv"
)

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/csv,*/*",
}

request = Request(URL, headers=headers)

with urlopen(request, timeout=30) as response:
    contenu = response.read().decode("utf-8-sig").splitlines()
    reader = csv.DictReader(contenu)

    for row in reader:
        if(not db.violation_exists(int(row["id_poursuite"]))):
            print("Insertion de la violation #" + str(row["id_poursuite"]) + " réuisste")
            violation = Violation.from_csv_row(row)
            db.insert_violation(violation)
