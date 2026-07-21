from blogger_poster import BloggerPoster
import json
import logging

logging.basicConfig(level=logging.INFO)

def check_posts():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    poster = BloggerPoster(blog_id=config['blogger']['blog_id'])
    posts = poster.list_posts(max_results=50) # 최근 50개
    
    print(f"총 {len(posts)}개의 글을 확인했습니다.")
    label_counts = {}
    
    for post in posts:
        title = post.get('title')
        labels = post.get('labels', [])
        print(f"- [{title}] {labels}")
        for label in labels:
            label_counts[label] = label_counts.get(label, 0) + 1
            
    print("\n라벨 분포:")
    for label, count in label_counts.items():
        print(f"  {label}: {count}")

if __name__ == "__main__":
    check_posts()
