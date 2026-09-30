# ComicCraft

ComicCraft is an AI-powered comic generator built with FastAPI, Google Gemini, and Stable Diffusion. Enter a story idea, choose a style and tone, and generate a five-panel comic with dialogue, illustrations, and a downloadable PDF.

## Features

- **5-Panel Comic Generation**: Automatic story structure with introduction, rising action, climax, resolution, and conclusion
- **AI-Powered Dialogue**: Gemini-powered conversation generation for each panel
- **Illustration Generation**: Stable Diffusion creates unique artwork for each panel with graceful fallbacks
- **PDF Export**: Download your complete comic as a printable PDF
- **Reference Images**: Upload reference images to guide AI generation
- **Dual Endpoints**: Synchronous generation for quick feedback and async for long-running tasks
- **Browser UI**: Clean, responsive interface served directly by FastAPI
- **Developer-Friendly**: Comprehensive REST API with Swagger documentation

## Quick Start

### Prerequisites
- Python 3.11+
- Google Gemini API key (optional for development)
- Stable Diffusion API key (optional for development)

### Installation

```bash
# Clone and setup
git clone https://github.com/manojlalchand046/ComicCraft.git
cd ComicCraft

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys (optional for testing)

# Run the server
uvicorn main:app --reload
```

Open http://localhost:8000 in your browser. API documentation available at http://localhost:8000/docs

## Docker Setup

```bash
docker-compose up --build
```

## API Endpoints

### Generate Comic (Synchronous)
```bash
POST /api/v1/comics/generate
Content-Type: application/json

{
  "title": "The Midnight Adventure",
  "description": "A curious astronomer discovers something extraordinary through her telescope",
  "style": "digital_art",
  "tone": "mysterious",
  "characters": ["Dr. Elena", "The Night Sky"]
}
```

**Response:**
```json
{
  "status": "success",
  "comic_id": "uuid-here",
  "title": "The Midnight Adventure",
  "panels": [...],
  "dialogues": {1: "...", 2: "..."},
  "images": {1: "/outputs/images/...", ...},
  "pdf_url": "/outputs/pdfs/comic_xyz.pdf",
  "message": "Comic generated successfully!"
}
```

### Generate Comic (Asynchronous)
```bash
POST /api/v1/comics/generate-async
```
Returns `task_id` for polling progress.

### Check Task Status
```bash
GET /api/v1/comics/status/{task_id}
```

### Retrieve Comic
```bash
GET /api/v1/comics/{comic_id}
```

### Upload Reference Image
```bash
POST /api/v1/comics/upload-reference
Content-Type: multipart/form-data

Form Data:
- file: (binary image)
- description: (optional text)
```

### List All Comics
```bash
GET /api/v1/comics?skip=0&limit=10
```

### Health Check
```bash
GET /health
```

## Configuration

Edit `.env` to customize:

```env
# API Keys (optional for development)
GEMINI_API_KEY=your_key_here
STABLE_DIFFUSION_API_KEY=your_key_here

# Comic Settings
COMIC_PANELS=5
IMAGE_RESOLUTION=768

# Output Directories
PDF_OUTPUT_DIR=./outputs/pdfs
IMAGE_CACHE_DIR=./outputs/images
```

## Project Structure

```
ComicCraft/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Multi-container setup
├── static/                # Browser UI assets
│   ├── index.html         # Main page
│   ├── styles.css         # Styling
│   └── app.js             # Client-side logic
├── models/
│   └── schemas.py         # Pydantic request/response models
├── routes/
│   ├── comic_routes.py    # Comic generation endpoints
│   └── health_routes.py   # Health and info endpoints
├── services/
│   ├── comic_service.py   # Story and task management
│   ├── gemini_service.py  # Gemini AI integration
│   ├── image_service.py   # Image generation and processing
│   └── pdf_service.py     # PDF creation
└── utils/
    ├── logger_config.py   # Logging setup
    ├── validators.py      # Input validation helpers
    └── frontend.py        # Frontend mounting utilities
```

## Development Notes

### Current Limitations
- Task registry and comic store are in-memory (use Redis/database for production)
- Rate limiting not yet implemented
- No authentication system
- Image generation requires Stable Diffusion API key (uses placeholders otherwise)

### Production Checklist
- [ ] Replace in-memory storage with persistent database (PostgreSQL/MongoDB)
- [ ] Add Redis for async task queue (Celery)
- [ ] Implement authentication and authorization
- [ ] Add rate limiting and request throttling
- [ ] Enable HTTPS and secure API keys
- [ ] Set up monitoring and error tracking
- [ ] Configure CORS properly for your domain
- [ ] Add request logging and audit trails

## Fallback Behavior

When API keys are not configured:
- **Gemini**: Returns placeholder dialogues
- **Stable Diffusion**: Generates colorful placeholder images with text

This allows full testing of the application flow without external APIs.

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.
