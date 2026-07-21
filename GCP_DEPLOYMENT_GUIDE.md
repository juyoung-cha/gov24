# GCP(Google Cloud Platform) 서버 배포 가이드

선배님의 컴퓨터를 꺼두어도 365일 자동으로 블로그 포스팅이 이루어지게 하는 클라우드 배포 방법입니다.

---

## 1. 사전 준비 (GCP 콘솔)

1. **[GCP 콘솔](https://console.cloud.google.com/)** 접속 및 프로젝트 선택.
2. **API 활성화**: 다음 API들을 사용 설정합니다.
   - Cloud Functions API
   - Cloud Scheduler API
   - Cloud Build API
   - Artifact Registry API
3. **GCS 버킷 생성**: `seen.json` 등을 저장할 버킷을 하나 만듭니다 (예: `gov24-blog-storage`).

## 2. 권한 설정

- Cloud Functions의 서비스 계정에 **'Storage 객체 관리자'** 권한을 부여해야 합니다.

## 3. 배포 실행 (제가 준비한 스크립트)

선배님의 터미널(PowerShell)에서 아래 명령어를 입력하면 자동으로 클라우드에 업로드됩니다.

```bash
# gcloud CLI가 설치되어 있어야 합니다.
.\deploy_gcp.bat
```

## 4. 자동 스케줄 등록

배포가 완료되면 **Cloud Scheduler**에서 다음과 같이 설정합니다.

- **빈도**: `0 1 * * *` (매일 새벽 1시 실행)
- **타겟**: HTTP
- **URL**: Cloud Function의 트리거 URL
- **인증**: OIDC 토큰 사용

---

**[주의 사항]**

- 클라우드 환경에서는 브라우저 로그인을 할 수 없으므로, **로컬의 `token.pickle` 파일**이 반드시 GCS 버킷에 먼저 업로드되어 있어야 합니다.
- 제가 이 과정을 조금 더 자동화할 수 있는 스크립트를 추가로 작성해 드릴 예정입니다.
