from src.utils import ImageFont
from pilmoji import Pilmoji
from PIL import Image, ImageDraw
from io import BytesIO
import requests
import sys
from selfcord.ext import commands
from src.utils import *


#cogs/panel.py
class MessagePanel(commands.Cog):
    def __init__(self, client):
        self.client = client

def create_message_panel(name, uid, reason, message, width=500, padding=15, avatar_url=None, 
                        show_title=True, max_chars=None, scale=1.0):
    """
    Create a message panel with options for truncation, scaling, and emoji support.
    """
    # Validate scale factor
    if scale not in [0.5, 0.8, 1.0, 2.0]:
        raise ValueError("Scale must be 0.5, 0.8, 1.0, or 2.0")
    
    # Apply scaling to base dimensions
    width = int(width * scale)
    padding = int(padding * scale)
    font_size = int(14 * scale)
    
    # Load font with fallback
    try:
        font = ImageFont.truetype("fonts/JetBrainsMono.ttf", font_size)
    except Exception:
        try:
            # Try system font as fallback
            font = ImageFont.truetype("Arial", font_size)
        except Exception:
            font = ImageFont.load_default()
    
    # Calculate scaled dimensions
    avatar_size = int(40 * scale)
    avatar_padding = int(20 * scale)
    
    # Truncate message if needed
    if max_chars and len(message) > max_chars:
        message = message[:max_chars-3] + "..."
    
    # Prepare the fields
    fields = [
        f"Username: {name}",
        f"UID: {uid}",
        f"Reason: {reason}",
        "Sent Message:",
    ]
    
    def calculate_text_size(text, font, pilmoji):
        """Helper function to calculate text dimensions with Pilmoji"""
        test_img = Image.new('RGBA', (width * 2, font_size * 2), (0, 0, 0, 0))
        with Pilmoji(test_img) as p:
            return p.getsize(text, font)
    
    def get_wrapped_text(text, font, max_width):
        """Improved text wrapping function that respects boundaries"""
        words = text.split()
        lines = []
        current_line = []
        
        # Create a test image for accurate text measurements
        test_img = Image.new('RGBA', (width * 2, font_size * 2), (0, 0, 0, 0))
        
        with Pilmoji(test_img) as pilmoji:
            current_width = 0
            space_width = pilmoji.getsize(" ", font)[0]
            
            for word in words:
                word_width = pilmoji.getsize(word, font)[0]
                
                # Check if adding this word would exceed the max width
                if current_width + word_width + (len(current_line) * space_width) <= max_width:
                    current_line.append(word)
                    current_width += word_width
                else:
                    # If the current line has words, add it to lines
                    if current_line:
                        lines.append(" ".join(current_line))
                    # Start new line with current word
                    current_line = [word]
                    current_width = word_width
            
            # Add the last line if it exists
            if current_line:
                lines.append(" ".join(current_line))
        
        return lines
    
    # Calculate available width for text
    available_width = width - (padding * 2) - border_width * 2
    if avatar_url:
        available_width -= (avatar_size + avatar_padding)
    
    # Calculate layout dimensions
    title_height = int(30 * scale) if show_title else 0
    line_height = int(20 * scale)
    spacing = int(10 * scale)
    border_width = max(1, int(2 * scale))
    
    # Create temporary image for text wrapping
    temp_img = Image.new('RGBA', (width, 100), (26, 26, 26, 255))
    with Pilmoji(temp_img) as pilmoji:
        wrapped_message = get_wrapped_text(message, font, available_width)
    
    # Calculate total height
    fields_height = len(fields) * line_height
    message_height = len(wrapped_message) * line_height
    total_height = title_height + fields_height + spacing + message_height + (padding * 2)
    
    # Create final image
    img = Image.new('RGBA', (width, total_height), (26, 26, 26, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([(0, 0), (width-1, total_height-1)], outline='#666666', width=border_width)
    
    # Draw title bar
    if show_title:
        draw.rectangle([(border_width, border_width), 
                       (width-border_width-1, title_height-1)], 
                       fill='#333333')
        
        with Pilmoji(img) as pilmoji:
            pilmoji.text((padding, int(8 * scale)), 
                        "Message Details", 
                        font=font, 
                        fill='white')
    
    # Handle avatar
    if avatar_url:
        try:
            response = requests.get(avatar_url, 
                                  headers={'User-Agent': 'Mozilla/5.0'}, 
                                  timeout=5)
            response.raise_for_status()
            
            avatar_img = Image.open(BytesIO(response.content))
            avatar_img = avatar_img.resize((avatar_size, avatar_size))
            
            # Create circular mask
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            
            # Apply mask
            output = Image.new('RGBA', (avatar_size, avatar_size), (0, 0, 0, 0))
            output.paste(avatar_img, (0, 0))
            output.putalpha(mask)
            
            # Place avatar
            avatar_x = width - avatar_size - avatar_padding
            avatar_y = title_height + padding
            img.paste(output, (avatar_x, avatar_y), output)
            
        except Exception as e:
            print(f"Failed to load avatar: {e}")
    
    # Draw fields and message
    with Pilmoji(img) as pilmoji:
        # Draw fields
        y = title_height + padding
        for field in fields:
            pilmoji.text((padding, y), field, font=font, fill='white')
            y += line_height
        
        y += spacing
        
        # Draw message
        for line in wrapped_message:
            pilmoji.text((padding, y), line, font=font, fill='white')
            y += line_height
    
    return img

async def setup(client):
    await client.add_cog(MessagePanel(client))