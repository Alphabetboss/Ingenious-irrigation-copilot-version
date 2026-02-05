import csv
from datetime import datetime

def log_hydration(score, path="data/hydration.csv"):
    with open(path, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), score])
