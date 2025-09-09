#!/usr/bin/env python3
"""
Create a tomato icon for the Pomodoro Timer
"""

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
            draw = ImageDraw.Draw(img)
            
            # Calculate proportions based on size
            margin = max(2, size // 16)
            tomato_size = size - margin * 2
            stem_height = max(4, size // 8)
            stem_width = max(6, size // 6)
            
            # Draw tomato body (red circle)
            tomato_rect = [margin, margin + stem_height//2, 
                          margin + tomato_size, margin + tomato_size + stem_height//2]
            draw.ellipse(tomato_rect, 
                        fill=(220, 38, 38, 255),  # Nice red color
                        outline=(180, 30, 30, 255), 
                        width=max(1, size//32))
            
            # Draw tomato highlight
            highlight_size = tomato_size // 4
            highlight_x = margin + tomato_size // 3
            highlight_y = margin + stem_height//2 + tomato_size // 4
            draw.ellipse([highlight_x, highlight_y, 
                         highlight_x + highlight_size, highlight_y + highlight_size//2],
                        fill=(255, 120, 120, 180))
            
            # Draw stem (green)
            stem_x = margin + tomato_size//2 - stem_width//2
            stem_y = margin
            draw.rectangle([stem_x, stem_y, 
                           stem_x + stem_width, stem_y + stem_height],
                          fill=(34, 139, 34, 255))
            
            # Draw small leaves
            leaf_size = max(2, size // 16)
            # Left leaf
            draw.ellipse([stem_x - leaf_size, stem_y + stem_height//3,
                         stem_x + leaf_size, stem_y + stem_height//3 + leaf_size],
                        fill=(46, 125, 50, 255))
            # Right leaf  
            draw.ellipse([stem_x + stem_width - leaf_size, stem_y + stem_height//3,
                         stem_x + stem_width + leaf_size, stem_y + stem_height//3 + leaf_size],
                        fill=(46, 125, 50, 255))
            
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
        print("  - pomodoro_icon.ico (for executable)")  
        print("  - pomodoro_icon.png (preview)")
    else:
        print("\n⚠️  Trying fallback simple icon...")
        if create_simple_icon():
            print("✅ Simple icon created as fallback")
        else:
            print("❌ Icon creation failed")
            print("You can use any .ico file as icon")
    
    print("\nTo use the icon in build:")
    print("  python -m PyInstaller --onefile --windowed --icon=pomodoro_icon.ico pomodoro_pyside6.py")

if __name__ == "__main__":
    main()
