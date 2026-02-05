"""
Generate a simple CSV-derived hydration summary (min/max/avg) to console.
Extend later to create charts for the dashboard.
"""
import csv, statistics as stats
from config import HYDRATION_SCORES_CSV

def main():
    scores = []
    with open(HYDRATION_SCORES_CSV, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                scores.append(float(row["score"]))
            except: ...
    if not scores:
        print("No records yet.")
        return
    print(f"Count: {len(scores)}")
    print(f"Avg:   {stats.mean(scores):.3f}")
    print(f"Min:   {min(scores):.3f}")
    print(f"Max:   {max(scores):.3f}")

if __name__ == "__main__":
    main()
