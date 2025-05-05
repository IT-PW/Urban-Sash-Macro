@echo off
set /p message="Enter commit message: "
echo.

git add -A
git commit -m "%message%"
git push origin main
