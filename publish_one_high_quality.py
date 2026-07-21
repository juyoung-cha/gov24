import json
import logging
import os
import random
from datetime import datetime
from dotenv import load_dotenv
from rss_collector import RSSCollector
from content_scraper import ContentScraper
from blog_writer import BlogWriter
from blogger_poster import BloggerPoster

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    filename='auto_scheduler.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    
    # 1. 설정 로드
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    gemini_api_key = os.getenv("GEMINI_API_KEY") or config["gemini"].get("api_key")
    if not gemini_api_key:
        logger.error("GEMINI_API_KEY가 설정되지 않았습니다.")
        return

    # 2. 뉴스 수집 및 선정
    collector = RSSCollector()
    feeds = config["rss_feeds"]
    
    try:
        with open("seen.json", "r", encoding="utf-8") as f:
            seen = set(json.load(f))
    except:
        seen = set()
    
    logger.info("최신 뉴스 수집 중...")
    all_items = collector.fetch_all(feeds)
    new_items = collector.filter_new_items(all_items, seen)
    
    if not new_items:
        logger.info("새로운 뉴스가 없습니다. 종료합니다.")
        return

    # 우선순위: 서울시 정책뉴스 또는 고용노동부 등 실생활 밀착형 우선
    preferred_depts = ["서울시 정책뉴스", "고용노동부", "보건복지부"]
    selected_item = None
    
    for dept in preferred_depts:
        items = [item for item in new_items if item["dept"] == dept]
        if items:
            selected_item = items[0] # 가장 최신 것 하나 선택
            break
    
    if not selected_item:
        selected_item = new_items[0]

    url = selected_item["link"]
    title = selected_item["title"]
    dept = selected_item["dept"]
    
    logger.info(f"선정된 주제: [{dept}] {title}")
    logger.info(f"URL: {url}")

    # 3. 크롤링
    scraper = ContentScraper()
    scraped_data = scraper.scrape(url)
    
    if not scraped_data:
        logger.error(f"크롤링 실패: {url}")
        return

    # 4. 블로그 글 작성 (AI)
    writer = BlogWriter(api_key=gemini_api_key, model=config["gemini"]["model"])
    poster = BloggerPoster()
    recent_posts = poster.list_posts(max_results=5)
    
    logger.info("AI 블로그 글 생성 중...")
    result = writer.write_post(
        title=title,
        content=scraped_data["content"],
        dept=dept,
        url=url,
        images=scraped_data["images"],
        recent_posts=recent_posts
    )

    if not result or result == 'QUOTA_EXHAUSTED':
        logger.error("AI 글 작성 실패")
        return

    # 5. 포스팅 (Blogger)
    logger.info("Blogger 포스팅 진행...")
    
    # 라벨 구성
    if dept == "서울시 정책뉴스":
        labels = result["tags"] + ["2. 서울시 정책 뉴스"]
    else:
        labels = result["tags"] + ["1. 국가 정부 자료"]
        if dept not in labels:
            labels.append(dept)

    post_url = poster.post(
        title=result["blog_title"],
        content=result["blog_content"],
        labels=labels,
        meta_description=result["meta_description"],
        dept=dept
    )

    if post_url:
        logger.info(f"✅ 포스팅 성공: {post_url}")
        
        # seen.json에 추가
        seen.add(url)
        with open("seen.json", "w", encoding="utf-8") as f:
            json.dump(list(seen), f, indent=2)
    else:
        logger.error("❌ 포스팅 실패")

if __name__ == "__main__":
    main()
