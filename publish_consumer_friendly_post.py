import sys
sys.stdout.reconfigure(encoding='utf-8')
from blog_writer import BlogWriter
from blogger_poster import BloggerPoster

writer = BlogWriter()
poster = BloggerPoster()

title = "매월 5만 원 절약! K-패스 & 기후동행카드 환급 혜택 총정리"
dept = "국토교통부 & 서울특별시 대중교통 정책과"
content = """
2026년 대중교통비 절약의 핵심인 K-패스(구 알뜰교통카드)와 서울시 기후동행카드 혜택이 대폭 강화되었습니다.
대중교통을 이용하는 청년, 직장인, 다자녀 가구, 어르신 등 다양한 시민들을 위해 매월 대중교통 지출 금액의 20%~53%까지 현금 환급(페이백) 또는 카드 청구 할인이 제공됩니다.

[주요 혜택 및 환급 비율]
- 일반 시민: 대중교통 이용 금액의 20% 환급
- 청년층(만 19세~34세): 30% 환급
- 저소득층: 최대 53.3% 환급
- 다자녀 가구(2자녀 이상): 30%~50% 환급 확대

[신청 및 이용 방법]
1. K-패스 공식 누리집 또는 모바일 앱 설치
2. 회원가입 및 기존 알뜰교통카드 이관 신청
3. 월 15회 이상 대중교통(지하철, 버스, 신분당선, 광역버스) 이용 시 자동으로 익월 환급 계좌로 입금

[서울시 기후동행카드 추가 혜택]
- 월 6만 2천 원(따릉이 포함 6만 5천 원)으로 서울 시내 지하철, 버스를 무제한 이용
- 청년 할인권 적용 시 월 5만 5천 원에 이용 가능
- 2026년부터 한강버스(리버버스) 및 주요 경기 연결 노선까지 탑승 범위 확대
"""

print("=" * 80)
print("유저 선호 5월 베스트 스타일 (생활 밀착형 공감 포스팅) 생성 및 발행")
print("=" * 80)

recent_items = poster.list_posts(10)
recent_posts = [{'title': r.get('title', ''), 'url': r.get('url', '')} for r in recent_items]

post_data = writer.write_post(
    title=title,
    content=content,
    dept=dept,
    url="https://www.korea.kr",
    recent_posts=recent_posts
)

if post_data and post_data != 'QUOTA_EXHAUSTED':
    print("\n✅ AI 포스팅 생성 성공!")
    print(f"📌 제목: {post_data['title']}")
    print(f"📌 분량: {len(post_data['content'])}자")
    
    result = poster.post(
        title=post_data['title'],
        content=post_data['content'],
        labels=post_data.get('tags', []),
        is_draft=False
    )
    print("\n🚀 블로그 발행 완료!")
    print(f"🔗 공개 URL: {result.get('url')}")
