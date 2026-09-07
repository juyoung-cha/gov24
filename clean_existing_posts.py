"""
기존 블로그 포스트 본문 클린업 스크립트
본문 상단에 유입된 '메타설명:', '제목:', 중복 meta-description 태그 등을 정제하여 업데이트합니다.
"""
import os
import re
import json
import logging
import time
from bs4 import BeautifulSoup
from blogger_poster import BloggerPoster

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def clean_content_text(content: str) -> str:
    """본문 상단의 메타설명, 제목 텍스트 및 중복 마크다운/태그 잔여물 정제"""
    if not content:
        return ""
    
    cleaned = content.strip()
    
    # 1. <div class="meta-description" ...> 중복 제거 (Blogger post의 description 필드가 있으므로 본문 내 숨김 div는 1개 이하 또는 제거)
    # 첫 번째 meta-description div 제거
    cleaned = re.sub(r"^\s*<div[^>]*class=['\"]meta-description['\"][^>]*>.*?</div>\s*", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"^\s*<div[^>]*class=['\"]meta-description['\"][^>]*>.*?</div>\s*", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    
    # 2. 본문 상단에 일반 텍스트로 노출된 '메타설명: ...', '제목: ...' 줄 제거
    patterns = [
        r"^\s*메타설명\s*:\s*[^\n<]+(?:\n|<br\s*/?>)*",
        r"^\s*메타\s*설명\s*:\s*[^\n<]+(?:\n|<br\s*/?>)*",
        r"^\s*제목\s*:\s*[^\n<]+(?:\n|<br\s*/?>)*",
        r"^\s*본문\s*:\s*(?:\n|<br\s*/?>)*"
    ]
    
    changed = True
    while changed:
        changed = False
        for pat in patterns:
            new_cleaned = re.sub(pat, "", cleaned, count=1, flags=re.IGNORECASE)
            if new_cleaned != cleaned:
                cleaned = new_cleaned.strip()
                changed = True
                
    # 3. 만약 <article> 태그가 존재한다면 <article> 앞쪽 잔여 텍스트 정제
    article_idx = cleaned.find("<article")
    if 0 < article_idx < 500:
        cleaned = cleaned[article_idx:]
        
    # 4. table 태그에 overflow-x 반응형 래퍼가 없으면 자동 적용
    try:
        soup = BeautifulSoup(cleaned, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            parent = table.parent
            if parent and "overflow-x" in str(parent.get("style", "")):
                continue
            wrapper = soup.new_tag("div", style="overflow-x: auto; width: 100%; -webkit-overflow-scrolling: touch; margin: 25px 0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);")
            table.wrap(wrapper)
        cleaned = str(soup)
    except Exception as e:
        logger.warning(f"테이블 래퍼 파싱 경고: {e}")
        
    return cleaned.strip()

def clean_labels(labels: list) -> list:
    """날짜형/코드형 라벨을 제거하고 정돈된 라벨 반환"""
    if not labels:
        return ["정부 정책 브리핑", "생활꿀팁"]
        
    cleaned = []
    for l in labels:
        l_str = str(l).strip()
        # 날짜형(2026년, 8월 12일 등) 및 시스템 코드 배제
        if re.search(r'\d+년|\d+월|\d+일|^[A-Z]\d+$', l_str):
            continue
        if l_str not in cleaned:
            cleaned.append(l_str)
            
    return cleaned[:5] if cleaned else ["정부 정책 브리핑", "생활꿀팁"]

def run_cleanup():
    logger.info("=" * 60)
    logger.info("Blogger 기존 포스트 정밀 클린업 시작")
    logger.info("=" * 60)
    
    poster = BloggerPoster()
    # 최근 100개 포스트 조회
    posts = poster.list_posts(max_results=100)
    logger.info(f"조회된 포스트 총 {len(posts)}개")
    
    updated_count = 0
    skipped_count = 0
    
    for idx, post in enumerate(posts, 1):
        post_id = post.get("id")
        title = post.get("title", "")
        content = post.get("content", "")
        labels = post.get("labels", [])
        
        logger.info(f"[{idx}/{len(posts)}] 점검 중: {title[:40]}...")
        
        cleaned_content = clean_content_text(content)
        cleaned_labels = clean_labels(labels)
        
        # 변경 사항이 있는지 확인
        content_changed = (cleaned_content != content)
        labels_changed = (cleaned_labels != labels)
        
        if content_changed or labels_changed:
            logger.info(f"  ✨ 수정 사항 발견 (본문 변경: {content_changed}, 라벨 변경: {labels_changed}) -> 업데이트 진행")
            success = poster.update_post(
                post_id=post_id,
                title=title,
                content=cleaned_content,
                labels=cleaned_labels
            )
            if success:
                updated_count += 1
                logger.info(f"  ✅ 포스트 {post_id} 업데이트 완료")
            else:
                logger.error(f"  ❌ 포스트 {post_id} 업데이트 실패")
                
            # API 할당량 보호 대기 (2.5초)
            time.sleep(2.5)
        else:
            logger.info("  👌 이미 깨끗한 상태 (수정 불필요)")
            skipped_count += 1
            
    logger.info("=" * 60)
    logger.info(f"클린업 완료: 수정 {updated_count}개, 유지 {skipped_count}개 (총 {len(posts)}개)")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_cleanup()
