"""간단한 1개 포스팅 테스트"""
import json
import logging
from rss_collector import RSSCollector
from content_scraper import ContentScraper
from blog_writer import BlogWriter
from blogger_poster import BloggerPoster
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# 설정
config = json.load(open("config.json", encoding="utf-8"))

# 모듈 초기화
rss_collector = RSSCollector()
content_scraper = ContentScraper()
blog_writer = BlogWriter(config["gemini"]["api_key"], config["gemini"]["model"])
blogger_poster = BloggerPoster(blog_id=config["blogger"]["blog_id"])

print("=" * 60)
print("간단 포스팅 테스트 (1개만)")
print("=" * 60)

# RSS 수집
print("\n1) RSS 수집 중...")
rss_feeds = {
    "기획재정부": "https://www.korea.kr/rss/dept_moef.xml"
}
all_items = rss_collector.collect_all(rss_feeds)
print(f"   수집: {len(all_items)}개")

if len(all_items) == 0:
    print("   ❌ RSS 항목 없음")
    exit(1)

# 첫 번째 항목만 처리
item = all_items[0]
print(f"\n2) 처리 중: {item['title'][:50]}...")

# 원문 크롤링
print("   - 원문 크롤링...")
scraped = content_scraper.scrape(item["link"])
if not scraped:
    print("   ❌ 크롤링 실패")
    exit(1)
print(f"   ✅ 크롤링 완료 (본문: {len(scraped['content'])}자)")

# 블로그 글 작성
print("   - AI 글 작성...")
blog_post = blog_writer.write_post(
    title=item["title"],
    content=scraped["content"],
    dept=item["dept"]
)
if not blog_post:
    print("   ❌ 글 작성 실패")
    exit(1)
print(f"   ✅ 글 작성 완료: {blog_post['blog_title'][:40]}...")

# 날짜 라벨 생성
date_labels = []
if "date" in item and item["date"]:
    try:
        pub_date_str = item["date"]
        dt = None
        
        # 날짜 파싱
        try:
            dt = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
        except:
            try:
                dt = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
            except:
                try:
                    dt = datetime.strptime(pub_date_str[:10], "%Y-%m-%d")
                except:
                    pass
        
        if dt:
            date_labels = [
                f"{dt.year}년",
                f"{dt.year}년-{dt.month:02d}월",
                f"{dt.year}-{dt.month:02d}-{dt.day:02d}"
            ]
            print(f"   ✅ 날짜 라벨: {date_labels}")
    except Exception as e:
        print(f"   ⚠️  날짜 파싱 실패: {e}")

# 라벨 병합
all_labels = blog_post["tags"] + date_labels
print(f"   - 전체 라벨: {all_labels}")

# Blogger 포스팅
print("   - Blogger 포스팅...")
post_url = blogger_poster.post(
    title=blog_post["blog_title"],
    content=blog_post["blog_content"],
    labels=all_labels,
    is_draft=False
)

if post_url:
    print(f"   ✅ 포스팅 성공!")
    print(f"   URL: {post_url}")
else:
    print("   ❌ 포스팅 실패")

print("\n" + "=" * 60)
print("테스트 완료!")
print("=" * 60)
