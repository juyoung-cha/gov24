"""
간단한 블로그 목록 조회 테스트
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pickle
import json

print("=" * 60)
print("Blogger 블로그 목록 확인")
print("=" * 60)

# 토큰 로드
with open("token.pickle", 'rb') as f:
    creds = pickle.load(f)

# Blogger API 서비스
service = build('blogger', 'v3', credentials=creds)

# 블로그 목록 조회
print("\n인증된 계정의 블로그 목록:")
print("-" * 60)

try:
    result = service.blogs().listByUser(userId='self').execute()
    
    if 'items' in result:
        blogs = result['items']
        print(f"\n총 {len(blogs)}개의 블로그 발견\n")
        
        for i, blog in enumerate(blogs, 1):
            print(f"블로그 #{i}:")
            print(f"  이름: {blog['name']}")
            print(f"  URL: {blog['url']}")
            print(f"  ID: {blog['id']}")
            print()
    else:
        print("\n❌ 블로그가 없습니다!")
        print("이 Google 계정에는 Blogger 블로그가 없습니다.")
        
except Exception as e:
    print(f"\n❌ 오류: {e}")

# config.json의 blog_id 비교
print("-" * 60)
print("config.json 설정:")
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
    config_blog_id = config.get("blogger", {}).get("blog_id")
    print(f"  blog_id: {config_blog_id}")

print("=" * 60)
