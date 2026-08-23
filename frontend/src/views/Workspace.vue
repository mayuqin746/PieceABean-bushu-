<template>
  <div class="workspace" :class="{ 'has-grid-data': hasGridData }">
    <button class="ws-toggle ws-toggle-left" :class="{ active: leftPanelOpen }" @click="leftPanelOpen = !leftPanelOpen">
      {{ leftPanelOpen ? '✕' : '☰' }} 参数
    </button>

    <button class="ws-toggle ws-toggle-right" :class="{ active: rightPanelOpen }" @click="rightPanelOpen = !rightPanelOpen">
      清单 {{ rightPanelOpen ? '✕' : '☰' }}
    </button>

    <!-- ====== 左侧参数面板 ====== -->
    <div
      v-if="leftPanelOpen || rightPanelOpen"
      class="panel-scrim"
      @click="leftPanelOpen = false; rightPanelOpen = false"
    ></div>

    <aside class="ws-sidebar" :class="{ 'panel-open': leftPanelOpen }">
      <div class="ws-header">参数设置</div>
      <div class="ws-body">
        <!-- 上传区域 -->
        <div class="upload-area" @click="triggerUpload">
          <input
            ref="fileInput"
            type="file"
            accept="image/jpeg,image/png,image/webp,image/bmp"
            hidden
            @change="onFileChange"
          />
          <img v-if="thumbnailUrl" :src="thumbnailUrl" class="upload-thumb" alt="预览" />
          <span v-if="thumbnailUrl && cropApplied" class="crop-applied-badge">已裁剪</span>
          <div v-else-if="!thumbnailUrl" class="upload-placeholder">
            <span class="upload-icon">+</span>
            <span>点击上传图片</span>
          </div>
        </div>

        <!-- 网格尺寸 -->
        <button
          v-if="thumbnailUrl"
          type="button"
          class="btn-crop"
          @click.stop="openCropEditor"
        >
          {{ cropApplied ? '重新调整裁剪区域' : '调整裁剪区域' }}
        </button>

        <div class="control-group">
          <div class="control-label-row">
            <span class="control-label">网格尺寸</span>
            <span class="bead-type-badge" title="Artkal Mini S系列">Mini 2.66mm</span>
          </div>
          <input
            type="range"
            class="range-slider"
            min="15"
            max="120"
            v-model.number="slidingSize"
          />
          <div class="size-input-row">
            <label>最长边</label>
            <input
              v-model.number="slidingSize"
              class="size-number-input"
              type="number"
              min="15"
              max="200"
              step="1"
            />
          </div>
          <div class="size-info-row">
            <span>{{ gridWidth || slidingSize }} × {{ gridHeight || slidingSize }} 格</span>
            <span class="physical-size">{{ physicalSize }}</span>
          </div>

        </div>

        <!-- 颜色数量 -->
        <div class="control-group">
          <div class="control-label-row">
            <span class="control-label">{{ hasBrandSelected ? '目标色号数' : '颜色数量' }}</span>
            <button type="button" class="text-mini-button" @click="slidingColors = 0">不限制</button>
          </div>
          <div class="preset-row">
            <button
              v-for="preset in colorPresetOptions"
              :key="preset.value"
              type="button"
              class="preset-button"
              :class="{ active: slidingColors === preset.value }"
              @click="slidingColors = preset.value"
            >
              {{ preset.label }}
            </button>
          </div>
          <input
            type="range"
            class="range-slider"
            min="6"
            max="64"
            step="1"
            :disabled="slidingColors === 0"
            :value="normalizedColorCount"
            @input="onColorSliderInput"
          />
          <div class="size-input-row">
            <label>{{ colorLimitLabel }}</label>
            <input
              v-model.number="slidingColors"
              class="size-number-input"
              type="number"
              min="0"
              max="64"
              step="1"
            />
          </div>
          <label class="option-check">
            <input v-model="strictColorLimit" type="checkbox" />
            <span>严格限制颜色总数（包含轮廓色）</span>
          </label>
        </div>

        <!-- 拼豆结构优化 -->
        <div class="control-group">
          <span class="control-label">背景处理</span>
          <select v-model="backgroundMode" class="tool-select">
            <option value="auto-light">自动留空连通的浅色背景</option>
            <option value="keep">保留原图背景</option>
          </select>
          <p class="control-hint">透明 PNG 会始终保留空格；自动模式仅清理与画布边缘相连的近白色背景。</p>
        </div>

        <div class="control-group">
          <span class="control-label">固定轮廓</span>
          <select v-model="outlineMode" class="tool-select">
            <option value="black">黑色一格轮廓</option>
            <option value="white">白色一格轮廓</option>
            <option value="clear">透明/留空边缘</option>
            <option value="none">不添加轮廓</option>
          </select>
          <p class="control-hint">轮廓根据透明区域或自动清理后的背景生成，并独立于普通颜色归并。</p>
        </div>

        <div class="control-group">
          <span class="control-label">杂色清理</span>
          <select v-model.number="cleanupMaxRegionSize" class="tool-select">
            <option :value="0">关闭（保留所有细节）</option>
            <option :value="1">清理单格杂色</option>
            <option :value="2">清理单格和双格杂色</option>
          </select>
          <p class="control-hint">只合并空间上孤立的小色块，不会填充透明空格或改写固定轮廓。</p>
        </div>

        <!-- 品牌下拉 -->
        <div class="control-group">
          <span class="control-label">品牌色板</span>
          <select :value="mapping.selectedBrand.value" @change="onBrandChange" class="tool-select">
            <option value="">不使用品牌色板</option>
            <option
              v-for="opt in brandOptions"
              :key="opt.value"
              :value="opt.value"
              :disabled="opt.disabled"
              :title="opt.title"
            >
              {{ opt.label }}
            </option>
          </select>
        </div>

        <!-- 生成按钮 -->
        <button
          class="btn-generate"
          :disabled="generating || !selectedFile"
          @click="doGenerate"
        >
          <span v-if="generating" class="btn-loading">
            <span class="spinner"></span>
            生成中...
          </span>
          <span v-else>生成拼豆图纸</span>
        </button>

        <button
          class="btn-export-plan"
          :disabled="!hasGridData"
          @click="onExport"
        >
          导出图纸清单
        </button>

        <button
          v-if="hasGridData"
          class="btn-save-work"
          :class="{ 'btn-login-hint': !auth.isLoggedIn }"
          @click.stop="handleLoginOrSave"
        >
          {{ auth.isLoggedIn ? '💾 保存到我的作品' : '登录后可保存到我的作品' }}
        </button>
      </div>
    </aside>

    <!-- ====== 中央画布 ====== -->
    <section class="ws-center">
      <!-- 生成前引导 -->
      <div v-if="!hasGridData" class="guide-placeholder" @click="triggerUpload">
        <span class="guide-icon">🖼️</span>
        <h2>上传图片开始创作</h2>
        <p>支持 JPG / PNG / WebP / BMP 格式</p>
        <button class="guide-action" type="button">点击上传</button>
      </div>

      <!-- 画布 -->
      <div v-else class="canvas-container">
        <div class="canvas-wrapper" :style="canvasWrapperStyle">
          <div
            class="canvas-grid"
            :style="{
              gridTemplateColumns: `repeat(${gridWidth}, 1fr)`,
              gridTemplateRows: `repeat(${gridHeight}, 1fr)`,
            }"
          >
            <div
              v-for="(cell, idx) in flatCells"
              :key="idx"
              class="cell"
              :class="{ 'cell-empty': !cell.hex }"
              :style="{ backgroundColor: cell.hex || 'transparent' }"
            >
              <span
                v-if="cell.color_no"
                class="cell-label"
                :style="{
                  color: cell.text_color,
                  fontSize: cellFontSize + 'px',
                  textShadow: cell.text_color === 'white'
                    ? '0 1px 2px rgba(0,0,0,0.6)'
                    : '0 1px 2px rgba(255,255,255,0.6)',
                }"
              >
                {{ cell.color_no }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 缩放控件 -->
      <div v-if="hasGridData" class="zoom-controls">
        <span class="zoom-btn" @click="changeZoom(-0.1)">➖</span>
        <span class="zoom-text">{{ Math.round(zoom * 100) }}%</span>
        <span class="zoom-btn" @click="changeZoom(0.1)">➕</span>
      </div>
    </section>

    <!-- ====== 右侧清单 ====== -->
    <aside class="ws-sidebar ws-sidebar-right" :class="{ 'panel-open': rightPanelOpen }">
      <div class="ws-header">拼豆清单</div>
      <div class="ws-body ws-body-flex">
        <!-- 未生成 -->
        <div v-if="!hasGridData" class="ws-tip">
          上传图片并生成图纸后，<br />此处将显示拼豆用量统计。
        </div>

        <!-- 颜色列表 -->
        <template v-else>
          <div class="brand-indicator">
            {{ hasBrandSelected ? '当前色板：' : '颜色清单：' }}<strong>{{ brandLabel }}</strong>
            <span class="brand-count">（{{ mapping.brandStats.value.length }} 种颜色）</span>
          </div>

          <div class="color-list">
            <div
              v-for="stat in mapping.brandStats.value"
              :key="stat.color_no"
              class="color-list-item"
            >
              <div class="c-left">
                <div class="c-dot" :style="{ background: stat.hex }"></div>
                <span>{{ stat.color_no }}</span>
              </div>
              <span>{{ stat.count }} 颗</span>
            </div>
          </div>

          <div class="ws-footer">
            <div class="total-row">
              <span>总豆数：</span>
              <span class="total-count">{{ mapping.totalBeads.value }} 颗</span>
            </div>
          </div>
        </template>
      </div>
    </aside>

    <Teleport to="body">
      <div v-if="showSaveForm" class="save-overlay" @click.self="showSaveForm = false">
        <div class="save-modal">
          <h3>保存到我的作品</h3>
          <input v-model="saveTitle" type="text" placeholder="给你的作品起个名字" class="save-input" autofocus />
          <select v-model="saveCategory" class="save-select">
            <option value="其他">其他</option>
            <option value="动漫/IP">动漫/IP</option>
            <option value="萌宠动物">萌宠动物</option>
            <option value="美食饮品">美食饮品</option>
            <option value="生活日常">生活日常</option>
            <option value="明星应援">明星应援</option>
          </select>
          <div class="save-actions">
            <button class="save-confirm" :disabled="!saveTitle.trim() || saving" @click="doSave">{{ saving ? '保存中...' : '确认保存' }}</button>
            <button class="save-cancel" @click="showSaveForm = false">取消</button>
          </div>
          <p v-if="saveMsg" :class="saveOk ? 'save-ok' : 'save-err'">{{ saveMsg }}</p>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="cropEditorOpen" class="crop-overlay" @click.self="cropEditorOpen = false">
        <div class="crop-modal">
          <div class="crop-head">
            <h3>裁剪主体区域</h3>
            <button type="button" class="crop-close" @click="cropEditorOpen = false">×</button>
          </div>
          <div v-if="cropImageUrl" class="crop-stage">
            <img :src="cropImageUrl" alt="裁剪预览" class="crop-image" />
            <div
              class="crop-box"
              :style="{
                left: crop.left + '%',
                top: crop.top + '%',
                width: (crop.right - crop.left) + '%',
                height: (crop.bottom - crop.top) + '%',
              }"
            ></div>
          </div>
          <div class="crop-controls">
            <label>左边界 <input v-model.number="crop.left" type="range" min="0" :max="crop.right - 20" /></label>
            <label>右边界 <input v-model.number="crop.right" type="range" :min="crop.left + 20" max="100" /></label>
            <label>上边界 <input v-model.number="crop.top" type="range" min="0" :max="crop.bottom - 20" /></label>
            <label>下边界 <input v-model.number="crop.bottom" type="range" :min="crop.top + 20" max="100" /></label>
          </div>
          <div class="crop-actions">
            <button type="button" class="save-cancel" @click="resetCrop">重置</button>
            <button type="button" class="save-confirm" @click="applyCrop">使用裁剪区域</button>
          </div>
          <p class="crop-note">调节四个边界，把主体留在亮色区域内；透明区域会保留为空格，不计入豆数。</p>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, inject } from 'vue'
