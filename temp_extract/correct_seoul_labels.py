from blogger_poster import BloggerPoster
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def correct_seoul_labels():
    poster = BloggerPoster()
    posts = poster.list_posts(max_results=500)
    
    updated = 0
    for i, post in enumerate(posts):
        labels = post.get('labels', [])
        title = post['title']
        
        # 서울 관련 키워드가 있는데 1번 라벨만 있거나 2번 라벨이 없는 경우
        is_seoul = "서울" in title or "서울시" in title or "강남구" in title or "송파구" in title or "강서구" in title
        
        if is_seoul and ("1. 국가 정부 자료" in labels or "2. 서울시 정책 뉴스" not in labels):
            new_labels = [l for l in labels if l != "1. 국가 정부 자료"]
            if "2. 서울시 정책 뉴스" not in new_labels:
                new_labels.append("2. 서울시 정책 뉴스")
            
            new_labels = sorted(list(set(new_labels)))
            
            logger.info(f"[{i+1}/{len(posts)}] 교정: {title[:20]}... -> 2. 서울시 정책 뉴스")
            poster.update_post(post['id'], title, post['content'], new_labels)
            updated += 1
            time.sleep(1)
            
    print(f"교정 완료! 총 {updated}개 업데이트")

if __name__ == "__main__":
    correct_seoul_labels()
