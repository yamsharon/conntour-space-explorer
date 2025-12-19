"""Main FastAPI application."""

from app.api.history_controller import HistoryController
from app.api.search_controller import SearchController
from app.api.sources_controller import SourcesController
from app.domain.services.history_service import HistoryService
from app.domain.services.search_service import SearchService
from app.domain.services.sources_service import SourcesService
from app.infra.db import SpaceDB
from app.infra.language_model import LanguageModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logger import logger
from dotenv import load_dotenv

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

# Initialize Infra
lm = LanguageModel()
db = SpaceDB(lm)
logger.info("All infra initialized")

# Initialize services
sources_service = SourcesService(db=db)
history_service = HistoryService(db=db)
search_service = SearchService(db=db, lm=lm, history_service=history_service)
logger.info("All services initialized")

# Initialize controllers
sources_controller = SourcesController(sources_service=sources_service)
app.include_router(sources_controller.router)
search_controller = SearchController(search_service=search_service)
app.include_router(search_controller.router)
history_controller = HistoryController(history_service=history_service)
app.include_router(history_controller.router)
logger.info("All controllers initialized")

