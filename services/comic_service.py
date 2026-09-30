from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from loguru import logger
import json
import os

from models.schemas import PanelData, ComicTone, ComicStyle
from config import settings

class ComicService:
    """Service for managing comic generation and storage"""
    
    def __init__(self):
        self.comics_db = {}  # In-memory storage (replace with DB)
        self.tasks = {}  # Async task tracking
    
    async def generate_comic_story(
        self,
        title: str,
        description: str,
        style: ComicStyle,
        tone: ComicTone,
        characters: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a 5-panel comic story structure.
        """
        try:
            comic_id = str(uuid.uuid4())
            logger.info(f"Generating story structure for comic: {comic_id}")
            
            # Create panel structure
            panels = await self._create_panel_structure(
                title=title,
                description=description,
                characters=characters,
                tone=tone
            )
            
            comic_data = {
                "id": comic_id,
                "title": title,
                "description": description,
                "style": style.value,
                "tone": tone.value,
                "characters": characters or [],
                "panels": panels,
                "story": self._build_narrative(panels, description),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in database
            self.comics_db[comic_id] = comic_data
            
            return comic_data
            
        except Exception as e:
            logger.error(f"Error generating story: {str(e)}")
            raise
    
    async def _create_panel_structure(
        self,
        title: str,
        description: str,
        characters: Optional[List[str]],
        tone: ComicTone
    ) -> List[PanelData]:
        """
        Create a 5-panel structure for the comic.
        Panel 1: Introduction
        Panel 2: Rising Action
        Panel 3: Climax
        Panel 4: Resolution
        Panel 5: Conclusion
        """
        panels = [
            PanelData(
                panel_number=1,
                description="Introduction - Introduce the main character(s) and setting",
                visual_elements=["main_character", "setting"],
                emotional_context="Establishing"
            ),
            PanelData(
                panel_number=2,
                description="Rising Action - Present the initial conflict or challenge",
                visual_elements=["action", "interaction"],
                emotional_context="Building tension"
            ),
            PanelData(
                panel_number=3,
                description="Climax - The peak of the story with the main event",
                visual_elements=["climactic_moment", "dramatic_action"],
                emotional_context="Peak drama"
            ),
            PanelData(
                panel_number=4,
                description="Resolution - Working towards solving the conflict",
                visual_elements=["solution_beginning", "turning_point"],
                emotional_context="Relief"
            ),
            PanelData(
                panel_number=5,
                description="Conclusion - Final resolution and emotional closure",
                visual_elements=["resolution", "final_scene"],
                emotional_context="Closure"
            )
        ]
        
        return panels
    
    def _build_narrative(self, panels: List[PanelData], description: str) -> str:
        """
        Build a narrative summary from panels.
        """
        narrative = f"Story: {description}\n\nPanel Sequence:\n"
        for panel in panels:
            narrative += f"Panel {panel.panel_number}: {panel.description}\n"
        return narrative
    
    async def create_async_task(
        self,
        prompt: Dict[str, Any]
    ) -> str:
        """
        Create an async task for comic generation.
        """
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "status": "pending",
            "progress": 0,
            "created_at": datetime.utcnow(),
            "prompt": prompt
        }
        logger.info(f"Async task created: {task_id}")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of an async task.
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")
        
        task = self.tasks[task_id]
        return {
            "task_id": task_id,
            "status": task["status"],
            "progress": task["progress"],
            "comic_id": task.get("comic_id"),
            "error_message": task.get("error_message"),
            "created_at": task["created_at"],
            "updated_at": datetime.utcnow()
        }
    
    async def get_comic(self, comic_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a comic by ID.
        """
        return self.comics_db.get(comic_id)
    
    async def list_comics(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        List all comics with pagination.
        """
        comics_list = list(self.comics_db.values())
        return comics_list[skip:skip + limit]
    
    async def count_comics(self) -> int:
        """
        Count total comics.
        """
        return len(self.comics_db)
