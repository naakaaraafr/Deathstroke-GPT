import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import os
from dotenv import load_dotenv
import time
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()

# Constants for API configuration

MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"

def generate_image(prompt, retries=3):
    try:
        hf_api_token =os.getenv("HUGGINGFACE_API_TOKEN")
        
        print(f"HuggingFace API token available: {bool(hf_api_token)}")
        
        if hf_api_token:
            try:
                print("Attempting to generate image using HuggingFace API...")
                image_bytes = generate_with_huggingface(prompt, hf_api_token, retries)
                return {"success": True, "image_bytes": image_bytes, "error_message": None}
            except Exception as e:
                print(f"HuggingFace API error: {str(e)}")
                placeholder = generate_enhanced_placeholder(prompt)
                return {"success": False, "image_bytes": placeholder, "error_message": str(e)}
        else:
            # No token available, use placeholder with a specific message
            placeholder = generate_enhanced_placeholder(prompt)
            return {"success": False, "image_bytes": placeholder, "error_message": "HuggingFace API token not found. Please set the HUGGINGFACE_API_TOKEN environment variable."}
    except Exception as e:
        print(f"Error in generate_image: {str(e)}")
        simple_placeholder = generate_simple_placeholder(f"Image generation error: {str(e)}")
        return {"success": False, "image_bytes": simple_placeholder, "error_message": str(e)}

def generate_with_huggingface(prompt, api_token, retries=3):
    """Generate image using the HuggingFace Hub with InferenceClient"""
    if not api_token:
        raise Exception("HuggingFace API token not provided")
    
    # Print partial token for debugging (safe way to verify token is correct format)
    token_prefix = api_token[:4] if len(api_token) > 8 else "****"
    token_suffix = api_token[-4:] if len(api_token) > 8 else "****"
    print(f"Using HuggingFace token: {token_prefix}...{token_suffix}")
    
    attempt = 0
    while attempt <= retries:
        try:
            print(f"Attempt {attempt + 1} to generate image via HuggingFace Hub")
            
            # Initialize the client with the correct token parameter
            client = InferenceClient(token=api_token)
            
            # Generate the image using SDXL model
            image = client.text_to_image(
                prompt,
                model=MODEL_ID,
            )
            
            # Convert PIL image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            print("Image generated successfully from HuggingFace Hub")
            return img_byte_arr.getvalue()
            
        except Exception as e:
            if "unauthorized" in str(e).lower() or "authentication" in str(e).lower():
                raise Exception(f"Authentication error with HuggingFace API. Error details: {str(e)}")
            elif "quota" in str(e).lower() or "credit" in str(e).lower():
                raise Exception("API credits exceeded. Please check your HuggingFace account.")
            elif "not available" in str(e).lower() or "loading" in str(e).lower():
                print("Model is loading, waiting to retry...")
                time.sleep(30)  # Wait longer for model to load
                attempt += 1
                continue
            elif attempt == retries:
                raise e
            
            wait_time = (2 ** attempt) * 5
            print(f"Retrying in {wait_time} seconds... Error: {str(e)}")
            time.sleep(wait_time)
            attempt += 1
    
    raise Exception("Failed to generate image after multiple attempts")

