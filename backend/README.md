# Conntour Space Explorer - Backend

## Overview

FastAPI backend for browsing and searching NASA space images. Provides REST endpoints for fetching images and performing semantic search using CLIP (Contrastive Language-Image Pre-training) for image-text matching.

## Prerequisites

- **Python 3.8+**
- **uv** (Python package installer)

## Setup Instructions

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Using uv
   uv venv
   source .venv/bin/activate  # On Unix/MacOS
   .venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies:**
   ```bash
   # Using uv
   uv pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   uvicorn app.main:app --reload --port 5000
   ```

   The API will be available at `http://localhost:5000`
   - API docs: `http://localhost:5000/docs`

## Project Structure

```
backend/
├── app/
│   ├── api/              # API controllers
│   ├── domain/           # Business logic and models
│   ├── infra/            # Infrastructure layer (DB, models)
│   ├── utils/            # Utilities (logging, embeddings, constants)
│   └── main.py           # FastAPI app entry point
├── logs/                 # Log files (auto-created)
├── requirements.txt      # Python dependencies
└── README.md
```

## Architecture

The backend follows a 3-layer architecture:

- **API Layer** (`api/`): Controllers handle HTTP requests/responses
- **Domain Layer** (`domain/`): Business logic and models
- **Infrastructure Layer** (`infra/`): Data access and external services

## API Endpoints

- `GET /api/sources` - Get all NASA image sources
- `GET /api/search?q=<query>&limit=<number>` - Semantic search using text-to-image matching with confidence scores. Default limit is 15

## Environment Variables

Create a `.env` file in the backend directory:

```env
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/app.log   # Log file path
```


## Logging

Logs are written to both console and file (`logs/app.log` by default). The log file rotates when it reaches 5MB, keeping 3 backup files.

Log format includes filename, line number, and function name for easier debugging:
```
2024-01-15 10:30:45 - conntour-space-explorer - INFO - [db.py:58:get_all_sources] - Getting all sources
```

## Embedding Cache

Image embeddings are cached to `app/infra/data/embeddings_cache.pkl` to speed up startup. The cache is automatically:
- Created on first run (when embeddings are generated)
- Used on subsequent runs (much faster startup)
- Invalidated if the data file (`mock_data.json`) is modified

## Notes

- The CLIP model is loaded once on startup
- Image embeddings are generated from image URLs using CLIP's vision encoder
- Text queries are encoded using CLIP's text encoder
- Search uses cosine similarity between normalized text and image embeddings
- Confidence scores are normalized to [0.2, 1.0] range for better UX

