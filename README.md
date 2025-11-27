# 高性能リサーチ AIBot 「[Fairy](https://fairy.krz-tech.net)」
HoyoverseのアクションRPG「ゼンレスゾーンゼロ」に登場するFairyというAIアシスタントをモチーフにしたリサーチAIBot。Discord上で簡易的なリサーチ結果を確認でき、より詳細な情報や参照URLなどを発行されたURLからブラウザ上で閲覧可能。URLを共有することでDiscord外でもリサーチ結果を共有することができる。

## デプロイ先
Fairy -> https://fairy.krz-tech.net

## 使い方
* Discord上で`@fairy Zenless Zone Zero`のように入力してください。
* Fairyがホロウを探索して情報を収集します。
* 探索が完了し、生成した回答が返答されます。また、より詳細な情報や参照したサイトのURLは外部リンクからアクセスすることができます。

## 利用規約
* **Gemini APIの利用**: 情報収集・分析のためにGoogle Gemini APIを使用します。
* **データの保存**: リサーチ結果や会話データは、サービスの品質向上および履歴管理のために保存されます。
* **免責事項**: 生成された情報の正確性について保証するものではありません。

## 技術構成
### Discord
* Python
* discord.py

### Web (Frontend)
* Vue.js (Vite)
* Tabler Icons

### Web & Discord (Backend)
* Python (FastAPI)
* Google Gemini 2.5 Flash Lite
* MongoDB (NoSQL)