import { fetchPalette, generatePattern } from '@/api/generator'
import type { GridColor } from '@/api/generator'
import { saveMyPattern } from '@/api/patterns'
import { useColorMapping } from '@/composables/useColorMapping'
import { useAuthStore } from '@/stores/auth'
import type { MappedCell } from '@/composables/useColorMapping'

// ========== 状态 ==========

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const originalImageUrl = ref<string | null>(null)
const thumbnailUrl = ref<string | null>(null)
const slidingSize = ref(29)
const gridWidth = ref(0)
const gridHeight = ref(0)
const slidingColors = ref(16)
const generating = ref(false)
const zoom = ref(1)
const sourceGridData = ref<GridColor[][]>([])
const backgroundMode = ref<'auto-light' | 'keep'>('auto-light')
const outlineMode = ref<'black' | 'white' | 'clear' | 'none'>('black')
const strictColorLimit = ref(true)
const cleanupMaxRegionSize = ref(1)

const mapping = useColorMapping()
const auth = useAuthStore()
const showExport = inject<(val: boolean) => void>('showExportModal', () => {})
const updateExportData = inject<(data: Record<string, unknown>) => void>('updateExportData', () => {})
const openLogin = inject<() => void>('openLogin', () => {})

const brandOptions = [
  { value: 'artkal', label: 'Artkal (224色)', disabled: false, title: '' },
  { value: 'perler', label: 'Perler — 色号数据整理中', disabled: true, title: '色号数据整理中，敬请期待' },
  { value: 'hama', label: 'Hama — 色号数据整理中', disabled: true, title: '色号数据整理中，敬请期待' },
]

