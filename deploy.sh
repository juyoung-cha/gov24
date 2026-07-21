#!/bin/bash

# Google Cloud Functions 배포 스크립트

# 사용법: ./deploy.sh

# 환경 설정
PROJECT_ID="petmind-10422"
REGION="asia-northeast3"  # 서울 리전
FUNCTION_NAME="gov-blog-auto-poster"
RUNTIME="python311"
ENTRY_POINT="run_auto_blog"
GCS_BUCKET="gov24-blog-data-petmind-10422"
GEMINI_API_KEY="AIzaSyDCkhHX4OmenOKMBrI_68vdH2YFzG0yHUk"


echo "==================================================="
echo "Google Cloud Functions 배포 시작"
echo "==================================================="

# 1. GCP 프로젝트 설정
echo "Step 1: GCP 프로젝트 설정"
gcloud config set project $PROJECT_ID

# 2. 필요한 API 활성화
echo "Step 2: 필요한 API 활성화"
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 3. GCS 버킷 생성 (이미 있으면 건너뜀)
echo "Step 3: GCS 버킷 생성"
gsutil mb -l $REGION gs://$GCS_BUCKET 2>/dev/null || echo "버킷이 이미 존재합니다"

# 4. Cloud Functions 배포
echo "Step 4: Cloud Functions 배포"
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime=$RUNTIME \
  --region=$REGION \
  --source=. \
  --entry-point=$ENTRY_POINT \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars GCS_BUCKET=$GCS_BUCKET,GEMINI_API_KEY=$GEMINI_API_KEY \
  --timeout=540s \
  --memory=512MB

echo ""
echo "==================================================="
echo "배포 완료!"
echo "==================================================="
echo ""
echo "함수 URL을 확인하세요:"
gcloud functions describe $FUNCTION_NAME --region=$REGION --gen2 --format="value(serviceConfig.uri)"
echo ""
echo "다음 단계: Cloud Scheduler 설정"
echo "./setup_scheduler.sh 실행"
