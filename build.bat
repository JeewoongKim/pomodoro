@echo off
chcp 65001 >nul
echo ===============================================
echo Pomodoro Timer - Final Build with Icon
echo ===============================================

echo Step 1: Creating icon...
python create_icon.py
if %errorlevel% neq 0 (
    echo WARNING: Icon creation had issues, continuing anyway...
)

echo.
echo Step 2: Building with icon...
if exist pomodoro_icon.ico (
    echo Using custom tomato icon
    python -m PyInstaller --onefile --windowed --icon=pomodoro_icon.ico --name=PomodoroTimer-Final pomodoro_pyside6.py
) else if exist simple_icon.ico (
    echo Using simple icon
    python -m PyInstaller --onefile --windowed --icon=simple_icon.ico --name=PomodoroTimer-Final pomodoro_pyside6.py
) else (
    echo No icon found, building without icon
    python -m PyInstaller --onefile --windowed --name=PomodoroTimer-Final pomodoro_pyside6.py
)

if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo Step 3: Creating distribution folder...
if not exist "PomodoroTimer_Final" mkdir "PomodoroTimer_Final"
copy "dist\PomodoroTimer-Final.exe" "PomodoroTimer_Final\"
if exist pomodoro_icon.png copy "pomodoro_icon.png" "PomodoroTimer_Final\"

echo.
echo Creating README...
(
echo # Pomodoro Timer
echo.
echo ## Features
echo - Work and break timer with customizable durations
echo - Floating widget mode with built-in controls
echo - Weekly statistics and progress tracking  
echo - System tray integration
echo - Auto-start break sessions
echo - Responsive UI with font size adjustment
echo.
echo ## Usage
echo 1. Run PomodoroTimer-Final.exe
echo 2. Configure work/break times in Settings
echo 3. Click Start - automatically switches to widget mode
echo 4. Use widget controls: Play/Pause, Reset, Expand
echo 5. Double-click widget timer area to return to main window
echo.
echo ## Widget Controls
echo - Start/Pause timer
echo - Reset timer
echo - Expand to main window
echo - Drag timer area to move
echo - Drag bottom-right corner to resize
echo.
echo Generated: %DATE% %TIME%
) > "PomodoroTimer_Final\README.txt"

echo.
echo ===============================================
echo BUILD COMPLETE!
echo ===============================================
echo.
echo Distribution folder: PomodoroTimer_Final\
echo Executable: PomodoroTimer-Final.exe
echo Icon: %~dp0pomodoro_icon.png (preview)
echo.
echo Test the application? (y/n)
set /p choice=
if /i "%choice%"=="y" (
    echo Starting application...
    start "PomodoroTimer_Final\PomodoroTimer-Final.exe"
)

echo.
echo Ready to distribute!
echo Share the entire 'PomodoroTimer_Final' folder.
pause
