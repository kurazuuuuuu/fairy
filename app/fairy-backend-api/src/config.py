"""
Environment Configuration / 環境設定モジュール

Centralized environment variable management with validation.
すべての環境変数を一元管理し、起動時に検証します。
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("uvicorn")


class Config:
    """
    Application configuration loaded from environment variables.
    環境変数から読み込むアプリケーション設定。
    """
    
    # Required environment variables / 必須環境変数
    GEMINI_API_KEY: str
    JWT_SECRET: str
    MONGODB_URI: str
    BASE_URL: str
    FRONTEND_URL: str
    
    # Optional environment variables with defaults / オプション環境変数（デフォルト値あり）
    CORS_ORIGINS: list[str]
    APP_VERSION: str
    OLLAMA_HOST: str
    GEMMA_MODEL: str
    
    def __init__(self):
        # Required variables - raise error if not set
        # 必須変数 - 未設定の場合はエラー
        self.GEMINI_API_KEY = self._get_required("GEMINI_API_KEY")
        self.JWT_SECRET = self._get_required("JWT_SECRET")
        self.MONGODB_URI = self._get_required("MONGODB_URI")
        self.BASE_URL = self._get_required("BASE_URL")
        self.FRONTEND_URL = self._get_required("FRONTEND_URL")
        
        # Optional variables with defaults
        # オプション変数（デフォルト値あり）
        self.APP_VERSION = os.getenv("APP_VERSION", "unknown")
        
        cors_origins = os.getenv("CORS_ORIGINS", "")
        if cors_origins:
            self.CORS_ORIGINS = [origin.strip() for origin in cors_origins.split(",")]
        else:
            self.CORS_ORIGINS = ["https://fairy.krz-tech.net"]
            logger.warning("CORS_ORIGINS not set, using default: https://fairy.krz-tech.net")
        
        # Ollama settings (for keyword extraction)
        self.OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.GEMMA_MODEL = os.getenv("GEMMA_MODEL", "gemma3:1b")
    
    def _get_required(self, key: str) -> str:
        """Get a required environment variable or raise an error."""
        value = os.getenv(key)
        if not value:
            error_msg = f"Required environment variable '{key}' is not set"
            logger.error(error_msg)
            raise ValueError(error_msg)
        return value
    
    def validate(self) -> bool:
        """Validate all configuration values are properly set."""
        logger.info("=" * 50)
        logger.info(f"Fairy Backend API Version: {self.APP_VERSION}")
        logger.info("=" * 50)
        logger.info("Configuration loaded successfully:")
        logger.info(f"  - MONGODB_URI: {self.MONGODB_URI[:20]}...")
        logger.info(f"  - BASE_URL: {self.BASE_URL}")
        logger.info(f"  - FRONTEND_URL: {self.FRONTEND_URL}")
        logger.info(f"  - CORS_ORIGINS: {self.CORS_ORIGINS}")
        logger.info(f"  - GEMINI_API_KEY: {'*' * 10}...")
        logger.info(f"  - JWT_SECRET: {'*' * 10}...")
        logger.info(f"  - OLLAMA_HOST: {self.OLLAMA_HOST}")
        logger.info(f"  - GEMMA_MODEL: {self.GEMMA_MODEL}")
        return True


# Singleton instance / シングルトンインスタンス
config = Config()
