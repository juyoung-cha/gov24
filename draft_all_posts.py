import json
import logging
import time
from blogger_poster import BloggerPoster

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def draft_all_automated_posts():
    logger.info("="*60)
    logger.info("남은 400여 개의 전체 글 비공개(임시저장) 스크립트 시작")
    logger.info("="*60)

    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        blogger_id = config['blogger']['blog_id']
        poster = BloggerPoster(blog_id=blogger_id)
    except Exception as e:
        logger.error(f"초기화 오류: {e}")
        return

    drafted_count = 0
    failed_count = 0
    page_token = None
    
    # 3월 21일자 오리지널 글의 중복 방지 (오늘 날짜 제외용 설정 가능)
    today_str = "2026-03-21"

    while True:
        try:
            req = poster.service.posts().list(
                blogId=blogger_id, 
                maxResults=100, 
                status='LIVE',
                pageToken=page_token,
                fetchBodies=False
            )
            res = req.execute()
            posts = res.get('items', [])
            
            if not posts:
                break
                
            for post in posts:
                post_id = post.get('id')
                post_title = post.get('title', '제목 없음')
                published_date = post.get('published', '')[:10]
                labels = post.get('labels', [])
                
                # 오늘(3/21) 새로 발행한 "오리지널 글 5개"는 절대 건드리지 않음
                if "3. 오리지널 콘텐츠" in labels and published_date == today_str:
                    logger.info(f"⏩ 통과 (오늘 올린 오리지널): {post_title[:20]}")
                    continue
                
                # 3월 1일에 중복으로 올라갔던 옛날 오리지널 글이나, 자동화 양산 글은 전부 숨김
                try:
                    poster.service.posts().revert(blogId=blogger_id, postId=post_id).execute()
                    drafted_count += 1
                    logger.info(f"✅ 비공개 성공 [{drafted_count}]: {post_title[:20]} ({published_date})")
                    time.sleep(2)  # 구글 429 에러 방지용 2초 휴식
                except Exception as e:
                    logger.error(f"❌ 비공개 실패: {e}")
                    failed_count += 1
                    time.sleep(5)
            
            page_token = res.get('nextPageToken')
            if not page_token:
                logger.info("더 이상 숨길 게시물이 없습니다.")
                break
                
        except Exception as e:
            logger.error(f"게시물 목록 조회 실패: {e}")
            break

    logger.info("="*60)
    logger.info(f"대청소 완료! 총 비공개 전환: {drafted_count}개 | 실패: {failed_count}개")
    logger.info("="*60)

if __name__ == "__main__":
    draft_all_automated_posts()
