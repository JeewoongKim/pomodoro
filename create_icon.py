#!/usr/bin/env python3
"""
Create a tomato icon for the Pomodoro Timer

Generates:
  - pomodoro_icon.ico  (Windows executable icon)
  - pomodoro_icon.icns (macOS app bundle icon, macOS only)
  - pomodoro_icon.png  (preview / Linux / fallback icon)
"""

import platform
import shutil
import subprocess
import tempfile
from pathlib import Path


def _draw_tomato(draw, size):
    """Draw a single tomato icon frame into an existing ImageDraw canvas."""
    margin = max(2, size // 16)
    tomato_size = size - margin * 2
    stem_height = max(4, size // 8)
    stem_width = max(6, size // 6)

    # Draw tomato body (red circle)
    tomato_rect = [margin, margin + stem_height // 2,
                   margin + tomato_size, margin + tomato_size + stem_height // 2]
    draw.ellipse(tomato_rect,
                fill=(220, 38, 38, 255),  # Nice red color
                outline=(180, 30, 30, 255),
                width=max(1, size // 32))

    # Draw tomato highlight
    highlight_size = tomato_size // 4
    highlight_x = margin + tomato_size // 3
    highlight_y = margin + stem_height // 2 + tomato_size // 4
    draw.ellipse([highlight_x, highlight_y,
                 highlight_x + highlight_size, highlight_y + highlight_size // 2],
                fill=(255, 120, 120, 180))

    # Draw stem (green)
    stem_x = margin + tomato_size // 2 - stem_width // 2
    stem_y = margin
    draw.rectangle([stem_x, stem_y,
                   stem_x + stem_width, stem_y + stem_height],
                  fill=(34, 139, 34, 255))

    # Draw small leaves
    leaf_size = max(2, size // 16)
    draw.ellipse([stem_x - leaf_size, stem_y + stem_height // 3,
                 stem_x + leaf_size, stem_y + stem_height // 3 + leaf_size],
                fill=(46, 125, 50, 255))
    draw.ellipse([stem_x + stem_width - leaf_size, stem_y + stem_height // 3,
                 stem_x + stem_width + leaf_size, stem_y + stem_height // 3 + leaf_size],
                fill=(46, 125, 50, 255))


def create_icns_icon():
    """Build pomodoro_icon.icns for macOS app bundles.

    Uses the macOS-native `iconutil` tool (ships with every Mac), so
    this only runs when executed on macOS. On other platforms it's a
    harmless no-op — the .ico/.png icons are used instead.
    """
    if platform.system() != "Darwin":
        return False
    if shutil.which("iconutil") is None:
        print("⚠️  iconutil not found, skipping .icns creation")
        return False

    try:
        from PIL import Image, ImageDraw

        # macOS iconset naming convention: base size + @2x retina variant
        iconset_sizes = [16, 32, 64, 128, 256, 512, 1024]

        with tempfile.TemporaryDirectory() as tmp:
            iconset_dir = Path(tmp) / "pomodoro.iconset"
            iconset_dir.mkdir()

            for size in iconset_sizes:
                img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                _draw_tomato(ImageDraw.Draw(img), size)

                if size <= 512:
                    img.save(iconset_dir / f"icon_{size}x{size}.png")
                if size >= 32:
                    half = size // 2
                    img.resize((half, half), Image.LANCZOS).save(
                        iconset_dir / f"icon_{half}x{half}@2x.png"
                    ) if size != 32 else None

            # Fill in the standard filenames iconutil expects
            mapping = {
                16: "icon_16x16.png",
                32: ["icon_16x16@2x.png", "icon_32x32.png"],
                64: "icon_32x32@2x.png",
                128: "icon_128x128.png",
                256: ["icon_128x128@2x.png", "icon_256x256.png"],
                512: ["icon_256x256@2x.png", "icon_512x512.png"],
                1024: "icon_512x512@2x.png",
            }
            for size, names in mapping.items():
                img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                _draw_tomato(ImageDraw.Draw(img), size)
                for name in ([names] if isinstance(names, str) else names):
                    img.save(iconset_dir / name)

            subprocess.run(
                ["iconutil", "-c", "icns", str(iconset_dir),
                 "-o", "pomodoro_icon.icns"],
                check=True
            )

        print("✅ Icon created: pomodoro_icon.icns")
        return True
    except Exception as e:
        print(f"❌ Error creating .icns icon: {e}")
        return False


def create_tomato_icon():
    """Create a nice tomato icon"""
    try:
        from PIL import Image, ImageDraw
        print("Creating tomato icon...")
        
        # Create icon with multiple sizes for better quality
        sizes = [16, 32, 48, 64, 128, 256]
        images = []
        
        for size in sizes:
            # Create image with transparent background
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            _draw_tomato(ImageDraw.Draw(img), size)
            images.append(img)
        
        # Save as ICO file with multiple sizes
        images[0].save('pomodoro_icon.ico', format='ICO', 
                      sizes=[(img.width, img.height) for img in images])
        print("✅ Icon created: pomodoro_icon.ico")
        
        # Also save as PNG for preview
        images[-1].save('pomodoro_icon.png', format='PNG')
        print("✅ Preview created: pomodoro_icon.png")
        
        return True
        
    except ImportError:
        print("⚠️  Pillow not installed. Installing...")
        import subprocess
        import sys
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
            print("✅ Pillow installed. Please run this script again.")
            return False
        except Exception as e:
            print(f"❌ Failed to install Pillow: {e}")
            return False
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        return False

def create_simple_icon():
    """Create a simple colored square icon as fallback"""
    try:
        from PIL import Image, ImageDraw
        
        # Create simple 64x64 icon
        img = Image.new('RGBA', (64, 64), (220, 38, 38, 255))
        draw = ImageDraw.Draw(img)
        
        # Add white circle in center
        draw.ellipse([16, 16, 48, 48], fill=(255, 255, 255, 255))
        
        # Add timer symbol
        draw.line([32, 20, 32, 32], fill=(220, 38, 38, 255), width=3)
        draw.line([32, 32, 40, 32], fill=(220, 38, 38, 255), width=2)
        
        img.save('simple_icon.ico', format='ICO')
        print("✅ Simple icon created: simple_icon.ico")
        return True
        
    except Exception as e:
        print(f"❌ Error creating simple icon: {e}")
        return False

def main():
    """Create icon for the application"""
    print("🍅 Creating Pomodoro Timer Icon")
    print("=" * 35)
    
    # Try to create nice tomato icon
    if create_tomato_icon():
        print("\n🎉 Tomato icon created successfully!")
        print("Files created:")
        print("  - pomodoro_icon.ico (for Windows executable)")
        print("  - pomodoro_icon.png (preview / Linux)")

        if platform.system() == "Darwin":
            create_icns_icon()
    else:
        print("\n⚠️  Trying fallback simple icon...")
        if create_simple_icon():
            print("✅ Simple icon created as fallback")
        else:
            print("❌ Icon creation failed")
            print("You can use any .ico/.icns file as icon")

    print("\nTo use the icon in build:")
    if platform.system() == "Darwin":
        print("  python -m PyInstaller --onefile --windowed --icon=pomodoro_icon.icns --name=PomodoroTimer pomodoro_pyside6.py")
    else:
        print("  python -m PyInstaller --onefile --windowed --icon=pomodoro_icon.ico pomodoro_pyside6.py")


if __name__ == "__main__":
    main()
