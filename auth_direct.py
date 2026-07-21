from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/blogger']
credentials_file = "credentials.json"
token_file = "token.pickle"

print("=" * 60)
print("Blogger OAuth 인증을 시작합니다.")
print("웹 브라우저가 열리면 로그인 및 승인을 완료해주세요.")
print("=" * 60)

flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
creds = flow.run_local_server(port=0, open_browser=True)

with open(token_file, 'wb') as token:
    pickle.dump(creds, token)

print("✅ 인증 성공! token.pickle 파일이 성공적으로 생성되었습니다.")
