"""
token.pickle을 base64로 인코딩하여 콘솔 출력 및 token_base64.txt에 저장하는 스크립트
GitHub Actions Secrets(TOKEN_PICKLE_BASE64)에 등록할 때 사용합니다.
"""
import base64
import os
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def export_token():
    if not os.path.exists("token.pickle"):
        print("❌ token.pickle 파일이 없습니다.")
        return

    with open("token.pickle", "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    with open("token_base64.txt", "w", encoding="utf-8") as f:
        f.write(encoded)

    print("=" * 60)
    print("✅ token.pickle -> token_base64.txt 생성 완료")
    print("GitHub Secrets (TOKEN_PICKLE_BASE64)에 아래 값을 등록하세요:")
    print("=" * 60)
    print(encoded[:50] + "..." + encoded[-50:])
    print("=" * 60)

if __name__ == "__main__":
    export_token()
