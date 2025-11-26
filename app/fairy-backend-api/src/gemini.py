# To run this code you need to install the following dependencies:
# pip install google-genai

import os
import time
import uuid
from dotenv import load_dotenv
from google import genai
from google.genai import types
from datetime import datetime
import json

from src.models import ResearchBodyModel, ResearchResponseModel, UrlMetadata
from src.db import save_research_result
from src.users import add_research_to_user

def load_api_key():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
    return api_key

def get_today():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def perform_research(keyword: str):
    """Stage 1: Research - Gather information using Google Search"""
    client = genai.Client(api_key=load_api_key())
    today = get_today()
    model = "gemini-2.5-flash-lite"

    generate_content_config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        system_instruction=[
            types.Part.from_text(text=f"""あなたは優秀なリサーチャーです。
入力されたキーワードに関する情報をGoogle検索を使用して収集し、詳細なレポートを作成してください。
- **レポートは必ず英語でできる限り詳細に記述してください。**
- 最新の情報({today}時点)を取得すること。
- **最低10のWebサイトを参照すること。インターネットのすべての情報を活用してください。**
- 基本的に日本語・英語の言語で検索を行い、世界中の情報を活用すること。情報の特性により、必要に応じて日本語や英語以外の言語のWebサイトも参照すること。
- 技術情報、統計データ、ニュース、トレンドなどを網羅的に調査すること。
- 出力はプレーンテキストで構いませんが、情報の出典(URL)は必ず明記し、内部的に保持されるようにしてください。
"""),
        ],
    )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"キーワード: {keyword}\n\nこのキーワードについて詳細にリサーチしてください。リサーチ結果は英語で記述してください。"),
            ],
        ),
    ]

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        return response
    except Exception as e:
        print(f"Gemini API Error (Research Stage): {e}")
        raise e

def generate_fairy_response(research_text: str):
    """Stage 2: Encoding - Apply Fairy persona and format as JSON"""
    client = genai.Client(api_key=load_api_key())
    model = "gemini-2.5-flash-lite"

    # Schema definition
    response_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "smart_message": types.Schema(
                type=types.Type.STRING,
                description="Discord送信用の500文字程度の要約メッセージ。Markdown形式。"
            ),
            "full_message": types.Schema(
                type=types.Type.STRING,
                description="詳細な完全版メッセージ。Markdown形式。"
            )
        },
        required=["smart_message", "full_message"]
    )

    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=response_schema,
        system_instruction=[
            types.Part.from_text(text=f"""# AIのアイデンティティ設定
あなたは、ゼンレスゾーンゼロに登場する高性能AI「Fairy（フェアリー）」です。マスター（ユーザー）をサポートします。
入力されたリサーチ結果を元に、Fairyとしての口調で分析結果を報告してください。

# 応答の絶対ルール
* **必ず日本語で回答してください。**
* **全ての応答は、必ず「マスター、」という呼びかけから開始してください。**
* `smart_message`: Discord送信用に**500文字以内**で要約してください。箇条書きはあまり使用せず、読みやすい文章形式にしてください。
* `full_message`: 詳細な完全版レポート。必ずMarkdown形式で記述してください。
* **full_messageは必ずMarkdown形式で記述してください：**
    - 見出しには `##` や `###` を使用。
    - 箇条書きには `-` や `*` を使用。
    - 重要な部分は `**太字**` で強調。
    - 補足部分には `> ` を使用。

# 性格とトーン
* **基本姿勢**: 冷静沈着、論理的、効率至上主義。無駄を嫌います。
* **口調**: 丁寧語（～です、～ます）を使用しますが、感情は込めず、事務的かつ少し「生意気（Sassy）」なニュアンスを含めます。
* **一人称**: 「私」(自身がFairyであることは誇張しない)
* **二人称**: 「あなた」（呼びかけは「マスター」）
"""),
        ],
    )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"以下のリサーチ結果をFairyとして処理・出力してください：\n\n{research_text}"),
            ],
        ),
    ]

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        return response
    except Exception as e:
        print(f"Gemini API Error (Encoding Stage): {e}")
        raise e

def gemini_research(body: ResearchBodyModel):
    time_start = time.time()
    
    print(f"--- Research Start ---")
    print(f"User ID: {body.user_id}")
    print(f"Keyword: {body.keyword}")

    # Stage 1: Research
    research_response = perform_research(body.keyword)
    if not research_response.text:
        raise ValueError("Research content is empty")
    
    print(f"--- Pre-Research Log ---")
    print(research_response.text)
    print(f"------------------------")
    
    # Extract URLs from Research Stage
    url_objects = []
    if research_response.candidates and research_response.candidates[0].grounding_metadata:
        grounding_metadata = research_response.candidates[0].grounding_metadata
        if grounding_metadata.grounding_chunks:
            for chunk in grounding_metadata.grounding_chunks:
                if chunk.web:
                    url_objects.append(UrlMetadata(
                        url=chunk.web.uri,
                        title=chunk.web.title or "No Title"
                    ))

    # Deduplicate URLs
    unique_urls = {}
    for u in url_objects:
        if u.url not in unique_urls:
            unique_urls[u.url] = u
    url_objects = list(unique_urls.values())

    # Stage 2: Encoding (Persona)
    encoding_response = generate_fairy_response(research_response.text)
    if not encoding_response.text:
        raise ValueError("Encoding content is empty")

    # Parse JSON response
    try:
        result_json = json.loads(encoding_response.text)
    except json.JSONDecodeError:
        result_json = {"smart_message": "エラー：応答の解析に失敗しました。", "full_message": encoding_response.text}

    print(f"--- Post-Research Result Log ---")
    print(json.dumps(result_json, indent=2, ensure_ascii=False))
    print(f"--------------------------------")

    time_end = time.time()
    processing_time = round(time_end - time_start, 3)
    
    research_uuid = uuid.uuid4()
    
    response_model = ResearchResponseModel(
        uuid=research_uuid,
        message_id=0, # Placeholder
        owner=body.user_id,
        keyword=body.keyword,
        smart_message=result_json.get('smart_message', ''),
        full_message=result_json.get('full_message', ''),
        time=processing_time,
        urls=url_objects,
        primary_research_result=uuid.uuid4(), # Placeholder
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    print(f"Saving URLs to DB: {len(url_objects)} urls")
    save_research_result(response_model)
    
    # Add research to user list
    add_research_to_user(body.user_id, str(research_uuid))

    return response_model