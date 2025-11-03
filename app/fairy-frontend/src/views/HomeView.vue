<script setup lang="ts">
</script>

<template>
  <main class="home">
    <div class="container">
      <h1>高性能リサーチAIBot「Fairy」</h1>
      <p class="subtitle">ゼンレスゾーンゼロの「Fairy」をモチーフにしたリサーチ用DiscordBot</p>
      
      <section class="overview">
        <h2>概要</h2>
        <ul>
          <li>Google Geminiを使用したリサーチ用Bot</li>
          <li>Deep Researchほどの精度は求めず、簡単な情報収集を目的としている</li>
          <li>インターネット検索によるグラウンディングを行い、最新情報をなるべく収集する</li>
          <li>Discordの中だけではなく外部サイトとの連携でより詳細な情報にアクセスすることができる</li>
        </ul>
      </section>

      <section class="usage">
        <h2>使い方</h2>
        <ol>
          <li><code>@fairy</code>のようにメンションを行い、その後に<strong>聞きたい内容</strong>を入力して送信する。
            <ul>
              <li>例: <code>@fairy ゼンレスゾーンゼロの最新アップデートについて教えて</code></li>
            </ul>
          </li>
          <li>Botが情報を収集し、回答を返すまで少し時間がかかります。</li>
          <li>情報収集が完了し、生成した回答が返答されます。また、より詳細な情報や参照したサイトのURLは外部リンク（Web側）にアップロードされているためそちらから確認をすることができます。</li>
        </ol>
      </section>

      <section class="tech">
        <h2>技術構成</h2>
        <div class="tech-grid">
          <div class="tech-item">
            <h3>Discord</h3>
            <ul>
              <li>Python</li>
              <li>discord.py</li>
            </ul>
          </div>
          <div class="tech-item">
            <h3>Web (Frontend)</h3>
            <ul>
              <li>Vue.js (Vite)</li>
            </ul>
          </div>
          <div class="tech-item">
            <h3>Web & Discord (Backend)</h3>
            <ul>
              <li>Python (FastAPI)</li>
              <li>Google Gemini 2.5 Flash</li>
              <li>MongoDB (NoSQL)</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>

<style scoped>
.home {
  min-height: 100vh;
  background: #222122;
  background-image: repeating-linear-gradient(
    -45deg,
    transparent,
    transparent 5px,
    #181718 5px,
    #181718 10px
  );
  padding: 60px 20px;
}

.container {
  max-width: 900px;
  margin: 0 auto;
}

h1 {
  color: #ffffff;
  font-size: 2.2em;
  margin-bottom: 10px;
  font-weight: 400;
  letter-spacing: 0.05em;
}

.subtitle {
  color: #cccccc;
  font-size: 0.95em;
  margin-bottom: 60px;
  font-weight: 400;
}

section {
  margin-bottom: 50px;
}

h2 {
  color: #ffffff;
  font-size: 1.4em;
  margin-bottom: 20px;
  font-weight: 400;
  letter-spacing: 0.05em;
}

ul, ol {
  line-height: 1.9;
  color: #e0e0e0;
  font-weight: 400;
}

ul li, ol li {
  margin-bottom: 10px;
}

code {
  background: #181718;
  padding: 3px 8px;
  border-radius: 4px;
  color: #e0e0e0;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.tech-item {
  background: #2a292a;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #181718;
  transition: all 0.2s ease;
}

.tech-item:hover {
  background: #323132;
  border-color: #3a393a;
}

.tech-item h3 {
  color: #ffffff;
  margin-bottom: 16px;
  font-size: 1.2em;
  font-weight: 600;
}

.tech-item ul {
  list-style: none;
  padding: 0;
}

.tech-item li {
  padding: 6px 0;
  color: #e0e0e0;
  font-size: 0.95em;
}
</style>
