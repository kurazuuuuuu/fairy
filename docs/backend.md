# バックエンド
## Discord

## FastAPIバックエンド
### URL：https://fairy.krz-tech.net/
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
            "content": str,
            "urls": ["url1", "url2"...]
        },
        "created_at": timestamp,
        "shared": bool
    }
    ```