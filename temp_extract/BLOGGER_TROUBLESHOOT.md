# 🔧 Blogger 블로그 설정 확인 가이드

## 문제 상황

- ✅ OAuth 인증: 정상
- ✅ Blogger API 활성화: 정상
- ✅ 블로그 인식: 정상 (Stories of people)
- ✅ blog_id 일치: 정상
- ❌ **포스팅: 403 Forbidden 오류**

## 원인

**Blogger 블로그 자체 설정에서 API 접근이 제한되어 있을 가능성이 높습니다.**

---

## 해결 방법

### 1단계: Blogger 관리자 페이지 접속

1. [Blogger.com](https://www.blogger.com/) 접속
2. **<kr4ciy@gmail.com>** 계정으로 로그인 확인
3. **Stories of people** 블로그 선택

### 2단계: 블로그 설정 확인

#### 2-1. 기본 설정 확인

1. 좌측 메뉴 → **설정** 클릭
2. **기본** 탭에서 다음 확인:
   - 블로그 제목: Stories of people
   - 블로그 주소: story0people.blogspot.com

#### 2-2. 권한 설정 확인

1. 좌측 메뉴 → **설정** → **권한** 클릭
2. **블로그 작성자** 확인:
   - `kr4ciy@gmail.com`이 **관리자** 권한인지 확인
   - 다른 계정이 있다면 제거하거나 권한 확인

#### 2-3.  사용자 추가 (필요시)

1. 권한 페이지에서 **작성자 초대** 클릭
2. `kr4ciy@gmail.com` 추가
3. 권한: **관리자** 선택

### 3단계: 다른 해결책 시도

#### 방법 1: 새 블로그 생성 테스트

간단한 테스트로 새 블로그를 만들어서 포스팅이 되는지 확인:

1. Blogger에서 **새 블로그** 생성
2. 생성 후 블로그 목록 확인:

```powershell
python list_blogs.py
```

3. 새 블로그의 ID를 `config.json`에 입력
2. 포스팅 테스트

#### 방법 2: OAuth 범위 명시적 추가

`blogger_poster.py`의 SCOPES를 확장:

```python
SCOPES = [
    'https://www.googleapis.com/auth/blogger',
    'https://www.googleapis.com/auth/blogger.readonly'
]
```

변경 후 재인증:

```powershell
Remove-Item "d:\AI\gov24\token.pickle"
python test_blogger.py
```

#### 방법 3: Google Cloud Console 프로젝트 재생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. **새 프로젝트** 생성
3. Blogger API 활성화
4. **새 OAuth 클라이언트 ID** 생성
5. 새 `credentials.json` 다운로드 및 교체

---

## 빠른 테스트

간단한 READ 권한 테스트:

```powershell
# 블로그 정보 읽기만 시도
python -c "from blogger_poster import BloggerPoster; b = BloggerPoster(); print(b.get_blogs())"
```

이것이 성공하고 포스팅만 실패한다면, **WRITE 권한**에 문제가 있는 것입니다.

---

## 다음 단계

1. Blogger 설정 확인
2. 위 해결책 중 하나 시도
3. 계속 실패시 → 새 블로그 생성 또는 새 프로젝트 생성 고려
