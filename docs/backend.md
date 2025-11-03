# バックエンド
## Discord
1. `@fairy ゼンレスゾーンゼロの最新アップデートについて教えて`
2. Discordの送信者のユーザーIDとkeywordを`/api/research`にPOST
3. レスポンスをDiscordに送信＆DBに保管、URLを発行。
## FastAPIバックエンド
### URL：https://fairy.krz-tech.net/api
### エンドポイント
- POST `/api/research`
    - Body:
    ```json
    {
        "user_id": str (DISCORD_ID),
        "keyword": str (Limit=200),
    }
    ```
    - Response:
    ```json
    {
        "uuid": str (UUID),
        "message": str
    }
    ```
- GET `/api/history/{UUID}`
    - Response:
    ```json
    {
        "user_id": str (DISCORD_ID),
        "keyword": str (Limit=200),
        "results": {
            "title": str,
            "content": str
        },
        "created_at": timestamp
    }
    ```