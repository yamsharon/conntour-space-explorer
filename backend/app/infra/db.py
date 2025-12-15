import json
import os
from typing import Dict, List

from app.utils.logger import logger


class SpaceDB:
    def __init__(self):
        logger.info("Initializing SpaceDB")
        # Load and parse the JSON data
        data_path = os.path.join(os.path.dirname(__file__), "data/mock_data.json")
        with open(data_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        logger.info(f"Loaded {len(json_data)} sources from {data_path}")
        # Flatten and map the data to the expected format
        self._sources = []
        items = json_data.get("collection", {}).get("items", [])
        logger.debug(f"Found {len(items)} items in the collection")
        for idx, item in enumerate(items, start=1):
            logger.debug(f"Processing item {idx}: {item}")
            data = item.get("data", [{}])[0]
            links = item.get("links", [])
            image_url = None
            logger.debug(f"Found {len(links)} links for item {idx}")
            for link in links:
                if link.get("render") == "image":
                    image_url = link.get("href")
                    break
            logger.debug(f"Found image URL: {image_url} for item {idx}")
            self._sources.append(
                {
                    "id": idx,
                    "name": data.get("title", f"NASA Item {idx}"),
                    "type": data.get("media_type", "unknown"),
                    "launch_date": data.get("date_created", ""),
                    "description": data.get("description", ""),
                    "image_url": image_url,
                    "status": "Active",
                }
            )
            logger.debug(f"Added source {idx}: {self._sources[-1]}")
        self._next_id = len(self._sources) + 1

    def get_all_sources(self) -> List[Dict]:
        """Get all space sources."""
        logger.info(f"Returning {len(self._sources)} sources")
        return self._sources
