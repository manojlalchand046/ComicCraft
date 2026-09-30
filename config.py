from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # FastAPI Configuration
    app_name: str = "ComicCraft"
    app_version: str = "1.0.0"
    app_description: str = "AI-powered comic generation platform"
    debug: bool = False
    api_prefix: str = "/api/v1"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API Keys
    gemini_api_key: str = ""
    stable_diffusion_api_key: str = ""
    stable_diffusion_api_url: str = "https://api.stability.ai/v1/generate"
    
    # Comic Configuration
    comic_panels: int = 5
    image_resolution: int = 768
    image_quality: int = 95
    
    # Output Directories
    output_base_dir: str = "./outputs"
    pdf_output_dir: str = "./outputs/pdfs"
    image_cache_dir: str = "./outputs/images"
    temp_dir: str = "./outputs/temp"
    
    # File Upload Configuration
    max_upload_size: int = 10485760  # 10MB
    allowed_extensions: List[str] = ["png", "jpg", "jpeg", "gif"]
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/comiccraft.log"
    
    # AI Model Configuration
    gemini_model: str = "gemini-pro"
    gemini_temperature: float = 0.7
    gemini_max_output_tokens: int = 2048
    
    # Stable Diffusion Configuration
    sd_steps: int = 50
    sd_guidance_scale: float = 7.5
    sd_seed: Optional[int] = None
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.pdf_output_dir,
            self.image_cache_dir,
            self.temp_dir,
            os.path.dirname(self.log_file)
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

# Load settings
settings = Settings()
settings.create_directories()
