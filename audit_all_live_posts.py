import sys
sys.stdout.reconfigure(encoding='utf-8')
from blogger_poster import BloggerPoster
from bs4 import BeautifulSoup
import re
import json

poster = BloggerPoster()
blog_id = poster.blog_id

print("=" * 80)
print("Blogger 블로그 전체 공개 게시글(LIVE Posts) 전수 조사 및 오디트 시작")
print("=" * 80)

page_token = None
live_posts = []

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
    live_posts.extend(items)
    page_token = res.get('nextPageToken')
    if not page_token:
        break

print(f"총 {len(live_posts)}개의 공개(LIVE) 게시글 발견!\n")

valid_posts = []
empty_posts = []

for idx, post in enumerate(live_posts, 1):
    title = post.get('title', '제목 없음')
    url = post.get('url', '')
    content_html = post.get('content', '')
    
    # HTML 태그를 떼어낸 순수 텍스트 추출
    soup = BeautifulSoup(content_html, 'html.parser')
    
    # 출처/저작권 박스 제거 후 순수 본문 텍스트만 평가
    for div in soup.find_all('div', style=re.compile(r'background-color:\s*#f1f8ff')):
        div.decompose()
    for div in soup.find_all('script'):
        div.decompose()
        
    pure_text = soup.get_text(strip=True)
    pure_length = len(pure_text)
    
    status_icon = "✅ 정상 고품질 본문" if pure_length > 500 else "❌ 본문 유실 (링크 박스만 존재)"
    
    item_info = {
        "index": idx,
        "id": post['id'],
        "title": title,
        "url": url,
        "pure_length": pure_length,
        "is_valid": pure_length > 500
    }
    
    if pure_length > 500:
        valid_posts.append(item_info)
    else:
        empty_posts.append(item_info)
        
    print(f"[{idx:02d}] {status_icon} | 순수 본문자수: {pure_length:5d}자 | {title[:35]}")

print("\n" + "=" * 80)
print(f"전수 조사 결과 요약:")
print(f"- 총 공개 게시글: {len(live_posts)}개")
print(f"- 정상 고품질 글: {len(valid_posts)}개")
print(f"- 본문 유실/링크만 존재하는 글: {len(empty_posts)}개")
print("=" * 80)
