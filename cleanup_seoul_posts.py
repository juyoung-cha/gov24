import json
import logging
import os
from blogger_poster import BloggerPoster

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def cleanup():
    # 1. 설정 로드
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    blogger_id = config['blogger']['blog_id']
    logger.info(f"블로그 ID: {blogger_id} 정리 시작")
    
    poster = BloggerPoster(blog_id=blogger_id)
    
    # 2. 게시물 목록 조회
    # (최근 글 위주로 조회하되, 서울시 뉴스는 개수가 적어 100개면 충분)
    posts = poster.list_posts(max_results=100)
    logger.info(f"전체 조회된 게시물 수: {len(posts)}")
    
    target_label = "2. 서울시 정책 뉴스"
    deleted_count = 0
    
    for post in posts:
        labels = post.get('labels', [])
        if target_label in labels:
            logger.info(f"삭제 대상 발견: {post['title']} (ID: {post['id']})")
            if poster.delete_post(post['id']):
                deleted_count += 1
    
    logger.info(f"총 {deleted_count}개의 서울시 정책 뉴스 게시물 삭제 완료.")
    
    # 3. seen.json 정리
    seen_file = "seen.json"
    if os.path.exists(seen_file):
        with open(seen_file, 'r', encoding='utf-8') as f:
            seen_urls = json.load(f)
        
        # 'mediahub.seoul.go.kr' 또는 'onseoul.net' 포함된 URL 제거
        original_count = len(seen_urls)
        filtered_urls = [url for url in seen_urls if "seoul.go.kr" not in url and "onseoul.net" not in url]
        
        if original_count != len(filtered_urls):
            with open(seen_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_urls, f, indent=2, ensure_ascii=False)
            logger.info(f"seen.json에서 서울 관련 URL {original_count - len(filtered_urls)}개 제거 완료.")

if __name__ == "__main__":
    cleanup()
