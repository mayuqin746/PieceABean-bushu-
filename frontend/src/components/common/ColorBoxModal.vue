<template>
  <Teleport to="body">
    <div class="modal-overlay" :class="{ active: visible }" @click.self="$emit('close')">
      <div class="modal-card" v-if="visible">
        <div class="close-btn" @click="$emit('close')">✖</div>

        <template v-if="loading">
          <div class="drawing-box">
            <div class="color-wheel"></div>
            <span class="drawing-text">专属色抽取中...</span>
          </div>
        </template>

        <template v-else-if="exhausted">
          <div class="exhausted-box">
            <div class="color-wheel exhausted"></div>
            <h2 class="modal-title">今日次数已用完</h2>
            <span class="drawing-text">每天可抽取 {{ limit }} 次，明天再来吧！</span>
          </div>
        </template>

        <template v-else-if="result">
          <h2 class="modal-title">今日专属色</h2>
          <div class="color-result">
            <div class="result-dot" :style="{ background: result.value }"></div>
          </div>
          <p class="color-name">{{ result.name }}</p>
          <div class="btn-row">
            <button class="btn-draw-again" @click="$emit('drawAgain')">再次抽取</button>
            <button class="btn-action" @click="onGoGallery">拼一个{{ result.nameShort }}图纸</button>
          </div>
        </template>

        <template v-else>
          <div class="drawing-box">
            <span class="drawing-text">暂无数据，请稍后重试</span>
          </div>
        </template>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

export interface ColorResult {
  name: string
  nameShort: string
  value: string
}

const props = defineProps<{
  visible: boolean
  result: ColorResult | null
  loading: boolean
  exhausted: boolean
  limit?: number
}>()

const emit = defineEmits<{
  close: []
  drawAgain: []
}>()

const router = useRouter()

function onGoGallery() {
  if (props.result) {
    emit('close')
    router.push({ path: '/gallery', query: { color: props.result.name } })
  }
}
</script>

<style scoped>
.modal-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 3000;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(5px);
}
.modal-overlay.active { display: flex; }

.modal-card {
  background: white;
  width: 400px; max-width: 90vw;
  border-radius: var(--radius-lg);
  padding: 36px 32px 28px;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  text-align: center;
  animation: popIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes popIn {
  from {
    opacity: 0;
    transform: scale(0.8) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.close-btn {
  position: absolute;
  top: 14px; right: 14px;
  font-size: 16px; cursor: pointer;
  background: var(--bg-color);
  width: 30px; height: 30px;
  border-radius: 50%;
  display: flex; justify-content: center; align-items: center;
  user-select: none; z-index: 1;
}

.modal-title {
  font-size: 20px;
  font-weight: 900;
  color: var(--text-main);
  margin: 0 0 24px;
}

.drawing-box {
  padding: 32px 0 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}
.exhausted-box {
  padding: 20px 0 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.color-wheel {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: conic-gradient(
    #F5F5F5, #A0AEC0, #333333, #FF6B6B, #FF9F43,
    #FECA57, #7BED9F, #54A0FF, #A29BFE, #FD79A8,
    #CD853F, #F5F5F5
  );
  animation: spin 0.8s linear infinite;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}
.color-wheel.exhausted {
  animation: none;
  filter: grayscale(1);
  opacity: 0.5;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.drawing-text {
  font-size: 15px;
  font-weight: bold;
  color: var(--text-light);
}

.color-result {
  margin-bottom: 16px;
}
.result-dot {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin: 0 auto;
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2);
  animation: popIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.color-name {
  font-size: 18px;
  font-weight: 900;
  color: var(--text-main);
  margin: 0 0 24px;
}

.btn-row {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-draw-again, .btn-action {
  padding: 10px 20px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 900;
  cursor: pointer;
  transition: 0.2s;
  border: none;
}
.btn-draw-again {
  background: var(--bg-color);
  color: var(--text-main);
}
.btn-draw-again:hover {
  background: var(--border-color);
}
.btn-action {
  background: var(--primary);
  color: #1e293b;
}
.btn-action:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>
