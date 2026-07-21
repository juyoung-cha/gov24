import json
import logging
from rss_collector import RSSCollector

# 조용히 수행하도록 로깅 레벨 조정
logging.basicConfig(level=logging.ERROR)

def main():
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    collector = RSSCollector()
    feeds = config["rss_feeds"]
    
    print("\n" + "="*80)
    print("오늘의 추천 포스팅 주제 후보 (2026-04-15)")
    print("="*80)
    
    # 주요 부처 뉴스 수집 (최근 5개씩)
    for dept, url in feeds.items():
        items = collector.fetch_rss(dept, url)
        if items:
            print(f"\n▶ [{dept}] 최신 소식")
            for i, item in enumerate(items[:3], 1):
                title = item['title'].strip()
                print(f"  {i}. {title}")
                print(f"     링크: {item['link']}")

if __name__ == "__main__":
    main()
