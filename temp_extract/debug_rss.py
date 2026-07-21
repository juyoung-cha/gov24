
import json
import logging
from rss_collector import RSSCollector

logging.basicConfig(level=logging.INFO)

def check_rss():
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    rss_collector = RSSCollector()
    print("RSS 피드 수집 중...")
    all_items = rss_collector.fetch_all(config["rss_feeds"])
    
    with open("seen.json", "r", encoding="utf-8") as f:
        seen = set(json.load(f))
    
    new_items = rss_collector.filter_new_items(all_items, seen)
    
    print(f"\n총 수집 항목: {len(all_items)}개")
    print(f"이미 처리된 항목: {len(seen)}개")
    print(f"신규 항목: {len(new_items)}개")
    
    if new_items:
        print("\n신규 항목 목록 (최대 5개):")
        for i, item in enumerate(new_items[:5], 1):
            print(f"{i}. {item['title']} ({item['dept']})")
            print(f"   URL: {item['link']}")
            print(f"   Date: {item.get('date', 'N/A')}")

if __name__ == "__main__":
    check_rss()