const colorPresetOptions = [
  { value: 24, label: '细节' },
  { value: 16, label: '均衡' },
  { value: 12, label: '简化' },
  { value: 8, label: '清爽' },
]

const BEAD_SIZE_MM = 2.66

const physicalSize = computed(() => {
  const w = (gridWidth.value || slidingSize.value) * BEAD_SIZE_MM
  const h = (gridHeight.value || slidingSize.value) * BEAD_SIZE_MM
  if (Math.max(w, h) < 100) return `${w.toFixed(0)} × ${h.toFixed(0)} mm`
  return `${(w / 10).toFixed(1)} × ${(h / 10).toFixed(1)} cm`
})

const hasGridData = computed(() => mapping.gridData.value.length > 0)
const hasBrandSelected = computed(() => mapping.selectedBrand.value !== '')

const brandLabel = computed(() => {
  if (!mapping.selectedBrand.value) return '自定义颜色'
  const opt = brandOptions.find(o => o.value === mapping.selectedBrand.value)
  return opt ? opt.label.split(' —')[0].split(' (')[0] : mapping.selectedBrand.value
})

const effectiveColorLimit = computed(() =>
  slidingColors.value > 0 ? slidingColors.value : 0
)

const normalizedColorCount = computed(() => {
  if (slidingColors.value <= 0) return 16
  return Math.min(64, Math.max(6, slidingColors.value))
})

const colorLimitLabel = computed(() => {
  if (slidingColors.value <= 0) return hasBrandSelected.value ? '不限制色号' : '不限制颜色'
  return hasBrandSelected.value ? `目标 ${slidingColors.value} 个色号` : `${slidingColors.value} 种颜色`
})

const flatCells = computed<MappedCell[]>(() => {
  const all: MappedCell[] = []
  for (const row of mapping.mappedGrid.value) {
    for (const cell of row) {
      all.push(cell)
    }
  }
  return all
})

const cellFontSize = computed(() => {
  const n = Math.max(gridWidth.value, gridHeight.value)
  if (n === 0) return 10
  if (n <= 20) return 6
  if (n <= 35) return 4
  if (n <= 50) return 2
  return 2
})

const canvasWrapperStyle = computed(() => {
  const w = gridWidth.value || 1
  const h = gridHeight.value || 1
  const availableW = Math.max(180, viewportWidth.value <= 900 ? viewportWidth.value - 40 : viewportWidth.value - 760)
  const availableH = Math.max(220, viewportHeight.value - 190)
  const fitWidth = Math.min(550, availableW, availableH * (w / h))
  return {
    width: `${Math.max(160, fitWidth)}px`,
    aspectRatio: `${w} / ${h}`,
    transform: `scale(${zoom.value})`,
  }
})

