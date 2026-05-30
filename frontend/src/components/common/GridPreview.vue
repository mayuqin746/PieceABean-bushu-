<template>
  <canvas ref="canvasRef" class="grid-preview" :width="canvasW" :height="canvasH"></canvas>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

const props = defineProps<{
  gridData: string[][] | null
  width: number
  height: number
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const MAX_SIZE = 160
const scale = Math.min(MAX_SIZE / props.width, MAX_SIZE / props.height)
const canvasW = Math.round(props.width * scale)
const canvasH = Math.round(props.height * scale)

function draw() {
  const c = canvasRef.value
  if (!c || !props.gridData || !props.gridData.length) return
  const ctx = c.getContext('2d')
  if (!ctx) return
  const rows = props.gridData.length
  const cols = rows > 0 ? props.gridData[0].length : 0
  const s = scale
  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const hex = props.gridData[y]?.[x] || '#ccc'
      ctx.fillStyle = hex
      ctx.fillRect(Math.round(x * s), Math.round(y * s), Math.ceil(s), Math.ceil(s))
    }
  }
}

onMounted(draw)
watch(() => props.gridData, draw)
</script>

<style scoped>
.grid-preview {
  width: 100%;
  height: 160px;
  object-fit: contain;
  image-rendering: pixelated;
  border-radius: 8px;
  background: #eee;
}
</style>
