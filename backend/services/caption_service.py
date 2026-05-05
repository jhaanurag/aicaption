"""
Caption Service - generates captions using AI from ai_service.py
"""

from ai_service import generate_caption_text


def generate_caption(description: str, tone: str = "professional") -> str:
    """
    Generate caption for image description
    
    Args:
        description: Text description of image
        tone: Caption tone (default: professional)
    
    Returns:
        Generated caption text
    """
    try:
        caption = generate_caption_text(description, tone)
        return caption
    except Exception as e:
        raise Exception(f"Caption generation failed: {e}")
