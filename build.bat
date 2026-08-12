@echo off
chcp 65001 >nul
echo ===============================================
echo Pomodoro Timer - Final Build with Icon
echo ===============================================

echo Step 0: Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies. Check the "python" and
    echo "pip" commands above point to the same Python you intend to
    echo build with.
    pause
    exit /b 1
)

echo.
echo Step 0b: Verifying PySide6 is importable...
python -c "import PySide6; print('PySide6 OK:', PySide6.__version__)"
if %errorlevel% neq 0 (
    echo ERROR: PySide6 did not import correctly even after install.
    echo This is almost always caused by having more than one Python
    echo installed and "python"/"pip" pointing to different ones.
    echo Try: python -m pip install --force-reinstall PySide6
    pause
    exit /b 1
)

echo.
echo Step 1: Creating icon...
python create_icon.py
if %errorlevel% neq 0 (
    echo WARNING: Icon creation had issues, continuing anyway...
)

echo.
echo Step 2: Cleaning previous build artifacts...
REM Stale build/dist folders from a broken earlier build are a common
REM cause of a "successful" build that still fails to import PySide6
REM at runtime, so always start clean.
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist PomodoroTimer-Final.spec del /q PomodoroTimer-Final.spec

echo.
echo Step 3: Building with icon...
REM --collect-all PySide6 is the officially recommended PyInstaller
REM flag for PySide6 apps: it force-bundles every PySide6 submodule,
REM Qt plugin, and shared library instead of relying on PyInstaller's
REM static import analysis, which is what "No module named PySide6"
REM at runtime usually means went wrong.
set ICON_ARG=
if exist pomodoro_icon.ico (
    echo Using custom tomato icon
    set ICON_ARG=--icon=pomodoro_icon.ico
) else if exist simple_icon.ico (
    echo Using simple icon
    set ICON_ARG=--icon=simple_icon.ico
) else (
    echo No icon found, building without icon
)

python -m PyInstaller --onefile --windowed --clean --noconfirm ^
    --collect-all PySide6 ^
    --collect-all shiboken6 ^
    %ICON_ARG% --name=PomodoroTimer-Final pomodoro_pyside6.py

if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

if not exist "dist\PomodoroTimer-Final.exe" (
    echo ERROR: Build reported success but dist\PomodoroTimer-Final.exe
    echo is missing. Something is wrong with the PyInstaller environment.
    pause
    exit /b 1
)

echo.
echo Step 4: Creating distribution folder...
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
