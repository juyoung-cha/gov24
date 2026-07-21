from blogger_poster import BloggerPoster

poster = BloggerPoster()
posts = poster.list_posts(max_results=500)

count_1 = 0
count_2 = 0
total = len(posts)

for p in posts:
    labels = p.get('labels', [])
    if "1. 국가 정부 자료" in labels:
        count_1 += 1
    if "2. 서울시 정책 뉴스" in labels:
        count_2 += 1

print("="*50)
print(f"최종 집계 결과 (총 {total}개)")
print(f"- 1. 국가 정부 자료: {count_1}개")
print(f"- 2. 서울시 정책 뉴스: {count_2}개")
print(f"- 기타(라벨 없음): {total - count_1 - count_2}개")
print("="*50)
