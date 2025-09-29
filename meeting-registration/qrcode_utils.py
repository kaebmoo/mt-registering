# qrcode_utils.py

import base64
from io import BytesIO
from PIL import Image, ImageDraw
from qrcodegen import QrCode
import os
import logging

# Setup logger
logger = logging.getLogger(__name__)

def generate_qr_code(data: str, with_logo: bool = False, logo_path: str = None):
    """
    Generate QR Code with optional logo
    
    Args:
        data: Text or URL to encode
        with_logo: Whether to add logo
        logo_path: Path to logo file
    
    Returns:
        PIL Image object
    """
    logger.info(f"Generating QR Code - with_logo: {with_logo}, logo_path: {logo_path}")
    
    # Generate QR Code with high error correction for logo overlay
    qr = QrCode.encode_text(data, QrCode.Ecc.QUARTILE)
    size = qr.get_size()
    scale = 8
    img_size = size * scale
    img = Image.new('1', (img_size, img_size), 'white')
    
    # Draw QR Code
    for y in range(size):
        for x in range(size):
            if qr.get_module(x, y):
                for dy in range(scale):
                    for dx in range(scale):
                        img.putpixel((x * scale + dx, y * scale + dy), 0)
    
    # Convert to RGB
    img = img.convert("RGB")
    
    # Add logo if requested and file exists
    if with_logo:
        logger.info(f"Attempting to add logo - path: {logo_path}")
        
        if logo_path:
            if os.path.exists(logo_path):
                logger.info(f"Logo file found at: {logo_path}")
                try:
                    logo = Image.open(logo_path)
                    logger.info(f"Logo opened successfully - size: {logo.size}, mode: {logo.mode}")
                    
                    # Maintain logo ratio
                    logo_width, logo_height = logo.size
                    logo_ratio = logo_width / logo_height
                    max_logo_size = img_size // 5
                    
                    if logo_width > logo_height:
                        new_logo_width = max_logo_size
                        new_logo_height = int(max_logo_size / logo_ratio)
                    else:
                        new_logo_height = max_logo_size
                        new_logo_width = int(max_logo_size * logo_ratio)
                    
                    logo = logo.resize((new_logo_width, new_logo_height), Image.Resampling.LANCZOS)
                    logger.info(f"Logo resized to: {new_logo_width}x{new_logo_height}")
                    
                    # Add white background padding around logo
                    padding = 10
                    logo_position = ((img_size - new_logo_width) // 2,
                                     (img_size - new_logo_height) // 2)
                    
                    draw = ImageDraw.Draw(img)
                    draw.rectangle([(logo_position[0] - padding, logo_position[1] - padding),
                                    (logo_position[0] + new_logo_width + padding,
                                     logo_position[1] + new_logo_height + padding)],
                                   fill="white")
                    
                    # Paste logo
                    if logo.mode == 'RGBA':
                        img.paste(logo, logo_position, mask=logo.split()[3])
                        logger.info("Logo pasted with alpha channel")
                    else:
                        img.paste(logo, logo_position)
                        logger.info("Logo pasted without alpha channel")
                        
                    logger.info("Logo added successfully to QR Code")
                except Exception as e:
                    logger.error(f"Error adding logo: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            else:
                logger.warning(f"Logo file not found at: {logo_path}")
                # List files in static directory for debugging
                static_dir = os.path.dirname(logo_path) if logo_path else 'static'
                if os.path.exists(static_dir):
                    files = os.listdir(static_dir)
                    logger.info(f"Files in {static_dir}: {files}")
        else:
            logger.warning("No logo path provided")
    
    return img

def generate_qr_base64(data: str, with_logo: bool = False, logo_path: str = None):
    """
    Generate QR Code and return as base64 string
    
    Args:
        data: Text or URL to encode
        with_logo: Whether to add logo
        logo_path: Path to logo file
    
    Returns:
        Base64 encoded PNG string
    """
    logger.info(f"Generating QR Base64 - data: {data[:50]}..., with_logo: {with_logo}")
    img = generate_qr_code(data, with_logo, logo_path)
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

def generate_meeting_qr(meeting_id: int, base_url: str, with_logo: bool = False, logo_path: str = None):
    """
    Generate QR Code for meeting registration URL
    
    Args:
        meeting_id: Meeting ID
        base_url: Base URL of the application
        with_logo: Whether to add logo
        logo_path: Path to logo file (optional - will search if not provided)
    
    Returns:
        Base64 encoded PNG string
    """
    # Create the registration URL
    registration_url = f"{base_url}/submit/{meeting_id}"
    logger.info(f"Generating meeting QR - ID: {meeting_id}, URL: {registration_url}, with_logo: {with_logo}, provided_logo_path: {logo_path}")
    
    # If logo_path is provided and exists, use it
    if logo_path and os.path.exists(logo_path):
        logger.info(f"Using provided logo path: {logo_path}")
        return generate_qr_base64(registration_url, with_logo, logo_path)
    
    # Otherwise, try to find logo
    logo_paths = [
        os.path.join('static', 'logo.png'),
        os.path.join('static', '01_NT-Logo.png'),
        'logo.png',
        '01_NT-Logo.png'
    ]
    
    found_logo_path = None
    for path in logo_paths:
        if os.path.exists(path):
            found_logo_path = path
            logger.info(f"Found logo at: {found_logo_path}")
            break
    
    if not found_logo_path and with_logo:
        logger.warning(f"No logo found. Tried paths: {logo_paths}")
        logger.info(f"Current directory: {os.getcwd()}")
        logger.info(f"Directory contents: {os.listdir('.')}")
    
    return generate_qr_base64(registration_url, with_logo, found_logo_path)
