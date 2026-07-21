@echo off
cd /d %~dp0
echo [Gov24 Blog] Daily High-Quality Posting starting...
python mass_publish_high_quality_v3.py
echo.
echo Process complete. Check mass_publish_v3.log for details.
pause
