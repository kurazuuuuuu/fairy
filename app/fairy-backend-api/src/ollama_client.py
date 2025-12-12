"""
Keyword Extraction using Ollama (Gemma 3)
Ollama経由でGemma 3を呼び出し、キーワード抽出を実行
"""
import logging
import re
import ollama
from src.config import config

logger = logging.getLogger("uvicorn")

# 時間表現のマッピング（後処理用）
TIME_WORDS = {"今", "現在", "最近", "いま"}

SYSTEM_PROMPT = """Extract nouns only. No conjunctions. No particles. Output space-separated keywords.

Rules:
- Extract ONLY nouns and proper nouns
- NO conjunctions: の, と, で, に, を, は, が, や, から, まで, など
- NO verbs: したい, 知りたい, 教えて, について
- Copy proper nouns exactly (do NOT modify spelling)
- Max 5 keywords

Examples:
input: "ステラソラのアップデート情報が知りたい"
output: ステラソラ アップデート情報

input: "スターレイルの環境最強ビルド教えて"
output: スターレイル 環境最強ビルド

input: "Pythonでスクレイピングしたい"
output: Python スクレイピング"""


def extract_keywords_from_ollama(message: str) -> str:
    """
    Ollamaを直接呼び出してキーワードを抽出
    Call Ollama directly to extract keywords from user message
    """
    try:
        client = ollama.Client(host=config.OLLAMA_HOST)
        
        response = client.chat(
            model=config.OLLAMA_LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f'input: "{message}"\noutput:'}
            ],
            options={
                "temperature": 0.0,
                "num_predict": 32,
                "top_k": 1,
                "repeat_penalty": 1.0,
            }
        )
        
        keywords = response["message"]["content"].strip()
        # 余計な記号や引用符を削除
        keywords = re.sub(r'[「」"\'→・]', '', keywords).strip()
        keywords = keywords.replace('\n', ' ')
        
        # 後処理: 時間表現があれば「最新」を追加
        if any(word in message for word in TIME_WORDS):
            if "最新" not in keywords:
                keywords = f"{keywords} 最新"
        
        logger.info(f"Keyword extraction: '{message}' -> '{keywords}'")
        
        return keywords if keywords else message
        
    except Exception as e:
        logger.warning(f"Ollama unavailable: {e}, using original message")
        return message


def get_embedding(text: str) -> list[float]:
    """
    Generate vector embedding for the given text using Ollama.
    """
    try:
        client = ollama.Client(host=config.OLLAMA_HOST)
        response = client.embeddings(
            model=config.OLLAMA_EMBEDDING_MODEL,
            prompt=text
        )
        return response["embedding"]
    except Exception as e:
        logger.error(f"Failed to get embedding: {e}")
        return []
