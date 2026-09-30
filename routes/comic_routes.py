from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import Optional
from loguru import logger
import asyncio

from models.schemas import (
    ComicPrompt,
    ComicResponse,
    ComicStatusResponse,
    ErrorResponse
)
from services.comic_service import ComicService
from services.gemini_service import GeminiService
from services.image_service import ImageService
from services.pdf_service import PDFService

router = APIRouter(tags=["Comics"])

# Initialize services
comic_service = ComicService()
gemini_service = GeminiService()
image_service = ImageService()
pdf_service = PDFService()

@router.post("/comics/generate", response_model=ComicResponse)
async def generate_comic(
    prompt: ComicPrompt,
    background_tasks: BackgroundTasks
):
    """
    Generate a 5-panel comic story with AI-generated dialogues and illustrations.
    
    Args:
        prompt: ComicPrompt object containing user's story idea
        
    Returns:
        ComicResponse with comic data, image URLs, and PDF download link
    """
    try:
        logger.info(f"Generating comic for prompt: {prompt.title}")
        
        # Generate comic story and panels
        comic_data = await comic_service.generate_comic_story(
            title=prompt.title,
            description=prompt.description,
            style=prompt.style,
            tone=prompt.tone,
            characters=prompt.characters
        )
        
        # Generate dialogues using Gemini AI
        dialogues = await gemini_service.generate_dialogues(
            story=comic_data["story"],
            panels=comic_data["panels"],
            tone=prompt.tone
        )
        
        # Generate illustrations for each panel
        image_urls = await image_service.generate_panel_images(
            panels=comic_data["panels"],
            style=prompt.style,
            dialogues=dialogues
        )
        
        # Create PDF comic
        pdf_path = await pdf_service.create_comic_pdf(
            title=prompt.title,
            panels=comic_data["panels"],
            images=image_urls,
            dialogues=dialogues
        )
        
        logger.success(f"Comic generated successfully: {prompt.title}")
        
        return ComicResponse(
            status="success",
            comic_id=comic_data["id"],
            title=prompt.title,
            panels=comic_data["panels"],
            dialogues=dialogues,
            images=image_urls,
            pdf_url=pdf_path,
            message="Comic generated successfully!"
        )
        
    except Exception as e:
        logger.error(f"Error generating comic: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate comic: {str(e)}"
        )

@router.post("/comics/generate-async")
async def generate_comic_async(
    prompt: ComicPrompt,
    background_tasks: BackgroundTasks
):
    """
    Generate a comic asynchronously (for long-running operations).
    Returns a task ID for polling progress.
    """
    try:
        task_id = await comic_service.create_async_task(
            prompt=prompt
        )
        logger.info(f"Async comic generation started: {task_id}")
        
        return {
            "status": "processing",
            "task_id": task_id,
            "message": "Comic generation started. Use task_id to check status."
        }
    except Exception as e:
        logger.error(f"Error starting async generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comics/status/{task_id}", response_model=ComicStatusResponse)
async def check_comic_status(task_id: str):
    """
    Check the status of an async comic generation task.
    """
    try:
        status = await comic_service.get_task_status(task_id)
        return ComicStatusResponse(**status)
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        raise HTTPException(status_code=404, detail="Task not found")

@router.get("/comics/{comic_id}")
async def get_comic(comic_id: str):
    """
    Retrieve a previously generated comic.
    """
    try:
        comic = await comic_service.get_comic(comic_id)
        if not comic:
            raise HTTPException(status_code=404, detail="Comic not found")
        return comic
    except Exception as e:
        logger.error(f"Error retrieving comic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comics/upload-reference")
async def upload_reference_image(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """
    Upload a reference image for comic generation.
    """
    try:
        image_data = await image_service.process_reference_image(file)
        logger.info(f"Reference image uploaded: {file.filename}")
        
        return {
            "status": "success",
            "filename": file.filename,
            "image_id": image_data["id"],
            "url": image_data["url"],
            "description": description
        }
    except Exception as e:
        logger.error(f"Error uploading reference image: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/comics")
async def list_comics(
    skip: int = 0,
    limit: int = 10
):
    """
    List all generated comics (with pagination).
    """
    try:
        comics = await comic_service.list_comics(skip=skip, limit=limit)
        total = await comic_service.count_comics()
        
        return {
            "status": "success",
            "total": total,
            "skip": skip,
            "limit": limit,
            "comics": comics
        }
    except Exception as e:
        logger.error(f"Error listing comics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
