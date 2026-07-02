<template>
    <NavHeader @open-login="showLogin = true" />
  <main :class="$route.name === 'workspace' ? 'workspace-layout' : 'default-layout'">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </main>
  <FloatingPet
    message="点这里抽个盲盒呀！(づ￣ 3￣)づ"
    @click="onBlindBox"
  />
  <ExportModal :visible="showExportModal" @close="showExportModal = false" />
  <BlindBoxModal :visible="showBlindBox" :pattern="blindPattern" :loading="blindLoading" :exhausted="blindExhausted" :limit="BLIND_DAILY_LIMIT" @close="showBlindBox = false" @draw-again="doBlindBox" />
  <ColorBoxModal :visible="showColorBox" :result="colorResult" :loading="colorLoading" :exhausted="colorExhausted" :limit="DAILY_LIMIT" @close="showColorBox = false" @draw-again="doColorBox" />
  <LoginModal :visible="showLogin" @close="showLogin = false" />
</template>

<script setup lang="ts">
import { ref, provide, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import NavHeader from '@/components/common/NavHeader.vue'
import FloatingPet from '@/components/common/FloatingPet.vue'
import ExportModal from '@/components/common/ExportModal.vue'
import BlindBoxModal from '@/components/common/BlindBoxModal.vue'
import ColorBoxModal from '@/components/common/ColorBoxModal.vue'
import LoginModal from '@/components/common/LoginModal.vue'
import type { ColorResult } from '@/components/common/ColorBoxModal.vue'
import { fetchRandomPattern, type PatternItem } from '@/api/patterns'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const auth = useAuthStore()
const showExportModal = ref(false)
const exportData = ref<any>(null)
const showBlindBox = ref(false)
const blindPattern = ref<PatternItem | null>(null)
const blindLoading = ref(false)
const blindExhausted = ref(false)
const showLogin = ref(false)

onMounted(() => {
  auth.fetchProfile()
})

const BLIND_DAILY_LIMIT = 3

function getTodayKey() {
  return new Date().toISOString().slice(0, 10)
}

function checkBlindLimit(): boolean {
  const key = getTodayKey()
  const stored = localStorage.getItem('blind_box_date')
  if (stored !== key) return false
  const count = Number(localStorage.getItem('blind_box_count') || '0')
  return count >= BLIND_DAILY_LIMIT
}

function incrementBlindCount() {
  const key = getTodayKey()
  const stored = localStorage.getItem('blind_box_date')
  if (stored !== key) {
    localStorage.setItem('blind_box_date', key)
    localStorage.setItem('blind_box_count', '1')
  } else {
    const count = Number(localStorage.getItem('blind_box_count') || '0')
    localStorage.setItem('blind_box_count', String(count + 1))
  }
}

async function doBlindBox() {
  if (checkBlindLimit()) {
    blindExhausted.value = true
    blindPattern.value = null
    blindLoading.value = false
    showBlindBox.value = true
    return
  }
  blindExhausted.value = false
  blindLoading.value = true
  showBlindBox.value = true
  blindPattern.value = null
  try {
    const [pattern] = await Promise.all([
      fetchRandomPattern(),
      new Promise(r => setTimeout(r, 1000)),
    ])
    blindPattern.value = pattern
    incrementBlindCount()
  } catch {
    blindPattern.value = null
  } finally {
    blindLoading.value = false
  }
}

provide('triggerBlindBox', doBlindBox)

const COLOR_OPTIONS: ColorResult[] = [
  { name: '白色系', nameShort: '白色', value: '#F5F5F5' },
  { name: '灰色系', nameShort: '灰色', value: '#A0AEC0' },
  { name: '黑色系', nameShort: '黑色', value: '#333333' },
  { name: '红色系', nameShort: '红色', value: '#FF6B6B' },
  { name: '橙色系', nameShort: '橙色', value: '#FF9F43' },
  { name: '黄色系', nameShort: '黄色', value: '#FECA57' },
  { name: '绿色系', nameShort: '绿色', value: '#7BED9F' },
  { name: '蓝色系', nameShort: '蓝色', value: '#54A0FF' },
  { name: '紫色系', nameShort: '紫色', value: '#A29BFE' },
  { name: '粉色系', nameShort: '粉色', value: '#FD79A8' },
  { name: '大地/棕色系', nameShort: '棕土色', value: '#CD853F' },
  { name: '多彩混色', nameShort: '多彩', value: 'linear-gradient(135deg, #FF6B6B, #FECA57, #7BED9F, #54A0FF, #A29BFE, #FD79A8)' },
]

const DAILY_LIMIT = 3
const showColorBox = ref(false)
const colorResult = ref<ColorResult | null>(null)
const colorLoading = ref(false)
const colorExhausted = ref(false)

function checkColorLimit(): boolean {
  const key = getTodayKey()
  const stored = localStorage.getItem('color_box_date')
  if (stored !== key) return false
  const count = Number(localStorage.getItem('color_box_count') || '0')
  return count >= DAILY_LIMIT
}

function incrementColorCount() {
  const key = getTodayKey()
  const stored = localStorage.getItem('color_box_date')
  if (stored !== key) {
    localStorage.setItem('color_box_date', key)
    localStorage.setItem('color_box_count', '1')
  } else {
    const count = Number(localStorage.getItem('color_box_count') || '0')
    localStorage.setItem('color_box_count', String(count + 1))
  }
}

async function doColorBox() {
  if (checkColorLimit()) {
    colorExhausted.value = true
    colorResult.value = null
    colorLoading.value = false
    showColorBox.value = true
    return
  }
  colorExhausted.value = false
  colorLoading.value = true
  showColorBox.value = true
  colorResult.value = null
  await new Promise(r => setTimeout(r, 1500))
  colorResult.value = COLOR_OPTIONS[Math.floor(Math.random() * COLOR_OPTIONS.length)]
  incrementColorCount()
  colorLoading.value = false
}

provide('triggerColorBox', doColorBox)

provide('openLogin', () => {
  showLogin.value = true
})

provide('showExportModal', (val: boolean) => {
  showExportModal.value = val
})
provide('exportData', exportData)
provide('updateExportData', (data: any) => {
  exportData.value = data
})

watch(
  () => route.name,
  (name) => {
    if (name === 'workspace') {
      document.body.classList.add('immersive')
    } else {
      document.body.classList.remove('immersive')
      window.scrollTo(0, 0)
    }
  },
  { immediate: true }
)

function onBlindBox() {
  doBlindBox()
}
</script>

<style>
@import '@/assets/styles/variables.css';
@import '@/assets/styles/base.css';

@media (max-width: 900px) {
  :root { --header-height: 70px; }
}
@media (max-width: 480px) {
  :root { --header-height: 64px; }
}
</style>

<style scoped>
.default-layout {
  padding-top: calc(var(--header-height) + 30px);
  padding-bottom: 80px;
  min-height: 100vh;
}

.workspace-layout {
  padding-top: var(--header-height);
  height: 100vh;
}

@media (max-width: 900px) {
  .default-layout {
    padding-top: calc(var(--header-height) + 18px);
    padding-bottom: 48px;
  }
}

@media (max-width: 480px) {
  .default-layout {
    padding-top: calc(var(--header-height) + 12px);
    padding-bottom: 36px;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(15px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-15px);
}
</style>
