# Google Cloud 배포 가이드

정부 정책 자동 블로그 포스팅 시스템을 Google Cloud에 배포하는 전체 가이드입니다.

## 📋 사전 준비

### 1. Google Cloud 계정 및 프로젝트

- [Google Cloud Console](https://console.cloud.google.com/) 접속
- 새 프로젝트 생성 또는 기존 프로젝트 선택
- 프로젝트 ID 기록

### 2. 결제 설정

- 결제 계정 연결 (무료 할당량 사용, 실제 과금 거의 없음)

### 3. gcloud CLI 설치

Windows PowerShell에서 실행:

```powershell
# Google Cloud SDK 설치
# https://cloud.google.com/sdk/docs/install 다운로드 및 설치

# 인증
gcloud auth login

# 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID
```

---

## 🔑 API 키 발급

### 1. Gemini API 키 발급

1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. "Get API Key" 클릭
3. API 키 복사 및 저장

---

## 🚀 배포 단계

### Step 1: 설정 파일 수정

`config.json` 파일을 실제 값으로 수정:

```json
{
  "gemini": {
    "api_key": "실제_Gemini_API_키",
    "model": "gemini-pro"
  },

  "gcs": {
    "bucket_name": "gov24-auto-blog",
    "project_id": "실제_GCP_프로젝트_ID"
  }
}
```

### Step 2: 배포 스크립트 수정

`deploy.sh` 파일 상단의 환경 변수 수정:

```bash
PROJECT_ID="your-gcp-project-id"  # 실제 값으로 변경
GEMINI_API_KEY="your_gemini_api_key"  # 실제 값으로 변경

```

### Step 3: 배포 실행

**Windows PowerShell에서 Git Bash 사용:**

```bash
# Git Bash 설치 필요: https://git-scm.com/downloads

# Git Bash 실행 후
cd d:/AI/gov24

# 실행 권한 부여
chmod +x deploy.sh setup_scheduler.sh

# 배포 실행
./deploy.sh
```

**또는 Windows에서 수동 배포:**

```powershell
cd d:\AI\gov24

# API 활성화
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com

# GCS 버킷 생성
gsutil mb -l asia-northeast3 gs://gov24-auto-blog

# Cloud Functions 배포
gcloud functions deploy gov-blog-auto-poster `
  --gen2 `
  --runtime=python311 `
  --region=asia-northeast3 `
  --source=. `
  --entry-point=main `
  --trigger-http `
  --allow-unauthenticated `
  --set-env-vars GEMINI_API_KEY=your_key,GCS_BUCKET=gov24-auto-blog `
  --timeout=540s `
  --memory=512MB
```

### Step 4: Cloud Scheduler 설정

```powershell
# 함수 URL 확인
gcloud functions describe gov-blog-auto-poster --region=asia-northeast3 --gen2 --format="value(serviceConfig.uri)"

# Scheduler 작업 생성 (1시간마다)
gcloud scheduler jobs create http gov-blog-hourly `
  --location=asia-northeast3 `
  --schedule="0 * * * *" `
  --uri="[위에서_확인한_URL]" `
  --http-method=GET `
  --time-zone="Asia/Seoul"
```

---

## ✅ 테스트 및 확인

### 1. 수동 실행 테스트

```powershell
# Scheduler 수동 트리거
gcloud scheduler jobs run gov-blog-hourly --location=asia-northeast3
```

### 2. 로그 확인

```powershell
# Cloud Functions 로그 확인
gcloud functions logs read gov-blog-auto-poster --region=asia-northeast3 --limit=50

# 실시간 로그 스트리밍
gcloud functions logs read gov-blog-auto-poster --region=asia-northeast3 --limit=50 --follow
```

### 3. Blogger 블로그 확인

블로그에서 새 포스트가 작성되었는지 확인

---

## 💰 비용 예상

**무료 할당량 (월간):**

- Cloud Functions: 200만 요청
- Cloud Storage: 5GB
- Gemini API: Pro 요금제 포함

**실제 사용량 (1시간마다 실행):**

- Cloud Functions: 약 720회/월
- Cloud Storage: 1MB 미만
- **예상 비용: 0원** (무료 할당량 내)

---

## 🔧 문제 해결

### 배포 실패 시

```powershell
# API 활성화 확인
gcloud services list --enabled

# 권한 확인
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

### 함수 실행 오류 시

```powershell
# 상세 로그 확인
gcloud functions logs read gov-blog-auto-poster --region=asia-northeast3 --limit=100
```

### Blogger 포스팅 실패 시

- Blogger API 인증 확인
- `credentials.json` 및 `token.pickle` 파일 확인

---

## 🛑 배포 중지/삭제

### Scheduler 중지

```powershell
gcloud scheduler jobs pause gov-blog-hourly --location=asia-northeast3
```

### 완전 삭제

```powershell
# Scheduler 삭제
gcloud scheduler jobs delete gov-blog-hourly --location=asia-northeast3

# Cloud Functions 삭제
gcloud functions delete gov-blog-auto-poster --region=asia-northeast3

# GCS 버킷 삭제
gsutil rm -r gs://gov24-auto-blog
```

---

## 📞 지원

- [Google Cloud 문서](https://cloud.google.com/functions/docs)
- [Blogger API 문서](https://developers.google.com/blogger)
- [Gemini API 문서](https://ai.google.dev/docs)
