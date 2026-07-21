import json
import logging
from rss_collector import RSSCollector

logging.basicConfig(level=logging.INFO)

def main():
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    collector = RSSCollector()
    feeds = config["rss_feeds"]
    
    # seen.json 로드
    try:
        with open("seen.json", "r", encoding="utf-8") as f:
            seen = set(json.load(f))
    except:
        seen = set()
    
    print("\n" + "="*60)
    print("최신 뉴스 수집 중...")
    print("="*60 + "\n")
    
    all_items = collector.fetch_all(feeds)
    new_items = collector.filter_new_items(all_items, seen)
    
    if not new_items:
        print("새로운 뉴스가 없습니다. (모든 뉴스가 이미 처리됨)")
        # 원본 뉴스 5개라도 보여주기
        print("\n최신 기존 뉴스 (이미 처리됨):")
        for i, item in enumerate(all_items[:5], 1):
            print(f"{i}. [{item['dept']}] {item['title']} - {item['link']}")
    else:
        print(f"총 {len(new_items)}개의 새로운 뉴스를 발견했습니다.\n")
        # 최근 뉴스 10개 출력
        for i, item in enumerate(new_items[:10], 1):
            print(f"{i}. [{item['dept']}] {item['title']}")
            print(f"   링크: {item['link']}")
            print(f"   날짜: {item.get('date', 'N/A')}\n")

if __name__ == "__main__":
    main()
