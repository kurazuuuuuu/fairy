"""
Redis Manager Service
Cache strategy:
1. Exact match (String Key): "research:keyword:{keyword}" -> JSON Result
2. Vector Search (RediSearch): "research:vector" index -> Similarity Search
"""
import logging
import json
import redis
import numpy as np
from typing import Optional, List, Dict, Any
from redis.commands.search.field import TextField, VectorField, NumericField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from src.config import config

logger = logging.getLogger("uvicorn")

# Redis Keys Prefix
PREFIX = "research:"
INDEX_NAME = "research_idx"
VECTOR_DIM = 768  # Assuming standard size, but should be configurable or match model output

class RedisManager:
    def __init__(self):
        try:
            self.client = redis.from_url(config.REDIS_URL, decode_responses=True)
            self.is_connected = self.client.ping()
            logger.info("Connected to Redis Stack successfully.")
            self._create_index()
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
            self.is_connected = False

    def _create_index(self):
        """Create RediSearch index if it doesn't exist."""
        if not self.is_connected:
            return

        try:
            self.client.ft(INDEX_NAME).info()
            logger.info(f"Index '{INDEX_NAME}' already exists.")
        except:
            logger.info(f"Creating index '{INDEX_NAME}'...")
            # Define schema
            schema = (
                TextField("$.keyword", as_name="keyword"),
                TextField("$.full_message", as_name="full_message"),
                VectorField(
                    "$.embedding",
                    "FLAT", # or HNSW for larger datasets
                    {
                        "TYPE": "FLOAT32",
                        "DIM": VECTOR_DIM,
                        "DISTANCE_METRIC": "COSINE",
                    },
                    as_name="embedding",
                ),
            )
            
            # Create Index for JSON documents
            self.client.ft(INDEX_NAME).create_index(
                schema,
                definition=IndexDefinition(prefix=[PREFIX], index_type=IndexType.JSON)
            )

    async def get_cache(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Get exact match from cache."""
        if not self.is_connected:
            return None
            
        key = f"{PREFIX}{keyword}"
        try:
            # Use JSON.GET for Redis Stack JSON
            data = self.client.json().get(key)
            if data:
                logger.info(f"Cache HIT for keyword: {keyword}")
                return data
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
        
        return None

    async def save_research(self, keyword: str, data: Dict[str, Any], embedding: List[float]):
        """Save research result with embedding."""
        if not self.is_connected:
            return

        key = f"{PREFIX}{keyword}"
        try:
            # Set data into JSON with Embedding
            data["embedding"] = embedding
            
            # Save to Redis JSON
            self.client.json().set(key, "$", data)
            # Set TTL (e.g., 24 hours = 86400 sec)
            self.client.expire(key, 86400) 
            logger.info(f"Saved research cache for: {keyword}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    async def vector_search(self, embedding: List[float], top_k: int = 3, threshold: float = 0.2) -> List[Dict[str, Any]]:
        """
        Search for similar research results using Vector Search.
        Returns list of similar full_messages or summary data.
        """
        if not self.is_connected:
            return []

        try:
            # Prepare query
            # KNN search syntax: "*=>[KNN {k} @embedding $vec_blob AS score]"
            # But redis-py handles params binding elegantly
            query = (
                Query(f"(*)=>[KNN {top_k} @embedding $query_vec AS vector_score]")
                .sort_by("vector_score")
                .return_fields("vector_score", "keyword", "full_message")
                .paging(0, top_k)
                .dialect(2)
            )
            
            # Convert list float to bytes for query param
            # Note: Redis expects raw bytes for FLOT32 vector
            vec_blob = np.array(embedding, dtype=np.float32).tobytes()
            
            params = {"query_vec": vec_blob}
            
            results = self.client.ft(INDEX_NAME).search(query, query_params=params)
            
            hits = []
            for doc in results.docs:
                score = float(doc.vector_score)
                # Cosine distance: lower is closer. 0 = exact match, 2 = opposite.
                # Threshold logic: if score < threshold (very close)
                if score < threshold: 
                    hits.append({
                        "keyword": doc.keyword,
                        "full_message": doc.full_message,
                        "score": score
                    })
            
            return hits

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

# Singleton
redis_manager = RedisManager()
