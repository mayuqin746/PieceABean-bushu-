<template>
  <Teleport to="body">
    <div v-if="visible" class="detail-overlay" @click.self="$emit('close')" @wheel.prevent="onWheel">
      <div class="detail-toolbar">
        <span class="dt-title">{{ title }}</span>
        <span class="dt-info">{{ width }}×{{ height }} · {{ beadsCount }} 颗</span>
        <div class="dt-controls">
          <button @click="zoomIn" title="放大">＋</button>
          <span class="dt-zoom">{{ Math.round(zoom * 100) }}%</span>
          <button @click="zoomOut" title="缩小">－</button>
          <button @click="resetView" title="重置">↺</button>
          <button class="dt-close" @click="$emit('close')" title="关闭">✕</button>
        </div>
      </div>
      <div
        class="detail-canvas-wrap"
        @mousedown="onMouseDown"
        @mousemove="onMouseMove"
        @mouseup="onMouseUp"
        @mouseleave="onMouseUp"
      >
        <canvas ref="canvasRef" class="detail-canvas" :width="canvasW" :height="canvasH"
          :style="{
            transform: `translate(${posX}px, ${posY}px) scale(${zoom})`,
            transformOrigin: 'center center',
          }"
        ></canvas>
      </div>
      <div class="detail-hint">滚轮缩放 · 拖拽平移 · 单击背景关闭</div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'

const props = defineProps<{
  visible: boolean
  gridData: string[][] | null
  width: number
  height: number
  title: string
  beadsCount: number
}>()

defineEmits<{ close: [] }>()

const canvasRef = ref<HTMLCanvasElement | null>(null)

const SCALE = 16
const canvasW = props.width * SCALE
const canvasH = props.height * SCALE

const zoom = ref(1)
const posX = ref(0)
const posY = ref(0)

const dragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const dragStartPosX = ref(0)
const dragStartPosY = ref(0)

const ZOOM_MIN = 0.2
const ZOOM_MAX = 8
const ZOOM_STEP = 0.2

function draw() {
  const c = canvasRef.value
  if (!c || !props.gridData || !props.gridData.length) return
  const ctx = c.getContext('2d')
  if (!ctx) return

  const rows = props.gridData.length
  const cols = rows > 0 ? props.gridData[0].length : 0

  ctx.clearRect(0, 0, canvasW, canvasH)

  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const hex = props.gridData[y]?.[x] || '#ccc'
      ctx.fillStyle = hex
      ctx.fillRect(x * SCALE, y * SCALE, SCALE, SCALE)
    }
  }

  ctx.strokeStyle = 'rgba(0,0,0,0.08)'
  ctx.lineWidth = 0.5
  for (let x = 0; x <= cols; x++) {
    ctx.beginPath()
    ctx.moveTo(x * SCALE, 0)
    ctx.lineTo(x * SCALE, rows * SCALE)
    ctx.stroke()
  }
  for (let y = 0; y <= rows; y++) {
    ctx.beginPath()
    ctx.moveTo(0, y * SCALE)
    ctx.lineTo(cols * SCALE, y * SCALE)
    ctx.stroke()
  }
}

function zoomIn() {
  zoom.value = Math.min(ZOOM_MAX, +(zoom.value + ZOOM_STEP).toFixed(1))
}

function zoomOut() {
  zoom.value = Math.max(ZOOM_MIN, +(zoom.value - ZOOM_STEP).toFixed(1))
}

function resetView() {
  zoom.value = 1
  posX.value = 0
  posY.value = 0
}

function onWheel(e: WheelEvent) {
  e.preventDefault()
  const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP
  zoom.value = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, +(zoom.value + delta).toFixed(1)))
}

function onMouseDown(e: MouseEvent) {
  if (e.button !== 0) return
  dragging.value = true
  dragStartX.value = e.clientX
  dragStartY.value = e.clientY
  dragStartPosX.value = posX.value
  dragStartPosY.value = posY.value
}

function onMouseMove(e: MouseEvent) {
  if (!dragging.value) return
  posX.value = dragStartPosX.value + (e.clientX - dragStartX.value)
  posY.value = dragStartPosY.value + (e.clientY - dragStartY.value)
}

function onMouseUp() {
  dragging.value = false
}

watch(() => props.visible, async (val) => {
  if (val) {
    resetView()
    await nextTick()
    draw()
  }
})

onMounted(() => {
  if (props.visible) draw()
})
</script>

<style scoped>
.detail-overlay {
  position: fixed; inset: 0; z-index: 4000;
  background: rgba(18, 18, 28, 0.94);
  display: flex; flex-direction: column;
  user-select: none;
}
.detail-toolbar {
  display: flex; align-items: center; gap: 16px;
  padding: 10px 20px; background: rgba(255,255,255,0.06);
  color: #ccc; font-size: 14px; font-weight: bold;
  flex-shrink: 0;
}
.dt-title { color: #fff; font-size: 16px; font-weight: 900; }
.dt-info { color: #888; font-size: 13px; margin-right: auto; }
.dt-controls { display: flex; align-items: center; gap: 8px; }
.dt-controls button {
  width: 30px; height: 30px; border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.15); background: rgba(255,255,255,0.05);
  color: #ccc; font-size: 15px; font-weight: bold; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}
.dt-controls button:hover { background: rgba(255,255,255,0.15); color: #fff; }
.dt-zoom { color: #aaa; font-size: 13px; min-width: 40px; text-align: center; font-variant-numeric: tabular-nums; }
.dt-close { font-size: 18px !important; }
.detail-canvas-wrap {
  flex: 1; display: flex; justify-content: center; align-items: center;
  cursor: grab; overflow: hidden;
}
.detail-canvas-wrap:active { cursor: grabbing; }
.detail-canvas {
  image-rendering: pixelated;
  will-change: transform;
  max-width: 90vw; max-height: calc(100vh - 100px);
  object-fit: contain;
}
.detail-hint {
  text-align: center; padding: 6px; color: #444;
  font-size: 12px; flex-shrink: 0;
}
</style>
