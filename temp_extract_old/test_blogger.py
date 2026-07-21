"""
Blogger API 연결 테스트 스크립트
"""
import json
from blogger_poster import BloggerPoster, BloggerAuthHelper

def test_blogger_connection():
    """Blogger 연결 테스트"""
    print("=" * 60)
    print("Blogger API 연결 테스트")
    print("=" * 60)
    
    try:
        # config.json 로드
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # Blogger 포스터 초기화
        print("\n1. Blogger API 인증 중...")
        print("   (처음 실행 시 브라우저가 열립니다)")
        
        blogger = BloggerPoster(
            blog_id=config.get("blogger", {}).get("blog_id") or None
        )
        
        print("✅ 인증 성공!")
        
        # 블로그 목록 조회
        print("\n2. 블로그 목록 조회")
        blogs = blogger.get_blogs()
        
        if blogs:
            print(f"✅ 성공: {len(blogs)}개 블로그 발견")
            for blog in blogs:
                print(f"  - {blog['name']}")
                print(f"    URL: {blog['url']}")
                print(f"    ID: {blog['id']}")
                print()
        else:
            print("❌ 블로그가 없습니다")
            print("https://www.blogger.com 에서 블로그를 먼저 생성하세요")
            return False
        
        # 테스트 포스팅 (임시저장)
        print("\n3. 테스트 포스팅 (임시저장)")
        
        test_content = """
        <h2>테스트 포스팅</h2>
        <p>정부 정책 자동 블로그 포스팅 시스템 테스트 중입니다.</p>
        <h3>시스템 구성</h3>
        <ul>
            <li>RSS 피드 수집</li>
            <li>Gemini AI 블로그 글 작성</li>
            <li>Blogger 자동 포스팅</li>
            <li>Google Cloud 자동 실행</li>
        </ul>
        <p>이 글은 테스트용으로 임시저장되었습니다.</p>
        """
        
        url = blogger.post(
            title="[테스트] 정부 정책 자동 포스팅 시스템",
            content=test_content,
            labels=["테스트", "자동화", "정부정책"],
            is_draft=True  # 임시저장
        )
        
        if url:
            print(f"✅ 성공: {url}")
            print("\n임시저장된 글은 Blogger 관리 페이지에서 확인 가능합니다.")
            print("https://www.blogger.com")
            return True
        else:
            print("❌ 실패: 포스팅할 수 없습니다")
            return False
    
    except FileNotFoundError as e:
        print(f"\n❌ 파일 오류: {e}")
        print("\n다음이 필요합니다:")
        BloggerAuthHelper.setup_credentials()
        return False
    
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        return False


if __name__ == "__main__":
    try:
        success = test_blogger_connection()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ 모든 테스트 통과!")
            print("다음 단계: Google Cloud에 배포하세요.")
        else:
            print("❌ 테스트 실패")
            print("BLOGGER_SETUP_GUIDE.md를 참조하여 설정을 확인하세요.")
        print("=" * 60)
    
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
