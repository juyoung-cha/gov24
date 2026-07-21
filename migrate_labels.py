import logging
import time
from blogger_poster import BloggerPoster
from typing import List

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def migrate_labels():
    poster = BloggerPoster()
    
    # 1. 모든 게시물 가져오기 (충분히 크게 설정)
    logger.info("기존 게시물 목록을 가져오는 중...")
    posts = poster.list_posts(max_results=500)
    logger.info(f"총 {len(posts)}개의 게시물을 찾았습니다.")
    
    updated_count = 0
    skipped_count = 0
    
    for i, post in enumerate(posts):
        post_id = post['id']
        title = post['title']
        old_labels = post.get('labels', [])
        
        new_labels = []
        changed = False
        
        for label in old_labels:
            processed_label = label
            
            # 카테고리 변환
            if label == "정부 공개 자료":
                processed_label = "1. 국가 정부 자료"
                changed = True
            elif label == "서울시 정책뉴스":
                processed_label = "2. 서울시 정책 뉴스"
                changed = True
            
            # 날짜 형식 변환 (예: 2026년-02월 -> 2026년 2월)
            if "년-" in label and "월" in label:
                processed_label = label.replace("-", " ")
                changed = True
            # 날짜 형식 변환 (예: 2026-02-06 -> 2026년 2월 6일)
            elif label.count("-") == 2 and len(label) >= 10:
                parts = label.split("-")
                if len(parts) == 3 and parts[0].isdigit():
                    processed_label = f"{parts[0]}년 {int(parts[1])}월 {int(parts[2])}일"
                    changed = True
            
            if processed_label not in new_labels:
                new_labels.append(processed_label)
        
        # 중복 제거 및 정렬
        new_labels = sorted(list(set(new_labels)))
        
        if changed or set(old_labels) != set(new_labels):
            logger.info(f"[{i+1}/{len(posts)}] 수정 중: {title[:30]}...")
            logger.info(f"   - 기존: {old_labels}")
            logger.info(f"   - 변경: {new_labels}")
            
            success = poster.update_post(
                post_id=post_id,
                title=title,
                content=post['content'],
                labels=new_labels
            )
            
            if success:
                updated_count += 1
                # 속도 조절 (API 할당량 고려)
                time.sleep(1)
            else:
                logger.error(f"수정 실패: {title}")
        else:
            skipped_count += 1
            if i % 50 == 0:
                logger.info(f"[{i+1}/{len(posts)}] 건너뜀 (변경 사항 없음)")

    logger.info("=" * 50)
    logger.info(f"마이그레이션 완료!")
    logger.info(f"업데이트: {updated_count}개")
    logger.info(f"유지: {skipped_count}개")
    logger.info("=" * 50)

if __name__ == "__main__":
    migrate_labels()
