<script setup lang="ts">
import { BrandDiscordIcon } from 'vue-tabler-icons';
const discordInviteUrl = import.meta.env.VITE_DISCORD_INVITE_URL
</script>

<template>
  <main class="home">
    <div class="container">
      <section class="hero">
        <img src="/images/fairy.webp" alt="Fairy Logo" class="hero-logo" />
        <h1 class="hero-title">Fairy</h1>
        <p class="hero-subtitle">助手1号</p>
      </section>
      
      <section class="content-section overview">
        <p>HoyoverseのアクションRPG「ゼンレスゾーンゼロ」に登場するFairyというAIアシスタントをモチーフにしたリサーチAIBot。Discord上で簡易的なリサーチ結果を確認でき、より詳細な情報や参照URLなどを発行されたURLからブラウザ上で閲覧可能。URLを共有することでDiscord外でもリサーチ結果を共有することができる。</p>
      </section>

      <section class="content-section usage">
        <ol>
          <li>Discord上で<code>@fairy Zenless Zone Zero</code>のように入力してください。</li>
          <li>Fairyがホロウを探索して情報を収集します。</li>
          <li>探索が完了し、生成した回答が返答されます。また、より詳細な情報や参照したサイトのURLは外部リンクからアクセスすることができます。</li>
        </ol>
      </section>

      <section class="content-section invite">
        <p>Fairyをあなたのサーバーに招待しましょう。</p>
        <a :href="discordInviteUrl" target="_blank" rel="noopener noreferrer" class="invite-button">
          <BrandDiscordIcon size="24" class="icon" />
          <span>Invite to Server</span>
        </a>
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
  color: #e0e0e0;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  margin-bottom: 80px;
  padding-top: 40px;
}

.hero-logo {
  width: 120px;
  height: 120px;
  margin-bottom: 20px;
  border-radius: 50%;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.1));
}

.hero-title {
  color: #ffffff;
  font-size: 3.5em;
  margin: 0;
  font-weight: 300;
}

.hero-subtitle {
  color: #888;
  font-size: 1.1em;
  margin-top: 10px;
  font-weight: 300;
}

.content-section {
  margin-bottom: 60px;
  background: rgba(42, 41, 42, 0.5);
  padding: 30px;
  border-radius: 12px;
  border: 1px solid #333;
}

h2 {
  color: #ffffff;
  font-size: 1.5em;
  margin-bottom: 25px;
  font-weight: 400;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #444;
  padding-bottom: 10px;
}

ul, ol {
  line-height: 1.8;
  padding-left: 20px;
}

li {
  margin-bottom: 12px;
}

code {
  background: #181718;
  padding: 3px 8px;
  border-radius: 4px;
  color: #aaddff;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.invite {
  text-align: center;
}

.invite p {
  margin-bottom: 25px;
}

.invite-button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: #5865F2;
  color: white;
  padding: 12px 30px;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 500;
  transition: background 0.2s;
}

.invite-button:hover {
  background: #4752C4;
}
</style>
