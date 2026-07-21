import requests
from bs4 import BeautifulSoup

URL = "https://www.korea.kr/rss/dept_moef.xml"

def fetch_latest():
    res = requests.get(URL, timeout=10)
    res.raise_for_status()

    res.encoding = "utf-8"   # ← 이 줄이 핵심

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


if __name__ == "__main__":
    data = fetch_latest()
    print("가져온 개수:", len(data))

    for d in data:
        print("제목:", d["title"])
        print("링크:", d["link"])
        print("날짜:", d["date"])
        print("-" * 40)
