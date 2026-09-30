from typing import Dict, List, Optional
import google.generativeai as genai
from loguru import logger

from config import settings
from models.schemas import ComicTone

class GeminiService:
    """Service for AI-powered dialogue and content generation using Gemini"""
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
    
    async def generate_dialogues(
        self,
        story: str,
        panels: List[Dict],
        tone: ComicTone
    ) -> Dict[int, str]:
        """
        Generate dialogues for each comic panel using Gemini AI.
        """
        try:
            logger.info("Generating dialogues using Gemini AI")
            
            dialogues = {}
            
            for i, panel in enumerate(panels, 1):
                prompt = self._create_dialogue_prompt(
                    panel=panel,
                    story=story,
                    tone=tone,
                    panel_number=i
                )
                
                dialogue = await self._generate_with_retry(prompt)
                dialogues[i] = dialogue
                logger.debug(f"Generated dialogue for panel {i}")
            
            return dialogues
            
        except Exception as e:
            logger.error(f"Error generating dialogues: {str(e)}")
            raise
    
    def _create_dialogue_prompt(self, panel: Dict, story: str, tone: ComicTone, panel_number: int) -> str:
        """
        Create a prompt for dialogue generation.
        """
        tone_desc = {
            ComicTone.HUMOROUS: "funny and lighthearted",
            ComicTone.DRAMATIC: "serious and intense",
            ComicTone.ROMANTIC: "tender and emotional",
            ComicTone.ACTION: "fast-paced and thrilling",
            ComicTone.MYSTERY: "suspenseful and intriguing",
            ComicTone.ADVENTURE: "exciting and adventurous"
        }
        
        return f"""Based on the following story and panel description, generate concise dialogue for a comic panel.
        
Story Context: {story}

Panel {panel_number} Description: {panel.get('description', '')}

Tone: {tone_desc.get(tone, 'neutral')}

Generate 2-3 lines of dialogue that fit this panel. Make it engaging and appropriate for the panel's content.
        """
    
    async def _generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3
    ) -> str:
        """
        Generate content with retry logic.
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=settings.gemini_temperature,
                        max_output_tokens=settings.gemini_max_output_tokens,
                    )
                )
                return response.text
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"All retries failed for prompt")
                    raise
        
        return ""
    
    async def generate_story_outline(
        self,
        title: str,
        description: str,
        characters: Optional[List[str]] = None
    ) -> str:
        """
        Generate a detailed story outline for the comic.
        """
        try:
            characters_str = ", ".join(characters) if characters else "not specified"
            
            prompt = f"""Create a detailed 5-panel comic story outline based on the following:
            
Title: {title}
Description: {description}
Characters: {characters_str}

Provide a structured outline with clear progression for each panel.
            """
            
            outline = await self._generate_with_retry(prompt)
            logger.info("Story outline generated successfully")
            return outline
            
        except Exception as e:
            logger.error(f"Error generating story outline: {str(e)}")
            raise
    
    async def generate_character_descriptions(
        self,
        characters: List[str],
        story_context: str
    ) -> Dict[str, str]:
        """
        Generate detailed descriptions for characters.
        """
        try:
            descriptions = {}
            
            for character in characters:
                prompt = f"""Based on the story context, provide a detailed physical and personality description for the character '{character}' suitable for visual illustration.
                
Story Context: {story_context}
                
Provide: appearance, clothing, distinctive features, and personality traits in 2-3 sentences.
                """
                
                description = await self._generate_with_retry(prompt)
                descriptions[character] = description
            
            return descriptions
            
        except Exception as e:
            logger.error(f"Error generating character descriptions: {str(e)}")
            raise
