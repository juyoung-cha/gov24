import sys
sys.stdout.reconfigure(encoding='utf-8')
from blogger_poster import BloggerPoster
from bs4 import BeautifulSoup
import re
import time

poster = BloggerPoster()
blog_id = poster.blog_id

print("=" * 80)
print("본문 유실 및 링크 박스만 존재하는 손상 글 61개 전량 비공개(Draft) 소탕 시작")
print("=" * 80)

page_token = None
purged_count = 0

while True:
    res = poster.service.posts().list(
        blogId=blog_id,
        maxResults=100,
        status='LIVE',
        pageToken=page_token,
        fetchBodies=True
    ).execute()
    
    items = res.get('items', [])
    if not items:
        break
        
    for post in items:
        title = post.get('title', '제목 없음')
        post_id = post['id']
        content_html = post.get('content', '')
        
        soup = BeautifulSoup(content_html, 'html.parser')
        for div in soup.find_all('div', style=re.compile(r'background-color:\s*#f1f8ff')):
            div.decompose()
        for div in soup.find_all('script'):
            div.decompose()
            
        pure_text = soup.get_text(strip=True)
        
        # 순수 본문 텍스트가 500자 이하인 손상 글 비공개 전환
        if len(pure_text) <= 500:
            print(f"🧹 [비공개 전환] {title[:35]} (ID: {post_id}, 본문자수: {len(pure_text)}자)")
            try:
                poster.service.posts().revert(blogId=blog_id, postId=post_id).execute()
                purged_count += 1
                time.sleep(1)
            except Exception as e:
                print(f"❌ 실패: {e}")
                
    page_token = res.get('nextPageToken')
    if not page_token:
        break

print("=" * 80)
print(f"소탕 완료! 총 {purged_count}개의 손상된 게시물이 블로그에서 완벽하게 비공개 처리되었습니다.")
print("=" * 80)