function updateViewport() {
  viewportWidth.value = window.innerWidth
  viewportHeight.value = window.innerHeight
}

function isLightNeutralBackground(hex: string): boolean {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return Math.min(r, g, b) >= 235 && Math.max(r, g, b) - Math.min(r, g, b) <= 24
}

function clearConnectedLightBackground(grid: GridColor[][]): GridColor[][] {
  if (grid.length === 0) return []
  const height = grid.length
  const width = grid[0]?.length || 0
  const output = grid.map(row => [...row])
  const visited = Array.from({ length: height }, () => Array(width).fill(false))
  const queue: [number, number][] = []

  function enqueue(x: number, y: number) {
    if (x < 0 || x >= width || y < 0 || y >= height || visited[y][x]) return
    const hex = grid[y][x]
    if (!hex || !isLightNeutralBackground(hex)) return
    visited[y][x] = true
    queue.push([x, y])
  }

  for (let x = 0; x < width; x++) {
    enqueue(x, 0)
    enqueue(x, height - 1)
  }
  for (let y = 0; y < height; y++) {
    enqueue(0, y)
    enqueue(width - 1, y)
  }

  const neighbors = [[-1, 0], [1, 0], [0, -1], [0, 1]] as const
  for (let index = 0; index < queue.length; index++) {
    const [x, y] = queue[index]
    output[y][x] = null
    for (const [dx, dy] of neighbors) enqueue(x + dx, y + dy)
  }

  return output
}

function applyFixedOutline(
  grid: GridColor[][]
): { grid: GridColor[][]; lockedColors: string[] } {
  const output = grid.map(row => [...row])
  if (outlineMode.value === 'none' || grid.length === 0) {
    return { grid: output, lockedColors: [] }
  }

  const height = grid.length
  const width = grid[0]?.length || 0
  const hasEmptySpace = grid.some(row => row.some(cell => !cell))
  if (!hasEmptySpace) return { grid: output, lockedColors: [] }

  const outlineHex = outlineMode.value === 'black'
    ? '#000000'
    : outlineMode.value === 'white'
      ? '#FFFFFF'
      : null
  const neighbors = [[-1, 0], [1, 0], [0, -1], [0, 1]] as const

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (!grid[y][x]) continue
      const isBoundary = neighbors.some(([dx, dy]) => {
        const nx = x + dx
        const ny = y + dy
        return nx < 0 || nx >= width || ny < 0 || ny >= height || !grid[ny][nx]
      })
      if (isBoundary) output[y][x] = outlineHex
    }
  }

  return {
    grid: output,
    lockedColors: outlineHex ? [outlineHex] : [],
  }
}

function refreshPatternProcessing() {
  const backgroundGrid = backgroundMode.value === 'auto-light'
    ? clearConnectedLightBackground(sourceGridData.value)
    : sourceGridData.value.map(row => [...row])
  const outlined = applyFixedOutline(backgroundGrid)
  mapping.setProcessing(outlined.grid, {
    targetColorCount: effectiveColorLimit.value,
    strictColorLimit: strictColorLimit.value,
    cleanupMaxRegionSize: cleanupMaxRegionSize.value,
    lockedColors: outlined.lockedColors,
  })
}

const showSaveForm = ref(false)
const saveTitle = ref('')
const saveCategory = ref('其他')
const saving = ref(false)
const saveMsg = ref('')
const saveOk = ref(false)
const leftPanelOpen = ref(false)
const rightPanelOpen = ref(false)
const cropEditorOpen = ref(false)
const cropImageUrl = ref<string | null>(null)
const crop = ref({ left: 0, top: 0, right: 100, bottom: 100 })
const cropApplied = ref(false)
const viewportWidth = ref(window.innerWidth)
const viewportHeight = ref(window.innerHeight)

// ========== 初始化 ==========

onMounted(async () => {
  updateViewport()
  window.addEventListener('resize', updateViewport)
  try {
    const data = await fetchPalette()
    mapping.setPalette(data)
  } catch (e) {
    console.error('Failed to load palette:', e)
  }
})

// ========== 方法 ==========

watch(slidingSize, (val) => {
  if (!Number.isFinite(val)) {
    slidingSize.value = 29
  } else if (val < 15) {
    slidingSize.value = 15
  } else if (val > 200) {
    slidingSize.value = 200
  }
})

watch(slidingColors, (val) => {
  if (!Number.isFinite(val)) {
    slidingColors.value = 16
  } else if (val < 0) {
    slidingColors.value = 0
  } else if (val > 64) {
    slidingColors.value = 64
  } else {
    slidingColors.value = Math.floor(val)
  }
})

watch(
  [effectiveColorLimit, strictColorLimit, cleanupMaxRegionSize, outlineMode, backgroundMode],
  () => refreshPatternProcessing(),
  { immediate: true }
)

watch(
  [() => mapping.mappedGrid.value, () => mapping.brandStats.value, () => mapping.totalBeads.value, brandLabel],
  () => {
    if (!hasGridData.value) return
    updateExportData({
      gridData: mapping.processedGrid.value,
      mappedGrid: mapping.mappedGrid.value,
      brandStats: mapping.brandStats.value,
      totalBeads: mapping.totalBeads.value,
      brandLabel: brandLabel.value,
      gridWidth: gridWidth.value,
      gridHeight: gridHeight.value,
    })
  }
)

onUnmounted(() => {
  window.removeEventListener('resize', updateViewport)
})

