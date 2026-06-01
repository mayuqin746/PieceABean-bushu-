<template>
  <div class="detail-container">
    <!-- 返回 -->
    <div class="back-row">
      <span class="back-btn" @click="$router.back()">← 返回</span>
    </div>

    <div class="detail-content" v-if="pattern">
      <!-- 左侧轮播 -->
      <div class="carousel">
        <div class="carousel-main">
          <div class="carousel-track" :style="{ transform: `translateX(-${currentIdx * 100}%)` }">
            <div
              v-for="(s, i) in slides"
              :key="s.key"
              class="carousel-slide"
            >
              <img :src="s.url" :alt="pattern.title" @dblclick="openViewer(s.url)" />
            </div>
          </div>
          <button v-if="currentIdx > 0" class="carousel-arrow left" @click="prevSlide">‹</button>
          <button v-if="currentIdx < slides.length - 1" class="carousel-arrow right" @click="nextSlide">›</button>
        </div>
        <div class="carousel-dots">
          <span
            v-for="(s, i) in slides"
            :key="s.key"
            class="dot"
            :class="{ active: currentIdx === i }"
            @click="currentIdx = i"
          >{{ s.label }}</span>
        </div>
      </div>

      <!-- 右侧信息 -->
      <div class="info">
        <h1 class="info-title">{{ pattern.title }}</h1>
        <div class="info-tags">
          <span class="tag-cat">{{ pattern.category }}</span>
          <span v-if="pattern.series" class="tag-series">{{ pattern.series }}</span>
          <span v-if="pattern.colors?.length" class="tag-colors">
            <span v-for="c in pattern.colors" :key="c" class="color-badge">{{ c }}</span>
          </span>
        </div>

        <div class="info-stats">
          <div class="stat">
            <span class="stat-value">{{ pattern.views }}</span>
            <span class="stat-label">浏览</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ pattern.likes }}</span>
            <span class="stat-label">收藏</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ pattern.beads_count }}</span>
            <span class="stat-label">豆数</span>
          </div>
        </div>

        <button
          class="fav-btn"
          :class="{ active: pattern.is_favorited }"
          :disabled="favoriting"
          @click="onToggleFavorite"
        >
          {{ pattern.is_favorited ? '❤️ 已收藏' : '🤍 收藏图纸' }}
        </button>

        <button class="download-btn" @click="downloadBlueprint" :disabled="downloading">
          {{ downloading ? '下载中...' : '下载像素图纸' }}
        </button>
      </div>
    </div>

    <!-- 加载 / 错误 -->
    <div v-else-if="error" class="state-msg error">{{ error }}</div>
    <div v-else class="state-msg">加载中...</div>

    <!-- 图片放大查看器 -->
    <Teleport to="body">
      <div v-if="viewerSrc" class="viewer-overlay" @click.self="closeViewer" @wheel.prevent="onViewerWheel">
        <button class="viewer-close" @click="closeViewer">✕</button>
        <div class="viewer-toolbar">
          <button @click="viewerZoom = Math.min(viewerZoom * 1.3, 5)">＋</button>
          <span class="viewer-zoom-label">{{ Math.round(viewerZoom * 100) }}%</span>
          <button @click="viewerZoom = Math.max(viewerZoom / 1.3, 0.3)">－</button>
          <button @click="resetViewer">↺</button>
        </div>
        <img
          ref="viewerImgRef"
          class="viewer-img"
          :src="viewerSrc"
          :style="{
            transform: `translate(${viewerX}px, ${viewerY}px) scale(${viewerZoom})`,
            cursor: viewerZoom > 1 ? 'grab' : 'default',
          }"
          @mousedown.prevent="onViewerDragStart"
          @mousemove="onViewerDragMove"
          @mouseup="onViewerDragEnd"
          @mouseleave="onViewerDragEnd"
        />
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, inject } from 'vue'
import { useRoute } from 'vue-router'
import { fetchPatternDetail, toggleFavorite, type PatternItem } from '@/api/patterns'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const id = Number(route.params.id)
const auth = useAuthStore()
const openLogin = inject<() => void>('openLogin', () => {})

