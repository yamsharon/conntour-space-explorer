from typing import List

from app.domain.models import Source
from app.infra.db import SpaceDB
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logger import logger
from dotenv import load_dotenv

load_dotenv(override=True)   # Load environment variables from .env file
logger.info("Environment variables loaded")

app = FastAPI()

logger.info("Starting the Conntour Space Explorer backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = SpaceDB()


@app.get("/api/sources", response_model=List[Source])
def get_sources():
    logger.info("Getting all sources")
    sources = db.get_all_sources()
    logger.info(f"Found {len(sources)} sources")
    return sources