function triggerUpload() {
  fileInput.value?.click()
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  selectedFile.value = file

  if (thumbnailUrl.value) {
    URL.revokeObjectURL(thumbnailUrl.value)
  }
  if (originalImageUrl.value && originalImageUrl.value !== thumbnailUrl.value) {
    URL.revokeObjectURL(originalImageUrl.value)
  }
  originalImageUrl.value = URL.createObjectURL(file)
  thumbnailUrl.value = originalImageUrl.value
  cropImageUrl.value = originalImageUrl.value
  sourceGridData.value = []
  gridWidth.value = 0
  gridHeight.value = 0
  refreshPatternProcessing()
  resetCrop()
  cropApplied.value = false
  cropEditorOpen.value = true
}

function openCropEditor() {
  if (!originalImageUrl.value) return
  cropImageUrl.value = originalImageUrl.value
  cropEditorOpen.value = true
}

function resetCrop() {
  crop.value = { left: 0, top: 0, right: 100, bottom: 100 }
}

async function applyCrop() {
  if (!originalImageUrl.value || !selectedFile.value) {
    cropEditorOpen.value = false
    return
  }

  if (isFullCrop()) {
    if (thumbnailUrl.value && thumbnailUrl.value !== originalImageUrl.value) {
      URL.revokeObjectURL(thumbnailUrl.value)
    }
    thumbnailUrl.value = originalImageUrl.value
    cropApplied.value = false
    cropEditorOpen.value = false
    return
  }

  const blob = await renderCropBlob()
  if (blob) {
    if (thumbnailUrl.value && thumbnailUrl.value !== originalImageUrl.value) {
      URL.revokeObjectURL(thumbnailUrl.value)
    }
    thumbnailUrl.value = URL.createObjectURL(blob)
    cropApplied.value = true
  }
  cropEditorOpen.value = false
}

function isFullCrop() {
  return crop.value.left === 0 && crop.value.top === 0 && crop.value.right === 100 && crop.value.bottom === 100
}

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error('Cannot load crop image'))
    img.src = src
  })
}

async function renderCropBlob(): Promise<Blob | null> {
  if (!originalImageUrl.value || isFullCrop()) {
    return null
  }

  const img = await loadImage(originalImageUrl.value)
  const padRatio = 0.015
  const left = Math.max(0, crop.value.left - padRatio * 100)
  const top = Math.max(0, crop.value.top - padRatio * 100)
  const right = Math.min(100, crop.value.right + padRatio * 100)
  const bottom = Math.min(100, crop.value.bottom + padRatio * 100)
  const sx = Math.round((left / 100) * img.naturalWidth)
  const sy = Math.round((top / 100) * img.naturalHeight)
  const sw = Math.max(1, Math.round(((right - left) / 100) * img.naturalWidth))
  const sh = Math.max(1, Math.round(((bottom - top) / 100) * img.naturalHeight))
  const canvas = document.createElement('canvas')
  canvas.width = sw
  canvas.height = sh
  const ctx = canvas.getContext('2d')
  if (!ctx) return null
  ctx.clearRect(0, 0, sw, sh)
  ctx.drawImage(img, sx, sy, sw, sh, 0, 0, sw, sh)

  return new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/png'))
}

async function createUploadFile(): Promise<File> {
  if (!selectedFile.value || !originalImageUrl.value || isFullCrop()) {
    return selectedFile.value!
  }

  const blob = await renderCropBlob()
  if (!blob) return selectedFile.value
  const name = selectedFile.value.name.replace(/\.[^.]+$/, '') + '_crop.png'
  return new File([blob], name, { type: 'image/png' })
}

function onColorSliderInput(e: Event) {
  slidingColors.value = Number((e.target as HTMLInputElement).value)
}

async function doGenerate() {
  if (!selectedFile.value) return
  generating.value = true
  showSaveForm.value = false
  saveMsg.value = ''
  try {
    const uploadFile = await createUploadFile()
    const res = await generatePattern({
      file: uploadFile,
      grid_size: slidingSize.value,
      color_count: 0,
      algorithm: 'kmeans',
    })
    sourceGridData.value = res.grid_data
    gridWidth.value = res.width
    gridHeight.value = res.height
    refreshPatternProcessing()
  } catch (e: any) {
    alert(e?.response?.data?.detail || e?.message || '生成失败，请重试')
  } finally {
    generating.value = false
  }
}

function changeZoom(delta: number) {
  zoom.value = Math.min(2.5, Math.max(0.3, zoom.value + delta))
}

function onExport() {
  showExport(true)
}

function openSaveForm() {
  showSaveForm.value = true
}

function handleLoginOrSave() {
  if (auth.isLoggedIn) {
    openSaveForm()
  } else {
    openLogin()
  }
}

async function doSave() {
  if (!saveTitle.value.trim()) return
  saving.value = true
  saveMsg.value = ''
  try {
    const colors = mapping.brandStats.value.map(s => s.hex)
    await saveMyPattern({
      title: saveTitle.value.trim(),
      category: saveCategory.value,
      colors,
      grid_data: mapping.processedGrid.value,
      width: gridWidth.value,
      height: gridHeight.value,
      beads_count: mapping.totalBeads.value,
    })
    saveOk.value = true
    saveMsg.value = '已保存到我的作品！'
    setTimeout(() => {
      showSaveForm.value = false
      saveMsg.value = ''
      saveTitle.value = ''
      saveOk.value = false
    }, 2000)
  } catch (e: any) {
    saveOk.value = false
    saveMsg.value = e?.response?.data?.detail ?? '保存失败'
  } finally {
    saving.value = false
  }
}

