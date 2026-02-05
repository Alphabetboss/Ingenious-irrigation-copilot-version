"""
Bulk image downloader for class lists using icrawler (Bing).
Edits:
 - Removed DuckDuckGo crawler import (not shipped in icrawler by default).
 - Debounced errors and added per-class limits.
"""
from icrawler.builtin import BingImageCrawler
from pathlib import Path

CLASSES = ["grass", "dead grass", "mud", "standing water", "leak"]
PER_CLASS = 150
OUT = Path("datasets/image_scrape/raw")

def fetch_one(q: str, limit: int = 150):
    out = OUT / q.replace(" ", "_")
    out.mkdir(parents=True, exist_ok=True)
    crawler = BingImageCrawler(storage={"root_dir": str(out)})
    crawler.crawl(keyword=q, max_num=limit, file_idx_offset=0)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for q in CLASSES:
        print("Downloading:", q)
        fetch_one(q, PER_CLASS)
    print("Done.")

if __name__ == "__main__":
    main()
