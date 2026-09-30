import os
import sys
from pathlib import Path

# Add the main route to mount the static frontend
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

def mount_static_files(app: FastAPI):
    """
    Mount static files and serve index.html as the root
    """
    static_dir = Path(__file__).resolve().parent.parent / "static"
    
    if static_dir.exists():
        # Mount static directory
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        
        # Serve index.html at root
        @app.get("/", include_in_schema=False)
        async def serve_index():
            return FileResponse(static_dir / "index.html")
    else:
        print(f"Warning: Static directory not found at {static_dir}")
