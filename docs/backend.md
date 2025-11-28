# バックエンド
## Discord
1. `@fairy ゼンレスゾーンゼロの最新アップデートについて教えて`
2. Discordの送信者のユーザーIDとkeywordを`/api/research`にPOST
3. レスポンスをDiscordに送信＆DBに保管、URLを発行。
## FastAPIバックエンド
### URL：https://api-fairy.krz-tech.net

### 認証
- **JWT Authentication**: ほとんどのエンドポイントで `Authorization: Bearer <token>` ヘッダーが必要です。
- トークンは `/api/auth/token` エンドポイントで取得できます。

### エンドポイント

#### ユーザー・認証
- **POST** `/api/auth/token`
    - ユーザーIDからJWTトークンを生成します。
    - Body:
    ```json
    {
        "user_id": int
    }
    ```
    - Response:
    ```json
    {
        "access_token": str,
        "token_type": "bearer"
    }
    ```

- **POST** `/api/users/tos`
    - 利用規約への同意状態を更新します。
    - Header: `Authorization: Bearer <token>`
    - Body:
    ```json
    {
        "user_id": int
    }
    ```

#### リサーチ
- **POST** `/api/research`
    - 新規リサーチを実行します。
    - Header: `Authorization: Bearer <token>`
    - Body:
    ```json
    {
        "user_id": int,
        "keyword": str
    }
    ```
    - Response: `ResearchResponseModel` (下記参照)

- **GET** `/api/research/{uuid}`
    - 過去のリサーチ結果を取得します。
    - Header: `Authorization: Bearer <token>`
    - Response: `ResearchResponseModel` (下記参照)

- **POST** `/api/research/followup`
    - 既存のリサーチ結果に基づいて追加リサーチを行います。
    - Header: `Authorization: Bearer <token>`
    - Body:
    ```json
    {
        "user_id": int,
        "keyword": str,
        "parent_message_id": int
    }
    ```
    - Response: `ResearchResponseModel` (下記参照)

- **PATCH** `/api/research/{uuid}/message`
    - リサーチ結果に関連するDiscordメッセージIDを更新します。
    - Header: `Authorization: Bearer <token>`
    - Body:
    ```json
    {
        "message_id": int
    }
    ```

### データモデル

#### ResearchResponseModel
```json
{
    "uuid": str (UUID),
    "message_id": int,
    "owner": int (User ID),
    "keyword": str,
    "smart_message": str (AIによる要約),
    "full_message": str (AIによる詳細レポート),
    "urls": [
        {
            "url": str,
            "title": str | null,
            "description": str | null,
            "image": str | null
        }
    ],
    "created_at": timestamp
}
```