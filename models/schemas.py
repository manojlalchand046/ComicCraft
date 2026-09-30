from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class ComicStyle(str, Enum):
    """Available comic art styles"""
    CARTOON = "cartoon"
    REALISTIC = "realistic"
    ANIME = "anime"
    COMIC_BOOK = "comic_book"
    WATERCOLOR = "watercolor"
    DIGITAL_ART = "digital_art"

class ComicTone(str, Enum):
    """Available comic tones"""
    HUMOROUS = "humorous"
    DRAMATIC = "dramatic"
    ROMANTIC = "romantic"
    ACTION = "action"
    MYSTERY = "mystery"
    ADVENTURE = "adventure"

class ComicPrompt(BaseModel):
    """Comic generation request"""
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    style: ComicStyle = Field(default=ComicStyle.CARTOON)
    tone: ComicTone = Field(default=ComicTone.HUMOROUS)
    characters: Optional[List[str]] = Field(default=None, max_items=5)
    setting: Optional[str] = Field(default=None, max_length=200)
    custom_instructions: Optional[str] = Field(default=None, max_length=500)

class PanelData(BaseModel):
    """Data for a single comic panel"""
    panel_number: int
    description: str
    visual_elements: List[str]
    dialogue: Optional[str] = None
    action: Optional[str] = None
    emotional_context: Optional[str] = None

class ComicResponse(BaseModel):
    """Comic generation response"""
    status: str
    comic_id: str
    title: str
    panels: List[PanelData]
    dialogues: Dict[int, str]
    images: Dict[int, str]
    pdf_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    message: str

class ComicStatusResponse(BaseModel):
    """Status response for async comic generation"""
    task_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: int = 0  # 0-100
    comic_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ErrorResponse(BaseModel):
    """Error response"""
    status: str = "error"
    detail: str
    error_code: Optional[str] = None