const pattern = ref<PatternItem | null>(null)
const error = ref('')
const downloading = ref(false)
const favoriting = ref(false)
const currentIdx = ref(0)

// 图片查看器
const viewerSrc = ref('')
const viewerZoom = ref(1)
const viewerX = ref(0)
const viewerY = ref(0)
const viewerImgRef = ref<HTMLImageElement | null>(null)
let dragging = false
let dragStartX = 0
let dragStartY = 0
let dragStartViewerX = 0
let dragStartViewerY = 0

function openViewer(url: string) {
  viewerSrc.value = url
  resetViewer()
}

function closeViewer() {
  viewerSrc.value = ''
}

function resetViewer() {
  viewerZoom.value = 1
  viewerX.value = 0
  viewerY.value = 0
  dragging = false
}

function onViewerWheel(e: WheelEvent) {
  const delta = e.deltaY > 0 ? 0.9 : 1.1
  viewerZoom.value = Math.min(Math.max(viewerZoom.value * delta, 0.3), 5)
}

function onViewerDragStart(e: MouseEvent) {
  if (viewerZoom.value <= 1) return
  dragging = true
  dragStartX = e.clientX
  dragStartY = e.clientY
  dragStartViewerX = viewerX.value
  dragStartViewerY = viewerY.value
}

function onViewerDragMove(e: MouseEvent) {
  if (!dragging) return
  viewerX.value = dragStartViewerX + (e.clientX - dragStartX)
  viewerY.value = dragStartViewerY + (e.clientY - dragStartY)
}

function onViewerDragEnd() {
  dragging = false
}

const slides = computed(() => {
  if (!pattern.value) return []
  const list: { key: string; url: string; label: string }[] = []
  if (pattern.value.thumbnail_url) {
    list.push({ key: 'thumb', url: pattern.value.thumbnail_url, label: '封面' })
  }
  if (pattern.value.blueprint_url) {
    list.push({ key: 'bp', url: pattern.value.blueprint_url, label: '高清图纸' })
  }
  return list
})

function prevSlide() {
  if (currentIdx.value > 0) currentIdx.value--
}

function nextSlide() {
  if (currentIdx.value < slides.value.length - 1) currentIdx.value++
}

async function onToggleFavorite() {
  if (!auth.isLoggedIn) {
    openLogin()
    return
  }
  if (!pattern.value) return
  favoriting.value = true
  try {
    const res = await toggleFavorite(pattern.value.id)
    pattern.value.is_favorited = res.favorited
    pattern.value.likes += res.favorited ? 1 : -1
  } finally {
    favoriting.value = false
  }
}

async function downloadBlueprint() {
  const fullUrl = pattern.value?.blueprint_url
  if (!fullUrl) {
    alert('暂无图纸可供下载')
    return
  }
  downloading.value = true
  try {
    const res = await fetch(fullUrl)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const blob = await res.blob()
    const objUrl = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = objUrl
    a.download = pattern.value?.title ? `${pattern.value.title}_图纸.png` : 'blueprint.png'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(objUrl)
  } catch (e: any) {
    alert('下载失败：' + (e?.message || '网络错误，请稍后重试'))
  } finally {
    downloading.value = false
  }
}

onMounted(async () => {
  try {
    pattern.value = await fetchPatternDetail(id)
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? '加载失败'
  }
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && viewerSrc.value) {
    closeViewer()
  }
}
</script>

<style scoped>
.detail-container { max-width: 1000px; margin: 0 auto; padding: 30px 20px; }

.back-row { margin-bottom: 20px; }
.back-btn {
  color: var(--primary); font-weight: bold; font-size: 15px; cursor: pointer;
  user-select: none;
}

.state-msg { text-align: center; padding: 80px 0; color: var(--text-light); font-size: 16px; }
.error { color: #e74c3c; }

.detail-content { display: flex; gap: 40px; }

/* 轮播 */
.carousel { flex: 1; min-width: 0; }
.carousel-main {
  position: relative; background: white; border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft); overflow: hidden;
  aspect-ratio: 1;
}
.carousel-track {
  display: flex; width: 100%; height: 100%;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
}
.carousel-slide {
  min-width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  padding: 16px; box-sizing: border-box;
}
.carousel-slide img {
  max-width: 100%; max-height: 100%;
  object-fit: contain; display: block;
}

