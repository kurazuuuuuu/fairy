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
    DISCORD_BOT_TOKEN: str
    BACKEND_INTERNAL_URL: str  # Internal cluster service URL / クラスタ内部サービスURL
    
    # Optional environment variables / オプション環境変数
    APP_VERSION: str
    
    def __init__(self):
        # Required variables - raise error if not set
        # 必須変数 - 未設定の場合はエラー
        self.DISCORD_BOT_TOKEN = self._get_required("DISCORD_BOT_TOKEN")
        self.BACKEND_INTERNAL_URL = self._get_required("BACKEND_INTERNAL_URL")
        
        # Optional variables
        self.APP_VERSION = os.getenv("APP_VERSION", "unknown")
    
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
        logger.info(f"Fairy Backend Bot Version: {self.APP_VERSION}")
        logger.info("=" * 50)
        logger.info("Configuration loaded successfully:")
        logger.info(f"  - DISCORD_BOT_TOKEN: {'*' * 10}...")
        logger.info(f"  - BACKEND_INTERNAL_URL: {self.BACKEND_INTERNAL_URL}")
        return True


# Singleton instance / シングルトンインスタンス
config = Config()
