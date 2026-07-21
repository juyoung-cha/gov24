import json
import logging
import os
import time
import random
from dotenv import load_dotenv
from rss_collector import RSSCollector
from content_scraper import ContentScraper
from blog_writer import BlogWriter
from blogger_poster import BloggerPoster
from storage_manager import StorageManager, LocalStorageManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mass_publish_v3.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MassPublisherV3")

def main():
    load_dotenv()
    
    # 1. 설정 로드
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    gemini_api_key = os.getenv("GEMINI_API_KEY") or config["gemini"].get("api_key")
    if not gemini_api_key:
        logger.error("GEMINI_API_KEY가 설정되지 않았습니다.")
        return

    # 2. 컴포넌트 초기화
    storage = LocalStorageManager(config["settings"]["data_file"])
    seen_links = list(storage.load_seen())
    collector = RSSCollector()
    scraper = ContentScraper()
    writer = BlogWriter(api_key=gemini_api_key, model=config["gemini"]["model"])
    poster = BloggerPoster()

    # 3. 뉴스 수집
    logger.info("모든 채널에서 최신 뉴스 수집 중...")
    rss_feeds = config["rss_feeds"]
    all_news = collector.fetch_all(rss_feeds)
    
    # 새 글만 필터링
    new_news = [item for item in all_news if item["link"] not in seen_links]
    logger.info(f"수집된 전체 뉴스: {len(all_news)}개, 새 뉴스: {len(new_news)}개")

    if not new_news:
        logger.info("새로운 뉴스가 없습니다. 종료합니다.")
        return

    # 4. 고품질 포스팅 시작 (최대 2개)
    max_posts = 2
    posted_count = 0
    
    # 섞어서 다양하게 발행
    random.shuffle(new_news)
    
    for item in new_news:
        if posted_count >= max_posts:
            break
            
        logger.info(f"[{posted_count + 1}/{max_posts}] 처리 중: {item['title']}")
        
        try:
            # 원문 크롤링
            scraped_data = scraper.scrape(item["link"])
            if not scraped_data or len(scraped_data["content"]) < 300:
                logger.warning(f"콘텐츠가 너무 적어 건너뜁니다: {item['link']}")
                continue

            # 최근 포스트 로드 (내부 링크용)
            recent_posts = poster.list_posts(max_results=10)
            
            # AI 글 생성
            result = writer.write_post(
                title=item["title"],
                content=scraped_data["content"],
                dept=item["dept"],
                url=item["link"],
                images=scraped_data["images"],
                recent_posts=recent_posts
            )

            if not result or result == 'QUOTA_EXHAUSTED':
                logger.error("AI 글 생성 실패 (할당량 초과 또는 오류)")
                if result == 'QUOTA_EXHAUSTED':
                    break # 할당량 초과 시 전체 중단
                continue

            # 포스팅
            post_url = poster.post(
                title=result["blog_title"],
                content=result["blog_content"],
                labels=result["tags"] + [f"1. {item['dept']}" if "뉴스" not in item['dept'] else item['dept']],
                meta_description=result["meta_description"],
                dept=item["dept"]
            )

            if post_url:
                logger.info(f"✅ 포스팅 성공: {post_url}")
                posted_count += 1
                
                # seen에 기록
                seen_links.append(item["link"])
                storage.save_seen(seen_links)
                
                # 다음 포스팅까지 대기 (3~5분 사이 랜덤) - 자연스럽게 보이게 함
                if posted_count < max_posts:
                    wait_time = random.randint(180, 300)
                    logger.info(f"다음 포스팅까지 {wait_time}초 대기 중...")
                    time.sleep(wait_time)
            else:
                logger.error("❌ 포스팅 실패")

        except Exception as e:
            logger.error(f"처리 중 예상치 못한 오류 발생: {str(e)}")
            continue

    logger.info(f"대량 포스팅 완료! 총 {posted_count}개의 고품질 글이 발행되었습니다.")

if __name__ == "__main__":
    main()
