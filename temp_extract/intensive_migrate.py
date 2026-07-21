from blogger_poster import BloggerPoster
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def intensive_migrate():
    poster = BloggerPoster()
    posts = poster.list_posts(max_results=500)
    
    gov_depts = ["기획재정부", "환경부", "국토교통부", "보건복지부", "해양수산부", "행정안전부", "환경정책", "설명절"]
    
    updated = 0
    for i, post in enumerate(posts):
        labels = post.get('labels', [])
        title = post['title']
        
        has_new_gov = "1. 국가 정부 자료" in labels
        has_new_seoul = "2. 서울시 정책 뉴스" in labels
        
        if not (has_new_gov or has_new_seoul):
            # 라벨이 없는 경우 판단 로직
            is_seoul = "서울" in title or "서울시" in title or "서울미디어허브" in labels
            
            new_labels = list(labels)
            if is_seoul:
                new_labels.append("2. 서울시 정책 뉴스")
            else:
                new_labels.append("1. 국가 정부 자료")
            
            # 중복 제거 및 정렬
            new_labels = sorted(list(set(new_labels)))
            
            logger.info(f"[{i+1}/{len(posts)}] 신규 분류: {title[:20]}... -> {new_labels[-1]}")
            poster.update_post(post['id'], title, post['content'], new_labels)
            updated += 1
            time.sleep(1)
            
    print(f"정밀 마이그레이션 완료! 총 {updated}개 업데이트")

if __name__ == "__main__":
    intensive_migrate()
