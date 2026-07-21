@echo off
echo ==========================================
echo  Blogger Automation GCP Deployment
echo ==========================================

:: 설정 파라미터 (선배님 환경에 맞게 수정 필요)
set PROJECT_ID=petmind-10422
set REGION=asia-northeast3
set FUNCTION_NAME=gov-blog-auto-poster
set ENTRY_POINT=run_auto_blog
set BUCKET_NAME=gov24-blog-data-petmind-10422
set GEMINI_API_KEY=YOUR_GEMINI_API_KEY

echo [1] Ensuring proper GCP project...
gcloud config set project %PROJECT_ID%

echo [2] Deploying Cloud Function...
gcloud functions deploy %FUNCTION_NAME% ^
--gen2 ^
--runtime=python311 ^
--region=%REGION% ^
--source=. ^
--entry-point=%ENTRY_POINT% ^
--trigger-http ^
--allow-unauthenticated ^
--memory=512Mi ^
--timeout=540s ^
--set-env-vars "GCS_BUCKET=%BUCKET_NAME%,GEMINI_API_KEY=%GEMINI_API_KEY%"

echo.
echo 배포가 완료되었습니다! 
echo 트리거 URL을 복사하여 Cloud Scheduler에 등록하세요.
pause
