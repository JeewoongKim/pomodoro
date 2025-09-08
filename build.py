#!/usr/bin/env python3
"""
Build script for creating executables for Windows and macOS
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def create_icons():
    """Create simple icons for the application"""
    try:
        from PIL import Image, ImageDraw
        
        icons_dir = Path("resources/icons")
        icons_dir.mkdir(parents=True, exist_ok=True)
        
        # Create settings icon
        img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Simple gear shape
        draw.ellipse([6, 6, 26, 26], fill=(100, 100, 100, 255))
        draw.ellipse([10, 10, 22, 22], fill=(255, 255, 255, 0))
        img.save(icons_dir / "settings.png")
        
        # Create stats icon
        img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Simple bar chart
        draw.rectangle([4, 20, 8, 28], fill=(100, 100, 100, 255))
        draw.rectangle([10, 15, 14, 28], fill=(100, 100, 100, 255))
        draw.rectangle([16, 10, 20, 28], fill=(100, 100, 100, 255))
        draw.rectangle([22, 18, 26, 28], fill=(100, 100, 100, 255))
        img.save(icons_dir / "stats.png")
        
        # Create back arrow icon
        img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Simple arrow
        draw.polygon([(8, 16), (16, 8), (16, 12), (24, 12), (24, 20), (16, 20), (16, 24)], fill=(100, 100, 100, 255))
        img.save(icons_dir / "back.png")
        
        # Create tray icon
        img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Simple tomato shape
        draw.ellipse([4, 8, 28, 28], fill=(220, 50, 50, 255))
        draw.ellipse([12, 4, 20, 12], fill=(50, 150, 50, 255))
        img.save(icons_dir / "tray_icon.png")
        
        print("✅ Icons created successfully")
        
    except ImportError:
        print("⚠️  Pillow not installed, creating placeholder icons")
        icons_dir = Path("resources/icons")
        icons_dir.mkdir(parents=True, exist_ok=True)
        
        # Create empty PNG files as placeholders
        for icon_name in ["settings.png", "stats.png", "back.png", "tray_icon.png"]:
            (icons_dir / icon_name).touch()

def create_stylesheet():
    """Create main stylesheet"""
    styles_dir = Path("resources/styles")
    styles_dir.mkdir(parents=True, exist_ok=True)
    
    stylesheet = """
QMainWindow {
    background-color: white;
    border-radius: 15px;
}

QPushButton {
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 10px 20px;
    text-align: center;
    font-size: 14px;
    border-radius: 8px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #45a049;
}

QPushButton:pressed {
    background-color: #3d8b40;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
}

QLabel {
    color: #333333;
}

QGroupBox {
    font-weight: bold;
    border: 2px solid #cccccc;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
}

QSpinBox {
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 5px;
    font-size: 12px;
}

QSlider::groove:horizontal {
    border: 1px solid #bbb;
    height: 10px;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #4CAF50;
    border: 1px solid #5c5c5c;
    width: 18px;
    margin: -2px 0;
    border-radius: 3px;
}
"""
    
    with open(styles_dir / "main.qss", 'w') as f:
        f.write(stylesheet)
    
    print("✅ Stylesheet created successfully")

def build_executable():
    """Build executable using PyInstaller"""
    system = platform.system().lower()
    
    # Ensure we're in the right directory
    if not Path("src/main.py").exists():
        print("❌ src/main.py not found. Please run this script from the project root.")
        return False
    
    # Create resources
    create_icons()
    create_stylesheet()
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "PomodoroTimer",
        "--add-data", "resources;resources" if system == "windows" else "resources:resources",
        "--icon", "resources/icons/tray_icon.png" if Path("resources/icons/tray_icon.png").exists() else None,
    ]
    
    # Remove None values
    cmd = [arg for arg in cmd if arg is not None]
    
    # Add the main script
    cmd.append("src/main.py")
    
    print(f"🔨 Building executable for {system}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        print(result.stdout)
        
        # Move executable to appropriate dist folder
        dist_dir = Path("dist") / system
        dist_dir.mkdir(parents=True, exist_ok=True)
        
        if system == "windows":
            exe_name = "PomodoroTimer.exe"
        else:
            exe_name = "PomodoroTimer"
            
        source_exe = Path("dist") / exe_name
        target_exe = dist_dir / exe_name
        
        if source_exe.exists():
            shutil.move(str(source_exe), str(target_exe))
            print(f"✅ Executable moved to {target_exe}")
        
        # Clean up PyInstaller files
        for cleanup_dir in ["build", "__pycache__"]:
            if Path(cleanup_dir).exists():
                shutil.rmtree(cleanup_dir)
                
        if Path("PomodoroTimer.spec").exists():
            os.remove("PomodoroTimer.spec")
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main build function"""
    print("🚀 Starting build process...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Build executable
    if build_executable():
        print("🎉 Build process completed successfully!")
        print(f"📁 Check the dist/{platform.system().lower()} directory for your executable")
    else:
        print("💥 Build process failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
