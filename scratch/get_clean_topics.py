import json
import logging
from rss_collector import RSSCollector

logging.basicConfig(level=logging.ERROR)

def main():
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    collector = RSSCollector()
    feeds = config["rss_feeds"]
    
    output = []
    output.append("="*80)
    output.append("오늘의 추천 포스팅 주제 후보 (2026-04-16)")
    output.append("="*80)
    
    for dept, url in feeds.items():
        try:
            items = collector.fetch_rss(dept, url)
            if items:
                output.append(f"\n▶ [{dept}] 최신 소식")
                for i, item in enumerate(items[:5], 1):
                    title = item['title'].strip()
                    output.append(f"  {i}. {title}")
                    output.append(f"     링크: {item['link']}")
        except Exception as e:
            output.append(f"\n[!] {dept} 수집 중 오류 발생: {str(e)}")

    with open("topics_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    print("Results saved to topics_output.txt")

if __name__ == "__main__":
    main()
