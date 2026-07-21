"""
직접 게시 방식으로 포스팅 테스트
"""
from blogger_poster import BloggerPoster
import json

def test_direct_publish():
    """임시저장이 아닌 직접 게시 방식으로 포스팅 테스트"""
    print("=" * 60)
    print("Blogger 직접 게시 테스트 (is_draft=False)")
    print("=" * 60)
    
    try:
        # config.json 로드
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # BloggerPoster 초기화
        print("\n1. Blogger API 연결 중...")
        blogger = BloggerPoster(
            blog_id=config.get("blogger", {}).get("blog_id")
        )
        print("✅ 연결 성공")
        
        # 직접 게시 테스트
        print("\n2. 직접 게시 테스트 (임시저장 아님)")
        
        test_content = """
        <h2>✅ 포스팅 테스트 성공!</h2>
        <p>이 글은 Blogger API를 통해 <strong>직접 게시</strong>되었습니다.</p>
        <h3>테스트 항목</h3>
        <ul>
            <li>OAuth 인증: 성공</li>
            <li>API 활성화: 성공</li>
            <li>직접 게시: 테스트 중</li>
        </ul>
        <p><em>이 글이 보인다면 문제가 해결되었습니다!</em></p>
        """
        
        url = blogger.post(
            title="[테스트] Blogger API 직접 게시 테스트",
            content=test_content,
            labels=["테스트", "API", "자동화"],
            is_draft=False  # 직접 게시!
        )
        
        if url:
            print(f"\n✅ 포스팅 성공!")
            print(f"URL: {url}")
            print("\n블로그 주소: http://story0people.blogspot.com/")
            print("브라우저에서 확인해보세요!")
            return True
        else:
            print("\n❌ 포스팅 실패")
            print("여전히 권한 문제가 있습니다.")
            return False
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n⚠️  주의: 이 테스트는 블로그에 실제로 글을 게시합니다!")
    print("테스트 후 블로그에서 글을 삭제할 수 있습니다.\n")
    
    success = test_direct_publish()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 테스트 성공! 문제가 해결되었습니다.")
    else:
        print("❌ 테스트 실패. 추가 조치가 필요합니다.")
    print("=" * 60)
