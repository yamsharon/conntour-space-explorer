"""Main FastAPI application."""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import get_db, get_language_model
from app.api.history_controller import HistoryController
from app.api.search_controller import SearchController
from app.api.sources_controller import SourcesController
from app.utils.logger import logger

load_dotenv(override=True)
logger.info("Environment variables loaded")

app = FastAPI(
    title="Conntour Space Explorer API",
    description="API for browsing and searching NASA space images",
    version="1.0.0",
)

logger.info("Starting Conntour Space Explorer backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize infrastructure components on app startup."""
    logger.info("Initializing infrastructure components...")

    # Initialize language model (will be cached by @lru_cache)
    logger.info("Initializing language model...")
    get_language_model()
    logger.info("Language model initialized")

    # Initialize database (will be cached by @lru_cache)
    logger.info("Initializing database...")
    get_db()
    logger.info("Database initialized")

    logger.info("All infrastructure components initialized")


# Initialize controllers (dependencies are injected via FastAPI Depends)
sources_controller = SourcesController()
app.include_router(sources_controller.router)
search_controller = SearchController()
app.include_router(search_controller.router)
history_controller = HistoryController()
app.include_router(history_controller.router)
logger.info("All controllers initialized")
