from blogger_poster import BloggerPoster
import re
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def fix_posts():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    blogger_id = config['blogger']['blog_id']
    poster = BloggerPoster(blog_id=blogger_id)
    
    posts = poster.list_posts(max_results=50)
    logger.info(f"최근 {len(posts)}개 게시물 검사 시작...")
    
    fixed_count = 0
    
    for post in posts:
        content = post.get('content', '')
        title = post.get('title', '')
        
        # ```html 또는 '''html 제거
        new_content = re.sub(r"```(?:html|HTML)?", "", content, flags=re.IGNORECASE)
        new_content = re.sub(r"'''(?:html|HTML)?", "", new_content, flags=re.IGNORECASE)
        
        # 본문 시작 부분의 단독 html 제거
        new_content = re.sub(r"^\s*html\s+", "", new_content, flags=re.IGNORECASE)
        new_content = re.sub(r"\n\s*html\s+", "\n", new_content, flags=re.IGNORECASE)
        
        if content != new_content:
            logger.info(f"수정 필요 발견: {title}")
            if poster.update_post(post['id'], title, new_content, post.get('labels')):
                fixed_count += 1
                logger.info("수정 성공")
    
    logger.info(f"총 {fixed_count}개의 게시물 수정 완료.")

if __name__ == "__main__":
    fix_posts()
