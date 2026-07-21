
import logging
import json
import os
from blogger_poster import BloggerPoster
from storage_manager import LocalStorageManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_and_prepare():
    # 1. Blogger에서 서울시 뉴스 삭제
    poster = BloggerPoster() # config.json 기반 초기화
    logger.info("서울시 정책 뉴스 게시물 검색 중...")
    
    posts = poster.list_posts(max_results=50) # 넉넉하게 50개
    target_label = "2. 서울시 정책 뉴스"
    
    to_delete = []
    for post in posts:
        labels = post.get('labels', [])
        if target_label in labels:
            to_delete.append((post['id'], post['title']))
            
    if not to_delete:
        logger.info("삭제할 서울시 정책 뉴스 게시물이 없습니다.")
    else:
        logger.info(f"총 {len(to_delete)}개의 게시물을 삭제합니다.")
        for p_id, p_title in to_delete:
            success = poster.delete_post(p_id)
            if success:
                logger.info(f"✅ 삭제 성공: {p_title}")
            else:
                logger.error(f"❌ 삭제 실패: {p_title}")

    # 2. seen.json에서 서울시 관련 링크 제거
    # config.json에서 seen.json 파일명 확인
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    data_file = config["settings"]["data_file"]
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8-sig") as f:
            seen_list = json.load(f)
            
        original_count = len(seen_list)
        # seoul.go.kr 이나 mediahub.seoul.go.kr이 포함된 링크 제거
        filtered_seen = [url for url in seen_list if "seoul.go.kr" not in url]
        
        removed_count = original_count - len(filtered_seen)
        
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(filtered_seen, f, ensure_ascii=False, indent=2)
            
        logger.info(f"seen.json 정리 완료: {removed_count}개 링크 제거됨 (남은 항목: {len(filtered_seen)}개)")
    else:
        logger.warning("seen.json 파일이 없어 정리를 건너뜁니다.")

if __name__ == "__main__":
    cleanup_and_prepare()
