<template>
  <header class="navbar">
    <img
      class="logo"
      src="/logo.png"
      alt="拼了个豆"
      @click="$router.push('/')"
    />
    <div class="nav-links">
      <div
        v-for="item in navItems"
        :key="item.target"
        class="nav-item"
        :class="{ active: isActive(item.target) }"
        @click="$router.push(item.path)"
      >
        {{ item.label }}
      </div>
    </div>

    <div class="header-search">
      <input v-model="searchKeyword" type="text" placeholder="搜索图纸、系列..." @keydown.enter="doSearch" />
    </div>

    <div class="theme-switcher">
      <span class="theme-label">主题：</span>
      <div
        v-for="t in themes"
        :key="t.name"
        class="theme-dot"
        :class="{ active: store.currentTheme === t.name }"
        :style="{ background: t.color }"
        :title="t.title"
        @click="store.setTheme(t.name)"
      ></div>
    </div>

    <template v-if="auth.isLoggedIn && auth.user">
      <div
        class="user-profile"
        @mouseenter="onMouseEnter"
        @mouseleave="onMouseLeave"
      >
        <img
          class="avatar"
          :src="auth.user.avatar_url || defaultAvatar"
          alt="头像"
          @click.stop="router.push('/profile')"
        />
        <div class="user-label" @click.stop="router.push('/profile')">{{ auth.user.username }}</div>
      </div>
      <div v-if="showDropdown" class="user-dropdown" @mouseenter="onMouseEnter" @mouseleave="showDropdown = false">
        <div class="dropdown-item" @click="router.push('/profile'); showDropdown = false">个人中心</div>
        <div class="dropdown-item logout" @click="doLogout">退出登录</div>
      </div>
    </template>
    <div v-else class="user-profile" @click="$emit('openLogin')">
      <img class="avatar" :src="defaultAvatar" alt="头像" />
      <div class="user-label">登录 / 注册</div>
    </div>

    <div class="hamburger" :class="{ open: menuOpen }" @click="menuOpen = !menuOpen">
      <span></span>
      <span></span>
      <span></span>
    </div>
  </header>

  <Teleport to="body">
    <div v-if="menuOpen" class="mobile-menu-overlay" @click.self="menuOpen = false">
      <div class="mobile-menu">
        <div class="mobile-nav">
          <div
            v-for="item in navItems"
            :key="item.target"
            class="mobile-nav-item"
            :class="{ active: isActive(item.target) }"
            @click="router.push(item.path); menuOpen = false"
          >
            {{ item.label }}
          </div>
        </div>

        <div class="mobile-search">
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索图纸、系列..."
            @keydown.enter="doSearch(); menuOpen = false"
          />
        </div>

        <div class="mobile-theme">
          <span class="mobile-theme-label">主题切换</span>
          <div class="mobile-theme-dots">
            <div
              v-for="t in themes"
              :key="t.name"
              class="mobile-theme-dot"
              :class="{ active: store.currentTheme === t.name }"
              :style="{ background: t.color }"
              @click="store.setTheme(t.name)"
            >
              {{ t.title }}
            </div>
          </div>
        </div>

        <div v-if="!auth.isLoggedIn" class="mobile-login" @click="menuOpen = false; $emit('openLogin')">登录 / 注册</div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useThemeStore, type ThemeName } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import defaultAvatar from '@/assets/images/headpic/headpic1.png'

defineEmits<{ openLogin: [] }>()

const route = useRoute()
const router = useRouter()
const store = useThemeStore()
const auth = useAuthStore()

const searchKeyword = ref('')
const showDropdown = ref(false)
const menuOpen = ref(false)
let leaveTimer: ReturnType<typeof setTimeout> | null = null

function onMouseEnter() {
  if (leaveTimer) clearTimeout(leaveTimer)
  showDropdown.value = true
}

function onMouseLeave() {
  leaveTimer = setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

function doLogout() {
  auth.logout()
  showDropdown.value = false
  router.push('/')
}

function doSearch() {
  const kw = searchKeyword.value.trim()
  if (!kw) return
  router.push({ path: '/search', query: { keyword: kw } })
}

const navItems = [
  { label: '首页', target: 'home', path: '/' },
  { label: '工作台', target: 'workspace', path: '/workspace' },
  { label: '分类', target: 'gallery', path: '/gallery' },
  { label: '指南', target: 'guide', path: '/guide' },
]

const themes = [
  { name: 'blue' as ThemeName, color: '#A6DDF9', title: '海盐蓝 🌊' },
  { name: 'pink' as ThemeName, color: '#FEADCF', title: '樱花粉' },
  { name: 'purple' as ThemeName, color: '#D9B6FB', title: '香芋紫' },
]

function isActive(name: string) {
  if (name === 'home') return route.path === '/'
  return route.path.startsWith(`/${name}`)
}

watch(
  () => route.fullPath,
  () => {
    menuOpen.value = false
    showDropdown.value = false
  }
)
</script>

<style scoped>
.navbar {
  height: var(--header-height);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 0 40px;
  display: flex;
  align-items: center;
  position: fixed;
  top: 0;
  width: 100%;
  z-index: 1000;
  border-bottom: 1px solid var(--border-color);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
  min-width: 0;
}

.logo {
  height: 100px;
  width: auto;
  margin-right: 40px;
  cursor: pointer;
  user-select: none;
  object-fit: contain;
}

.nav-links {
  display: flex;
  gap: 8px;
  min-width: 0;
}

.nav-item {
  padding: 8px 18px;
  font-weight: bold;
  font-size: 15px;
  cursor: pointer;
  border-radius: 20px;
  transition: 0.2s;
  user-select: none;
}

.nav-item.active {
  background: var(--primary);
  color: white;
}

.nav-item:hover:not(.active) {
  background: var(--primary-light);
  color: var(--primary);
}

.header-search {
  margin-left: auto;
  margin-right: 20px;
  position: relative;
}

.header-search::before {
  content: "";
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  background: url("/search_icon.png") center / contain no-repeat;
  z-index: 1;
}

.header-search input {
  padding: 10px 20px 10px 35px;
  border-radius: 20px;
  border: none;
  background: var(--bg-color);
  width: 200px;
  font-weight: bold;
  outline: none;
  transition: 0.3s;
  color: var(--text-main);
}

.header-search input:focus {
  width: 260px;
  background: white;
  box-shadow: 0 0 0 2px var(--primary-light);
}

.theme-switcher {
  display: flex;
  gap: 8px;
  margin-right: 25px;
  background: var(--bg-color);
  padding: 5px 10px;
  border-radius: 20px;
  border: 1px solid var(--border-color);
  align-items: center;
}

.theme-label {
  font-size: 12px;
  font-weight: bold;
  color: var(--text-light);
}

.theme-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  border: 1px solid transparent;
}

