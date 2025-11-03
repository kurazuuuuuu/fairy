<template>
  <div class="research-view">
    <div v-if="loading" class="loading">読み込み中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="research" class="research-content">
      <h1>{{ research.keyword }}</h1>
      <div class="meta">
        <p>処理時間: {{ research.time }}秒</p>
        <p>作成日時: {{ new Date(research.created_at).toLocaleString('ja-JP') }}</p>
      </div>
      <div class="message" v-html="formatMarkdown(research.full_message)"></div>
      <div v-if="research.urls && Array.isArray(research.urls) && research.urls.length > 0" class="urls">
        <h2>参考URL</h2>
        <div class="url-grid">
          <a v-for="urlData in research.urls" :key="urlData.url || urlData" :href="urlData.url || urlData" target="_blank" class="url-card">
            <div class="url-thumbnail">
              <img :src="getFaviconUrl(urlData.url || urlData)" :alt="urlData.title || urlData.url || urlData" />
            </div>
            <div class="url-info">
              <div class="url-title">{{ urlData.title || getHostname(urlData.url || urlData) }}</div>
              <div class="url-link">{{ urlData.url || urlData }}</div>
            </div>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'

const route = useRoute()
const research = ref<any>(null)
const loading = ref(true)
const error = ref('')

const formatMarkdown = (text: string) => {
  return marked(text)
}

const getHostname = (url: string) => {
  try {
    const hostname = new URL(url).hostname
    // www. を削除して見やすくする
    return hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

const getFaviconUrl = (url: string) => {
  try {
    const hostname = new URL(url).hostname
    return `https://www.google.com/s2/favicons?domain=${hostname}&sz=64`
  } catch {
    return ''
  }
}

onMounted(async () => {
  try {
    const uuid = route.params.uuid
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const response = await fetch(`${apiUrl}/api/research/${uuid}`)
    if (!response.ok) {
      throw new Error('リサーチ結果が見つかりませんでした')
    }
    research.value = await response.json()
    console.log('Research data:', research.value)
    console.log('URLs:', research.value.urls)
    console.log('URLs length:', research.value.urls?.length)
  } catch (e: any) {
    console.error('Error fetching research:', e)
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.research-view {
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

.loading, .error {
  text-align: center;
  padding: 60px;
  font-size: 18px;
  max-width: 600px;
  margin: 100px auto;
}

.loading {
  color: #cccccc;
}

.error {
  color: #ff6b6b;
}

.research-content {
  max-width: 900px;
  margin: 0 auto;
}

.research-content h1 {
  color: #ffffff;
  font-size: 2em;
  margin-bottom: 20px;
  font-weight: 600;
  letter-spacing: -0.5px;
  border-bottom: 1px solid #181718;
  padding-bottom: 15px;
}

.meta {
  color: #cccccc;
  margin-bottom: 30px;
  padding: 15px;
  background: #2a292a;
  border-radius: 6px;
  font-size: 0.9em;
}

.meta p {
  margin: 5px 0;
}

.message {
  line-height: 1.8;
  margin-bottom: 40px;
  color: #e0e0e0;
}

.message :deep(h1),
.message :deep(h2),
.message :deep(h3) {
  color: #ffffff;
  margin-top: 24px;
  margin-bottom: 12px;
  font-weight: 600;
  letter-spacing: -0.3px;
}

.message :deep(code) {
  background: #181718;
  padding: 2px 6px;
  border-radius: 4px;
  color: #e0e0e0;
  font-family: 'Courier New', monospace;
}

.message :deep(a) {
  color: #ffffff;
  text-decoration: underline;
  text-decoration-color: #666666;
}

.message :deep(a:hover) {
  text-decoration-color: #ffffff;
}

.urls {
  padding: 20px 0;
}

.urls h2 {
  color: #ffffff;
  margin-bottom: 20px;
  font-size: 1.5em;
  font-weight: 600;
  letter-spacing: -0.3px;
}

.url-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
}

.url-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #2a292a;
  border: 1px solid #181718;
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.url-card:hover {
  background: #323132;
  border-color: #3a393a;
}

.url-thumbnail {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  margin-right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #181718;
  border-radius: 6px;
}

.url-thumbnail img {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.url-info {
  flex: 1;
  min-width: 0;
}

.url-title {
  color: #ffffff;
  font-weight: 500;
  font-size: 0.95em;
  margin-bottom: 4px;
}

.url-link {
  color: #cccccc;
  font-size: 0.85em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
