"""
정부 정책 자동 블로그 포스팅 시스템
메인 실행 로직
"""
import json
from difflib import SequenceMatcher
import logging
import os
from typing import Dict
from datetime import datetime, timezone, timedelta
import locale
import time

from rss_collector import RSSCollector
from content_scraper import ContentScraper
from blog_writer import BlogWriter
from blogger_poster import BloggerPoster
from storage_manager import StorageManager, LocalStorageManager

# .env 파일에서 환경변수 로드 (로컬 실행 시)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv 미설치 시 환경변수 직접 설정 필요

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
        gemini_api_key = os.getenv("GEMINI_API_KEY") or config["gemini"].get("api_key")
        blogger_blog_id = os.getenv("BLOGGER_BLOG_ID", config.get("blogger", {}).get("blog_id"))
        gcs_bucket = os.getenv("GCS_BUCKET", config.get("gcs", {}).get("bucket_name"))
        
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY 환경변수를 설정하세요. (예: set GEMINI_API_KEY=AIza...)")
        
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
        blog_writer = BlogWriter()
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
        
        logger.info(f"Step 2.2: 필터링 완료 (서울시: {len(seoul_items)}개, 기타: {len(other_items)}개)")
        
        # [FIX] 공정 배분: 서울시와 정부정책에 각각 최소 슬롯 보장 (starvation 방지)
        max_posts = config["settings"].get("max_posts_per_run", 10)
        
        if len(seoul_items) + len(other_items) > max_posts:
            # 양쪽 모두 글이 있으면 공정하게 나눔
            if seoul_items and other_items:
                # 최소 1개씩 보장, 나머지는 교대 배분
                other_quota = max(1, max_posts // 2)  # 정부정책 최소 절반
                seoul_quota = max_posts - other_quota
                
                selected_seoul = seoul_items[:seoul_quota]
                selected_other = other_items[:other_quota]
                logger.info(f"⚖️ 공정 배분: 서울시 {len(selected_seoul)}개, 정부정책 {len(selected_other)}개 (max: {max_posts})")
            elif seoul_items:
                selected_seoul = seoul_items[:max_posts]
                selected_other = []
            else:
                selected_seoul = []
                selected_other = other_items[:max_posts]
        else:
            selected_seoul = seoul_items
            selected_other = other_items
        
        # 교대 배치: 서울시 → 정부 → 서울시 → 정부 (다양한 포스팅)
        new_items = []
        for i in range(max(len(selected_seoul), len(selected_other))):
            if i < len(selected_other):
                new_items.append(selected_other[i])
            if i < len(selected_seoul):
                new_items.append(selected_seoul[i])
        
        logger.info(f"Step 2.3: 최종 처리 대상: {len(new_items)}개")
        
        # 3. 각 항목 처리
        posted_count = 0
        failed_count = 0
        consecutive_quota_fails = 0  # [NEW] 연속 할당량 초과 카운터
        MAX_CONSECUTIVE_QUOTA_FAILS = 3  # [NEW] 연속 3회 초과 시 조기 중단
        
        # [SEO-5] 내부 링크용 최근 포스트 조회
        recent_posts = []
        recent_items = []
        try:
            recent_items = blogger_poster.list_posts(20)
            for rp in recent_items:
                recent_posts.append({
                    'title': rp.get('title', ''),
                    'url': rp.get('url', '')
                })
            logger.info(f"📎 내부 링크용 최근 포스트 {len(recent_posts)}개 조회 완료")
        except Exception as e:
            logger.warning(f"⚠️ 최근 포스트 조회 실패 (계속 진행): {e}")
        
        # [NEW] 오늘 KST 기준으로 이미 블로그에 발행된 포스트 수 파악하여 하루 제한 보장
        kst = timezone(timedelta(hours=9))
        today_kst_str = datetime.now(kst).strftime("%Y-%m-%d")
        
        today_published_count = 0
        for rp in recent_items:
            pub_time_str = rp.get('published', '')
            if pub_time_str.startswith(today_kst_str):
                today_published_count += 1
                
        daily_limit = config["settings"].get("max_posts_per_run", 2)
        remaining_slots = max(0, daily_limit - today_published_count)
        logger.info(f"오늘({today_kst_str}) 이미 게시된 글: {today_published_count}개 / 하루 제한: {daily_limit}개")
        logger.info(f"오늘 추가로 발행 가능한 글 슬롯: {remaining_slots}개")
        
        if remaining_slots <= 0:
            logger.info("오늘 허용된 포스팅 한도(2개)를 이미 채웠습니다. 포스팅 작업을 진행하지 않고 조기 종료합니다.")
            return {
                "status": "success",
                "posted": 0,
                "failed": 0,
                "message": f"오늘 한도({daily_limit}개) 이미 달성으로 조기 종료"
            }
        
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
                
                # [NEW] 기사 유용성 평가 (Gemini 필터링)
                min_score = config["settings"].get("min_relevance_score", 7)
                eval_result = blog_writer.evaluate_item_relevance(item["title"], scraped["content"])
                if eval_result["score"] < min_score:
                    logger.info(f"⏭️ 필터 적용 - 유용성 평가 점수 미달로 건너뜀 (점수: {eval_result['score']}/{min_score}, 이유: {eval_result['reason']})")
                    # 이미 확인한 것으로 간주하여 중복 처리 방지(seen에 추가)
                    seen.add(item["link"])
                    try:
                        storage_mgr.save_seen(seen)
                    except Exception as save_err:
                        logger.warning(f"⚠️ seen.json 저장 실패: {save_err}")
                    continue
                
                logger.info(f"🎯 필터 통과 (점수: {eval_result['score']}/{min_score}, 이유: {eval_result['reason']})")
                
                # 3-2. 블로그 글 작성 (Gemini) — SEO v2: recent_posts 전달
                blog_post = blog_writer.write_post(
                    title=item["title"],
                    content=scraped["content"],
                    dept=item["dept"],
                    url=item["link"],
                    images=scraped.get("images"),
                    recent_posts=recent_posts  # [SEO-5] 내부 링크용
                )
                
                # [NEW] Gemini API 할당량 초과 circuit breaker
                if blog_post == 'QUOTA_EXHAUSTED':
                    consecutive_quota_fails += 1
                    failed_count += 1
                    logger.warning(f"🚫 Gemini 할당량 초과 연속 {consecutive_quota_fails}/{MAX_CONSECUTIVE_QUOTA_FAILS}회")
                    if consecutive_quota_fails >= MAX_CONSECUTIVE_QUOTA_FAILS:
                        logger.error("🛑 Gemini API 할당량 연속 초과 — 나머지 큐 중단합니다.")
                        break
                    continue
                
                if not blog_post:
                    logger.warning("블로그 글 작성 실패. 건너뜁니다.")
                    failed_count += 1
                    continue
                
                # 성공 시 연속 실패 카운터 리셋
                consecutive_quota_fails = 0
                
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
                    all_labels = ["2. 서울시 정책 뉴스"] + blog_post["tags"] + date_labels
                else:
                    all_labels = ["1. 국가 정부 자료"] + blog_post["tags"] + date_labels
                    if item["dept"] not in all_labels:
                        all_labels.append(item["dept"])
                
                logger.info(f"📌 전송할 라벨: {all_labels}")
                
                # [중복 방지] 블로그에 이미 유사한 제목의 글이 있는지 확인
                is_duplicate = False
                for rp in recent_posts:
                    similarity = SequenceMatcher(None, blog_post["title"], rp['title']).ratio()
                    if similarity > 0.6:
                        logger.warning(f"⚠️ 중복 감지! 유사도 {similarity:.1%}: '{blog_post['title'][:30]}' ↔ '{rp['title'][:30]}'")
                        is_duplicate = True
                        break
                
                if is_duplicate:
                    logger.info("⏭️ 이미 유사한 글이 존재합니다. 건너뜁니다.")
                    seen.add(item["link"])  # 중복이므로 seen에 추가하여 재처리 방지
                    continue
                
                                # 3-3. Blogger 포스팅 (재시도 로직 포함, SEO v2)
                post_url = None
                max_retries = 3
                retry_delay = 60  # 초 (단기 할당량 에러 차단 및 지수 백오프 대비)
                blogger_quota_exhausted = False
                
                for attempt in range(max_retries):
                    if attempt > 0:
                        logger.info(f"재시도 {attempt}/{max_retries-1}... ({retry_delay}초 대기)")
                        time.sleep(retry_delay)
                    
                    post_url = blogger_poster.post(
                        title=blog_post["title"],
                        content=blog_post["content"],
                        labels=all_labels,
                        is_draft=False,
                        meta_description=blog_post.get("meta_description", ""),  # [SEO-3]
                        dept=item["dept"]  # [SEO-3]
                    )
                    
                    if post_url == 'RATE_LIMIT_EXHAUSTED':
                        logger.error("🛑 Blogger API 일일 할당량 초과 (429) 감지 — 작업을 즉시 중단합니다.")
                        blogger_quota_exhausted = True
                        break
                    
                    if post_url:
                        logger.info(f"✅ 포스팅 성공: {post_url}")
                        seen.add(item["link"])  # 성공 시에만 seen에 추가
                        posted_count += 1
                        
                        # [중복 방지] 즉시 seen.json 저장 (동시 실행 시 중복 포스팅 방지)
                        try:
                            storage_mgr.save_seen(seen)
                            logger.info("💾 seen.json 즉시 저장 완료")
                        except Exception as save_err:
                            logger.warning(f"⚠️ seen.json 즉시 저장 실패 (최종 저장에서 재시도): {save_err}")
                        
                        # [NEW] 오늘 남은 발행 슬롯을 모두 채웠는지 체크
                        if posted_count >= remaining_slots:
                            logger.info(f"오늘 허용된 추가 발행 슬롯({remaining_slots}개)을 모두 채웠습니다. 남은 대기열 처리를 중단합니다.")
                            break
                        
                        # [SEO-4] Sitemap ping — Google에 새 콘텐츠 알림
                        try:
                            import requests
                            sitemap_url = f"https://story0people.blogspot.com/sitemap.xml"
                            ping_url = f"https://www.google.com/ping?sitemap={sitemap_url}"
                            requests.get(ping_url, timeout=10)
                            logger.info(f"📡 Sitemap ping 성공: {ping_url}")
                        except Exception as ping_err:
                            logger.warning(f"⚠️ Sitemap ping 실패 (계속 진행): {ping_err}")
                        
                        # [SEO-5] 새로 올린 글도 내부 링크 후보에 추가
                        recent_posts.insert(0, {
                            'title': blog_post["title"],
                            'url': post_url
                        })
                        if len(recent_posts) > 5:
                            recent_posts = recent_posts[:5]
                        
                        break
                    elif attempt < max_retries - 1:
                        logger.warning(f"포스팅 실패, 재시도합니다...")
                else:
                    logger.error("포스팅 최종 실패 (재시도 횟수 초과)")
                    failed_count += 1
                
                if blogger_quota_exhausted:
                    break
                
                # [SEO-FIX] 포스팅 간 랜덤 대기 (3~8분) — 자연스러운 게시 패턴으로 스팸 판정 회피
                if idx < len(new_items):  # 마지막 항목이 아니면
                    import random
                    wait_seconds = random.randint(180, 480)  # 3분~8분
                    logger.info(f"⏳ 다음 포스팅까지 {wait_seconds//60}분 {wait_seconds%60}초 대기...")
                    time.sleep(wait_seconds)
            
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
