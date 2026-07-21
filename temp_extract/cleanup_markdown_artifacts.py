import json
import logging
import re
import time
from blogger_poster import BloggerPoster

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def cleanup_existing_posts(max_results=50, dry_run=False):
    """
    기존 블로그 포스트에서 ```html 등의 마크다운 잔재를 제거합니다.
    """
    # 설정 로드
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    blogger_id = config['blogger']['blog_id']
    logger.info(f"블로그 ID: {blogger_id} 정리 시작 (최근 {max_results}개 대상)")
    
    poster = BloggerPoster(blog_id=blogger_id)
    posts = poster.list_posts(max_results=max_results)
    
    updated_count = 0
    
    for post in posts:
        content = post.get('content', '')
        title = post.get('title', '')
        post_id = post.get('id')
        
        # 정규표현식으로 ```html, ```, '''html, ''' 제거
        # 본문의 맨 앞이나 맨 뒤에 주로 위치하므로 이를 타겟팅
        new_content = content
        
        # 1. 시작 부분의 ```html 또는 ``` 제거
        new_content = re.sub(r"^\s*```(?:html|HTML)?\s*", "", new_content, flags=re.MULTILINE)
        new_content = re.sub(r"^\s*'''(?:html|HTML)?\s*", "", new_content, flags=re.MULTILINE)
        
        # 2. 끝 부분의 ``` 또는 ''' 제거
        new_content = re.sub(r"\s*```\s*$", "", new_content, flags=re.MULTILINE)
        new_content = re.sub(r"\s*'''\s*$", "", new_content, flags=re.MULTILINE)
        
        # 3. 본문 내에 남은 잔여 기호들 (가끔 중간에 생김)
        new_content = new_content.replace("```html", "").replace("```", "").replace("'''", "")
        
        new_content = new_content.strip()
        
        if content.strip() != new_content:
            logger.info(f"정리 대상 발견: {title}")
            if dry_run:
                logger.info(f"[Dry Run] {title} 수정 예정")
                updated_count += 1
            else:
                success = poster.update_post(post_id, title, new_content, post.get('labels', []))
                if success:
                    logger.info(f"✅ 수정 완료: {title}")
                    updated_count += 1
                    time.sleep(1) # API 할당량 고려
                else:
                    logger.error(f"❌ 수정 실패: {title}")
        
    logger.info(f"총 {updated_count}개의 포스트를 정리했습니다.")

if __name__ == "__main__":
    # 안전을 위해 처음에는 dry_run=True로 실행해볼 수 있습니다.
    # 여기서는 바로 수정을 진행합니다.
    cleanup_existing_posts(max_results=50, dry_run=False)
