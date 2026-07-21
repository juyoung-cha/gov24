import json
import logging
import time
from blogger_poster import BloggerPoster

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def draft_automated_posts():
    """
    기존에 구글 블로거에 발행된 게시물들을 조회하여,
    '비공개(임시저장)' 상태로 돌려놓는 스크립트입니다.
    애드센스 승인을 받기 전, 양산형 글들을 숨기기 위해 사용합니다.
    """
    logger.info("="*60)
    logger.info("기존 포스팅 비공개(임시저장) 스크립트 시작")
    logger.info("="*60)

    # 1. 설정 로드
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        blogger_id = config['blogger']['blog_id']
    except Exception as e:
        logger.error(f"설정 파일(config.json) 로드 및 파싱 오류: {e}")
        return

    # 2. BloggerPoster 초기화
    try:
        poster = BloggerPoster(blog_id=blogger_id)
        logger.info(f"블로그 ID: {blogger_id} 에 연결되었습니다.")
    except Exception as e:
        logger.error(f"Blogger 인증 오류: {e}")
        return

    # 3. 최근 게시물 최대 100개 가져오기
    # 주의: 한 번에 너무 많은 게시물을 처리하면 Google API 제한에 걸릴 수 있으므로 100개씩 처리
    max_to_draft = 100
    try:
        posts = poster.list_posts(max_results=max_to_draft)
    except Exception as e:
        logger.error(f"게시물 목록을 가져오지 못했습니다: {e}")
        return

    if not posts:
        logger.info("비공개 처리할 발행된 게시물이 없습니다.")
        return

    logger.info(f"총 {len(posts)}개의 발행된 게시물을 찾았습니다. 비공개 처리를 시작합니다.")

    drafted_count = 0
    failed_count = 0

    for idx, post in enumerate(posts, 1):
        post_id = post.get('id')
        post_title = post.get('title', '제목 없음')
        
        # 특정 라벨이 붙은 오리지널 콘텐츠('3. 오리지널 콘텐츠')는 숨기지 않도록 예외 처리
        labels = post.get('labels', [])
        if "3. 오리지널 콘텐츠" in labels:
            logger.info(f"⏩ 통과 (수동/오리지널 글): [{idx}/{len(posts)}] {post_title[:30]}")
            continue

        try:
            logger.info(f"🛠️ 비공개 처리 중... [{idx}/{len(posts)}] {post_title[:30]}")
            
            # Blogger API v3 의 revert 메소드 활용하여 Draft 상태로 되돌리기
            poster.service.posts().revert(blogId=poster.blog_id, postId=post_id).execute()
            
            drafted_count += 1
            logger.info(f"✅ 비공개 성공")
            
            # API 제한(Rate limit) 방지를 위해 2초 대기
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ 비공개 실패 (ID: {post_id}): {e}")
            failed_count += 1
            time.sleep(5)  # 에러 발생 시 조금 더 깁게 대기

    logger.info("="*60)
    logger.info(f"작업 완료! 비공개 성공: {drafted_count}개 | 실패: {failed_count}개")
    logger.info("="*60)

if __name__ == "__main__":
    draft_automated_posts()
