<template>
  <div class="admin-container">
    <form class="login-form" @submit.prevent="onLogin">
      <h1>管理员登录</h1>
      <input v-model="username" type="text" placeholder="用户名" required />
      <input v-model="password" type="password" placeholder="密码" required />
      <p v-if="error" class="error">{{ error }}</p>
      <button type="submit" :disabled="loading">登录</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function onLogin() {
  loading.value = true
  error.value = ''
  try {
    const res = await login(username.value, password.value)
    auth.setToken(res.access_token)
    auth.setUser(res.user)
    router.replace('/admin/upload')
  } catch {
    error.value = '用户名或密码错误'
  } finally {
    loading.value = false
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
}
.login-form {
  background: white;
  padding: 40px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
h1 { font-size: 22px; text-align: center; color: var(--text-main); }
input {
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 15px;
  outline: none;
}
input:focus { border-color: var(--primary); }
button {
  padding: 12px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
}
button:disabled { opacity: 0.6; }
.error { color: #e74c3c; font-size: 13px; text-align: center; }
</style>
