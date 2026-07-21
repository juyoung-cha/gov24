import sys
sys.stdout.reconfigure(encoding='utf-8')
from blogger_poster import BloggerPoster
from bs4 import BeautifulSoup

poster = BloggerPoster()
blog_id = poster.blog_id

page_token = None
print("=" * 80)
print("5월 전후의 블로그 포스팅 전체 수집 및 분석")
print("=" * 80)

may_posts = []

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
        published = post.get('published', '')
        url = post.get('url', '')
        if '2026-05' in published or '2026/05' in url:
            may_posts.append(post)
            
    page_token = res.get('nextPageToken')
    if not page_token:
        break

print(f"총 {len(may_posts)}개의 5월 포스트 발견!\n")

for idx, post in enumerate(may_posts, 1):
    published = post.get('published', '')
    title = post.get('title', '')
    url = post.get('url', '')
    print(f"[{idx}] 날짜: {published[:10]} | 제목: {title}")
    print(f"    URL: {url}")
    content_html = post.get('content', '')
    soup = BeautifulSoup(content_html, 'html.parser')
    pure_text = soup.get_text(strip=True)[:250]
    print(f"    서두: {pure_text}...")
    print("-" * 80)