function onBrandChange(e: Event) {
  const val = (e.target as HTMLSelectElement).value
  mapping.selectedBrand.value = val
}
</script>

<style scoped>
/* ========== 布局 ========== */
.workspace {
  display: flex;
  height: calc(100vh - var(--header-height));
}

/* ========== 左侧面板 ========== */
.ws-sidebar {
  width: 320px;
  background: white;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 15px rgba(0, 0, 0, 0.02);
  z-index: 10;
  flex-shrink: 0;
}
.ws-sidebar-right {
  box-shadow: -2px 0 15px rgba(0, 0, 0, 0.02);
  border-left: 1px solid var(--border-color);
}

.ws-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  font-weight: 900;
  font-size: 16px;
}

.ws-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}
.ws-body-flex {
  display: flex;
  flex-direction: column;
}

/* ========== 上传区域 ========== */
.upload-area {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;
  border: 2px dashed var(--primary);
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #f8fafc;
  margin-bottom: 20px;
  transition: border-color 0.2s;
}
.upload-area:hover {
  border-color: var(--text-main);
}

.btn-crop {
  width: 100%;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: #f8fafc;
  color: var(--text-main);
  font-size: 13px;
  font-weight: 900;
  cursor: pointer;
  margin: -8px 0 18px;
}
.btn-crop:hover {
  border-color: var(--primary);
  background: var(--primary-light);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--text-light);
  font-weight: bold;
}
.upload-icon {
  font-size: 32px;
  line-height: 1;
  color: var(--primary);
}

.upload-thumb {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.crop-applied-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 8px;
  border-radius: 999px;
  background: var(--primary);
  color: #1e293b;
  font-size: 12px;
  font-weight: 900;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.12);
}

/* ========== 控件 ========== */
.control-group {
  margin-bottom: 25px;
}
.control-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.control-label {
  font-size: 13px;
  font-weight: bold;
  color: var(--text-light);
}
.control-hint {
  margin: 6px 0 0;
  color: var(--text-light);
  font-size: 11px;
  line-height: 1.4;
}
.option-check {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  color: var(--text-light);
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
}
.option-check input {
  width: 16px;
  height: 16px;
  accent-color: var(--primary);
}
.bead-type-badge {
  font-size: 11px;
  font-weight: 700;
  color: #1e293b;
  background: var(--primary);
  padding: 2px 8px;
  border-radius: 6px;
  cursor: default;
}
.size-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
  font-size: 13px;
  font-weight: bold;
}
.size-input-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 8px;
  font-size: 12px;
  font-weight: 800;
  color: var(--text-light);
}
.size-number-input {
  width: 90px;
  padding: 7px 9px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: white;
  color: var(--text-main);
  font-weight: 900;
  text-align: right;
  outline: none;
}
.size-number-input:focus {
  border-color: var(--primary);
}
.physical-size {
  color: var(--primary);
  filter: brightness(0.85);
}

.tool-select {
  width: 100%;
  padding: 10px 15px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  font-weight: bold;
  outline: none;
  background: #f8fafc;
  color: var(--text-main);
  font-size: 13px;
  cursor: pointer;
}
.tool-select option:disabled {
  color: #c0c0c0;
}

.text-mini-button {
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: #f8fafc;
  color: var(--text-light);
  font-size: 12px;
  font-weight: 900;
  padding: 4px 10px;
  cursor: pointer;
}
.control-label + .tool-select {
  margin-top: 8px;
}
.text-mini-button:hover {
  border-color: var(--primary);
  color: var(--text-main);
}

.preset-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 6px;
  margin-top: 8px;
}
.preset-button {
  min-width: 0;
  padding: 8px 4px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: #f8fafc;
  color: var(--text-main);
  font-size: 12px;
  font-weight: 900;
  cursor: pointer;
}
.preset-button.active {
  border-color: var(--primary);
  background: var(--primary-light);
}

.range-slider {
  width: 100%;
  -webkit-appearance: none;
  height: 6px;
  background: var(--border-color);
  border-radius: 3px;
  outline: none;
  margin: 10px 0;
}
.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
}
.range-slider:disabled {
  opacity: 0.45;
}

.size-val {
  text-align: right;
  font-weight: bold;
  color: var(--primary);
  font-size: 14px;
  margin-top: 5px;
}

