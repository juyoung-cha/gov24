# 🔧 Blogger API 403 Forbidden 오류 해결 가이드

## 문제 증상

```
ERROR: Blogger 포스팅 오류: <HttpError 403 when requesting 
https://blogger.googleapis.com/v3/blogs/3345493778668670443/posts?alt=json 
returned "The caller does not have permission"
```

## ✅ 확인 완료

- OAuth 토큰 권한: 정상 ✓
- credentials.json: 정상 ✓
- token.pickle: 정상 ✓

## ❌ 문제 원인

Google Cloud Console에서 Blogger API가 제대로 활성화되지 않았거나, 프로젝트 설정이 잘못되었습니다.

---

## 🔑 해결 방법 (단계별 진행)

### 1단계: Google Cloud Console 접속

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. **프로젝트: petmind-10422** 선택 확인
   - 화면 상단에서 현재 프로젝트 확인
   - `credentials.json`의 `project_id`와 일치해야 함

### 2단계: Blogger API 활성화 확인

#### 2-1. API 라이브러리로 이동

1. 좌측 메뉴 → **API 및 서비스** → **사용 설정된 API 및 서비스**
2. 검색창에 **"Blogger"** 입력
3. **Blogger API v3** 확인

#### 2-2. API가 없다면 활성화

1. 좌측 메뉴 → **API 및 서비스** → **라이브러리**
2. 검색창에 **"Blogger API"** 입력
3. **Blogger API v3** 클릭
4. **"사용 설정"** 버튼 클릭
   - ⚠️ **주의:** `petmind-10422` 프로젝트에서 활성화해야 함!

### 3단계: OAuth 동의 화면 확인

#### 3-1. 테스트 사용자 추가 확인

1. 좌측 메뉴 → **API 및 서비스** → **OAuth 동의 화면**
2. **"테스트 사용자"** 섹션 확인
3. 본인 Gmail 주소(`kr4ciy@gmail.com`)가 추가되어 있는지 확인
   - 없다면 **+ ADD USERS** 클릭하여 추가

#### 3-2. 범위(Scopes) 확인 (선택사항)

1. OAuth 동의 화면에서 **"수정"** 클릭
2. **"범위"** 단계로 이동
3. 다음 범위가 포함되어 있는지 확인:
   - `https://www.googleapis.com/auth/blogger`
   - 없다면 추가할 필요 없음 (OAuth 인증 시 자동으로 요청됨)

### 4단계: 재인증 필수

API 활성화 후 **반드시 재인증** 필요:

```powershell
# 1. 기존 토큰 삭제
Remove-Item "d:\AI\gov24\token.pickle"

# 2. 재인증 실행
python test_blogger.py
```

브라우저가 열리면:

1. "계속" 버튼 클릭 (앱이 확인되지 않음 경고는 정상)
2. **모든 권한 승인** → "계속" 클릭
3. 인증 완료 대기

### 5단계: 포스팅 테스트

```powershell
python test_blogger.py
```

예상 결과:

```
✅ 인증 성공!
✅ 성공: 1개 블로그 발견
✅ 성공: https://story0people.blogspot.com/...
```

---

## 🎯 빠른 체크리스트

- [ ] Google Cloud Console에서 `petmind-10422` 프로젝트 선택 확인
- [ ] **Blogger API v3** 활성화 확인
- [ ] OAuth 동의 화면에서 테스트 사용자(`kr4ciy@gmail.com`) 추가 확인
- [ ] `token.pickle` 삭제 후 재인증
- [ ] `python test_blogger.py` 실행하여 포스팅 테스트

---

## 💡 추가 참고사항

### 프로젝트 확인 방법

`credentials.json` 파일에서 확인:

```json
{
  "installed": {
    "project_id": "petmind-10422"  // 이 프로젝트에서 API 활성화 필요
  }
}
```

### API 활성화 확인 명령어 (gcloud CLI 설치 시)

```powershell
gcloud services list --enabled --project=petmind-10422 | Select-String "blogger"
```

결과에 `blogger.googleapis.com`이 표시되어야 함.

---

## 🔗 관련 링크

- [Google Cloud Console](https://console.cloud.google.com/)
- [Blogger API v3 문서](https://developers.google.com/blogger/docs/3.0/getting_started)
- [OAuth 2.0 가이드](https://developers.google.com/identity/protocols/oauth2)
