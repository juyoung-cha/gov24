# Google Blogger API 설정 가이드

Google Blogger를 사용하여 자동 포스팅하는 방법을 안내합니다.

## 📋 사전 준비

- Google 계정
- Blogger 블로그 (없으면 생성)

---

## 🌐 1단계: Blogger 블로그 생성

### 1-1. Blogger 접속
<https://www.blogger.com> 접속 후 Google 계정으로 로그인

### 1-2. 블로그 만들기

1. "블로그 만들기" 클릭
2. 블로그 이름 입력 (예: "정부정책블로그")
3. 블로그 주소 입력 (예: "gov-policy-korea")
   - 최종 주소: `gov-policy-korea.blogspot.com`
4. "블로그 만들기" 완료

---

## 🔑 2단계: Google Cloud OAuth 인증 설정

### 2-1. Google Cloud Console 접속
<https://console.cloud.google.com/> 접속

### 2-2. 프로젝트 선택

- 기존 프로젝트 선택 (Gemini API 사용 중인 프로젝트)
- 또는 새 프로젝트 생성

### 2-3. Blogger API 활성화

1. 좌측 메뉴: **API 및 서비스** > **라이브러리**
2. 검색창에 **"Blogger API"** 입력
3. **Blogger API v3** 선택
4. **"사용 설정"** 클릭

### 2-4. OAuth 동의 화면 구성

1. 좌측 메뉴: **API 및 서비스** > **OAuth 동의 화면**
2. **외부** 선택 → **만들기**
3. 필수 정보 입력:
   - 앱 이름: `정부정책블로그`
   - 사용자 지원 이메일: 본인 Gmail
   - 개발자 연락처 정보: 본인 Gmail
4. **저장 후 계속** 클릭
5. 범위 추가는 건너뛰기
6. 테스트 사용자 추가:
   - **+ ADD USERS** 클릭
   - 본인 Gmail 주소 입력
7. **저장 후 계속**

### 2-5. OAuth 클라이언트 ID 만들기

1. 좌측 메뉴: **API 및 서비스** > **사용자 인증 정보**
2. **+ 사용자 인증 정보 만들기** → **OAuth 클라이언트 ID** 선택
3. 애플리케이션 유형: **데스크톱 앱** 선택
4. 이름: `정부정책블로그 데스크톱` 입력
5. **만들기** 클릭

### 2-6. JSON 다운로드

1. 생성된 클라이언트 ID 옆의 **다운로드 아이콘** (↓) 클릭
2. JSON 파일이 다운로드됨
3. 파일 이름을 **`credentials.json`**으로 변경
4. `d:\AI\gov24` 폴더에 복사

---

## ✅ 3단계: 로컬 테스트

### 3-1. 필요한 패키지 설치

```powershell
cd d:\AI\gov24
pip install google-auth-oauthlib google-api-python-client
```

### 3-2. 테스트 실행

```powershell
python test_blogger.py
```

### 3-3. OAuth 인증 플로우

1. 명령어 실행 시 **브라우저가 자동으로 열림**
2. Google 계정 선택
3. **"앱이 확인되지 않음"** 경고 화면이 나타남:
   - **"고급"** 클릭
   - **"정부정책블로그(안전하지 않음)로 이동"** 클릭
4. 권한 승인:
   - "Blogger 블로그 관리" 권한 요청
   - **"계속"** 클릭
5. 인증 완료!

### 3-4. 결과 확인

- 콘솔에 블로그 목록이 표시됨
- 테스트 글이 임시저장됨
- Blogger 관리 페이지에서 확인 가능

---

## 📝 4단계: config.json 설정 (선택)

특정 블로그 ID를 지정하고 싶다면 (여러 블로그가 있는 경우):

```json
{
  "blogger": {
    "blog_id": "1234567890123456789",
    "credentials_file": "credentials.json"
  }
}
```

블로그 ID는 `test_blogger.py` 실행 시 출력됩니다.

---

## 🔧 문제 해결

### credentials.json 파일이 없다는 오류

- Google Cloud Console에서 OAuth 클라이언트 ID JSON 다운로드
- 파일명을 정확히 `credentials.json`으로 변경
- `d:\AI\gov24` 폴더에 위치

### "앱이 확인되지 않음" 경고

- 정상입니다! 본인이 만든 앱이므로 안전
- "고급" → "앱으로 이동" 클릭하여 진행

### 블로그가 없다는 오류

- <https://www.blogger.com> 에서 블로그 먼저 생성

### API가 활성화되지 않았다는 오류

- Google Cloud Console에서 Blogger API v3 활성화 확인

---

## 📞 참고 자료

- [Blogger API 공식 문서](https://developers.google.com/blogger/docs/3.0/getting_started)
- [OAuth 2.0 인증 가이드](https://developers.google.com/identity/protocols/oauth2)
- [Blogger 고객센터](https://support.google.com/blogger/)

---

## 🎉 다음 단계

테스트 성공 후:

1. `python main.py`로 전체 시스템 테스트
2. Google Cloud Functions 배포 ([DEPLOYMENT_GUIDE.md](file:///d:/AI/gov24/DEPLOYMENT_GUIDE.md) 참조)
