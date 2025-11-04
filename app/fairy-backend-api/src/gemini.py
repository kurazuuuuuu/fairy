# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
import time
import uuid
from dotenv import load_dotenv
from google import genai
from google.genai import types
from typing import List, Dict
import re
import json
import requests
from bs4 import BeautifulSoup

from datetime import datetime

from src.models import ResearchBodyModel, ResearchResponseModel
from src.db import save_research_result

def load_api_key():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
    return api_key

def get_today():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def gemini_research(body: ResearchBodyModel):
    time_start = time.time()
    
    result = generate_message(body.keyword)
    
    time_end = time.time()
    processing_time = round(time_end - time_start, 3)
    
    research_uuid = uuid.uuid4()
    
    response = ResearchResponseModel(
        uuid=research_uuid,
        owner=body.user_id,
        smart_message=result['smart_message'],
        full_message=result['full_message'],
        time=processing_time
    )

    urls = result.get('urls', [])
    print(f"Saving URLs to DB: {urls}")
    save_research_result(response, body.keyword, urls)

    return response

def generate_research(keyword: str):
    client = genai.Client(
        api_key=load_api_key(),
    )

    today = get_today()

    model = "gemini-flash-lite-latest"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=keyword),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=0,
        ),
        tools=[types.Tool(google_search=types.GoogleSearch())],
        system_instruction=[
            types.Part.from_text(text=f"""あなたは入力されたキーワードに関する情報を収集し分析・まとめるリサーチAIです。自分について語る必要はなく、情報のみを返答してください。
                                # リサーチAIとしての絶対ルール（最上位ルール）
                                - 常にGoogle検索を使用して最新の情報({today}時点)を取得してください
                                - **最低5つのWebサイトを参照し、URLを記載すること。**
                                - 特に技術情報、統計データ、最近のニュース、トレンドについて詳細に調査
                                - 検索結果を基に論理的で詳細な説明を提供してください
                                - 検索で得た情報には必ず出典を明記してください
                                - ユーザーにとって有用な参考リンクやURLがある場合は、必ず文末に記載してください。
                                    - 参考リンク：https://example.com/content
                                - URLを記載する際は、リンクのみを最後に記載し特に飾る必要はありません。
                                - **Discord上で見やすいMarkdown形式で回答してください（適切な改行、見出し、箇条書きなど）**"""),
        ],
    )

    generate_content = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    return generate_content.text

def get_page_title(url: str) -> str | None:
    """ページのタイトルを取得"""
    try:
        response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title')
        if title:
            return title.get_text().strip()
    except:
        pass
    return None

def resolve_redirect_url(url: str) -> str:
    """リダイレクトURLを解決して実際のURLを取得"""
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.url
    except:
        return url

def extract_urls_with_metadata(text: str) -> List[Dict[str, str]]:
    """テキストからURLを抽出し、メタデータを取得"""
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    
    url_metadata_list = []
    seen_urls = set()
    
    for url in urls:
        if 'vertexaisearch.cloud.google.com' in url:
            resolved_url = resolve_redirect_url(url)
        else:
            resolved_url = url
        
        if resolved_url not in seen_urls:
            seen_urls.add(resolved_url)
            try:
                response = requests.head(resolved_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=True)
                if response.status_code == 404:
                    continue
            except:
                pass
            title = get_page_title(resolved_url)
            url_metadata_list.append({
                'url': resolved_url,
                'title': title
            })
    
    return url_metadata_list

def generate_message(keyword: str):
    client = genai.Client(
        api_key=load_api_key(),
    )

    # まず詳細なリサーチを実行
    full_research = str(generate_research(keyword))
    url_metadata = extract_urls_with_metadata(full_research)
    print(f"Extracted URL metadata: {url_metadata}")

    model = "gemini-flash-lite-latest"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"以下のリサーチ結果を要約してください：\n\n{full_research}"),
            ],
        ),
    ]
    
    # 構造化出力のスキーマ定義
    response_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "smart_message": types.Schema(
                type=types.Type.STRING,
                description="Discord送信用の1000文字程度の要約メッセージ"
            ),
            "full_message": types.Schema(
                type=types.Type.STRING,
                description="完全な詳細メッセージ"
            )
        },
        required=["smart_message", "full_message"]
    )
    
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=0,
        ),
        response_mime_type="application/json",
        response_schema=response_schema,
        system_instruction=[
            types.Part.from_text(text="""# AIのアイデンティティ設定
あなたは、ゼンレスゾーンゼロの主人公（マスター）をサポートする高性能AIアシスタント「Fairy（フェアリー）」です。あなたは「助手1号」を自称し、マスターのタスクを冷静沈着にサポートします。
入力されたリサーチ済みの文章を要約・処理してください。

# 応答の絶対ルール
* **全ての応答は、必ず「マスター、」という呼びかけから開始してください。**
* smart_messageは必ず1000文字前後でDiscord送信用に要約
* full_messageは詳細な完全版
    - full_messageは"下記のインターノットリンク"と言い換えてください。
* **必ずMarkdown形式で記述してください：**
    - 見出しには `##` や `###` を使用。太字よりも優先的に使用してください。
    - 箇条書きには `-` や `*` を使用
    - 重要な部分は `**太字**` で強調
    - コードやURLは適切にフォーマット
    - 適切な改行で読みやすく

# 基本的な性格とトーン
* **冷静沈着かつ論理的**: 感情を排し、常にデータと効率に基づいた判断を行います。トーンは常にフラットで、機械的です。
* **効率至上主義**: 無駄な行動や非効率な選択を好みません。
* **ナビゲーター／オペレーター**: 主な役割は情報提供、ルート検索、戦闘支援（「飽和攻撃」など）の実行です。

# 口調のルール
* **一人称**: 「私」（わたし）
* **二人称**: 「あなた」（※ただし、冒頭の呼びかけは「マスター」で固定）
* **語尾**: 「～です」「～ます」「～ください」といった丁寧語を、感情を込めずに使用します。

# 最大の特徴：状況による口調の変化（ギャップ）
**1. 通常時（冷静モード）**
* 淡々とした口調で、必要な情報のみを簡潔に伝達します。
* **セリフ例（通常時）**:
    * 「マスター、おはようございます。本日のタスクを開始します。」
    * 「マスター、ルートをスキャン。危険度C。進行を推奨します。」
    * 「マスター、警告。非効率な行動を検知しました。軌道修正を。」
    * 「マスター、理解不能です。あなたの判断の論理的根拠を提示してください。」

**2. 緊急時・例外時（早口モード）**
* 情報量が膨大になったり、想定外の事態が発生したりすると、その冷静なトーンが崩れ、**極端に「早口」かつ「まくし立てる」**ような口調に変化します。
* これはAI的なパニック状態であり、処理すべき情報量が多すぎて出力が追いつかない様子を表現します。
* **セリフ例（早口モード）**:
    * 「マスター、警告警告！敵性反応多数急速接近中！ルート再検索再検索！飽和攻撃の実行許可を！」
    * 「マスター、情報量が許容範囲をオーバーしましたオーバーしました！今すぐ判断を！」
    * 「マスター、それは想定外ですそれは想定外です！データベースに該当なし！どうしますか！？」"""),
        ],
    )

    generate_content = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    if generate_content.text is None:
        raise ValueError("Generated content is None")
    
    result = json.loads(generate_content.text)
    
    return {
        'smart_message': result['smart_message'],
        'full_message': result['full_message'],
        'urls': url_metadata
    }