import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import Home from '@/views/Home.vue'
import Workspace from '@/views/Workspace.vue'
import Gallery from '@/views/Gallery.vue'
import Guide from '@/views/Guide.vue'
import Profile from '@/views/Profile.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: Home,
    meta: { title: '首页' },
  },
  {
    path: '/workspace',
    name: 'workspace',
    component: Workspace,
    meta: { title: '工作台' },
  },
  {
    path: '/pattern/:id',
    name: 'pattern-detail',
    component: () => import('@/views/PatternDetail.vue'),
    meta: { title: '图纸详情' },
  },
  {
    path: '/gallery',
    name: 'gallery',
    component: Gallery,
    meta: { title: '图鉴' },
  },
  {
    path: '/guide',
    name: 'guide',
    component: Guide,
    meta: { title: '新手指南' },
  },
  {
    path: '/profile',
    name: 'profile',
    component: Profile,
    meta: { title: '个人中心' },
  },
  {
    path: '/search',
    name: 'search',
    component: () => import('@/views/SearchResults.vue'),
    meta: { title: '搜索图纸' },
  },
  {
    path: '/admin/login',
    name: 'admin-login',
    component: () => import('@/views/AdminLogin.vue'),
    meta: { title: '管理员登录' },
  },
  {
    path: '/admin/upload',
    name: 'admin-upload',
    component: () => import('@/views/AdminUpload.vue'),
    meta: { title: '图纸上传' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  document.title = `${to.meta.title} - 拼豆` || '拼豆 - Piece a Bean'
})

export default router