.theme-dot.active {
  border-color: var(--text-light);
  transform: scale(1.1);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 12px 4px 4px;
  border-radius: 20px;
  background: white;
  border: 1px solid var(--border-color);
  position: relative;
  flex-shrink: 0;
}

.user-label {
  font-weight: bold;
  font-size: 13px;
}

.avatar {
  width: 32px; height: 32px; border-radius: 50%;
  object-fit: cover; display: block; user-select: none;
}

.user-dropdown {
  position: absolute;
  top: calc(var(--header-height) - 6px);
  right: 34px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
  padding: 6px 0;
  z-index: 1001;
  min-width: 130px;
}

.dropdown-item {
  padding: 10px 18px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  color: var(--text-main);
  transition: 0.15s;
}

.dropdown-item:hover {
  background: var(--bg-color);
}

.dropdown-item.logout {
  color:  var(--text-main);
}

.hamburger {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 28px;
  height: 28px;
  cursor: pointer;
  z-index: 1001;
  margin-left: 12px;
  flex-shrink: 0;
}
.hamburger span {
  display: block;
  width: 100%;
  height: 2.5px;
  background: var(--text-main);
  border-radius: 2px;
  transition: 0.3s;
}
.hamburger.open span:nth-child(1) {
  transform: translateY(7.5px) rotate(45deg);
}
.hamburger.open span:nth-child(2) {
  opacity: 0;
}
.hamburger.open span:nth-child(3) {
  transform: translateY(-7.5px) rotate(-45deg);
}

.mobile-menu-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 2000;
  display: flex;
  justify-content: flex-end;
}
.mobile-menu {
  width: 280px;
  max-width: 85vw;
  height: 100%;
  background: white;
  padding: 24px 20px;
  overflow-y: auto;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
  animation: slideIn 0.25s ease-out;
}
@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.mobile-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 24px;
}
.mobile-nav-item {
  padding: 14px 16px;
  font-weight: bold;
  font-size: 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: 0.2s;
}
.mobile-nav-item.active {
  background: var(--primary);
  color: white;
}
.mobile-nav-item:hover:not(.active) {
  background: var(--bg-color);
}

.mobile-search {
  margin-bottom: 24px;
}
.mobile-search input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--bg-color);
  font-weight: bold;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
}
.mobile-search input:focus {
  border-color: var(--primary);
}

.mobile-theme {
  margin-bottom: 24px;
}
.mobile-theme-label {
  font-size: 13px;
  font-weight: bold;
  color: var(--text-light);
  display: block;
  margin-bottom: 10px;
}
.mobile-theme-dots {
  display: flex;
  gap: 10px;
}
.mobile-theme-dot {
  flex: 1;
  padding: 10px;
  border-radius: 12px;
  text-align: center;
  font-size: 12px;
  font-weight: bold;
  cursor: pointer;
  border: 2px solid transparent;
  transition: 0.2s;
}
.mobile-theme-dot.active {
  border-color: var(--text-light);
}

.mobile-login {
  padding: 14px;
  text-align: center;
  font-weight: bold;
  font-size: 15px;
  background: var(--primary);
  color: white;
  border-radius: 12px;
  cursor: pointer;
  transition: 0.2s;
}
.mobile-login:hover {
  opacity: 0.9;
}

@media (max-width: 900px) {
  .navbar {
    padding: 0 20px;
    height: 70px;
  }
  .logo {
    height: 48px;
    margin-right: 15px;
  }
  .nav-links,
  .header-search,
  .theme-switcher {
    display: none;
  }
  .hamburger {
    display: flex;
  }
  .user-profile {
    margin-left: auto;
  }
  .user-label {
    display: none;
  }
  .user-profile {
    padding: 4px;
    background: transparent;
    border: none;
  }
}

@media (max-width: 360px) {
  .mobile-menu {
    width: 100%;
    max-width: 100vw;
  }
  .mobile-theme-dots {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .navbar {
    padding: 0 12px;
    height: 56px;
  }
  .logo {
    height: 38px;
    margin-right: 8px;
  }
}
</style>
