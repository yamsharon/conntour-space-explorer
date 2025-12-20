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
  - `sources_controller.py`: Handles `/api/sources` endpoint
  - `search_controller.py`: Handles `/api/search` endpoint
  - `history_controller.py`: Handles `/api/history` endpoints
- **Domain Layer** (`domain/`): Business logic and models
  - `services/`: Business logic services (SourcesService, SearchService, HistoryService)
  - `models.py`: Pydantic models for API responses
- **Infrastructure Layer** (`infra/`): Data access and external services
  - `db.py`: Database access and embedding storage
  - `language_model.py`: CLIP model wrapper for embeddings

## API Endpoints

- `GET /api/sources` - Get all NASA image sources
- `GET /api/search?q=<query>&limit=<number>&skipHistory=<boolean>` - Semantic search using text-to-image matching with confidence scores. 
  - `q`: Natural language search query (required)
  - `limit`: Maximum number of results (default: 15, range: 1-100)
  - `skipHistory`: If `true`, don't save this search to history (default: `false`). Useful when navigating from history page to prevent duplicate entries.
- `GET /api/history?startIndex=<number>&limit=<number>` - Get paginated search history
  - `startIndex`: Starting index for pagination (default: 0)
  - `limit`: Number of items to return (default: 10, max: 100)
  - Returns: `HistoryResponse` with `items` (list of `SearchResultHistoryResponse`) and `total` count
  - Each item includes: `id`, `query`, `time_searched`, and `top_three_images` (for display in history list)
- `GET /api/history/{history_id}/results` - Get the full search results for a specific history item
  - `history_id`: UUID of the history item
  - Returns: List of `SearchResult` objects (the complete original search results)
  - Used by the frontend to display the exact results from a past search without re-running the search
- `DELETE /api/history/{history_id}` - Delete a specific history item by ID
  - Returns: 204 No Content if successful, 404 if not found

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

## Dependency Injection

The backend uses FastAPI's dependency injection system for managing service lifecycles:

- Infrastructure components (`LanguageModel`, `SpaceDB`) are initialized on app startup
- Services are injected into controllers using `Depends()` and `@lru_cache()` decorators
- This ensures singleton behavior and improves testability

See `app/api/dependencies.py` for dependency definitions.

## Notes

- The CLIP model is loaded once on startup (eager initialization)
- Image embeddings are generated from image URLs using CLIP's vision encoder
- Text queries are encoded using CLIP's text encoder
- Search uses cosine similarity between normalized text and image embeddings
- Confidence scores are normalized to [0.2, 1.0] range for better UX
- Search history is automatically saved unless `skipHistory=true` is specified
- History items are sorted by most recent first
- Full search results are stored with each history entry, allowing retrieval of exact original results via `/api/history/{id}/results`
- The history list endpoint returns only `top_three_images` for efficiency; use the results endpoint to get all results

