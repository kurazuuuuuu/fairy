import discord
import logging
from logging import getLogger, StreamHandler

# ログ設定を初期化
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        StreamHandler()
    ]
)

# 共通のloggerを提供
logger = getLogger('fairy')

class Logger():
    @staticmethod
    def get_logger(name: str = 'fairy'):
        return getLogger(name)