<template>
  <div class="page-container">
    <template v-if="!auth.isLoggedIn">
      <div class="login-prompt">
        <img :src="defaultAvatar" alt="头像" class="prompt-avatar" />
        <h2>登录后查看个人中心</h2>
        <p>登录即可管理你的作品和收藏</p>
        <button class="prompt-btn" @click="openLogin">登录 / 注册</button>
      </div>
    </template>

    <template v-else-if="profile">
      <div class="profile-header">
        <img class="p-avatar" :src="profile.avatar_url || defaultAvatar" alt="头像" />
        <div class="p-info">
          <template v-if="!editing">
            <h1>{{ profile.username }}</h1>
            <p class="p-bio">{{ profile.bio || '这个人很懒，什么都没写...' }}</p>
            <button class="edit-btn" @click="startEdit">编辑资料</button>
          </template>
          <template v-else>
            <input v-model="editForm.username" class="edit-input name-input" placeholder="用户名" />
            <input v-model="editForm.bio" class="edit-input bio-input" placeholder="个人简介" />
            <div class="edit-actions">
              <button class="save-btn" @click="doSave">保存</button>
              <button class="cancel-btn" @click="editing = false">取消</button>
            </div>
            <p v-if="editError" class="edit-error">{{ editError }}</p>
          </template>
        </div>
      </div>

      <div class="p-stats">
        <div class="stat-item"><span class="stat-num">{{ profile.patterns_count ?? 0 }}</span>作品</div>
        <div class="stat-item"><span class="stat-num">{{ profile.favorites_count ?? 0 }}</span>收藏</div>
      </div>

      <div class="p-tabs">
        <div
          v-for="tab in tabs"
          :key="tab.key"
          class="p-tab"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >{{ tab.label }}</div>
      </div>

      <div v-if="activeTab === 'creations'" class="cat-filter">
        <div
          v-for="c in categoryOptions"
          :key="c"
          class="cat-tag"
          :class="{ active: activeCategory === c }"
          @click="onCategoryChange(c)"
        >{{ c }}</div>
      </div>

      <div v-if="loading" class="loading-text">加载中...</div>

      <div v-else-if="displayItems.length === 0" class="empty-text">
        {{ activeTab === 'creations' ? '还没有创作过图纸' : '还没有收藏过图纸' }}
      </div>

      <div v-else class="gallery-grid">
        <div
          v-for="item in displayItems"
          :key="item.id"
          class="g-card"
          :class="{ clickable: 'thumbnail_url' in item }"
          @click="onCardClick(item)"
          @dblclick="onCardDblClick(item)"
        >
          <button
            v-if="activeTab === 'creations'"
            class="card-delete"
            title="删除"
            @click.stop="onDeletePattern(item as any)"
          >✕</button>
          <img
            v-if="'thumbnail_url' in item && (item as any).thumbnail_url"
            class="g-img"
            :src="(item as any).thumbnail_url"
            :alt="item.title"
          />
          <GridPreview
            v-else-if="(item as any).grid_data"
            :grid-data="(item as any).grid_data"
            :width="item.width"
            :height="item.height"
          />
          <div v-else class="g-img-placeholder">{{ item.title.charAt(0) }}</div>
          <div class="g-title">{{ item.title }}</div>
          <div class="g-meta">
            <span>{{ item.width }}x{{ item.height }}</span>
            <span v-if="'beads_count' in item">{{ (item as any).beads_count }} 颗</span>
            <span v-else>{{ (item as any).views }} 浏览</span>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="loading-text">加载中...</div>
  </div>

  <GridDetailModal
    v-if="detailPattern?.grid_data"
    :visible="true"
    :grid-data="detailPattern.grid_data"
    :width="detailPattern.width"
    :height="detailPattern.height"
    :title="detailPattern.title"
    :beads-count="detailPattern.beads_count"
    @close="detailPattern = null"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { fetchMyPatterns, fetchMyFavorites, deleteUserPattern, type PatternItem, type UserPatternItem } from '@/api/patterns'
import GridPreview from '@/components/common/GridPreview.vue'
import GridDetailModal from '@/components/common/GridDetailModal.vue'
import defaultAvatar from '@/assets/images/headpic/headpic1.png'

const openLogin = inject<() => void>('openLogin', () => {})
const router = useRouter()

const auth = useAuthStore()

