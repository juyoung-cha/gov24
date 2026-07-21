@echo off
setlocal
cd /d "d:\AI\gov24"

echo ========================================== >> auto_blog_run.log
echo [%date% %time%] 자동 포스팅 작업 시작 >> auto_blog_run.log

python main.py >> auto_blog_run.log 2>&1

if %ERRORLEVEL% equ 0 (
    echo [%date% %time%] 작업 성공 완료 >> auto_blog_run.log
) else (
    echo [%date% %time%] 작업 중 오류 발생 (Exit Code: %ERRORLEVEL%) >> auto_blog_run.log
)

echo [%date% %time%] 자동 포스팅 작업 종료 >> auto_blog_run.log
echo ========================================== >> auto_blog_run.log
echo. >> auto_blog_run.log

endlocal
