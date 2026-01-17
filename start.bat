@echo off
cd /d "C:\Users\Company i7\Desktop\altutex-main"

echo ✅ Starting Flask API...
start "FLASK API" cmd /k python server.py

echo ✅ Starting Frontend (HTML)...
start "FRONTEND HTML" cmd /k python -m http.server 8080 --bind 0.0.0.0

exit