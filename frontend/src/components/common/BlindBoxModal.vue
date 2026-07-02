<template>
  <Teleport to="body">
    <div class="modal-overlay" :class="{ active: visible }" @click.self="$emit('close')">
      <div class="modal-card" v-if="visible">
        <div class="close-btn" @click="$emit('close')">✖</div>

        <template v-if="loading">
          <div class="drawing-box">
            <span class="box-icon">🎁</span>
            <span class="drawing-text">抽取中...</span>
          </div>
        </template>

        <template v-else-if="exhausted">
          <div class="exhausted-box">
            <span class="exhausted-icon">🎁</span>
            <h2 class="modal-title">今日次数已用完</h2>
            <span class="drawing-text">每天可抽取 {{ limit }} 次，明天再来吧！</span>
          </div>
        </template>

        <template v-else-if="pattern">
          <h2 class="modal-title">恭喜抽中！</h2>
          <div class="pattern-preview">
            <img
              v-if="pattern.thumbnail_url"
              :src="pattern.thumbnail_url"
              :alt="pattern.title"
              class="preview-img"
            />
          </div>
          <p class="pattern-name">{{ pattern.title }}</p>
          <div class="btn-row">
            <button class="btn-draw-again" @click="$emit('drawAgain')">再来一个</button>
            <button class="btn-detail" @click="onViewDetail">查看详情</button>
          </div>
        </template>

        <template v-else>
          <div class="drawing-box">
            <span class="drawing-text">暂无图纸，请先上传</span>
          </div>
        </template>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { PatternItem } from '@/api/patterns'

const props = defineProps<{
  visible: boolean
  pattern: PatternItem | null
  loading: boolean
  exhausted: boolean
  limit?: number
}>()

const emit = defineEmits<{
  close: []
  drawAgain: []
}>()

const router = useRouter()

function onViewDetail() {
  if (props.pattern) {
    emit('close')
    router.push(`/pattern/${props.pattern.id}`)
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
  margin: 0 0 20px;
}

.pattern-preview {
  width: 200px;
  height: 200px;
  margin: 0 auto 16px;
  border-radius: 12px;
  overflow: hidden;
  background: var(--bg-color);
  display: flex;
  align-items: center;
  justify-content: center;
}
.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.pattern-name {
  font-size: 16px;
  font-weight: bold;
  color: var(--text-main);
  margin: 0 0 24px;
}

.btn-row {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn-draw-again, .btn-detail {
  padding: 10px 24px;
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
.btn-detail {
  background: var(--primary);
  color: #1e293b;
}
.btn-detail:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.drawing-box {
  padding: 48px 0 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.exhausted-box {
  padding: 32px 0 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.exhausted-icon {
  font-size: 48px;
  filter: grayscale(1);
  opacity: 0.6;
}
.box-icon {
  font-size: 48px;
  animation: shake 0.6s ease-in-out infinite;
}
.drawing-text {
  font-size: 16px;
  font-weight: bold;
  color: var(--text-light);
}

@keyframes shake {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-8deg); }
  75% { transform: rotate(8deg); }
}

@media (max-width: 480px) {
  .modal-overlay {
    padding: 12px;
    align-items: flex-end;
  }
  .modal-card {
    width: 100%;
    max-width: none;
    padding: 28px 18px 22px;
    border-radius: 18px;
  }
  .pattern-preview {
    width: min(180px, 58vw);
    height: min(180px, 58vw);
  }
  .btn-row {
    flex-direction: column;
  }
  .btn-draw-again,
  .btn-detail {
    width: 100%;
  }
}
</style>
