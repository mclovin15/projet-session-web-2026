# Script Python pour importer les contraventions depuis un fichier CSV dans une base de données SQLite
# Projet Session - INF5190 - 2026
# Yoan Desjardins - DESY77040109
import csv
from urllib.request import Request, urlopen

try:
    from .database import Database
    from .violation import Violation
except ImportError:
    from database import Database
    from violation import Violation


URL = (
    "https://data.montreal.ca/dataset/"
    "05a9e718-6810-4e73-8bb9-5955efeb91a0/resource/"
    "7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/csv,*/*",
}


def update_violations():
    db = Database()
    number_inserted = 0
    number_updated = 0

    try:
        request = Request(URL, headers=HEADERS)

        with urlopen(request, timeout=30) as response:
            contenu = response.read().decode("utf-8-sig").splitlines()
            reader = csv.DictReader(contenu)

            for row in reader:
                if not db.violation_exists(int(row["id_poursuite"])):
                    violation = Violation.from_csv_row(row)
                    db.insert_violation(violation)
                    number_inserted += 1
                elif db.is_violation_updated(int(row["id_poursuite"]), row):
                    violation = Violation.from_csv_row(row)
                    db.update_violation(violation)
                    number_updated += 1

        return {
            "inserted": number_inserted,
            "updated": number_updated,
        }
    finally:
        db.disconnect()


if __name__ == "__main__":
    result = update_violations()
    print(f"Nombre de violations inserees: {result['inserted']}")
    print(f"Nombre de violations mises a jour: {result['updated']}")
