import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
from blogger_poster import BloggerPoster
from googleapiclient.discovery import build
import pickle

with open("token.pickle", 'rb') as f:
    creds = pickle.load(f)

service = build('blogger', 'v3', credentials=creds)
p = BloggerPoster()
blog_id = p.blog_id

posts = p.list_posts(30)

print("=" * 70)
print("과거 파싱 버그로 본문 유실된 포스트 자동 정리 (Draft 전환)")
print("=" * 70)

cleaned_count = 0
for post in posts:
    content = post.get("content", "")
    # 본문 길이가 1,500자 이하인 과거 본문 유실 포스트 정리
    if len(content) < 1500:
        title = post['title']
        post_id = post['id']
        print(f"🧹 [Draft 비공개 전환 중] {title} (ID: {post_id}, 길이: {len(content)}자)")
        try:
            service.posts().revert(blogId=blog_id, postId=post_id).execute()
            cleaned_count += 1
            print(f"   ✅ 성공적으로 비공개 처리됨")
            time.sleep(1)
        except Exception as e:
            print(f"   ❌ 실패: {e}")

print("=" * 70)
print(f"총 {cleaned_count}개의 과거 본문 유실 손상 포스트가 블로그에서 비공개(Draft) 처리되었습니다.")
