#!/bin/bash
# ===============================================
# Pomodoro Timer - macOS Build Script
# ===============================================
set -e

echo "==============================================="
echo "Pomodoro Timer - macOS Build"
echo "==============================================="

# Step 0: dependencies
echo "Step 0: Checking dependencies..."
python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet -r requirements.txt pyinstaller

echo "Step 0b: Verifying PySide6 is importable..."
python3 -c "import PySide6; print('PySide6 OK:', PySide6.__version__)"

echo "Step 0c: Verifying PyObjC is importable..."
python3 -c "import objc, AppKit; print('PyObjC OK')" || \
    echo "WARNING: PyObjC not importable -- the floating widget's native always-on-top fix won't work. Run: python3 -m pip install pyobjc-framework-Cocoa"

# Step 1: icon
echo ""
echo "Step 1: Creating icon..."
python3 create_icon.py || echo "WARNING: Icon creation had issues, continuing anyway..."

# Step 2: build
echo ""
echo "Step 2: Cleaning previous build artifacts..."
rm -rf build dist PomodoroTimer.spec

echo ""
echo "Step 3: Building .app bundle..."
ICON_ARG=()
if [ -f "pomodoro_icon.icns" ]; then
    echo "Using tomato icon (pomodoro_icon.icns)"
    ICON_ARG=(--icon=pomodoro_icon.icns)
else
    echo "No .icns icon found, building without a custom icon"
fi

# --collect-all PySide6 force-bundles every PySide6 submodule, Qt
# plugin, and shared library instead of relying on PyInstaller's
# static import analysis, which avoids "No module named PySide6" at
# runtime after an apparently successful build. Likewise for PyObjC:
# without --collect-all objc/AppKit/Foundation, the native
# always-on-top code silently ImportErrors inside the packaged .app
# (invisible, since --windowed apps have no console) and falls back to
# a much less reliable behavior.
python3 -m PyInstaller \
    --windowed \
    --clean --noconfirm \
    --collect-all PySide6 \
    --collect-all shiboken6 \
    --collect-all objc \
    --collect-all AppKit \
    --collect-all Foundation \
    --name "PomodoroTimer" \
    "${ICON_ARG[@]}" \
    pomodoro_pyside6.py

if [ ! -d "dist/PomodoroTimer.app" ]; then
    echo "ERROR: Build failed - dist/PomodoroTimer.app not found"
    exit 1
fi

# Step 4: distribution folder
echo ""
echo "Step 4: Creating distribution folder..."
DIST_DIR="PomodoroTimer_Mac"
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"
cp -R "dist/PomodoroTimer.app" "$DIST_DIR/"
[ -f "pomodoro_icon.png" ] && cp "pomodoro_icon.png" "$DIST_DIR/"

cat > "$DIST_DIR/README.txt" << EOF
Pomodoro Timer (macOS)

Features
- Work and break timer with customizable durations
- Floating widget mode with built-in controls
- Weekly statistics and progress tracking
- Menu bar (system tray) integration
- Auto-start break sessions
- Responsive UI with font size adjustment

Usage
1. Move PomodoroTimer.app to /Applications (optional)
2. Double-click PomodoroTimer.app to run
   - If macOS blocks it as "unidentified developer": right-click the app
     -> Open, then confirm in the dialog. This is only needed the first
     time, since the app isn't notarized/signed with an Apple Developer ID.
3. Configure work/break times in Settings
4. Click Start - automatically switches to widget mode
5. Use widget controls: Play/Pause, Reset, drag to move
6. Double-click widget timer area to return to main window

Widget Controls
- Click to Start/Pause timer
- Drag timer area to move
- Drag bottom-right corner to resize

Data is stored in ~/PomodoroData and settings in ~/.pomodoro/config.json

Generated: $(date)
EOF

echo ""
echo "==============================================="
echo "BUILD COMPLETE!"
echo "==============================================="
echo ""
echo "Distribution folder: $DIST_DIR/"
echo "App bundle: $DIST_DIR/PomodoroTimer.app"
echo ""
read -p "Test the application now? (y/n) " choice
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo "Starting application..."
    open "$DIST_DIR/PomodoroTimer.app"
fi

echo ""
echo "Ready to distribute!"
echo "Share the entire '$DIST_DIR' folder, or zip PomodoroTimer.app."
