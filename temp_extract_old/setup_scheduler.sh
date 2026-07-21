#!/bin/bash

# Cloud Scheduler 설정 스크립트 (1시간마다 실행)

# 사용법: ./setup_scheduler.sh

# 환경 설정
PROJECT_ID="petmind-10422"
REGION="asia-northeast3"
SCHEDULER_JOB_NAME="gov-blog-hourly"
FUNCTION_NAME="gov-blog-auto-poster"

echo "==================================================="
echo "Cloud Scheduler 설정 시작"
echo "==================================================="

# 1. 함수 URL 가져오기
echo "Step 1: Cloud Functions URL 조회"
FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME --region=$REGION --gen2 --format="value(serviceConfig.uri)")

if [ -z "$FUNCTION_URL" ]; then
  echo "오류: Cloud Functions URL을 찾을 수 없습니다."
  echo "먼저 deploy.sh를 실행하세요."
  exit 1
fi

echo "함수 URL: $FUNCTION_URL"

# 2. 기존 스케줄러 작업 삭제 (있으면)
echo "Step 2: 기존 스케줄러 작업 확인"
gcloud scheduler jobs delete $SCHEDULER_JOB_NAME --location=$REGION --quiet 2>/dev/null || echo "기존 작업 없음"

# 3. 새 스케줄러 작업 생성 (6시간마다 실행: 00, 06, 12, 18시)
echo "Step 3: 스케줄러 작업 생성 (6시간마다 실행)"
gcloud scheduler jobs create http $SCHEDULER_JOB_NAME \
  --location=$REGION \
  --schedule="0 */6 * * *" \
  --uri="$FUNCTION_URL" \
  --http-method=GET \
  --time-zone="Asia/Seoul" \
  --attempt-deadline=540s \
  --description="정부 정책 자동 블로그 포스팅 (6시간마다)"

echo ""
echo "==================================================="
echo "Cloud Scheduler 설정 완료!"
echo "==================================================="
echo ""
echo "스케줄: 매시간 정각 (00분)"
echo "다음 실행 시간: $(date -d '+1 hour' '+%Y-%m-%d %H:00:00')"
echo ""
echo "수동 실행 테스트:"
echo "gcloud scheduler jobs run $SCHEDULER_JOB_NAME --location=$REGION"
echo ""
echo "로그 확인:"
echo "gcloud functions logs read $FUNCTION_NAME --region=$REGION --limit=50"
