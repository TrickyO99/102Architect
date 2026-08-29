@echo off
cd /d "%~dp0"
echo Building the 3x3 transformation matrix for translating point (3,4) by vector (1,2)...
python 102architect 3 4 -t 1 2
echo.
pause
