import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://www.korea.kr/rss/dept_moef.xml"
DATA_FILE = "seen.json"

def fetch_latest():
    res = requests.get(URL, timeout=10)
    res.raise_for_status()
    res.encoding = "utf-8"

    soup = BeautifulSoup(res.text, "xml")
    items = soup.find_all("item")[:5]

    results = []
    for it in items:
        title = it.title.text.strip()
        link = it.link.text.strip()
        date = it.pubDate.text.strip() if it.pubDate else ""

        results.append({
            "title": title,
            "link": link,
            "date": date
        })

    return results


def load_seen():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False, indent=2)


def filter_new(items, seen):
    new_items = []
    for it in items:
        key = it["link"]
        if key not in seen:
            new_items.append(it)
            seen.add(key)
    return new_items


if __name__ == "__main__":
    print("시작")

    seen = load_seen()
    items = fetch_latest()
    new_items = filter_new(items, seen)

    if new_items:
        print("🆕 새 글 발견:", len(new_items))
        for d in new_items:
            print("제목:", d["title"])
            print("링크:", d["link"])
            print("날짜:", d["date"])
            print("-" * 40)

        save_seen(seen)
    else:
        print("새 글 없음")

    print("끝")
