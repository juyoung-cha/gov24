"""
Blogger 블로그 목록 조회 및 권한 확인
"""
from blogger_poster import BloggerPoster
import json

def check_blog_access():
    """블로그 접근 권한 확인"""
    print("=" * 60)
    print("Blogger 블로그 접근 권한 확인")
    print("=" * 60)
    
    try:
        # BloggerPoster 초기화 (blog_id 없이)
        print("\n1. Blogger API 연결 중...")
        blogger = BloggerPoster(blog_id=None)
        print("✅ 연결 성공")
        
        # 블로그 목록 조회
        print("\n2. 사용자의 블로그 목록 조회 중...")
        blogs = blogger.get_blogs()
        
        if not blogs:
            print("❌ 접근 가능한 블로그가 없습니다!")
            print("\n원인:")
            print("  - 현재 인증한 계정에 Blogger 블로그가 없음")
            print("  - 또는 API 권한 문제")
            return
        
        print(f"✅ 발견된 블로그: {len(blogs)}개\n")
        
        # config.json의 blog_id 확인
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            config_blog_id = config.get("blogger", {}).get("blog_id")
        
        print(f"📋 config.json의 blog_id: {config_blog_id}\n")
        print("-" * 60)
        
        # 블로그 목록 출력
        blog_found = False
        for i, blog in enumerate(blogs, 1):
            print(f"\n블로그 #{i}")
            print(f"  이름: {blog['name']}")
            print(f"  URL: {blog['url']}")
            print(f"  ID: {blog['id']}")
            
            if blog['id'] == config_blog_id:
                print("  ✅ config.json과 일치!")
                blog_found = True
            else:
                print("  ⚠️ config.json과 다름")
        
        print("\n" + "=" * 60)
        
        # 결과 분석
        if not blog_found and config_blog_id:
            print("\n❌ 문제 발견!")
            print(f"config.json의 blog_id ({config_blog_id})가")
            print("현재 계정에서 접근 가능한 블로그 목록에 없습니다!")
            print("\n해결 방법:")
            print("1. config.json의 blog_id를 위 목록의 ID로 변경")
            print("2. 또는 올바른 Google 계정으로 재인증")
        else:
            print("\n✅ 블로그 접근 권한 정상!")
            
            # 간단한 포스팅 테스트
            print("\n3. 임시저장 테스트 중...")
            test_content = "<h2>테스트</h2><p>권한 테스트</p>"
            url = blogger.post(
                title="[권한 테스트]",
                content=test_content,
                is_draft=True
            )
            
            if url:
                print(f"✅ 포스팅 성공: {url}")
                print("\n모든 테스트 통과! 시스템이 정상입니다.")
            else:
                print("❌ 포스팅 실패")
                print("블로그 설정에서 API 접근이 차단되었을 수 있습니다.")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_blog_access()
