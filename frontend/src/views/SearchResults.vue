<template>
  <div class="page-container">
    <div class="search-header">
      <h2 class="search-title">
        搜索：<span class="keyword">"{{ keyword }}"</span>
      </h2>
      <div class="search-subtitle">共检索到 {{ totalCount }} 张相关图纸</div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在搜索...</p>
    </div>

    <div v-else-if="items.length === 0" class="empty-state">
      <div class="empty-icon">🔍</div>
      <h3>暂时没有找到相关图纸</h3>
      <p>换个关键词试试吧~</p>
    </div>

    <div v-else class="results-grid">
      <div v-for="item in items" :key="item.id" class="r-card" @click="$router.push(`/pattern/${item.id}`)">
        <div class="r-img">
          <img v-if="item.thumbnail_url" :src="item.thumbnail_url" :alt="item.title" />
          <span v-else class="r-placeholder">{{ item.title.slice(0, 2) }}</span>
        </div>
        <div class="r-title">{{ item.title }}</div>
        <div class="r-meta">
          <span>{{ item.width }}x{{ item.height }}</span>
          <span>被收藏 {{ item.likes }}</span>
        </div>
      </div>
    </div>

    <div class="pagination" v-if="totalPages > 1">
      <button :disabled="page <= 1" @click="changePage(page - 1)">上一页</button>
      <span class="page-info">{{ page }} / {{ totalPages }}</span>
      <button :disabled="page >= totalPages" @click="changePage(page + 1)">下一页</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchPatterns, type PatternItem } from '@/api/patterns'

const route = useRoute()
const router = useRouter()

const keyword = ref((route.query.keyword as string) || '')
const items = ref<PatternItem[]>([])
const loading = ref(false)
const totalCount = ref(0)
const page = ref(1)
const pageSize = 12
const totalPages = ref(0)

onMounted(() => {
  if (keyword.value) {
    loadResults()
  }
})

watch(
  () => route.query.keyword,
  (newKw) => {
    keyword.value = (newKw as string) || ''
    page.value = 1
    if (keyword.value) {
      loadResults()
    }
  }
)

async function loadResults() {
  if (!keyword.value.trim()) return
  loading.value = true
  try {
    const res = await fetchPatterns({
      keyword: keyword.value.trim(),
      page: page.value,
      page_size: pageSize,
    })
    items.value = res.items
    totalCount.value = res.total
    totalPages.value = Math.ceil(res.total / pageSize)
  } catch {
    items.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

function changePage(p: number) {
  page.value = p
  loadResults()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
.page-container {
  max-width: 1100px;
  margin: 0 auto;
  padding-left: 20px;
  padding-right: 20px;
}

.search-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 30px 0;
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
  border: 1px solid var(--border-color);
}

.search-title {
  font-size: 24px;
  font-weight: 900;
  margin-bottom: 8px;
  color: var(--text-main);
}

.keyword {
  color: var(--primary);
}

.search-subtitle {
  color: var(--text-light);
  font-size: 14px;
  font-weight: bold;
}

.loading-state {
  text-align: center;
  padding: 80px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: var(--text-light);
  font-weight: bold;
}

.empty-state {
  text-align: center;
  padding: 80px 0;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 900;
  color: var(--text-main);
  margin-bottom: 10px;
}

.empty-state p {
  color: var(--text-light);
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 25px;
}

.r-card {
  background: white;
  border-radius: var(--radius-md);
  padding: 15px;
  cursor: pointer;
  box-shadow: var(--shadow-soft);
  transition: 0.3s;
  position: relative;
  overflow: hidden;
}

.r-card::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(166,221,249,0.15) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.35s;
  pointer-events: none;
}

.r-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 35px var(--primary-light), 0 0 0 4px var(--primary-light-light);
}

.r-card:hover::after {
  opacity: 1;
}

.r-img {
  width: 100%;
  aspect-ratio: 1 / 1;
  height: auto;
  border-radius: 14px;
  border: 3px solid var(--primary-light-light);
  overflow: hidden;
  margin-bottom: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.r-img img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 14px;
  box-sizing: border-box;
}

.r-placeholder {
  font-size: 40px;
  color: var(--text-light);
}

.r-title {
  font-weight: 900;
  font-size: 15px;
  margin-bottom: 5px;
}

.r-meta {
  font-size: 12px;
  color: var(--text-light);
  display: flex;
  justify-content: space-between;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 40px;
  padding-bottom: 40px;
}

.pagination button {
  padding: 8px 20px;
  border-radius: 20px;
  border: none;
  font-weight: bold;
  cursor: pointer;
  background: var(--bg-color);
  color: var(--text-main);
  transition: 0.2s;
}

.pagination button:hover:not(:disabled) {
  background: var(--primary);
  color: white;
}

.pagination button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-info {
  font-weight: bold;
  color: var(--text-light);
}

@media (max-width: 768px) {
  .page-container { padding-left: 12px; padding-right: 12px; }
  .search-header { padding: 20px 16px; margin-bottom: 20px; }
  .search-title { font-size: 18px; }
  .results-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 14px; }
  .r-card { padding: 10px; }
  .r-title { font-size: 13px; }
  .r-img img { padding: 8px; }
}

@media (max-width: 480px) {
  .results-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
  .r-card { padding: 8px; }
  .search-title { font-size: 16px; }
  .search-subtitle { font-size: 12px; }
  .pagination { gap: 10px; margin-top: 30px; }
  .pagination button { padding: 7px 14px; font-size: 13px; }
  .r-title { overflow-wrap: anywhere; }
  .r-meta { font-size: 11px; flex-direction: column; gap: 2px; }
}
</style>
