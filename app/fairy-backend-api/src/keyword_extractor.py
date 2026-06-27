"""
Rule-based keyword extraction for search queries.
検索クエリ用のルールベースキーワード抽出。
"""
import logging
import re

logger = logging.getLogger("uvicorn")

TIME_WORDS = frozenset({"今", "現在", "最近", "いま"})
MAX_KEYWORDS = 5

# Trailing phrases to strip before splitting
TAIL_PATTERN = re.compile(
    r"(が知りたい|を教えて|教えて|について|したい|して|ください|欲しい|は何|はなに|は？|は\?)$"
)
TOKEN_CLEAN_PATTERN = re.compile(r"[？?！!。、,]+$")
PARTICLE_SUFFIX_PATTERN = re.compile(r"(?:は|が)$")
PARTICLE_SPLIT_PATTERN = re.compile(r"[のをがにはでとや]")

DROP_TOKENS = frozenset({"今", "最近", "いま", "次", "何", "なに"})
VERB_SUFFIXES = ("評価教えて", "教えて", "知りたい")


def _clean_token(token: str) -> str:
    token = token.strip()
    token = TOKEN_CLEAN_PATTERN.sub("", token)
    token = PARTICLE_SUFFIX_PATTERN.sub("", token)
    token = TAIL_PATTERN.sub("", token)
    for suffix in VERB_SUFFIXES:
        if token.endswith(suffix) and len(token) > len(suffix):
            token = token[: -len(suffix)]
    return token.strip()


def _expand_compounds(tokens: list[str]) -> list[str]:
    expanded: list[str] = []
    for token in tokens:
        if token.startswith("最新") and len(token) > 2:
            expanded.extend(["最新", token[2:]])
        else:
            expanded.append(token)
    return expanded


def extract_keywords(message: str) -> str:
    """
    Extract search keywords from a user message using deterministic rules.
    ユーザー入力からルールベースで検索キーワードを抽出する。
    """
    text = TAIL_PATTERN.sub("", message.strip())
    chunks = PARTICLE_SPLIT_PATTERN.split(text)

    tokens: list[str] = []
    for chunk in chunks:
        cleaned = _clean_token(chunk)
        if not cleaned or cleaned in DROP_TOKENS:
            continue
        if len(cleaned) == 1 and not re.match(r"[A-Za-z0-9]", cleaned):
            continue
        tokens.append(cleaned)

    tokens = _expand_compounds(tokens)

    seen: set[str] = set()
    keywords: list[str] = []
    for token in tokens:
        if token not in seen:
            seen.add(token)
            keywords.append(token)
        if len(keywords) >= MAX_KEYWORDS:
            break

    result = " ".join(keywords)
    if any(word in message for word in TIME_WORDS) and "最新" not in result:
        result = f"{result} 最新"

    if not result:
        result = message

    logger.info(f"Keyword extraction: '{message}' -> '{result}'")
    return result