/* ========== 生成按钮 ========== */
.btn-generate {
  width: 100%;
  padding: 16px;
  border-radius: 16px;
  border: none;
  background: var(--primary);
  color: #1e293b;
  font-size: 16px;
  font-weight: 900;
  cursor: pointer;
  transition: 0.2s;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.05);
}
.btn-generate:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}
.btn-generate:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-export-plan {
  width: 100%;
  padding: 14px;
  border-radius: 14px;
  border: 2px solid var(--primary);
  background: transparent;
  color: var(--text-main);
  font-size: 14px;
  font-weight: 900;
  cursor: pointer;
  transition: 0.2s;
  margin-top: 12px;
}
.btn-export-plan:hover:not(:disabled) {
  background: var(--primary-light);
}
.btn-export-plan:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-save-work {
  width: 100%;
  padding: 14px;
  border-radius: 14px;
  border: 2px solid var(--primary);
  background: var(--primary);
  color: #1e293b;
  font-size: 14px;
  font-weight: 900;
  cursor: pointer;
  transition: 0.2s;
  margin-top: 12px;
}
.btn-save-work:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
}
.btn-save-work:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.btn-login-hint {
  background: transparent;
  border: 2px dashed var(--primary);
  color: var(--primary);
}
.save-overlay {
  position: fixed; inset: 0; z-index: 3000;
  background: rgba(0, 0, 0, 0.4);
  display: flex; justify-content: center; align-items: center;
}
.save-modal {
  background: white; padding: 30px; border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2); width: 380px;
}
.save-modal h3 { font-size: 18px; font-weight: 900; margin-bottom: 16px; text-align: center; color: var(--text-main); }
.save-input, .save-select {
  width: 100%; padding: 10px 12px; border-radius: 8px;
  border: 1px solid var(--border-color); font-size: 14px;
  font-weight: bold; outline: none; margin-bottom: 12px; background: white;
}
.save-input:focus, .save-select:focus { border-color: var(--primary); }
.save-actions { display: flex; gap: 10px; }
.save-confirm {
  flex: 1; padding: 10px; border: none; border-radius: 8px;
  background: var(--primary); color: #1e293b; font-weight: bold; font-size: 14px; cursor: pointer;
}
.save-confirm:disabled { opacity: 0.5; }
.save-cancel {
  padding: 10px 20px; border: 1px solid var(--border-color); border-radius: 8px;
  background: white; color: var(--text-light); font-weight: bold; font-size: 14px; cursor: pointer;
}
.save-ok { color: #27ae60; font-size: 13px; margin-top: 10px; text-align: center; font-weight: bold; }
.save-err { color: #e74c3c; font-size: 13px; margin-top: 10px; text-align: center; font-weight: bold; }
.crop-overlay {
  position: fixed;
  inset: 0;
  z-index: 3100;
  background: rgba(15, 23, 42, 0.58);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.crop-modal {
  width: min(720px, 96vw);
  max-height: 92vh;
  overflow: auto;
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.24);
}
.crop-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}
.crop-head h3 {
  margin: 0;
  color: var(--text-main);
  font-size: 18px;
  font-weight: 900;
}
.crop-close {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: #f1f5f9;
  color: var(--text-main);
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
}
.crop-stage {
  position: relative;
  width: fit-content;
  max-width: 100%;
  margin: 0 auto;
  overflow: hidden;
  border-radius: 10px;
  background:
    linear-gradient(45deg, #e2e8f0 25%, transparent 25%),
    linear-gradient(-45deg, #e2e8f0 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #e2e8f0 75%),
    linear-gradient(-45deg, transparent 75%, #e2e8f0 75%);
  background-size: 18px 18px;
  background-position: 0 0, 0 9px, 9px -9px, -9px 0;
}
.crop-image {
  width: auto;
  max-width: 100%;
  height: auto;
  max-height: 52vh;
  display: block;
}
.crop-box {
  position: absolute;
  border: 2px solid var(--primary);
  box-shadow: 0 0 0 9999px rgba(15, 23, 42, 0.42);
  pointer-events: none;
}
.crop-controls {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}
.crop-controls label {
  display: grid;
  gap: 6px;
  font-size: 12px;
  font-weight: 900;
  color: var(--text-light);
}
.crop-controls input {
  width: 100%;
}
.crop-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
}
.crop-note {
  margin: 12px 0 0;
  color: var(--text-light);
  font-size: 12px;
  line-height: 1.5;
}
.btn-loading {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  border-top-color: #1e293b;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ========== 中央画布 ========== */
.ws-center {
  flex: 1;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  background: #eaeaef;
}

.guide-placeholder {
  text-align: center;
  color: var(--text-light);
  cursor: pointer;
}
.guide-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
}
.guide-placeholder h2 {
  font-size: 20px;
  margin-bottom: 8px;
  color: var(--text-main);
}
.guide-placeholder p {
  font-size: 13px;
}
.guide-action {
  margin-top: 18px;
  padding: 10px 22px;
  border: none;
  border-radius: 999px;
  background: var(--primary);
  color: #1e293b;
  font-weight: 900;
  cursor: pointer;
  box-shadow: var(--shadow-soft);
}

.canvas-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  padding: 40px;
}

.canvas-wrapper {
  width: min(65vh, calc(100vw - 680px));
  max-width: 550px;
  background: white;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease-out;
  overflow: hidden;
  border-radius: 4px;
}

.canvas-grid {
  display: grid;
  width: 100%;
  height: 100%;
}

.cell {
  position: relative;
  overflow: hidden;
  outline: 1px solid rgba(0,0,0,0.3);
}
.cell-empty {
  background-image:
    linear-gradient(45deg, rgba(148,163,184,0.18) 25%, transparent 25%),
    linear-gradient(-45deg, rgba(148,163,184,0.18) 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, rgba(148,163,184,0.18) 75%),
    linear-gradient(-45deg, transparent 75%, rgba(148,163,184,0.18) 75%);
  background-size: 8px 8px;
  background-position: 0 0, 0 4px, 4px -4px, -4px 0;
}

.cell-label {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-family:
    'Courier New', 'Consolas', monospace;
  user-select: none;
  pointer-events: none;
  line-height: 1;
}

/* ========== 缩放控件 ========== */
.zoom-controls {
  position: absolute;
  right: 20px;
  bottom: 20px;
  display: flex;
  gap: 10px;
  background: white;
  padding: 8px 15px;
  border-radius: 20px;
  box-shadow: var(--shadow-soft);
  font-weight: bold;
  align-items: center;
  border: 1px solid var(--border-color);
}
.zoom-btn {
  cursor: pointer;
  user-select: none;
}
.zoom-text {
  min-width: 44px;
  text-align: center;
}

/* ========== 右侧清单 ========== */
.brand-indicator {
  font-size: 13px;
  color: var(--text-light);
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}
.brand-count {
  font-weight: normal;
}

.ws-tip {
  font-size: 12px;
  color: var(--text-light);
  margin-bottom: 15px;
  line-height: 1.5;
}
.color-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 5px;
}

.color-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: bold;
  background: #f8fafc;
}
.c-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.c-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.ws-footer {
  border-top: 1px solid var(--border-color);
  padding-top: 15px;
  margin-top: 15px;
}
.total-row {
  display: flex;
  justify-content: space-between;
  font-weight: 900;
  margin-bottom: 10px;
}
.total-count {
  color: var(--primary);
  filter: brightness(0.85);
}

