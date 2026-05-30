<template>
  <div class="admin-container">
    <div class="upload-card">
      <h1>上传图纸</h1>
      <form @submit.prevent="onSubmit">
        <div class="field">
          <label>封面缩略图（将自动压缩）</label>
          <input type="file" accept=".png,.jpg,.jpeg,.webp" @change="onThumbChange" required />
        </div>
        <div class="field">
          <label>高清网格图纸</label>
          <input type="file" accept=".png,.jpg,.jpeg,.webp" @change="onBlueprintChange" required />
        </div>
        <div class="field">
          <label>标题</label>
          <input v-model="title" type="text" placeholder="图纸标题" required />
        </div>
        <div class="field">
          <label>主题</label>
          <select v-model="category" required>
            <option v-for="t in themes" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
        <div class="field">
          <label>系列</label>
          <select v-model="series">
            <option v-for="s in seriesList" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <div class="field">
          <label>色系（多选）</label>
          <div class="color-checkboxes">
            <label v-for="c in colorOptions" :key="c" class="color-label">
              <input type="checkbox" :value="c" v-model="colors" />
              {{ c }}
            </label>
          </div>
        </div>
        <p v-if="msg" :class="msgType">{{ msg }}</p>
        <button type="submit" :disabled="uploading">上传图纸</button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { uploadPattern } from '@/api/admin'

const router = useRouter()
const auth = useAuthStore()

if (!auth.isLoggedIn) {
  router.replace('/admin/login')
}

const themes = ['动漫/IP', '萌宠动物', '美食饮品', '生活日常', '明星应援', '其他']
const seriesList = ['三丽鸥', '线条小狗', '星之卡比', '马里奥', '吉伊卡哇(Chiikawa)']
const colorOptions = ['白色系', '灰色系', '黑色系', '红色系', '橙色系', '黄色系', '绿色系', '蓝色系', '紫色系', '粉色系', '大地/棕色系', '多彩混色']

const thumbFile = ref<File | null>(null)
const blueprintFile = ref<File | null>(null)
const title = ref('')
const category = ref('其他')
const series = ref('')
const colors = ref<string[]>([])
const msg = ref('')
const msgType = ref<'success' | 'error'>('success')
const uploading = ref(false)

function onThumbChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) thumbFile.value = input.files[0]
}

function onBlueprintChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) blueprintFile.value = input.files[0]
}

async function onSubmit() {
  if (!thumbFile.value || !blueprintFile.value) return
  uploading.value = true
  msg.value = ''
  try {
    const fd = new FormData()
    fd.append('thumbnail_file', thumbFile.value)
    fd.append('blueprint_file', blueprintFile.value)
    fd.append('title', title.value)
    fd.append('category', category.value)
    fd.append('series', series.value)
    fd.append('colors', JSON.stringify(colors.value))
    await uploadPattern(fd)
    msg.value = '上传成功！'
    msgType.value = 'success'
    title.value = ''
    series.value = ''
    colors.value = []
    thumbFile.value = null
    blueprintFile.value = null
  } catch (e: any) {
    msg.value = e?.response?.data?.detail ?? '上传失败'
    msgType.value = 'error'
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--bg-color);
  padding: 40px 20px;
}
.upload-card {
  background: white;
  padding: 40px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
  width: 500px;
}
h1 { font-size: 22px; text-align: center; color: var(--text-main); margin-bottom: 24px; }
.field { margin-bottom: 16px; }
.field label { display: block; font-weight: bold; font-size: 14px; margin-bottom: 6px; color: var(--text-main); }
.field input[type="text"],
.field select {
  width: 100%; padding: 10px; border: 1px solid var(--border-color);
  border-radius: 8px; font-size: 15px; outline: none;
}
.field input:focus,
.field select:focus { border-color: var(--primary); }
.color-checkboxes { display: flex; flex-wrap: wrap; gap: 12px; }
.color-label { display: flex; align-items: center; gap: 4px; font-size: 14px; cursor: pointer; }
button {
  width: 100%; padding: 12px; background: var(--primary); color: white;
  border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 8px;
}
button:disabled { opacity: 0.6; }
.success { color: #27ae60; font-size: 14px; text-align: center; }
.error { color: #e74c3c; font-size: 14px; text-align: center; }
</style>
