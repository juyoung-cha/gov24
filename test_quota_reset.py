"""
자정 할당량 리셋 확인 테스트
2026-02-04 00:00 이후에 실행하세요
"""
from blogger_poster import BloggerPoster
import json
from datetime import datetime

def test_quota_reset():
    """할당량 리셋 확인"""
    print("=" * 60)
    print("Blogger API 할당량 리셋 확인 테스트")
    print(f"현재 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
        
        # 간단한 테스트 포스팅 3개
        print("\n2. 테스트 포스팅 (3개)")
        print("   할당량이 리셋되었다면 성공할 것입니다.\n")
        
        success_count = 0
        
        for i in range(1, 4):
            print(f"--- 테스트 {i}/3 ---")
            
            test_content = f"""
            <h2>할당량 리셋 확인 테스트 #{i}</h2>
            <p>자정 이후 Blogger API 할당량이 정상적으로 리셋되었는지 확인하는 테스트입니다.</p>
            <p>현재 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <ul>
                <li>테스트 번호: {i}</li>
                <li>목적: 일일 할당량 리셋 확인</li>
            </ul>
            """
            
            url = blogger.post(
                title=f"[할당량 리셋 확인] 테스트 #{i}",
                content=test_content,
                labels=["테스트", "할당량확인"],
                is_draft=False
            )
            
            if url:
                print(f"✅ 성공: {url}")
                success_count += 1
            else:
                print(f"❌ 실패")
            
            print()
        
        print("=" * 60)
        print(f"결과: {success_count}/3 성공")
        print("=" * 60)
        
        if success_count == 3:
            print("\n🎉 할당량이 리셋되었습니다!")
            print("이제 main.py를 실행하여 나머지 RSS 글을 포스팅할 수 있습니다.")
            return True
        elif success_count > 0:
            print("\n⚠️ 일부만 성공했습니다.")
            print("잠시 더 기다린 후 다시 시도하거나,")
            print("다중 블로그 전략을 고려해보세요.")
            return False
        else:
            print("\n❌ 모두 실패했습니다.")
            print("할당량이 아직 리셋되지 않았거나,")
            print("다른 문제가 있을 수 있습니다.")
            print("\n참고: Google API 할당량은 PST(태평양 표준시) 자정에 리셋됩니다.")
            print("한국 시간으로는 오후 5시(여름), 오후 4시(겨울)입니다.")
            return False
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n⚠️ 중요: 이 테스트는 2026-02-04 00:00 이후에 실행하세요!")
    print("현재 시각을 확인하세요.\n")
    
    input("Enter 키를 눌러 테스트를 시작하세요...")
    
    result = test_quota_reset()
    
    if not result:
        print("\n💡 대안:")
        print("1. PST 시간대 자정까지 기다리기 (한국 시간 오후 4-5시)")
        print("2. 다중 블로그 전략 사용하기")
        print("   - CREATE_BLOGS_GUIDE.md 참조")
