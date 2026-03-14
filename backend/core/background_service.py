import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

# Path to your textures
BG_ASSETS_PATH = os.path.join("assets", "backgrounds")

def create_gradient(width, height, start_color=(20, 20, 20), end_color=(40, 40, 60)):
    """Creates a smooth vertical linear gradient."""
    base = Image.new("RGB", (width, height), start_color)
    draw = ImageDraw.Draw(base)
    
    for i in range(height):
        r = int(start_color[0] + (end_color[0] - start_color[0]) * (i / height))
        g = int(start_color[1] + (end_color[1] - start_color[1]) * (i / height))
        b = int(start_color[2] + (end_color[2] - start_color[2]) * (i / height))
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    return base

def get_processed_image(width=1080, height=1080):
    """Loads a random image, center-crops, and applies finalized pro filters."""
    try:
        all_files = [f for f in os.listdir(BG_ASSETS_PATH) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        if not all_files:
            return create_gradient(width, height)
        
        random_bg = random.choice(all_files)
        img_path = os.path.join(BG_ASSETS_PATH, random_bg)
        img = Image.open(img_path).convert("RGB")

        # Aspect Ratio Resize & Center Crop
        img_width, img_height = img.size
        aspect = img_width / img_height
        
        if aspect > 1: # Wide image
            new_width = int(aspect * height)
            img = img.resize((new_width, height), Image.Resampling.LANCZOS)
            left = (new_width - width) / 2
            img = img.crop((left, 0, left + width, height))
        else: # Tall or Square
            new_height = int(width / aspect)
            img = img.resize((width, new_height), Image.Resampling.LANCZOS)
            top = (new_height - height) / 2
            img = img.crop((0, top, width, top + height))

        # --- FINALIZED PRO FILTERS ---
        # 1. Subtle Blur (Radius 2 is the sweet spot for textures)
        img = img.filter(ImageFilter.GaussianBlur(radius=2)) 
        
        # 2. Brightness (Keep at 60%)
        brightness_enhancer = ImageEnhance.Brightness(img)
        img = brightness_enhancer.enhance(0.6) 

        # 3. Contrast Boost (Makes textures pop)
        contrast_enhancer = ImageEnhance.Contrast(img)
        img = contrast_enhancer.enhance(1.3) 

        return img
    except Exception as e:
        print(f"Error processing background: {e}")
        return create_gradient(width, height)

def get_background(bg_type="gradient", width=1080, height=1080):
    if bg_type == "image":
        return get_processed_image(width, height)
    if bg_type == "gradient":
        return create_gradient(width, height, (10, 10, 12), (30, 35, 45))
    return Image.new("RGB", (width, height), (15, 15, 15))