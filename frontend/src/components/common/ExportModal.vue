<template>
  <Teleport to="body">
    <div class="modal-overlay" :class="{ active: visible }" @click.self="$emit('close')">
      <div class="modal-content" v-if="visible">
        <div class="close-btn" @click="$emit('close')">✖</div>
        <h2>导出图纸清单</h2>

        <div class="export-body">
          <!-- 左栏：预览 + 下载 -->
          <div class="ex-left">
            <canvas ref="canvasRef" class="ex-canvas"></canvas>
            <button class="ex-action-btn" @click="onDownload">下载图纸</button>
          </div>

          <!-- 右栏：材料清单 -->
          <div class="ex-right">

            <div v-if="!hasData" class="ex-empty">暂无图纸数据</div>
            <div v-else-if="stats.length === 0" class="ex-empty">请选择品牌以查看材料清单</div>

            <template v-else>
              <div class="ex-list">
                <div v-for="s in stats" :key="s.color_no" class="ex-item">
                  <div class="ex-swatch" :style="{ background: s.hex }"></div>
                  <span class="ex-item-name">{{ s.color_no }}</span>
                  <span class="ex-item-count">{{ s.count }} 颗</span>
                </div>
              </div>

              <div class="ex-summary">
                总豆数：<strong>{{ totalBeads }} 颗</strong>
                <span class="ex-summary-detail">（{{ stats.length }} 种颜色，不含透明空格）</span>
              </div>

              <button class="ex-action-btn ex-copy-btn" @click="onCopy">复制清单</button>
            </template>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, inject, type Ref } from 'vue'
import type { GridColor } from '@/api/generator'

const props = defineProps<{ visible: boolean }>()
defineEmits<{ close: [] }>()

interface ExportData {
  gridData: GridColor[][]
  mappedGrid: { hex: GridColor; color_no: string | null; text_color: string }[][]
  brandStats: { color_no: string; hex: string; count: number }[]
  totalBeads: number
  brandLabel: string
  gridWidth: number
  gridHeight: number
}

const data = inject<Ref<ExportData | null>>('exportData', ref(null))

const canvasRef = ref<HTMLCanvasElement | null>(null)
const hasData = ref(false)
const stats = ref<ExportData['brandStats']>([])
const totalBeads = ref(0)
const brandLabel = ref('')

const BORDER_PX = 1
const LABEL_MARGIN = 32
const TITLE_HEIGHT = 48
const FONT = "'Courier New', 'Consolas', monospace"
const CELL_PX = 24
const SCALE = 2

watch(
  () => data.value,
  (val) => {
    if (!val || val.gridData.length === 0) {
      hasData.value = false; stats.value = []; totalBeads.value = 0; brandLabel.value = ''
      return
    }
    hasData.value = true
    stats.value = val.brandStats
    totalBeads.value = val.totalBeads
    brandLabel.value = val.brandLabel || '未选品牌'
  }
)

watch(
  () => props.visible,
  (v) => {
    if (v && data.value) {
      nextTick(() => drawCanvas(data.value!))
    }
  }
)

function drawCanvas(d: ExportData) {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const gw = d.gridWidth
  const gh = d.gridHeight
  const gpW = gw * (CELL_PX + BORDER_PX) + BORDER_PX
  const gpH = gh * (CELL_PX + BORDER_PX) + BORDER_PX
  const w = LABEL_MARGIN + gpW
  const h = TITLE_HEIGHT + LABEL_MARGIN + gpH

  canvas.width = w * SCALE
  canvas.height = h * SCALE
  ctx.scale(SCALE, SCALE)

  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, w, h)

  ctx.fillStyle = '#1e293b'
  ctx.font = `bold 14px ${FONT}`
  ctx.textAlign = 'center'
  ctx.fillText(
    `拼豆图纸 | ${gw}×${gh} | ${d.brandLabel || '未选品牌'} | 共计 ${d.totalBeads} 颗`,
    w / 2,
    TITLE_HEIGHT / 2 + 4
  )

  const ox = LABEL_MARGIN
  const oy = TITLE_HEIGHT + LABEL_MARGIN

  ctx.fillStyle = '#c8c8c8'
  ctx.fillRect(ox, oy, gpW, gpH)

  for (let y = 0; y < gh; y++) {
    for (let x = 0; x < gw; x++) {
      const cell = d.mappedGrid[y]?.[x]
      const hex = cell?.hex ?? d.gridData[y][x]
      if (!hex) continue
      const left = ox + x * (CELL_PX + BORDER_PX) + BORDER_PX
      const top = oy + y * (CELL_PX + BORDER_PX) + BORDER_PX

      ctx.fillStyle = hex
      ctx.fillRect(left, top, CELL_PX, CELL_PX)

      if (cell?.color_no) {
        const fs = Math.min(8, Math.max(5, CELL_PX * 0.35))
        ctx.fillStyle = cell.text_color
        ctx.font = `bold ${fs}px ${FONT}`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(cell.color_no, left + CELL_PX / 2, top + CELL_PX / 2)
      }
    }
  }

  ctx.fillStyle = '#64748b'
  ctx.font = `bold 10px ${FONT}`
  ctx.textAlign = 'right'
  ctx.textBaseline = 'middle'
  for (let y = 0; y < gh; y++) {
    const cy = oy + y * (CELL_PX + BORDER_PX) + CELL_PX / 2 + BORDER_PX
    ctx.fillText(String(y + 1), ox - 6, cy)
  }

  ctx.textAlign = 'center'
  ctx.textBaseline = 'bottom'
  for (let x = 0; x < gw; x++) {
    const cx = ox + x * (CELL_PX + BORDER_PX) + CELL_PX / 2 + BORDER_PX
    ctx.fillText(String(x + 1), cx, oy - 6)
  }
  ctx.textBaseline = 'top'
  for (let x = 0; x < gw; x++) {
    const cx = ox + x * (CELL_PX + BORDER_PX) + CELL_PX / 2 + BORDER_PX
    ctx.fillText(String(x + 1), cx, oy + gpH + 6)
  }
}

