from blogger_poster import BloggerPoster
poster = BloggerPoster()
posts = poster.list_posts(max_results=5)
print("="*50)
print("최근 포스팅 라벨 상태 확인")
print("="*50)
for p in posts:
    print(f"제목: {p['title'][:30]}...")
    print(f"라벨: {p.get('labels', [])}")
    print("-"*30)
