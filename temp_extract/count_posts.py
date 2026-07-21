"""블로그 포스팅 개수 확인"""
from blogger_poster import BloggerPoster

bp = BloggerPoster()
posts = bp.service.posts().list(blogId=bp.blog_id, maxResults=500).execute()
items = posts.get("items", [])

print(f"\n{'='*60}")
print(f"총 포스팅 개수: {len(items)}개")
print(f"{'='*60}\n")

print("최근 20개 포스팅:")
print("-" * 60)
for i, post in enumerate(items[:20], 1):
    title = post["title"][:70]
    print(f"{i:2d}. {title}")