def generate_enhanced_placeholder(prompt):
    """Generate a more visually appealing placeholder image"""
    # Log the reason for using a placeholder
    print("Generating placeholder image due to API issues")
    
    width, height = 512, 512
    
    # Choose a gradient background
    gradient_colors = [
        [(25, 25, 112), (70, 130, 180)],  # Dark blue to steel blue
        [(47, 79, 79), (95, 158, 160)],   # Dark slate to cadet blue
        [(72, 61, 139), (139, 0, 139)],   # Dark slate blue to dark magenta
        [(46, 139, 87), (152, 251, 152)], # Sea green to pale green
        [(139, 69, 19), (244, 164, 96)]   # Saddle brown to sandy brown
    ]
    
    bg_colors = random.choice(gradient_colors)
    
    # Create a new image with a white background
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Draw gradient background
    for y in range(height):
        r = int(bg_colors[0][0] + (bg_colors[1][0] - bg_colors[0][0]) * y / height)
        g = int(bg_colors[0][1] + (bg_colors[1][1] - bg_colors[0][1]) * y / height)
        b = int(bg_colors[0][2] + (bg_colors[1][2] - bg_colors[0][2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add grid pattern
    line_color = (255, 255, 255, 30)
    for i in range(0, width, 20):
        draw.line([(i, 0), (i, height)], fill=line_color, width=1)
    for i in range(0, height, 20):
        draw.line([(0, i), (width, i)], fill=line_color, width=1)
    
    # Add some random decorative elements
    for _ in range(25):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(5, 40)
        shape_type = random.choice(['circle', 'square', 'diamond'])
        
        # Random semi-transparent color
        color = (random.randint(200, 255), 
                random.randint(200, 255), 
                random.randint(200, 255), 
                random.randint(50, 120))
        
        if shape_type == 'circle':
            draw.ellipse((x-size, y-size, x+size, y+size), 
                         fill=color if random.random() > 0.5 else None,
                         outline=(255, 255, 255, 100), width=1)
        elif shape_type == 'square':
            draw.rectangle((x-size, y-size, x+size, y+size),
                          fill=color if random.random() > 0.5 else None,
                          outline=(255, 255, 255, 100), width=1)
        else:  # diamond
            draw.polygon([(x, y-size), (x+size, y), (x, y+size), (x-size, y)],
                        fill=color if random.random() > 0.5 else None,
                        outline=(255, 255, 255, 100), width=1)
    
    # Apply a slight blur for a softer look
    try:
        image = image.filter(ImageFilter.GaussianBlur(radius=1.5))
    except Exception as blur_error:
        print(f"Warning: Could not apply blur: {str(blur_error)}")
    
    # Add text information
    draw = ImageDraw.Draw(image)
    try:
        # Try to use Arial font, fallback to default if not available
        font_path = "arial.ttf"
        title_font = ImageFont.truetype(font_path, 26)
        subtitle_font = ImageFont.truetype(font_path, 20)
        text_font = ImageFont.truetype(font_path, 16)
    except Exception:
        # Use default font if Arial is not available
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Add title
    title = "AI Image Visualization"
    y_position = 80
    
    # Get text width for centering
    def get_text_width(text, font):
        try:
            if hasattr(draw, 'textlength'):
                return draw.textlength(text, font=font)
            else:
                bbox = draw.textbbox((0, 0), text, font=font)
                return bbox[2] - bbox[0]
        except Exception:
            return len(text) * 8
    
    # Draw title with shadow effect
    title_width = get_text_width(title, title_font)
    # Shadow
    draw.text(((width - title_width) // 2 + 2, y_position + 2), title, font=title_font, fill=(30, 30, 30, 150))
    # Main text
    draw.text(((width - title_width) // 2, y_position), title, font=title_font, fill=(255, 255, 255))
    
    # Add subtitle
    y_position += 50
    subtitle = "Placeholder Image"
    subtitle_width = get_text_width(subtitle, subtitle_font)
    draw.text(((width - subtitle_width) // 2, y_position), subtitle, font=subtitle_font, fill=(255, 255, 255))
    
    # Add prompt text
    y_position += 40
    words = prompt.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if get_text_width(test_line, text_font) < width - 60:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # Draw text with a semi-transparent background
    if lines:
        text_block_height = len(lines) * 25 + 20
        text_block_y = y_position - 10
        draw.rectangle((30, text_block_y, width-30, text_block_y + text_block_height), 
                      fill=(0, 0, 0, 80), outline=(255, 255, 255, 100), width=1)
    
    for line in lines:
        line_width = get_text_width(line, text_font)
        draw.text(((width - line_width) // 2, y_position), line, font=text_font, fill=(255, 255, 255))
        y_position += 25
    
    # Add footer note
    footer_text = "Set HUGGINGFACE_API_TOKEN to enable image generation"
    y_position = height - 50
    footer_width = get_text_width(footer_text, text_font)
    draw.text(((width - footer_width) // 2, y_position), footer_text, font=text_font, fill=(255, 255, 255, 200))
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()

def generate_simple_placeholder(message):
    """Generate a very simple placeholder for error cases"""
    width, height = 512, 512
    image = Image.new('RGB', (width, height), (60, 60, 80))
    draw = ImageDraw.Draw(image)
    draw.rectangle([10, 10, width-10, height-10], outline=(200, 200, 200))
    
    lines = []
    words = message.split()
    current_line = ""
    for word in words:
        if len(current_line + " " + word) < 40:
            current_line += " " + word if current_line else word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    y_pos = 50
    for line in lines:
        draw.text((30, y_pos), line, fill=(255, 255, 255))
        y_pos += 30
    
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()

if __name__ == "__main__":
    test_prompt = "A beautiful mountain landscape with a sunset"
    result = generate_image(test_prompt)
    with open("test_image.png", "wb") as f:
        f.write(result["image_bytes"])
    print(f"Test image saved as test_image.png (Success: {result['success']})")