const activeTab = ref<'creations' | 'favorites'>('creations')
const activeCategory = ref('全部')
const categoryOptions = ['全部', '动漫/IP', '萌宠动物', '美食饮品', '生活日常', '明星应援', '其他']
const creations = ref<UserPatternItem[]>([])
const favorites = ref<PatternItem[]>([])
const loading = ref(false)
const editing = ref(false)
const editForm = ref({ username: '', bio: '' })
const editError = ref('')
const detailPattern = ref<UserPatternItem | null>(null)

const profile = computed(() => auth.user)

const tabs = computed(() => [
  { key: 'creations' as const, label: `🎨 我的作品 (${creations.value.length})` },
  { key: 'favorites' as const, label: `❤️ 我的收藏 (${favorites.value.length})` },
])

const displayItems = computed(() => {
  return activeTab.value === 'creations' ? creations.value : favorites.value
})

function onCardClick(item: any) {
  if (item.thumbnail_url !== undefined) {
    router.push(`/pattern/${item.id}`)
  }
}

function onCardDblClick(item: any) {
  if (item.grid_data && item.grid_data.length) {
    detailPattern.value = item
  }
}

function onCategoryChange(c: string) {
  activeCategory.value = c
  loadCreations()
}

async function onDeletePattern(item: UserPatternItem) {
  if (!confirm(`确定删除「${item.title}」吗？此操作不可撤销。`)) return
  try {
    await deleteUserPattern(item.id)
    creations.value = creations.value.filter(p => p.id !== item.id)
  } catch {
    // ignore
  }
}

async function loadCreations() {
  try {
    creations.value = await fetchMyPatterns(activeCategory.value)
  } catch {
    // ignore
  }
}

async function loadData() {
  loading.value = true
  try {
    const [, f] = await Promise.all([loadCreations(), fetchMyFavorites()])
    favorites.value = f
  } catch {
    // ignore
  } finally {
    loading.value = false
  }
}

function startEdit() {
  editForm.value = {
    username: profile.value?.username ?? '',
    bio: profile.value?.bio ?? '',
  }
  editError.value = ''
  editing.value = true
}

async function doSave() {
  editError.value = ''
  try {
    await auth.updateProfile({
      username: editForm.value.username,
      bio: editForm.value.bio,
    })
    editing.value = false
  } catch (e: any) {
    editError.value = e?.response?.data?.detail ?? '保存失败'
  }
}

onMounted(() => {
  if (auth.isLoggedIn) {
    auth.fetchProfile()
    loadData()
  }
})
</script>

<style scoped>
.page-container { max-width: 900px; margin: 0 auto; padding-left: 20px; padding-right: 20px; }

.login-prompt {
  text-align: center; padding: 80px 20px;
  background: white; border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft); border: 1px solid var(--border-color);
}
.prompt-avatar { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; margin-bottom: 16px; }
.login-prompt h2 { font-weight: 900; margin-bottom: 8px; }
.login-prompt p { color: var(--text-light); margin-bottom: 20px; }
.prompt-btn { padding: 10px 32px; background: var(--primary); color: white; border: none; border-radius: 20px; font-size: 15px; font-weight: bold; cursor: pointer; }

.profile-header {
  display: flex; align-items: flex-start; gap: 20px; margin-bottom: 20px;
  background: white; padding: 30px; border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft); border: 1px solid var(--border-color);
}
.p-avatar { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; display: block; user-select: none; }
.p-info { flex: 1; }
.p-info h1 { font-weight: 900; margin-bottom: 5px; }
.p-bio { color: var(--text-light); font-size: 14px; margin-bottom: 10px; }
.edit-btn { padding: 5px 16px; background: var(--bg-color); border: 1px solid var(--border-color); border-radius: 14px; font-size: 13px; font-weight: bold; cursor: pointer; color: var(--text-light); }
.edit-btn:hover { background: var(--primary-light); color: var(--primary); }