.carousel-arrow {
  position: absolute; top: 50%; transform: translateY(-50%);
  width: 40px; height: 40px; border-radius: 50%; border: none;
  background: rgba(0,0,0,0.4); color: white; font-size: 26px; line-height: 1;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: background 0.2s; padding: 0;
}
.carousel-arrow:hover { background: rgba(0,0,0,0.65); }
.carousel-arrow.left { left: 12px; }
.carousel-arrow.right { right: 12px; }

.carousel-dots { display: flex; gap: 10px; margin-top: 12px; justify-content: center; }
.dot {
  padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: bold;
  cursor: pointer; background: var(--bg-color); color: var(--text-light);
  transition: 0.2s; user-select: none; border: 1px solid transparent;
}
.dot.active { background: var(--primary); color: white; }

/* 信息区 */
.info { width: 320px; flex-shrink: 0; }
.info-title { font-size: 26px; font-weight: 900; color: var(--text-main); margin: 0 0 12px; }

.info-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.tag-cat, .tag-series {
  padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: bold;
  background: var(--primary-light); color: var(--theme-text-dark);
}
.color-badge {
  padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;
  background: var(--bg-color); color: var(--text-main);
}

.info-stats { display: flex; gap: 20px; margin-bottom: 24px; }
.stat { text-align: center; }
.stat-value { display: block; font-size: 22px; font-weight: 900; color: var(--text-main); }
.stat-label { display: block; font-size: 12px; color: var(--text-light); margin-top: 2px; }

.download-btn {
  width: 100%; padding: 14px; border: none; border-radius: var(--radius-md);
  background: var(--primary); color: white; font-size: 17px; font-weight: bold;
  cursor: pointer; transition: opacity 0.2s;
}
.download-btn:hover { opacity: 0.85; }
.download-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.fav-btn {
  width: 100%; padding: 12px; margin-bottom: 12px;
  border: 2px solid var(--border-color); border-radius: var(--radius-md);
  background: white; color: var(--text-light); font-size: 15px; font-weight: bold;
  cursor: pointer; transition: 0.2s;
}
.fav-btn:hover { border-color: #e74c3c; color: #e74c3c; }
.fav-btn.active { border-color: #e74c3c; background: #fef0f0; color: #e74c3c; }
.fav-btn:disabled { opacity: 0.5; cursor: not-allowed; }

@media (max-width: 768px) {
  .detail-container { padding: 20px 12px; }
  .detail-content { flex-direction: column; gap: 24px; }
  .info { width: 100%; }
  .info-title { font-size: 22px; }
  .carousel-dots { flex-wrap: wrap; }
  .dot { padding: 5px 12px; font-size: 12px; }
  .carousel-arrow { width: 32px; height: 32px; font-size: 20px; }
  .viewer-toolbar { padding: 6px 12px; gap: 4px; }
  .viewer-toolbar button { width: 32px; height: 32px; font-size: 16px; }
  .viewer-close { top: 10px; right: 10px; width: 36px; height: 36px; }
}

@media (max-width: 480px) {
  .info-title { font-size: 18px; }
  .info-stats { gap: 12px; }
  .stat-value { font-size: 18px; }
  .download-btn { font-size: 15px; padding: 12px; }
  .fav-btn { font-size: 14px; padding: 10px; }
}

/* 图片查看器 */
.viewer-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
}

.viewer-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: white;
  font-size: 22px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  z-index: 2;
}
.viewer-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

.viewer-toolbar {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 8px 16px;
  border-radius: 24px;
  z-index: 2;
}

.viewer-toolbar button {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  line-height: 1;
  padding: 0;
}
.viewer-toolbar button:hover {
  background: rgba(255, 255, 255, 0.4);
}

.viewer-zoom-label {
  color: white;
  font-weight: bold;
  font-size: 13px;
  min-width: 48px;
  text-align: center;
}

.viewer-img {
  max-width: 90vw;
  max-height: 85vh;
  object-fit: contain;
  transition: transform 0.15s ease-out;
  user-select: none;
  -webkit-user-drag: none;
}
</style>
