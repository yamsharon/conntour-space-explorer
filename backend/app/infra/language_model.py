from sentence_transformers import SentenceTransformer

from app.utils.logger import logger


class LanguageModel:
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self):
        logger.info("Initializing a language model with sentence-transformers")
        try:
            # Using all-MiniLM-L6-v2: fast, good quality, 384 dimensions
            # Possible to use a better model, but it may cause performance issues
            # I chose this lean one as one of the requirement was -
            #   the browsing experience should be clear, visually friendly...
            self.model = SentenceTransformer(LanguageModel.MODEL_NAME)
            logger.info(f"Model loaded: {LanguageModel.MODEL_NAME}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