.edit-input { display: block; width: 100%; padding: 8px 12px; border: 1px solid var(--border-color); border-radius: 8px; font-size: 15px; outline: none; margin-bottom: 8px; }
.edit-input:focus { border-color: var(--primary); }
.name-input { font-weight: 900; }
.bio-input { font-size: 14px; }
.edit-actions { display: flex; gap: 10px; margin-top: 4px; }
.save-btn { padding: 6px 18px; background: var(--primary); color: white; border: none; border-radius: 14px; font-size: 13px; font-weight: bold; cursor: pointer; }
.cancel-btn { padding: 6px 18px; background: var(--bg-color); border: 1px solid var(--border-color); border-radius: 14px; font-size: 13px; font-weight: bold; cursor: pointer; color: var(--text-light); }
.edit-error { color: #e74c3c; font-size: 13px; margin-top: 6px; }

.p-stats { display: flex; gap: 20px; margin-bottom: 25px; }
.stat-item { background: white; padding: 12px 24px; border-radius: var(--radius-md); box-shadow: var(--shadow-soft); font-size: 14px; color: var(--text-light); font-weight: bold; }
.stat-num { font-size: 22px; color: var(--primary); margin-right: 6px; font-weight: 900; }

.p-tabs { display: flex; gap: 25px; margin-bottom: 15px; border-bottom: 2px solid var(--border-color); }
.p-tab {
  padding: 10px 5px; font-weight: 900; font-size: 18px; cursor: pointer;
  color: var(--text-light); position: relative; user-select: none;
}
.p-tab.active { color: var(--text-main); }
.p-tab.active::after {
  content: ''; position: absolute; bottom: -2px; left: 0;
  width: 100%; height: 4px; background: var(--primary); border-radius: 2px;
}

.cat-filter { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
.cat-tag {
  padding: 6px 16px; border-radius: 16px;
  border: 1px solid var(--border-color); background: white;
  font-size: 13px; font-weight: bold; color: var(--text-light);
  cursor: pointer; user-select: none; transition: 0.2s;
}
.cat-tag:hover { border-color: var(--primary); color: var(--primary); }
.cat-tag.active { background: var(--primary); color: #1e293b; border-color: var(--primary); }

.loading-text { text-align: center; padding: 40px; color: var(--text-light); font-weight: bold; }
.empty-text { text-align: center; padding: 60px 20px; color: var(--text-light); font-size: 15px; }

.gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 25px; }
.g-card { background: white; border-radius: var(--radius-md); padding: 15px; box-shadow: var(--shadow-soft); transition: 0.3s; position: relative; }
.g-card.clickable { cursor: pointer; }
.g-card.clickable:hover { transform: translateY(-5px); }
.g-img { width: 100%; height: 160px; object-fit: cover; border-radius: 12px; margin-bottom: 12px; }
.g-img-placeholder { height: 160px; border-radius: 12px; display: flex; justify-content: center; align-items: center; font-size: 60px; font-weight: 900; background: var(--bg-color); color: var(--primary); margin-bottom: 12px; }
.g-title { font-weight: 900; font-size: 15px; margin-bottom: 5px; padding-right: 22px; }
.g-meta { font-size: 12px; color: var(--text-light); display: flex; justify-content: space-between; }

.card-delete {
  position: absolute; top: 10px; right: 10px; z-index: 10;
  width: 24px; height: 24px; border-radius: 50%;
  border: none; background: rgba(0,0,0,0.35); color: white;
  font-size: 12px; font-weight: bold; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity 0.2s;
}
.g-card:hover .card-delete { opacity: 1; }
.card-delete:hover { background: #e74c3c; }

@media (max-width: 768px) {
  .page-container { padding-left: 12px; padding-right: 12px; }
  .profile-header { flex-direction: column; align-items: center; text-align: center; padding: 20px; gap: 12px; }
  .p-avatar { width: 64px; height: 64px; }
  .p-info h1 { font-size: 20px; }
  .p-stats { justify-content: center; }
  .stat-item { padding: 10px 18px; }
  .stat-num { font-size: 18px; }
  .p-tabs { gap: 15px; }
  .p-tab { font-size: 15px; }
  .cat-filter { gap: 6px; }
  .cat-tag { padding: 5px 12px; font-size: 12px; }
  .gallery-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 14px; }
  .g-card { padding: 10px; }
  .g-title { font-size: 13px; }
}

@media (max-width: 480px) {
  .login-prompt { padding: 40px 16px; }
  .prompt-avatar { width: 60px; height: 60px; }
  .login-prompt h2 { font-size: 18px; }
  .p-tabs { gap: 10px; }
  .p-tab { font-size: 14px; }
  .edit-actions { flex-direction: column; }
  .gallery-grid { grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; }
  .g-card { padding: 8px; }
  .g-meta { font-size: 11px; flex-direction: column; gap: 2px; }
}
</style>
