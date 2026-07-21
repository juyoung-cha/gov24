"""
OAuth 토큰의 권한 범위 확인 스크립트
"""
import pickle
import os

def check_token_scopes():
    """현재 토큰의 권한 범위를 확인합니다"""
    token_file = "token.pickle"
    
    if not os.path.exists(token_file):
        print("❌ token.pickle 파일이 없습니다.")
        print("먼저 python test_blogger.py를 실행하여 인증하세요.")
        return
    
    try:
        with open(token_file, 'rb') as f:
            creds = pickle.load(f)
        
        print("=" * 60)
        print("OAuth 토큰 정보")
        print("=" * 60)
        print(f"\n✅ 토큰 파일 발견: {token_file}")
        print(f"\n📋 권한 범위 (Scopes):")
        
        if hasattr(creds, 'scopes'):
            for scope in creds.scopes:
                print(f"  - {scope}")
        else:
            print("  ⚠️  권한 범위 정보를 찾을 수 없습니다")
        
        print(f"\n🔑 토큰 유효성:")
        print(f"  - Valid: {creds.valid}")
        print(f"  - Expired: {creds.expired if hasattr(creds, 'expired') else 'N/A'}")
        
        if hasattr(creds, 'token'):
            print(f"  - Access Token: {creds.token[:20]}...")
        
        print("\n" + "=" * 60)
        
        # 필요한 권한 확인
        required_scope = 'https://www.googleapis.com/auth/blogger'
        if hasattr(creds, 'scopes') and required_scope in creds.scopes:
            print("✅ Blogger API 권한이 있습니다!")
        else:
            print("❌ Blogger API 권한이 없습니다!")
            print(f"\n필요한 권한: {required_scope}")
            print("\n해결 방법:")
            print("1. token.pickle 파일을 삭제하세요")
            print("2. python test_blogger.py를 다시 실행하세요")
            print("3. 브라우저에서 모든 권한을 승인하세요")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("\ntoken.pickle 파일이 손상되었을 수 있습니다.")
        print("파일을 삭제하고 재인증하세요.")

if __name__ == "__main__":
    check_token_scopes()
