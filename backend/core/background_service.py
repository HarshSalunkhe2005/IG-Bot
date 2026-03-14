from PIL import Image, ImageDraw

def create_gradient(width, height, start_color=(20, 20, 20), end_color=(40, 40, 60)):
    """Creates a smooth vertical linear gradient."""
    base = Image.new("RGB", (width, height), start_color)
    draw = ImageDraw.Draw(base)
    
    for i in range(height):
        # Calculate transition
        r = int(start_color[0] + (end_color[0] - start_color[0]) * (i / height))
        g = int(start_color[1] + (end_color[1] - start_color[1]) * (i / height))
        b = int(start_color[2] + (end_color[2] - start_color[2]) * (i / height))
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    return base

def get_background(bg_type="gradient", width=1080, height=1080):
    """
    Modular selector for background type.
    Future-proofed for 'image' or 'ai_generated' types.
    """
    if bg_type == "gradient":
        # Deep moody navy/charcoal gradient
        return create_gradient(width, height, (10, 10, 12), (30, 35, 45))
    
    # Fallback to solid dark
    return Image.new("RGB", (width, height), (15, 15, 15))