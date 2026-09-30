from typing import Dict, List, Optional, Tuple
from pathlib import Path
import uuid
import aiohttp
from loguru import logger
from PIL import Image
import io
import os

from config import settings

class ImageService:
    """Service for generating and processing comic panel images"""
    
    def __init__(self):
        self.api_key = settings.stable_diffusion_api_key
        self.api_url = settings.stable_diffusion_api_url
        self.image_cache = {}
    
    async def generate_panel_images(
        self,
        panels: List[Dict],
        style: str,
        dialogues: Dict[int, str]
    ) -> Dict[int, str]:
        """
        Generate images for each comic panel using Stable Diffusion.
        """
        try:
            logger.info("Starting panel image generation")
            images = {}
            
            for i, panel in enumerate(panels, 1):
                prompt = self._create_image_prompt(
                    panel=panel,
                    style=style,
                    dialogue=dialogues.get(i, "")
                )
                
                image_url = await self._generate_image(prompt)
                images[i] = image_url
                logger.debug(f"Generated image for panel {i}")
            
            return images
            
        except Exception as e:
            logger.error(f"Error generating panel images: {str(e)}")
            raise
    
    def _create_image_prompt(
        self,
        panel: Dict,
        style: str,
        dialogue: str
    ) -> str:
        """
        Create a detailed image generation prompt.
        """
        style_descriptors = {
            "cartoon": "cartoon style, colorful, expressive, comic book art",
            "realistic": "realistic, detailed, photorealistic",
            "anime": "anime style, manga, Japanese art style",
            "comic_book": "comic book art, bold lines, dynamic composition",
            "watercolor": "watercolor painting, soft edges, artistic",
            "digital_art": "digital art, modern, sleek design"
        }
        
        style_desc = style_descriptors.get(style, "cartoon style")
        
        prompt = f"""Create a comic panel illustration with the following specifications:
        
Panel Description: {panel.get('description', '')}
Visual Elements: {', '.join(panel.get('visual_elements', []))}
Emotional Context: {panel.get('emotional_context', '')}
Dialogue Hint: {dialogue[:50] if dialogue else 'dialogue-free panel'}
Art Style: {style_desc}

Make it vivid, dynamic, and suitable for a comic strip.
        """
        
        return prompt
    
    async def _generate_image(
        self,
        prompt: str,
        height: int = 768,
        width: int = 768,
        steps: int = None,
        guidance_scale: float = None
    ) -> str:
        """
        Generate an image using Stable Diffusion API.
        """
        try:
            if not self.api_key:
                logger.warning("Stable Diffusion API key not configured, using placeholder")
                return await self._create_placeholder_image(prompt)
            
            steps = steps or settings.sd_steps
            guidance_scale = guidance_scale or settings.sd_guidance_scale
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "text_prompts": [
                    {"text": prompt, "weight": 1.0}
                ],
                "cfg_scale": guidance_scale,
                "steps": steps,
                "width": width,
                "height": height,
                "samples": 1,
                "sampler": "k_lms"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Save and return the image
                        image_data = result.get('artifacts', [{}])[0].get('base64')
                        if image_data:
                            image_url = await self._save_generated_image(image_data)
                            return image_url
                    else:
                        logger.error(f"API error: {response.status}")
                        return await self._create_placeholder_image(prompt)
                        
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return await self._create_placeholder_image(prompt)
    
    async def _create_placeholder_image(
        self,
        prompt: str,
        width: int = 768,
        height: int = 768
    ) -> str:
        """
        Create a placeholder image with text when API fails.
        """
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple colored image with text
            colors = [
                (255, 200, 124),  # Peach
                (144, 238, 144),  # Light green
                (173, 216, 230),  # Light blue
                (255, 182, 193),  # Light pink
                (240, 230, 200)   # Beige
            ]
            
            import random
            bg_color = random.choice(colors)
            
            img = Image.new('RGB', (width, height), color=bg_color)
            draw = ImageDraw.Draw(img)
            
            # Add text
            text = prompt[:100] + "..." if len(prompt) > 100 else prompt
            draw.text((20, height // 2), text, fill=(0, 0, 0))
            
            # Save image
            image_id = str(uuid.uuid4())
            image_path = Path(settings.image_cache_dir) / f"{image_id}.png"
            img.save(image_path)
            
            image_url = f"/outputs/images/{image_id}.png"
            logger.info(f"Placeholder image created: {image_url}")
            return image_url
            
        except Exception as e:
            logger.error(f"Error creating placeholder image: {str(e)}")
            return f"/outputs/images/placeholder_{str(uuid.uuid4())}.png"
    
    async def _save_generated_image(self, image_data: str) -> str:
        """
        Save generated image to disk.
        """
        try:
            import base64
            
            image_id = str(uuid.uuid4())
            image_path = Path(settings.image_cache_dir) / f"{image_id}.png"
            
            # Decode and save
            image_bytes = base64.b64decode(image_data)
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            
            return f"/outputs/images/{image_id}.png"
            
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            raise
    
    async def process_reference_image(
        self,
        file
    ) -> Dict[str, str]:
        """
        Process an uploaded reference image.
        """
        try:
            contents = await file.read()
            image_id = str(uuid.uuid4())
            file_path = Path(settings.image_cache_dir) / f"ref_{image_id}_{file.filename}"
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(contents)
            
            logger.info(f"Reference image saved: {file_path}")
            
            return {
                "id": image_id,
                "url": f"/outputs/images/ref_{image_id}_{file.filename}",
                "filename": file.filename
            }
            
        except Exception as e:
            logger.error(f"Error processing reference image: {str(e)}")
            raise
