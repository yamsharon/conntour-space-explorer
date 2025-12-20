import os.path

# Data Paths
MOCK_DATA_JSON = os.path.join("data", "mock_data.json")
EMBEDDING_CACHE = os.path.join("data", "embeddings_cache.pkl")
DEFAULT_LOG_PATH = os.path.join("logs", "app.log")

# Embedding
EMBEDDING_KEY = "embedding"
NORMALIZED_MINIMUM = 0.2
NORMALIZED_MAXIMUM = 1.0
NORMALIZED_MEDIAN = (NORMALIZED_MAXIMUM + NORMALIZED_MINIMUM) / 2
