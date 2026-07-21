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

# 한강 수영장 1차 테스트 버그글 ID: 2690661447699028006
post_id = "2690661447699028006"

try:
    print(f"🧹 [버그글 비공개 전환] ID: {post_id}")
    service.posts().revert(blogId=blog_id, postId=post_id).execute()
    print("✅ 성공적으로 비공개 처리 완료!")
except Exception as e:
    print(f"❌ 실패: {e}")
