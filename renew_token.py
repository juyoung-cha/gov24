"""
OAuth 토큰 재발급 전용 스크립트
- 기존 token.pickle이 없거나 만료된 경우, 브라우저를 열어 재인증
- 인증 완료 후 token.pickle 생성 + base64 인코딩까지 한 번에 처리
"""
import os
import sys
import pickle
import base64

sys.stdout.reconfigure(encoding='utf-8')

SCOPES = ['https://www.googleapis.com/auth/blogger']
TOKEN_FILE = "token.pickle"
CREDENTIALS_FILE = "credentials.json"
BASE64_OUTPUT = "token_base64.txt"


def main():
    print("=" * 60)
    print("🔑 OAuth 토큰 재발급 스크립트")
    print("=" * 60)
    
    # 1. 기존 토큰 확인
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "rb") as f:
                creds = pickle.load(f)
            
            if creds and creds.valid:
                print(f"✅ 기존 토큰이 유효합니다.")
                _export_base64()
                return
            
            if creds and creds.expired and creds.refresh_token:
                print("⚠️ Access Token 만료됨. 자동 갱신 시도...")
                try:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                    _save_token(creds)
                    print("✅ 토큰 자동 갱신 성공!")
                    _export_base64()
                    return
                except Exception as e:
                    print(f"❌ 자동 갱신 실패: {e}")
                    print("   → 브라우저 재인증이 필요합니다.")
        except Exception as e:
            print(f"⚠️ 기존 토큰 읽기 실패: {e}")
    
    # 2. credentials.json 확인
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ {CREDENTIALS_FILE} 파일이 없습니다!")
        print("   Google Cloud Console에서 OAuth 클라이언트 ID를 다운로드하세요.")
        sys.exit(1)
    
    # 3. 브라우저 인증
    print("\n🌐 브라우저가 열립니다. Google 계정으로 로그인해 주세요.")
    print("   → '이 앱은 확인되지 않았습니다' 경고 시:")
    print("     → '고급' → '(안전하지 않음)' 링크 클릭")
    print("   → 'Blogger' 접근 허용 클릭")
    print()
    
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        
        _save_token(creds)
        print("\n✅ 인증 성공! token.pickle 생성 완료.")
        _export_base64()
        
    except Exception as e:
        print(f"\n❌ 인증 실패: {e}")
        sys.exit(1)


def _save_token(creds):
    """토큰을 pickle 파일로 저장"""
    with open(TOKEN_FILE, "wb") as f:
        pickle.dump(creds, f)
    print(f"💾 {TOKEN_FILE} 저장 완료")


def _export_base64():
    """token.pickle을 base64로 인코딩하여 출력 및 파일 저장"""
    with open(TOKEN_FILE, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    
    with open(BASE64_OUTPUT, "w", encoding="utf-8") as f:
        f.write(encoded)
    
    print(f"\n📋 GitHub Secrets 업데이트용 base64 값:")
    print("=" * 60)
    print(f"   파일: {BASE64_OUTPUT}")
    print(f"   길이: {len(encoded)} chars")
    print("=" * 60)
    print(f"\n📌 다음 단계:")
    print(f"   1. GitHub → Settings → Secrets → TOKEN_PICKLE_BASE64")
    print(f"   2. 값을 {BASE64_OUTPUT} 파일 내용으로 교체")
    print(f"   3. Actions 탭 → 'Run workflow'로 수동 실행 테스트")


if __name__ == "__main__":
    main()
