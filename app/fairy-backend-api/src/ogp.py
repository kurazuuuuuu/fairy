"""
OGP Image Generation Module / OGP画像生成モジュール

Generates dynamic OGP images with keyword and body text overlay
using Pillow for research result sharing.
"""

import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Configuration / 設定
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
TEMPLATE_PATH = os.path.join(ASSETS_DIR, "fairy-ogp.png")
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "MochiyPopOne-Regular.ttf")

# OGP Image dimensions (standard size for social media)
OGP_WIDTH = 1200
OGP_HEIGHT = 630

# Text positioning (adjust based on template)
KEYWORD_POSITION = (100, 175)  # Position for keyword text
KEYWORD_FONT_SIZE = 40
KEYWORD_MAX_WIDTH = 20  # Max characters before truncation

BODY_POSITION = (80, 250)  # Position for body text
BODY_FONT_SIZE = 32
BODY_MAX_WIDTH_PX = 1040  # Max width in pixels (1200 - 80*2 padding)
BODY_MAX_LINES = 5  # Max lines to display
BODY_LINE_HEIGHT = 1.6  # Line height multiplier

# Colors
TEXT_COLOR = (222, 222, 222)  # White text


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load the Mochiy Pop One font at the specified size."""
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        # Fallback to default font if custom font not found
        print(f"Warning: Font not found at {FONT_PATH}, using default font")
        return ImageFont.load_default()


def _truncate_text(text: str, max_chars: int) -> str:
    """Truncate text and add ellipsis if too long."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "…"


def _wrap_text_by_pixel(text: str, font: ImageFont.FreeTypeFont, max_width_px: int, max_lines: int) -> list[str]:
    """
    Wrap text based on actual pixel width (handles mixed Japanese/ASCII properly).
    ピクセル幅に基づいてテキストを折り返す（日本語・英数字混在対応）。
    """
    # Remove markdown formatting
    clean_text = text.replace("#", "").replace("*", "").replace("`", "")
    clean_text = clean_text.replace("\n\n", "\n").replace("\n", " ").strip()
    
    lines = []
    current_line = ""
    
    for char in clean_text:
        test_line = current_line + char
        # Get the width of the test line using textbbox
        bbox = font.getbbox(test_line)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width_px:
            current_line = test_line
        else:
            # Line is full, start a new one
            if current_line:
                lines.append(current_line)
            current_line = char
            
            # Check if we've reached max lines
            if len(lines) >= max_lines:
                break
    
    # Add the last line
    if current_line and len(lines) < max_lines:
        lines.append(current_line)
    
    # If we hit max lines, add ellipsis to last line
    if len(lines) >= max_lines:
        last_line = lines[-1]
        # Remove chars until ellipsis fits
        while last_line:
            test_with_ellipsis = last_line + "…"
            bbox = font.getbbox(test_with_ellipsis)
            if bbox[2] - bbox[0] <= max_width_px:
                lines[-1] = test_with_ellipsis
                break
            last_line = last_line[:-1]
    
    return lines


def generate_ogp_image(keyword: str, body_text: str) -> bytes:
    """
    Generate an OGP image with keyword and body text overlay.
    
    Args:
        keyword: The search keyword to display
        body_text: The body text (will be truncated/wrapped)
    
    Returns:
        PNG image as bytes
    """
    # Load and resize template image
    keyword = keyword[:20]
    keyword = f"【 {keyword} 】"

    try:
        template = Image.open(TEMPLATE_PATH)
    except FileNotFoundError:
        # Create a fallback dark background if template not found
        template = Image.new("RGB", (OGP_WIDTH, OGP_HEIGHT), (34, 33, 34))
    
    # Resize to OGP dimensions while maintaining aspect ratio
    template = template.resize((OGP_WIDTH, OGP_HEIGHT), Image.Resampling.LANCZOS)
    
    # Create drawing context
    draw = ImageDraw.Draw(template)
    
    # Load fonts
    keyword_font = _load_font(KEYWORD_FONT_SIZE)
    body_font = _load_font(BODY_FONT_SIZE)
    
    # Draw keyword
    keyword_text = _truncate_text(keyword, KEYWORD_MAX_WIDTH)
    draw.text(KEYWORD_POSITION, keyword_text, font=keyword_font, fill=TEXT_COLOR)
    
    # Draw body text using pixel-based wrapping
    body_lines = _wrap_text_by_pixel(body_text, body_font, BODY_MAX_WIDTH_PX, BODY_MAX_LINES)
    
    # Calculate line height
    line_height = int(BODY_FONT_SIZE * BODY_LINE_HEIGHT)
    
    # Draw each line
    y_offset = BODY_POSITION[1]
    for line in body_lines:
        draw.text((BODY_POSITION[0], y_offset), line, font=body_font, fill=TEXT_COLOR)
        y_offset += line_height
    
    # Save to bytes
    output = BytesIO()
    template.save(output, format="PNG", optimize=True)
    output.seek(0)
    
    return output.getvalue()


def generate_ogp_html(
    uuid: str,
    keyword: str,
    smart_message: str,
    base_url: str,
    frontend_url: str,
) -> str:
    """
    Generate HTML page with OGP meta tags for social media crawlers.
    
    Args:
        uuid: Research result UUID
        keyword: Search keyword
        smart_message: Short message for description
        base_url: Backend API base URL
        frontend_url: Frontend base URL for redirect
    
    Returns:
        HTML string with OGP meta tags
    """
    # Truncate description for og:description
    description = smart_message[:200] + "…" if len(smart_message) > 200 else smart_message
    
    # Build OGP image URL
    ogp_image_url = f"{base_url}/api/research/{uuid}/ogp.png"
    
    # Frontend redirect URL
    redirect_url = f"{frontend_url}/{uuid}"
    
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{keyword} - Fairy Research</title>
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="{redirect_url}">
    <meta property="og:title" content="{keyword} - Fairy Research">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{ogp_image_url}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{keyword} - Fairy Research">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{ogp_image_url}">
    
    <!-- Redirect to frontend -->
    <meta http-equiv="refresh" content="0; url={redirect_url}">
</head>
<body>
    <p>Redirecting to <a href="{redirect_url}">{redirect_url}</a>...</p>
</body>
</html>"""