.ws-toggle {
  display: none;
  position: fixed;
  z-index: 160;
  padding: 8px 14px;
  border-radius: 20px;
  border: 1px solid var(--border-color);
  background: white;
  font-weight: bold;
  font-size: 13px;
  cursor: pointer;
  box-shadow: var(--shadow-soft);
  color: var(--text-main);
  transition: 0.2s;
}
.ws-toggle.active {
  background: var(--primary);
  color: #1e293b;
}
.ws-toggle-left {
  top: calc(var(--header-height) + 10px);
  left: 10px;
}
.ws-toggle-right {
  top: calc(var(--header-height) + 10px);
  right: 10px;
}

.panel-scrim {
  display: none;
}

@media (max-width: 900px) {
  .workspace { flex-direction: column; height: auto; min-height: calc(100vh - var(--header-height)); }
  .ws-toggle { display: block; }
  .panel-scrim {
    display: block;
    position: fixed;
    inset: var(--header-height) 0 0;
    z-index: 90;
    background: rgba(15, 23, 42, 0.28);
    backdrop-filter: blur(2px);
  }
  .ws-sidebar {
    position: fixed;
    top: var(--header-height);
    left: 0;
    bottom: 0;
    width: 320px;
    max-width: 85vw;
    z-index: 140;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    box-shadow: 2px 0 20px rgba(0, 0, 0, 0.1);
  }
  .ws-sidebar.panel-open {
    transform: translateX(0);
  }
  .ws-sidebar-right {
    position: fixed;
    top: var(--header-height);
    right: 0;
    bottom: 0;
    left: auto;
    transform: translateX(100%);
    box-shadow: -2px 0 20px rgba(0, 0, 0, 0.1);
    border-left: 1px solid var(--border-color);
  }
  .ws-sidebar-right.panel-open {
    transform: translateX(0);
  }
  .ws-center {
    flex: none;
    height: calc(100vh - var(--header-height));
    min-height: 400px;
  }
  .canvas-wrapper {
    width: min(75vh, calc(100vw - 40px));
  }
  .zoom-controls {
    right: 10px;
    bottom: 10px;
  }
  .save-modal {
    width: 90vw;
  }
}

@media (max-width: 640px) {
  .workspace {
    display: flex;
    flex-direction: column;
    height: auto;
    min-height: calc(100dvh - var(--header-height));
    overflow: visible;
    background: #eaeaef;
  }
  .ws-toggle,
  .panel-scrim {
    display: none;
  }
  .workspace > .ws-sidebar:not(.ws-sidebar-right) {
    order: 1;
  }
  .ws-center {
    order: 2;
  }
  .ws-sidebar-right {
    order: 3;
  }
  .ws-sidebar,
  .ws-sidebar.panel-open,
  .ws-sidebar-right,
  .ws-sidebar-right.panel-open {
    position: static;
    inset: auto;
    width: 100%;
    max-width: none;
    height: auto;
    transform: none;
    z-index: 1;
    box-shadow: none;
  }
  .ws-sidebar {
    border-bottom: 1px solid var(--border-color);
  }
  .ws-sidebar-right {
    display: none;
    border-left: none;
    border-top: 1px solid var(--border-color);
  }
  .workspace.has-grid-data .ws-sidebar-right {
    display: flex;
  }
  .ws-body {
    overflow: visible;
  }
  .upload-area {
    aspect-ratio: 16 / 9;
    min-height: 160px;
    max-height: none;
  }
  .ws-center {
    height: auto;
    min-height: 360px;
    flex: none;
  }
  .canvas-container {
    min-height: 360px;
  }
  .canvas-wrapper {
    width: min(100%, calc(100vw - 32px));
  }
}

@media (max-width: 480px) {
  .ws-toggle {
    top: calc(var(--header-height) + 8px);
    padding: 7px 10px;
    font-size: 12px;
  }
  .ws-sidebar {
    width: 100%;
  }
  .ws-header {
    padding: 14px 16px;
    font-size: 15px;
  }
  .ws-body {
    padding: 14px;
  }
  .upload-area {
    min-height: 150px;
    max-height: none;
  }
  .control-group {
    margin-bottom: 18px;
  }
  .ws-center {
    height: auto;
    min-height: 340px;
  }
  .canvas-wrapper {
    width: min(70vh, calc(100vw - 28px));
  }
  .canvas-container {
    padding: 20px;
  }
  .guide-placeholder h2 {
    font-size: 17px;
  }
  .guide-icon {
    font-size: 48px;
  }
  .zoom-controls {
    left: 50%;
    right: auto;
    transform: translateX(-50%);
    bottom: max(10px, env(safe-area-inset-bottom));
    padding: 7px 12px;
  }
  .save-overlay {
    padding: 14px;
    align-items: flex-end;
  }
  .save-modal {
    width: 100%;
    padding: 20px;
  }
  .save-actions {
    flex-direction: column;
  }
}
</style>
