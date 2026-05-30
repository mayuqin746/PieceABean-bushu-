<template>
  <div class="floating-pet" @click="$emit('click')">
    <div class="chat-bubble">{{ message }}</div>
    <div class="sprite"></div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ message?: string }>()
defineEmits<{ click: [] }>()
</script>

<style scoped>
.floating-pet {
  position: fixed;
  bottom: 40px;
  right: 40px;
  z-index: 999;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  animation: float 2s infinite ease-in-out;
}

.chat-bubble {
  background: white;
  padding: 10px 18px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: bold;
  color: var(--primary);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.06);
  margin-bottom: 12px;
  opacity: 0;
  transform: translateY(10px);
  transition: 0.3s;
  position: relative;
  border: 1px solid var(--border-color);
  white-space: nowrap;
}

.chat-bubble::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px 6px 0;
  border-style: solid;
  border-color: white transparent transparent transparent;
}

.floating-pet:hover .chat-bubble {
  opacity: 1;
  transform: translateY(0);
}

.sprite {
  width: 102px;
  height: 125px;
  background: url("/sprite.png") no-repeat;
  background-size: 410px 125px;
  animation: play 2s steps(4) infinite;
  user-select: none;
}

@keyframes play {
  from { background-position: 0 0; }
  to { background-position: -410px 0; }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}
</style>
