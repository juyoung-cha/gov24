import sys
sys.stdout.reconfigure(encoding='utf-8')
from blogger_poster import BloggerPoster

p = BloggerPoster()
posts = p.list_posts(15)

print("=" * 70)
print("최근 공개 포스트 15개 본문 길이 분석")
print("=" * 70)

for idx, post in enumerate(posts, 1):
    content = post.get("content", "")
    print(f"{idx}. [{post['title']}]")
    print(f"   - URL: {post['url']}")
    print(f"   - 본문 텍스트 길이: {len(content)} 자")
    if len(content) < 1500:
        print("   ⚠️ (과거 버그 시절 작성된 본문 누락 글)")
    else:
        print("   ✅ (정상 고품질 본문 글)")
    print()
