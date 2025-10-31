# 高性能リサーチAIBot「Fairy」
ゼンレスゾーンゼロの「Fairy」をモチーフにしたリサーチ用DiscordBot

## 概要
- Google Geminiを使用したリサーチ用Bot
- Deep Researchほどの精度は求めず、簡単な情報収集を目的としている
- インターネット検索によるグラウンディングを行い、最新情報をなるべく収集する
- Discordの中だけではなく外部サイトとの連携でより詳細な情報にアクセスすることができる

## 使い方
1. `@fairy`のようにメンションを行い、その後に**聞きたい内容**を入力して送信する。
    - 例: `@fairy ゼンレスゾーンゼロの最新アップデートについて教えて`
2. Botが情報を収集し、回答を返すまで少し時間がかかります。
3. 情報収集が完了し、生成した回答が返答されます。また、より詳細な情報や参照したサイトのURLは外部リンク（Web側）にアップロードされているためそちらから確認をすることができます。

## 技術構成
### Discord
- Python
- discord.py

### Web (Frontend)
- Vue.js (Vite)

### Web & Discord (Backend)
- Python (FastAPI)
- Google Gemini 2.5 Flash
- MongoDB (NoSQL)