function onDownload() {
  const canvas = canvasRef.value
  const d = data.value
  if (!canvas || !d) return

  const gw = d.gridWidth
  const gh = d.gridHeight
  const brand = (d.brandLabel || '未选品牌').replace(/\s/g, '')
  const now = new Date()
  const ts = [
    now.getFullYear(),
    String(now.getMonth() + 1).padStart(2, '0'),
    String(now.getDate()).padStart(2, '0'),
    '_',
    String(now.getHours()).padStart(2, '0'),
    String(now.getMinutes()).padStart(2, '0'),
  ].join('')
  const filename = `拼豆图纸_${gw}x${gh}_${brand}_${ts}.png`

  canvas.toBlob((blob) => {
    if (!blob) return
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }, 'image/png')
}

async function onCopy() {
  const lines = stats.value.map((s) => `${s.color_no} ${s.hex} × ${s.count} 颗`)
  lines.push('')
  lines.push(`总豆数：${totalBeads.value} 颗（${stats.value.length} 种颜色）`)
  const text = lines.join('\n')
  try {
    await navigator.clipboard.writeText(text)
    alert('清单已复制到剪贴板')
  } catch {
    const ta = document.createElement('textarea')
    ta.value = text
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    alert('清单已复制到剪贴板')
  }
}
</script>

<style scoped>
.modal-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 2000;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(5px);
}
.modal-overlay.active { display: flex; }

.modal-content {
  background: white;
  width: 95vw;
  max-width: 1400px;
  max-height: 92vh;
  border-radius: var(--radius-lg);
  padding: 30px;
  position: relative;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}
.modal-content h2 { font-weight: 900; text-align: center; margin-bottom: 20px; flex-shrink: 0; }

.close-btn {
  position: absolute;
  top: 20px; right: 20px;
  font-size: 18px; cursor: pointer;
  background: var(--bg-color);
  width: 32px; height: 32px;
  border-radius: 50%;
  display: flex; justify-content: center; align-items: center;
  user-select: none; z-index: 1;
}

.export-body { display: flex; gap: 24px; flex: 1; min-height: 0; }

.ex-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 0;
}
.ex-canvas {
  flex: 1;
  width: 100%;
  min-height: 0;
  object-fit: contain;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  margin-bottom: 12px;
}

.ex-right { width: 260px; flex-shrink: 0; display: flex; flex-direction: column; overflow: hidden; }
.ex-empty { font-size: 12px; color: var(--text-light); line-height: 1.6; }
.ex-list { flex: 1; overflow-y: auto; }
.ex-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 10px; border: 1px solid var(--border-color);
  border-radius: 8px; margin-bottom: 6px;
  font-size: 12px; font-weight: bold; background: #f8fafc;
}
.ex-swatch {
  width: 16px; height: 16px; border-radius: 4px;
  border: 1px solid rgba(0,0,0,0.1); flex-shrink: 0;
}
.ex-item-name { flex: 1; }
.ex-item-count { color: var(--text-light); font-weight: 900; }
.ex-summary {
  font-size: 13px; padding: 10px 0;
  border-top: 1px solid var(--border-color); margin-bottom: 10px;
}
.ex-summary-detail { font-weight: normal; color: var(--text-light); font-size: 11px; }

.ex-action-btn {
  width: 100%; padding: 14px; border: none; border-radius: 12px;
  font-weight: 900; font-size: 14px; cursor: pointer; transition: 0.2s;
  background: var(--primary); color: #1e293b;
  flex-shrink: 0;
}
.ex-action-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.ex-copy-btn { background: #f1f5f9; color: var(--text-main); margin-top: 8px; }

@media (max-width: 768px) {
  .modal-overlay {
    align-items: flex-end;
  }
  .export-body { flex-direction: column; }
  .ex-right { width: 100%; min-height: 180px; }
  .ex-left { min-height: 240px; }
  .modal-content {
    width: 100vw;
    max-width: none;
    max-height: 92dvh;
    border-radius: 18px 18px 0 0;
    padding: 20px;
  }
  .modal-content h2 {
    font-size: 18px;
    margin-bottom: 14px;
    padding-right: 34px;
  }
  .close-btn {
    top: 14px;
    right: 14px;
  }
}

@media (max-width: 420px) {
  .modal-content { padding: 16px 12px; }
  .export-body { gap: 14px; }
  .ex-left { min-height: 220px; }
  .ex-action-btn { padding: 12px; }
  .ex-list { max-height: 28dvh; }
}
</style>
