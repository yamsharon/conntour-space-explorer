
from transformers import CLIPProcessor, CLIPModel

from app.utils.logger import logger


class LanguageModel:
    """Language model for generating embeddings."""

    MODEL_NAME = "openai/clip-vit-base-patch32"

    def __init__(self):
        """Initialize the LanguageModel."""
        logger.info("Initializing a language model with sentence-transformers")
        # Load the model and processor
        self.model = CLIPModel.from_pretrained(LanguageModel.MODEL_NAME)
        logger.debug(f"Model loaded: {LanguageModel.MODEL_NAME}")
        self.processor = CLIPProcessor.from_pretrained(LanguageModel.MODEL_NAME)
        logger.debug(f"Processor loaded: {LanguageModel.MODEL_NAME}")
