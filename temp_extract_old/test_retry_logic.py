"""
재시도 로직 테스트 스크립트
"""
from blogger_poster import BloggerPoster
import json
import time

def test_with_retry():
    """재시도 로직이 포함된 포스팅 테스트"""
    print("=" * 60)
    print("Blogger API 재시도 로직 테스트")
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
        
        # 5개 연속 포스팅 테스트 (Rate Limiting 확인)
        print("\n2. 연속 포스팅 테스트 (5개, 각 2초 간격)")
        
        success_count = 0
        fail_count = 0
        
        for i in range(1, 6):
            print(f"\n--- 테스트 {i}/5 ---")
            
            test_content = f"""
            <h2>재시도 로직 테스트 #{i}</h2>
            <p>Rate Limiting 방지를 위한 포스팅 간격 테스트입니다.</p>
            <p>현재 시각: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <ul>
                <li>포스팅 번호: {i}</li>
                <li>간격: 2초</li>
                <li>재시도: 최대 3회</li>
            </ul>
            """
            
            # 재시도 로직
            post_url = None
            max_retries = 3
            retry_delay = 3
            
            for attempt in range(max_retries):
                if attempt > 0:
                    print(f"  재시도 {attempt}/{max_retries-1}... ({retry_delay}초 대기)")
                    time.sleep(retry_delay)
                
                post_url = blogger.post(
                    title=f"[재시도 테스트] #{i} - Rate Limiting 방지",
                    content=test_content,
                    labels=["테스트", "재시도로직", f"테스트{i}"],
                    is_draft=False
                )
                
                if post_url:
                    print(f"  ✅ 성공: {post_url}")
                    success_count += 1
                    break
                elif attempt < max_retries - 1:
                    print(f"  ⚠️ 실패, 재시도합니다...")
            else:
                print(f"  ❌ 최종 실패")
                fail_count += 1
            
            # 다음 포스팅까지 2초 대기 (마지막 항목 제외)
            if i < 5:
                print("  (2초 대기...)")
                time.sleep(2)
        
        print("\n" + "=" * 60)
        print(f"결과: 성공 {success_count}개, 실패 {fail_count}개")
        print("=" * 60)
        
        if fail_count == 0:
            print("\n✅ 모든 테스트 통과! Rate Limiting 문제가 해결되었습니다.")
            return True
        else:
            print(f"\n⚠️ {fail_count}개 실패. 추가 조정이 필요할 수 있습니다.")
            return False
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_with_retry()
