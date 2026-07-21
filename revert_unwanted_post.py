import sys
sys.stdout.reconfigure(encoding='utf-8')
from blogger_poster import BloggerPoster
from googleapiclient.discovery import build
import pickle

with open("token.pickle", 'rb') as f:
    creds = pickle.load(f)

service = build('blogger', 'v3', credentials=creds)
p = BloggerPoster()
blog_id = p.blog_id

# 유저 비선호 관료형 글 (선거 현수막 작업 안전)
post_id = "5676742513470001859" # URL: 2026/05/20.html

posts = p.list_posts(30)
for post in posts:
    if "선거 현수막" in post.get('title', ''):
        print(f"🧹 [유저 비선호 포스트 비공개 처리] {post['title']} (ID: {post['id']})")
        try:
            service.posts().revert(blogId=blog_id, postId=post['id']).execute()
            print("✅ 비공개 전환 완료!")
        except Exception as e:
            print(f"❌ 실패: {e}")
