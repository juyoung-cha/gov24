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

posts = p.list_posts(5)
target_post = posts[0]

title = target_post['title']
post_id = target_post['id']
content = target_post.get('content', '')

print(f"📌 최신 포스트 발견: {title} (ID: {post_id})")

source_url = "https://www.korea.kr"
dept_name = "국토교통부 & 서울특별시 대중교통 정책과"

source_box = f"""
<div style="margin-top: 40px; padding: 20px; background-color: #f1f8ff; border-radius: 10px; border: 1px solid #c8e1ff;">
  <p style="font-size: 18px; margin-bottom: 15px; font-weight: bold;">
    💡 좀 더 자세한 내용은 <a href="{source_url}" style="color: #0366d6; text-decoration: underline;" target="_blank">"여기"</a>를 눌러 원문을 볼 수 있습니다.
  </p>
  <hr style="border: 0; border-top: 1px solid #c8e1ff; margin-bottom: 15px;"/>
  <div style="font-size: 14px; color: #586069;">
    <p style="margin-bottom: 5px;"><strong>출처 정보:</strong> {dept_name}</p>
    <p style="margin-bottom: 5px;">본 글은 정부 공개 자료를 바탕으로 재구성 및 분석한 글입니다.</p>
    <p style="margin-bottom: 0;">저작권은 원 저작권자에게 있으며, 상업적 이용 시 출처를 명시해주세요.</p>
  </div>
</div>
"""

updated_content = content + "\n" + source_box

body = {
    'title': title,
    'content': updated_content
}

res = service.posts().patch(blogId=blog_id, postId=post_id, body=body).execute()
print("✅ 원문 출처 박스 부착 완료!")
print("🔗 URL:", res.get('url'))
