from blogger_poster import BloggerPoster
from collections import Counter

poster = BloggerPoster()
posts = poster.list_posts(max_results=500)

label_counts = Counter()
for post in posts:
    labels = post.get('labels', [])
    for label in labels:
        label_counts[label] += 1

print("="*50)
print(f"전체 게시물 수: {len(posts)}")
print("="*50)
print("라벨별 게시물 분포:")
for label, count in sorted(label_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"- {label}: {count}개")
print("="*50)
