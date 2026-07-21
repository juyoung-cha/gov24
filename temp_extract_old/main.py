"""
정부 정책 자동 블로그 포스팅 시스템
메인 실행 로직
"""
import json
import logging
import os
from typing import Dict
from datetime import datetime
import locale
import time

from rss_collector import RSSCollector
from content_scraper import ContentScraper
from blog_writer import BlogWriter
from blogger_poster import BloggerPoster
from storage_manager import StorageManager, LocalStorageManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config() -> Dict:
    """설정 파일 로드"""
    config_file = os.getenv("CONFIG_FILE", "config.json")
    
    if not os.path.exists(config_file):
        logger.error(f"설정 파일이 없습니다: {config_file}")
        raise FileNotFoundError(f"{config_file} 파일이 필요합니다.")
    
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)


def run_auto_blog(request=None):
    """
    메인 실행 함수 (Cloud Functions 진입점)
    
    Args:
        request: Flask request (Cloud Functions용, 로컬 실행 시 None)
    """
    logger.info("=" * 60)
    logger.info("정부 정책 자동 블로그 포스팅 시작")
    logger.info("=" * 60)
    
    try:
        # 설정 로드
        config = load_config()
        
        # 환경 변수에서 Override 가능
        gemini_api_key = os.getenv("GEMINI_API_KEY", config["gemini"]["api_key"])
        blogger_blog_id = os.getenv("BLOGGER_BLOG_ID", config.get("blogger", {}).get("blog_id"))
        gcs_bucket = os.getenv("GCS_BUCKET", config.get("gcs", {}).get("bucket_name"))
        
        logger.info(f"API Key 확인: {gemini_api_key[:10]}... (길이: {len(gemini_api_key)})")
        
        # 스토리지 매니저 초기화 (GCS 사용 가능하면 GCS, 아니면 로컬)
        storage_mgr = None
        effective_gcs_bucket = gcs_bucket
        
        if gcs_bucket:
            try:
                storage_mgr = StorageManager(gcs_bucket)
                logger.info(f"GCS 스토리지 사용 중: {gcs_bucket}")
            except Exception as e:
                logger.warning(f"⚠️ GCS 초기화 실패 (인증 오류 등): {e}")
                logger.info("💡 로컬 스토리지로 전환하여 계속 진행합니다.")
                effective_gcs_bucket = None # 인증 실패 시 BloggerPoster에서도 GCS 사용 안 하도록 함
        
        if not storage_mgr:
            storage_mgr = LocalStorageManager(config["settings"]["data_file"])
        
        # 모듈 초기화
        rss_collector = RSSCollector(timeout=config["settings"]["request_timeout"])
        content_scraper = ContentScraper(timeout=config["settings"]["request_timeout"])
        blog_writer = BlogWriter(gemini_api_key, config["gemini"]["model"])
        blogger_poster = BloggerPoster(blog_id=blogger_blog_id, gcs_bucket=effective_gcs_bucket)
        
        # 1. RSS 수집
        logger.info("Step 1: RSS 피드 수집")
        all_items = rss_collector.fetch_all(config["rss_feeds"])
        
        if not all_items:
            logger.info("수집된 항목이 없습니다. 종료합니다.")
            return {"status": "success", "message": "수집된 항목 없음"}
        
        # 2. 새 글 필터링
        logger.info("Step 2: 새 글 필터링")
        seen = storage_mgr.load_seen()
        new_items = rss_collector.filter_new_items(all_items, seen)
        
        if not new_items:
            logger.info("새 글이 없습니다. 종료합니다.")
            return {"status": "success", "message": "새 글 없음"}
        
        logger.info(f"새 글 {len(new_items)}개 발견!")
        
        # [NEW] 서울시 정책뉴스 2025년 6월 이후 필터링 및 우선순위 조정
        filtered_items = []
        target_date_filter = datetime(2026, 1, 1)
        
        logger.info(f"Step 2.1: 서울시 정책뉴스 필터링 및 우선순위 조정 시작 (전체 새 글: {len(new_items)}개)")
        
        seoul_items = []
        other_items = []
        
        for item in new_items:
            if item.get("dept") == "서울시 정책뉴스":
                date_str = item.get("date")
                if not date_str:
                    logger.warning(f"⏭️ 날짜 정보 없음, 건너뜀: {item['title']}")
                    continue
                    
                try:
                    # 다양한 날짜 형식 파싱 시도 (main.py의 파싱 로직 그대로 유지)
                    dt = None
                    try:
                        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                    
                    if not dt:
                        try:
                            dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
                        except:
                            pass
                    
                    if not dt:
                        try:
                            # 2026.02.07. or 2026.02.07
                            clean_date_str = date_str.rstrip(".")
                            dt = datetime.strptime(clean_date_str, "%Y.%m.%d")
                        except:
                            pass

                    if not dt:
                        try:
                            from email.utils import parsedate_to_datetime
                            dt = parsedate_to_datetime(date_str).replace(tzinfo=None)
                        except:
                            pass
                    
                    if dt and dt >= target_date_filter:
                        seoul_items.append(item)
                    else:
                        logger.info(f"⏭️ 2026년 이전 데이터 제외 ({date_str}): {item['title']}")
                except Exception as e:
                    logger.warning(f"⚠️ 날짜 파싱 오류 ({date_str}), 일단 포함: {e}")
                    seoul_items.append(item)
            else:
                other_items.append(item)
        
        # 서울시 뉴스를 앞에 배치하여 우선적으로 처리되게 함
        new_items = seoul_items + other_items
        logger.info(f"Step 2.2: 필터링 완료 (서울시: {len(seoul_items)}개, 기타: {len(other_items)}개)")
        
        # 최대 포스팅 개수 제한 (필터링 및 정렬 후에 적용)
        max_posts = config["settings"].get("max_posts_per_run", 10)
        if len(new_items) > max_posts:
            logger.info(f"⚠️ 한 번에 최대 {max_posts}개만 처리합니다. (전체: {len(new_items)}개)")
            new_items = new_items[:max_posts]
            
        # [FIX] 최신 뉴스가 블로그 상단에 오도록 포스팅 순서 뒤집기 (가장 최신 기사를 마지막에 포스팅)
        # 단, 서울시 뉴스는 항상 최상단에 오도록 보장하기 위해 뒤집기 후에 맨 앞으로 이동
        new_items.reverse()
        
        # 서울시 항목을 다시 추출하여 맨 앞으로 배치
        seoul_only = [item for item in new_items if item.get("dept") == "서울시 정책뉴스"]
        others_only = [item for item in new_items if item.get("dept") != "서울시 정책뉴스"]
        new_items = seoul_only + others_only
        
        logger.info(f"Step 2.3: 최종 처리 대상: {len(new_items)}개")
        
        # 3. 각 항목 처리
        posted_count = 0
        failed_count = 0
        
        for idx, item in enumerate(new_items, 1):
            logger.info("-" * 60)
            logger.info(f"처리 중 ({idx}/{len(new_items)}): {item['title'][:50]}...")
            
            try:
                # 3-1. 원문 크롤링
                scraped = content_scraper.scrape(item["link"])
                if not scraped:
                    logger.warning("원문 크롤링 실패. 건너뜁니다.")
                    failed_count += 1
                    continue
                
                # 3-2. 블로그 글 작성 (Gemini)
                blog_post = blog_writer.write_post(
                    title=item["title"],
                    content=scraped["content"],
                    dept=item["dept"],
                    url=item["link"],
                    images=scraped.get("images")
                )
                
                if not blog_post:
                    logger.warning("블로그 글 작성 실패. 건너뜁니다.")
                    failed_count += 1
                    continue
                
                # 날짜 라벨 생성 (상세 페이지의 정확한 발행일 사용 시도)
                date_labels = []
                pub_date_str = scraped.get("publish_date") or item.get("date")
                logger.info(f"🔍 사용할 발행일 정보: {pub_date_str}")
                
                if pub_date_str:
                    try:
                        dt = None
                        # 상세 페이지 형식: "2026.04.03. 11:36"
                        try:
                            clean_date = pub_date_str.split(" ")[0].rstrip(".")
                            dt = datetime.strptime(clean_date, "%Y.%m.%d")
                        except:
                            pass
                        
                        if not dt:
                            # RSS 형식: "Mon, 03 Feb 2026 10:00:00 +0900"
                            try:
                                dt = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
                            except:
                                pass
                        
                        if not dt:
                            # 기타 형식: "2026-02-05"
                            try:
                                dt = datetime.strptime(pub_date_str[:10], "%Y-%m-%d")
                            except:
                                pass
                        
                        # 형식 2: "2026-02-03T10:00:00+09:00" (ISO 8601)
                        if not dt:
                            try:
                                dt = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                            except:
                                pass
                        
                        # 형식 3: "2026-02-03"
                        if not dt:
                            try:
                                dt = datetime.strptime(pub_date_str[:10], "%Y-%m-%d")
                            except:
                                pass
                        
                        if dt:
                            date_labels = [
                                f"{dt.year}년",
                                f"{dt.year}년 {dt.month}월",
                                f"{dt.year}년 {dt.month}월 {dt.day}일"
                            ]
                            logger.info(f"날짜 라벨 생성: {date_labels}")
                    except Exception as e:
                        logger.warning(f"날짜 파싱 실패: {e}")
                
                # [FIX] 사용자 요청에 따른 카테고리(라벨) 체계 개편
                if item["dept"] == "서울시 정책뉴스":
                    # 서울시 뉴스는 "2. 서울시 정책 뉴스" 전용 라벨만 부여
                    all_labels = ["2. 서울시 정책 뉴스"] + blog_post["tags"] + date_labels
                else:
                    # 일반 부처 뉴스는 "1. 국가 정부 자료" 라벨만 부여
                    all_labels = ["1. 국가 정부 자료"] + blog_post["tags"] + date_labels
                    # 부처명 라벨 추가
                    if item["dept"] not in all_labels:
                        all_labels.append(item["dept"])
                
                logger.info(f"📌 전송할 라벨: {all_labels}")
                
                                # 3-3. Blogger 포스팅 (재시도 로직 포함)
                post_url = None
                max_retries = 3
                retry_delay = 3  # 초
                
                for attempt in range(max_retries):
                    if attempt > 0:
                        logger.info(f"재시도 {attempt}/{max_retries-1}... ({retry_delay}초 대기)")
                        time.sleep(retry_delay)
                    
                    post_url = blogger_poster.post(
                        title=blog_post["blog_title"],
                        content=blog_post["blog_content"],
                        labels=all_labels,
                        is_draft=False  # 바로 게시
                    )
                    
                    if post_url:
                        logger.info(f"✅ 포스팅 성공: {post_url}")
                        seen.add(item["link"])  # 성공 시에만 seen에 추가
                        posted_count += 1
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(f"포스팅 실패, 재시도합니다...")
                else:
                    logger.error("포스팅 최종 실패 (재시도 횟수 초과)")
                    failed_count += 1
                
                # Rate Limiting 방지: 각 포스팅 사이 2초 대기
                if idx < len(new_items):  # 마지막 항목이 아니면
                    time.sleep(2)
            
            except Exception as e:
                logger.error(f"항목 처리 오류: {str(e)}", exc_info=True)
                failed_count += 1
                continue
        
        # 4. seen.json 저장
        logger.info("Step 4: seen.json 저장")
        storage_mgr.save_seen(seen)
        
        logger.info("=" * 60)
        logger.info(f"작업 완료: 성공 {posted_count}개, 실패 {failed_count}개")
        logger.info("=" * 60)
        
        return {
            "status": "success",
            "posted": posted_count,
            "failed": failed_count,
            "total_new": len(new_items)
        }
    
    except Exception as e:
        logger.error(f"프로그램 실행 오류: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    # 로컬 실행
    result = run_auto_blog()
    print(json.dumps(result, ensure_ascii=False, indent=2))
