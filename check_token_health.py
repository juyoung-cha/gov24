"""
OAuth 토큰 건강 상태 사전 검증 스크립트
- main.py 실행 전에 호출하여 토큰 만료를 조기 감지
- 실패 시 GitHub Issue 자동 생성으로 알림
"""
import os
import sys
import pickle
import json
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def check_token():
    """token.pickle의 유효성을 사전 검증"""
    token_file = "token.pickle"
    
    if not os.path.exists(token_file):
        logger.error("❌ token.pickle 파일이 존재하지 않습니다.")
        return False, "token.pickle 파일 없음"
    
    try:
        with open(token_file, "rb") as f:
            creds = pickle.load(f)
    except Exception as e:
        logger.error(f"❌ token.pickle 파싱 실패: {e}")
        return False, f"token.pickle 파싱 실패: {e}"
    
    # 1. Refresh Token 존재 확인
    if not creds.refresh_token:
        logger.error("❌ Refresh Token이 없습니다. 재인증 필요.")
        return False, "Refresh Token 없음"
    
    # 2. 토큰 만료 여부 확인
    if creds.expired:
        logger.warning("⚠️ Access Token이 만료됨. Refresh 시도...")
        try:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            logger.info("✅ Access Token 자동 갱신 성공!")
            
            # 갱신된 토큰을 다시 저장
            with open(token_file, "wb") as f:
                pickle.dump(creds, f)
            logger.info("💾 갱신된 토큰 저장 완료")
            return True, "토큰 갱신 성공"
            
        except Exception as e:
            error_msg = str(e)
            if "invalid_grant" in error_msg:
                logger.error("🛑 Refresh Token이 만료/취소되었습니다!")
                logger.error("   원인: OAuth 동의 화면이 '테스트' 모드일 경우 7일 후 자동 만료")
                logger.error("   해결: Google Cloud Console → OAuth 동의 화면 → '앱 게시' 클릭")
                logger.error("   이후: 로컬에서 token.pickle 삭제 후 python main.py 재실행")
                return False, "Refresh Token 만료 (invalid_grant)"
            else:
                logger.error(f"❌ 토큰 갱신 실패: {e}")
                return False, f"토큰 갱신 실패: {e}"
    
    # 3. 유효한 토큰
    if creds.valid:
        logger.info("✅ 토큰이 유효합니다.")
        
        # 만료 시간 정보 출력
        if creds.expiry:
            now = datetime.now(timezone.utc)
            expiry = creds.expiry.replace(tzinfo=timezone.utc) if creds.expiry.tzinfo is None else creds.expiry
            remaining = expiry - now
            logger.info(f"   Access Token 만료까지: {remaining}")
        
        return True, "토큰 유효"
    
    # 4. 알 수 없는 상태
    logger.warning("⚠️ 토큰 상태를 확인할 수 없습니다. 갱신을 시도합니다...")
    try:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
        with open(token_file, "wb") as f:
            pickle.dump(creds, f)
        logger.info("✅ 토큰 갱신 성공!")
        return True, "토큰 갱신 성공"
    except Exception as e:
        logger.error(f"❌ 토큰 갱신 실패: {e}")
        return False, f"토큰 갱신 실패: {e}"


def create_github_issue(error_reason: str):
    """토큰 만료 시 GitHub Issue를 자동 생성하여 알림"""
    github_token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    
    if not github_token or not repo:
        logger.warning("GitHub Issue 생성 불가 (GITHUB_TOKEN 또는 GITHUB_REPOSITORY 없음)")
        return
    
    try:
        import requests
        
        # 이미 열린 동일 이슈가 있는지 확인 (중복 방지)
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        existing = requests.get(
            f"https://api.github.com/repos/{repo}/issues",
            headers=headers,
            params={"state": "open", "labels": "token-expired"},
            timeout=10
        )
        
        if existing.ok and len(existing.json()) > 0:
            logger.info("⏭️ 이미 열린 토큰 만료 이슈가 있으므로 중복 생성하지 않습니다.")
            return
        
        # 새 이슈 생성
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        issue_data = {
            "title": f"🔴 OAuth 토큰 만료 — 자동 포스팅 중단됨 ({now_str})",
            "body": (
                f"## 🚨 자동 포스팅 실패 알림\n\n"
                f"**발생 시각**: {now_str}\n"
                f"**에러 원인**: {error_reason}\n\n"
                f"## 해결 방법\n\n"
                f"### 1단계: OAuth 동의 화면 프로덕션 전환 (최초 1회)\n"
                f"1. [Google Cloud Console](https://console.cloud.google.com/apis/credentials/consent?project=gov24-auto-blog) 접속\n"
                f"2. **'앱 게시(Publish App)'** 버튼 클릭\n\n"
                f"### 2단계: 토큰 재발급\n"
                f"```bash\n"
                f"del token.pickle\n"
                f"python main.py  # 브라우저 인증 진행\n"
                f"python export_token_base64.py\n"
                f"```\n\n"
                f"### 3단계: GitHub Secrets 업데이트\n"
                f"- `TOKEN_PICKLE_BASE64` 값을 `token_base64.txt` 내용으로 교체\n\n"
                f"### 4단계: 수동 실행으로 확인\n"
                f"- Actions 탭 → 'Daily Auto Blog Posting' → 'Run workflow' 클릭\n\n"
                f"---\n"
                f"이 이슈는 토큰 재발급 후 자동으로 닫힙니다."
            ),
            "labels": ["token-expired", "automated"]
        }
        
        response = requests.post(
            f"https://api.github.com/repos/{repo}/issues",
            headers=headers,
            json=issue_data,
            timeout=10
        )
        
        if response.ok:
            issue_url = response.json().get("html_url")
            logger.info(f"📢 GitHub Issue 생성 완료: {issue_url}")
        else:
            logger.warning(f"GitHub Issue 생성 실패: {response.status_code} {response.text}")
            
    except Exception as e:
        logger.warning(f"GitHub Issue 생성 중 오류: {e}")


def close_token_expired_issues():
    """토큰이 정상일 때, 열려있는 토큰 만료 이슈를 자동으로 닫기"""
    github_token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    
    if not github_token or not repo:
        return
    
    try:
        import requests
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        existing = requests.get(
            f"https://api.github.com/repos/{repo}/issues",
            headers=headers,
            params={"state": "open", "labels": "token-expired"},
            timeout=10
        )
        
        if existing.ok:
            for issue in existing.json():
                issue_number = issue["number"]
                # 이슈 닫기
                requests.patch(
                    f"https://api.github.com/repos/{repo}/issues/{issue_number}",
                    headers=headers,
                    json={
                        "state": "closed",
                        "state_reason": "completed"
                    },
                    timeout=10
                )
                # 코멘트 추가
                requests.post(
                    f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments",
                    headers=headers,
                    json={"body": "✅ 토큰이 정상 복구되었습니다. 자동 포스팅이 재개됩니다."},
                    timeout=10
                )
                logger.info(f"✅ 토큰 만료 이슈 #{issue_number} 자동 닫힘")
                
    except Exception as e:
        logger.warning(f"이슈 닫기 중 오류: {e}")


if __name__ == "__main__":
    is_valid, reason = check_token()
    
    if is_valid:
        close_token_expired_issues()
        logger.info("🎉 토큰 검증 완료. main.py 실행 가능합니다.")
        sys.exit(0)
    else:
        create_github_issue(reason)
        logger.error(f"🛑 토큰 검증 실패: {reason}")
        logger.error("   자동 포스팅을 진행할 수 없습니다.")
        sys.exit(1)
