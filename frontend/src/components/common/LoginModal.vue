<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-card">
        <h2>{{ isRegister ? '注册' : '登录' }}</h2>

        <form @submit.prevent="onSubmit">
          <input v-model="username" type="text" placeholder="用户名" required />
          <input v-if="isRegister" v-model="email" type="email" placeholder="邮箱" required />
          <input v-model="password" type="password" placeholder="密码" required />

          <p v-if="error" class="error">{{ error }}</p>
          <button type="submit" :disabled="loading">{{ isRegister ? '注册' : '登录' }}</button>
        </form>

        <p class="switch">
          {{ isRegister ? '已有账号？' : '还没有账号？' }}
          <span class="link" @click="toggleMode">{{ isRegister ? '去登录' : '去注册' }}</span>
        </p>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { login, register } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

defineProps<{ visible: boolean }>()
const emit = defineEmits<{ close: [] }>()

const auth = useAuthStore()

const isRegister = ref(false)
const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

function toggleMode() {
  isRegister.value = !isRegister.value
  error.value = ''
}

async function onSubmit() {
  loading.value = true
  error.value = ''
  try {
    if (isRegister.value) {
      await register(username.value, email.value, password.value)
      const res = await login(username.value, password.value)
      auth.setToken(res.access_token)
      auth.setUser(res.user)
    } else {
      const res = await login(username.value, password.value)
      auth.setToken(res.access_token)
      auth.setUser(res.user)
    }
    emit('close')
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; z-index: 2000;
  background: rgba(0, 0, 0, 0.35);
  display: flex; justify-content: center; align-items: center;
}
.modal-card {
  background: white; padding: 36px; border-radius: var(--radius-lg);
  box-shadow: 0 10px 40px rgba(0,0,0,0.12); width: 360px; max-width: 90vw;
}
h2 { font-size: 22px; text-align: center; margin-bottom: 20px; color: var(--text-main); }
form { display: flex; flex-direction: column; gap: 14px; }
input {
  padding: 12px; border: 1px solid var(--border-color);
  border-radius: 8px; font-size: 15px; outline: none;
}
input:focus { border-color: var(--primary); }
button {
  padding: 12px; background: var(--primary); color: white;
  border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer;
}
button:disabled { opacity: 0.6; }
.error { color: #e74c3c; font-size: 13px; text-align: center; }
.switch { text-align: center; font-size: 14px; color: var(--text-light); margin-top: 14px; }
.link { color: var(--primary); cursor: pointer; font-weight: bold; }
.link:hover { text-decoration: underline; }

@media (max-width: 480px) {
  .modal-overlay {
    padding: 12px;
    align-items: flex-end;
  }
  .modal-card {
    width: 100%;
    max-width: none;
    padding: 28px 20px 24px;
    border-radius: 18px;
  }
}
</style>
