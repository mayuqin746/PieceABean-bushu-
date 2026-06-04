<template>
  <div class="page-container">
    <!-- ========== 第一模块：快速上手（交互式步骤面板） ========== -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">快速上手</h2>
        <p class="section-subtitle">简单三步，把喜欢的一切变成拼豆画</p>
      </div>

      <div class="step-dashboard">
        <div class="step-controls">
          <button
            v-for="(item, i) in quickStartItems"
            :key="i"
            class="step-control-btn"
            :class="{ active: carouselIdx === i }"
            @click="carouselIdx = i; restartCarousel()"
          >
            <div class="step-num">0{{ i + 1 }}</div>
            <div class="step-btn-content">
              <span class="step-btn-title">{{ item.title }}</span>
              <span class="step-btn-desc">Step {{ i + 1 }} of 3</span>
            </div>
            <div class="step-progress-indicator" v-if="carouselIdx === i"></div>
          </button>
        </div>

        <div class="step-display-window">
          <div class="step-display-track" :style="{ transform: `translateY(-${carouselIdx * 100}%)` }">
            <div v-for="(item, i) in quickStartItems" :key="i" class="step-display-item">
              <div class="step-details-card">
                <h3 class="step-detail-title">
                  <span class="title-decor-dot"></span>
                  {{ item.title }}
                </h3>
                <ul class="step-detail-list">
                  <li v-for="(tip, j) in item.tips" :key="j">
                    <div class="step-list-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    </div>
                    <span class="step-list-text">{{ tip }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== 第二模块：核心功能详解（横向滑动卡片） ========== -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">核心功能详解</h2>
        <p class="section-subtitle">专为拼豆发烧友打造的数字工作台</p>
      </div>

      <div class="scroll-container">
        <button class="scroll-btn scroll-btn-left" @click="scrollCards(-1)" aria-label="Previous">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
          </svg>
        </button>

        <div class="scroll-viewport" ref="scrollViewport">
          <div class="scroll-wrapper" :style="{ transform: `translateX(-${scrollX}px)` }">
            <div v-for="(card, idx) in featureCards" :key="card.title" class="scroll-card card-hover">
              <div class="scroll-card-inner">
                <div class="scroll-card-decor"></div>
                <div class="scroll-card-icon-container" :class="'icon-theme-' + (idx % 4)">
                  <svg v-if="idx === 0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9.53 16.122l.75 1.5H13.25l.75-1.5H9.53zM12 2.25c-4.28 0-7.75 3.47-7.75 7.75 0 2.44 1.13 4.6 2.89 6a.75.75 0 01.26.57v2.68c0 .41.34.75.75.75h5.7c.41 0 .75-.34.75-.75v-2.68c0-.22.1-.43.26-.57 1.76-1.4 2.89-3.56 2.89-6 0-4.28-3.47-7.75-7.75-7.75z" />
                  </svg>
                  <svg v-else-if="idx === 1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 14.15v4.25c0 .96-.78 1.75-1.75 1.75H5.5c-.97 0-1.75-.79-1.75-1.75v-4.25m16.5 0c0-.96-.78-1.75-1.75-1.75H5.5c-.97 0-1.75.79-1.75 1.75m16.5 0V9.9c0-.96-.78-1.75-1.75-1.75H5.5c-.97 0-1.75.79-1.75 1.75v4.25" />
                  </svg>
                  <svg v-else-if="idx === 2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 13.5l3 3 6-6M20.25 12c0 4.556-3.694 8.25-8.25 8.25S3.75 16.556 3.75 12 7.444 3.75 12 3.75s8.25 3.694 8.25 8.25z" />
                  </svg>
                  <svg v-else-if="idx === 3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9.568 3H5.25A2.25 2.25 0 003 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581a1.5 1.5 0 002.122 0l4.318-4.318a1.5 1.5 0 000-2.122L11.16 3.659A2.25 2.25 0 009.568 3z" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </div>
                <h3 class="scroll-card-title">{{ card.title }}</h3>
                <p class="scroll-card-desc">{{ card.desc }}</p>
              </div>
            </div>
          </div>
        </div>

        <button class="scroll-btn scroll-btn-right" @click="scrollCards(1)" aria-label="Next">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
          </svg>
        </button>
      </div>
    </section>

    <!-- ========== 第三模块：常见问题 ========== -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">常见问题</h2>
        <p class="section-subtitle">解答您在图纸转换和制作过程中的各种疑惑</p>
      </div>

      <div class="faq-box">
        <p v-if="faqLoading" class="faq-loading">加载中...</p>
        <p v-else-if="faqList.length === 0" class="faq-empty">暂无常见问题</p>
        <details v-for="q in faqList" :key="q.id" class="faq-item">
          <summary class="faq-question">
            <span class="faq-q-text">{{ q.question }}</span>
            <div class="faq-btn-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
              </svg>
            </div>
          </summary>
          <div class="faq-answer-wrapper">
            <p class="faq-answer">{{ q.answer }}</p>
          </div>
        </details>
      </div>
    </section>

    <!-- ========== 第四模块：用户建议 & 反馈 ========== -->
    <section class="section">
      <div class="feedback-card-wrapper">
        <div class="feedback-info">
          <span class="feedback-badge">FEEDBACK</span>
          <h2 class="feedback-hero-title">你的声音，<br>是我们的创意燃料</h2>
          <p class="feedback-hero-desc">
            我是开发者，也是拼豆深度爱好者。欢迎提出任何好玩、有趣、或者不顺手的地方，让我们一起构建更好用的拼豆乐园。
          </p>
        </div>
        <div class="feedback-forms-grid">
          <div class="feedback-option-card hover-lift">
            <div class="feedback-option-header">
              <div class="feedback-option-icon feat-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                </svg>
              </div>
              <h3 class="feedback-option-title">新功能提案</h3>
            </div>
            <p class="feedback-option-desc">希望支持某种品牌的特殊色卡？想要批量拼贴排版功能？告诉我你的奇思妙想！</p>
            <button class="feedback-action-btn primary-action" @click="openSuggestionModal">提交新创意</button>
          </div>

          <div class="feedback-option-card hover-lift">
            <div class="feedback-option-header">
              <div class="feedback-option-icon bug-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
              </div>
              <h3 class="feedback-option-title">问题与故障反馈</h3>
            </div>
            <p class="feedback-option-desc">图纸转换颜色偏差太大？移动端排版显示不全？请附带设备情况，帮我们快速修正。</p>
            <button class="feedback-action-btn secondary-action" @click="openFeedbackModal">提交 Bug 反馈</button>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== 第五模块：你可能还想了解 ========== -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">你可能还想了解</h2>
      </div>
      <div class="link-grid">
        <div v-for="link in quickLinks" :key="link.label" class="link-card hover-lift" @click="openGuideModal(link.key)">
          <span class="link-card-label">{{ link.label }}</span>
          <span class="link-card-arrow">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12h15m0 0l-6.75-6.75M19.5 12l-6.75 6.75" />
            </svg>
          </span>
        </div>
      </div>
    </section>
  </div>

  <Teleport to="body">
    <div v-if="modalType" class="guide-modal-overlay" @click.self="modalType = null">
      <div class="guide-modal">
        <button class="gm-close" @click="modalType = null">✕</button>

        <template v-if="modalType === 'suggestion'">
          <h2>提交新创意</h2>
          <p class="gm-desc">告诉我们你的奇思妙想，一起让拼豆工具变得更好</p>
          <div v-if="suggestionSubmitted" class="rating-thanks">
            <span class="thanks-icon">💡</span>
            <p>感谢你的创意！我们会认真评估每一个提案。</p>
          </div>
          <div v-else class="suggestion-form">
            <div class="form-field">
              <label class="form-label">创意标题 <span class="required">*</span></label>
              <input
                v-model="suggestionForm.title"
                class="form-input"
                placeholder="给你的创意起个名字"
                maxlength="200"
              />
            </div>
            <div class="form-field">
              <label class="form-label">创意描述 <span class="required">*</span></label>
              <textarea
                v-model="suggestionForm.content"
                class="form-textarea"
                placeholder="详细描述你的想法，越具体越容易被采纳哦"
                rows="4"
              ></textarea>
            </div>
            <div class="form-field">
              <label class="form-label">联系方式 <span class="optional">(选填)</span></label>
              <input
                v-model="suggestionForm.contact"
                class="form-input"
                placeholder="邮箱或微信，方便我们进一步沟通"
                maxlength="200"
              />
            </div>
            <p v-if="suggestionError" class="rating-err">{{ suggestionError }}</p>
            <button class="rating-submit" :disabled="suggestionSubmitting" @click="submitSuggestionFn">
              {{ suggestionSubmitting ? '提交中...' : '提交创意' }}
            </button>
          </div>
        </template>

        <template v-if="modalType === 'feedback'">
          <h2>提交反馈</h2>
          <p class="gm-desc">遇到问题或有改进建议？请告诉我们</p>
          <div v-if="feedbackSubmitted" class="rating-thanks">
            <span class="thanks-icon">🙏</span>
            <p>感谢你的反馈！我们会尽快处理。</p>
          </div>
          <div v-else class="feedback-form">
            <div class="form-field">
              <label class="form-label">反馈类型 <span class="required">*</span></label>
              <select v-model="feedbackForm.type" class="form-select">
                <option value="bug">🐛 Bug 报告</option>
                <option value="suggestion">💡 功能建议</option>
                <option value="other">📋 其他</option>
              </select>
            </div>
            <div class="form-field">
              <label class="form-label">反馈内容 <span class="required">*</span></label>
              <textarea
                v-model="feedbackForm.content"
                class="form-textarea"
                placeholder="请详细描述你遇到的问题或建议，包括设备、浏览器等信息"
                rows="4"
              ></textarea>
            </div>
            <div class="form-field">
              <label class="form-label">联系方式 <span class="optional">(选填)</span></label>
              <input
                v-model="feedbackForm.contact"
                class="form-input"
                placeholder="邮箱或微信，方便我们跟进回复"
                maxlength="200"
              />
            </div>
            <p v-if="feedbackError" class="rating-err">{{ feedbackError }}</p>
            <button class="rating-submit" :disabled="feedbackSubmitting" @click="submitFeedbackFn">
              {{ feedbackSubmitting ? '提交中...' : '提交反馈' }}
            </button>
          </div>
        </template>

        <template v-if="modalType === 'versions'">
          <h2>版本日志</h2>
          <div class="version-list">
            <div v-for="v in versions" :key="v.ver" class="version-item">
              <span class="ver-tag">{{ v.ver }}</span>
              <span class="ver-date">{{ v.date }}</span>
              <ul class="ver-changes">
                <li v-for="c in v.changes" :key="c">{{ c }}</li>
              </ul>
            </div>
          </div>
        </template>

        <template v-if="modalType === 'community'">
          <h2>加入交流基地</h2>
          <p class="gm-desc">扫描下方二维码，加入全国拼豆爱好者交流群</p>
          <div class="qr-wrap">
            <img src="/qr-placeholder.png" alt="群聊二维码" class="qr-img" @error="onQrError" />
            <p v-if="qrError" class="qr-hint">请将二维码图片放置于 public/qr-placeholder.png</p>
          </div>
        </template>

        <template v-if="modalType === 'rating'">
          <h2>为本站打分</h2>
          <p class="gm-desc">你的反馈是我们改进的动力</p>
          <div v-if="ratingSubmitted" class="rating-thanks">
            <span class="thanks-icon">🎉</span>
            <p>感谢你的评价！</p>
          </div>
          <div v-else class="rating-form">
            <div v-for="q in ratingQuestions" :key="q.key" class="rating-row">
              <span class="rating-label">{{ q.label }}</span>
              <div class="stars">
                <span
                  v-for="n in 5"
                  :key="n"
                  class="star"
                  :class="{ filled: n <= ratingScores[q.key] }"
                  @click="ratingScores[q.key] = n"
                >★</span>
              </div>
            </div>
            <textarea v-model="ratingComment" class="rating-comment" placeholder="说点什么吧（选填）" rows="3"></textarea>
            <p v-if="ratingError" class="rating-err">{{ ratingError }}</p>
            <button class="rating-submit" :disabled="ratingSubmitting" @click="submitRating">
              {{ ratingSubmitting ? '提交中...' : '提交评价' }}
            </button>
          </div>
        </template>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, inject } from 'vue'
import api from '@/api/index'
import { submitSuggestion, submitFeedback, fetchFaqs } from '@/api/feedback'
import type { FeedbackType, FAQItem } from '@/api/feedback'
import { useAuthStore } from '@/stores/auth'

const carouselIdx = ref(0)
let carouselTimer: ReturnType<typeof setInterval> | null = null

const quickStartItems = [
  {
    title: '查找图纸',
    tips: [
      '使用顶部搜索框，输入名称、角色、风格快速检索图纸',
      '进入分类页面，按题材、难度、尺寸筛选海量素材',
      '支持模糊搜索，关键词不全也能匹配相关内容',
    ],
  },
  {
    title: '图片转拼豆图纸',
    tips: [
      '进入工作台，上传本地图片一键生成像素图纸',
      '可调整豆子尺寸、色彩数量、画面精细度',
      '实时预览效果，不满意可反复重新生成',
    ],
  },
  {
    title: '浏览与收藏保存',
    tips: [
      '点击图纸即可查看大图、色号明细与排版布局',
      '收藏心仪图纸，存入个人账号永久查看',
      '支持下载高清图纸，方便线下打印使用',
    ],
  },
]

function autoCarousel() {
  carouselTimer = setInterval(() => {
    carouselIdx.value = (carouselIdx.value + 1) % quickStartItems.length
  }, 6000)
}

function restartCarousel() {
  if (carouselTimer) clearInterval(carouselTimer)
  autoCarousel()
}

const scrollX = ref(0)
const scrollViewport = ref<HTMLElement | null>(null)
let cardWidth = 300

const featureCards = [
  { title: '智能拼豆生成器', desc: '支持 5mm 及 2.6mm 规格。独家色彩聚类算法，自动匹配各大常用拼豆品牌色卡。' },
  { title: '个人素材库云同步', desc: '支持多设备在线管理个人收藏。建立私有专属标签树，归类备份永不丢失。' },
  { title: '一键分享与高精度导出', desc: '支持 PDF 格式多页精准拼贴打印，以及超高分辨率矢量图、色号说明图打包导出。' },
  { title: '系统化素材分类', desc: '通过多重交叉标签（颗粒度、难度系数、画幅尺寸等），秒级定位最想制作的版块。' },
  { title: '全景像素预览机制', desc: '高仿真 3D 拼豆效果预渲染，无需上手，即可在网页端提前洞察作品在不同材质下的成色表现。' },
]

function getCardWidth() {
  const card = document.querySelector<HTMLElement>('.scroll-card')
  if (card) {
    cardWidth = card.offsetWidth + 24
  }
}

function scrollCards(dir: number) {
  getCardWidth()
  const maxScroll = scrollViewport.value
    ? scrollViewport.value.scrollWidth - scrollViewport.value.offsetWidth
    : 0
  scrollX.value = Math.min(Math.max(scrollX.value + dir * cardWidth, 0), Math.max(maxScroll, 0))
}

window.addEventListener('resize', () => {
  scrollX.value = 0
})

const faqList = ref<FAQItem[]>([])
const faqLoading = ref(false)

async function loadFaqs() {
  faqLoading.value = true
  try {
    faqList.value = await fetchFaqs()
  } catch {
    // 加载失败时保持空列表，页面不报错
  } finally {
    faqLoading.value = false
  }
}

const quickLinks = [
  { key: 'versions', label: '查看系统历史版本与更新日志' },
  { key: 'community', label: '加入全国玩家日常交流基地' },
  { key: 'rating', label: '写下反馈，为本站打个评测分' },
]

const auth = useAuthStore()
const openLogin = inject<() => void>('openLogin', () => {})

const modalType = ref<'versions' | 'community' | 'rating' | 'suggestion' | 'feedback' | null>(null)

function openGuideModal(key: string) {
  if (key === 'rating' && !auth.isLoggedIn) {
    openLogin()
    return
  }
  modalType.value = key as typeof modalType.value
}

const versions = [
  {
    ver: 'v1.0.0', date: '2025-05-27',
    changes: ['首发上线，支持图片转拼豆图纸', 'Artkal 224 色色板支持', '图鉴浏览与搜索功能', '用户注册/登录系统', '个人中心：我的作品、我的收藏'],
  },
]

const qrError = ref(false)
function onQrError() {
  qrError.value = true
}

const ratingQuestions = [
  { key: 'score_ui' as const, label: 'UI 设计' },
  { key: 'score_layout' as const, label: '页面布局' },
  { key: 'score_feature' as const, label: '功能完善度' },
  { key: 'score_ux' as const, label: '使用体验' },
]
const ratingScores = ref<Record<string, number>>({
  score_ui: 0,
  score_layout: 0,
  score_feature: 0,
  score_ux: 0,
})
const ratingComment = ref('')
const ratingSubmitting = ref(false)
const ratingSubmitted = ref(false)
const ratingError = ref('')

// ─── 创意建议 ─────────────────────────────────────────────────
const suggestionForm = ref({ title: '', content: '', contact: '' })
const suggestionSubmitting = ref(false)
const suggestionSubmitted = ref(false)
const suggestionError = ref('')

function openSuggestionModal() {
  suggestionForm.value = { title: '', content: '', contact: '' }
  suggestionSubmitted.value = false
  suggestionError.value = ''
  modalType.value = 'suggestion'
}

async function submitSuggestionFn() {
  if (!suggestionForm.value.title.trim() || !suggestionForm.value.content.trim()) {
    suggestionError.value = '请填写标题和描述'
    return
  }
  suggestionSubmitting.value = true
  suggestionError.value = ''
  try {
    await submitSuggestion({
      title: suggestionForm.value.title.trim(),
      content: suggestionForm.value.content.trim(),
      contact: suggestionForm.value.contact.trim() || undefined,
    })
    suggestionSubmitted.value = true
  } catch (e: any) {
    suggestionError.value = e?.response?.data?.detail ?? '提交失败，请重试'
  } finally {
    suggestionSubmitting.value = false
  }
}

// ─── 问题反馈 ─────────────────────────────────────────────────
const feedbackForm = ref({ type: 'bug' as FeedbackType, content: '', contact: '' })
const feedbackSubmitting = ref(false)
const feedbackSubmitted = ref(false)
const feedbackError = ref('')

function openFeedbackModal() {
  feedbackForm.value = { type: 'bug', content: '', contact: '' }
  feedbackSubmitted.value = false
  feedbackError.value = ''
  modalType.value = 'feedback'
}

async function submitFeedbackFn() {
  if (!feedbackForm.value.content.trim()) {
    feedbackError.value = '请填写反馈内容'
    return
  }
  feedbackSubmitting.value = true
  feedbackError.value = ''
  try {
    await submitFeedback({
      type: feedbackForm.value.type,
      content: feedbackForm.value.content.trim(),
      contact: feedbackForm.value.contact.trim() || undefined,
    })
    feedbackSubmitted.value = true
  } catch (e: any) {
    feedbackError.value = e?.response?.data?.detail ?? '提交失败，请重试'
  } finally {
    feedbackSubmitting.value = false
  }
}

async function submitRating() {
  const scores = ratingScores.value
  if (!scores.score_ui || !scores.score_layout || !scores.score_feature || !scores.score_ux) {
    ratingError.value = '请为所有项目打分'
    return
  }
  ratingSubmitting.value = true
  ratingError.value = ''
  try {
    await api.post('/ratings/', {
      score_ui: scores.score_ui,
      score_layout: scores.score_layout,
      score_feature: scores.score_feature,
      score_ux: scores.score_ux,
      comment: ratingComment.value || null,
    })
    ratingSubmitted.value = true
  } catch (e: any) {
    ratingError.value = e?.response?.data?.detail ?? '提交失败，请重试'
  } finally {
    ratingSubmitting.value = false
  }
}

onMounted(() => {
  autoCarousel()
  loadFaqs()
})

onUnmounted(() => {
  if (carouselTimer) clearInterval(carouselTimer)
})
</script>

<style scoped>
.page-container {
  max-width: 1040px;
  margin: 0 auto;
  padding: 60px 24px 100px;
}

.section {
  margin-bottom: 80px;
}

.section-header {
  text-align: center;
  margin-bottom: 40px;
}

.section-title {
  font-size: 26px;
  font-weight: 900;
  color: var(--text-main);
  margin: 0 0 10px 0;
  letter-spacing: -0.5px;
}

.section-subtitle {
  font-size: 15px;
  color: var(--text-light);
  margin: 0;
}

/* ===== 悬浮过渡 ===== */
.hover-lift {
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.hover-lift:hover {
  transform: translateY(-4px);
}

.card-hover {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s;
}
.card-hover:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 35px var(--primary-light);
}

/* ========== 第一模块：步骤面板 ========== */
.step-dashboard {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 32px;
  background: white;
  padding: 24px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
  border: 1px solid var(--border-color);
}

.step-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step-control-btn {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  background: transparent;
  text-align: left;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.step-control-btn:hover {
  background: var(--bg-color);
}

.step-control-btn.active {
  background: var(--primary-light);
  border-color: var(--primary);
}

.step-num {
  font-size: 20px;
  font-weight: 900;
  color: var(--text-light);
  font-family: ui-monospace, SFMono-Regular, monospace;
  transition: color 0.3s;
}
.step-control-btn.active .step-num {
  color: var(--theme-text-dark);
}

.step-btn-content {
  display: flex;
  flex-direction: column;
}

.step-btn-title {
  font-size: 15px;
  font-weight: 800;
  color: var(--text-main);
  margin-bottom: 2px;
}

.step-btn-desc {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.step-progress-indicator {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--primary);
  border-radius: 0 4px 4px 0;
}

.step-display-window {
  background: linear-gradient(135deg, #ffffff 0%, var(--primary-light-light) 100%);
  border-radius: var(--radius-md);
  padding: 40px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  position: relative;
  height: 280px;
}

.step-display-track {
  height: 100%;
  transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.step-display-item {
  height: 100%;
  display: flex;
  align-items: center;
}

.step-details-card {
  position: relative;
  width: 100%;
}

.step-detail-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 22px;
  font-weight: 900;
  color: var(--text-main);
  margin: 0 0 24px 0;
}

.title-decor-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary);
  box-shadow: 0 0 0 4px var(--primary-light);
}

.step-detail-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 16px;
}

.step-detail-list li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.step-list-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 6px;
  background: var(--primary);
  color: white;
  flex-shrink: 0;
  margin-top: 2px;
}

.step-list-icon svg {
  width: 12px;
  height: 12px;
}

.step-list-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-light);
}

/* ========== 第二模块：横向滚动卡片 ========== */
.scroll-container {
  position: relative;
  padding: 0 12px;
}

.scroll-viewport {
  overflow: hidden;
  padding: 16px 4px;
}

.scroll-wrapper {
  display: flex;
  gap: 24px;
  transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
  will-change: transform;
}

.scroll-card {
  flex: 0 0 calc(33.333% - 16px);
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
  border: 1px solid var(--border-color);
  min-width: 280px;
  overflow: hidden;
}

.scroll-card-inner {
  padding: 32px 28px;
  position: relative;
}

.scroll-card-decor {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--primary);
  opacity: 0;
  transition: opacity 0.3s;
}
.scroll-card:hover .scroll-card-decor {
  opacity: 1;
}

.scroll-card-icon-container {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  box-shadow: inset 0 -2px 4px rgba(0,0,0,0.03);
}

.scroll-card-icon-container svg {
  width: 24px;
  height: 24px;
}

.icon-theme-0 { background: var(--primary-light); color: var(--theme-text-dark); }
.icon-theme-1 { background: var(--primary-light-light); color: var(--theme-text-dark); }
.icon-theme-2 { background: var(--mood-bg); color: var(--theme-text-dark); }
.icon-theme-3 { background: var(--blindbox-bg); color: var(--theme-text-dark); }

.scroll-card-title {
  font-size: 16px;
  font-weight: 800;
  color: var(--text-main);
  margin: 0 0 10px 0;
}

.scroll-card-desc {
  font-size: 13px;
  color: var(--text-light);
  line-height: 1.65;
  margin: 0;
}

.scroll-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  background: white;
  cursor: pointer;
  color: var(--text-light);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-soft);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  padding: 0;
}
.scroll-btn svg {
  width: 18px;
  height: 18px;
}
.scroll-btn:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}
.scroll-btn-left { left: -16px; }
.scroll-btn-right { right: -16px; }

/* ========== 第三模块：常见问题 ========== */
.faq-box {
  background: white;
  border-radius: var(--radius-lg);
  padding: 16px;
  box-shadow: var(--shadow-soft);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.faq-loading, .faq-empty {
  text-align: center;
  padding: 32px 16px;
  font-size: 14px;
  color: var(--text-light);
}

.faq-item {
  border-radius: var(--radius-md);
  transition: background-color 0.3s, border-color 0.3s;
  border: 1px solid transparent;
}

.faq-item[open] {
  background: var(--bg-color);
  border-color: var(--border-color);
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 18px 24px;
  user-select: none;
  list-style: none;
  outline: none;
}
.faq-question::-webkit-details-marker {
  display: none;
}

.faq-q-text {
  font-size: 14.5px;
  font-weight: 800;
  color: var(--text-main);
}

.faq-btn-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--bg-color);
  color: var(--text-light);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  flex-shrink: 0;
}
.faq-btn-icon svg {
  width: 14px;
  height: 14px;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.faq-item:hover .faq-btn-icon {
  background: var(--primary-light);
  color: var(--theme-text-dark);
}
.faq-item[open] .faq-btn-icon {
  background: var(--primary);
  color: white;
}
.faq-item[open] .faq-btn-icon svg {
  transform: rotate(180deg);
}

.faq-answer-wrapper {
  overflow: hidden;
}

.faq-answer {
  padding: 0 24px 20px 48px;
  font-size: 13.5px;
  color: var(--text-light);
  line-height: 1.7;
  margin: 0;
  position: relative;
}

.faq-answer::before {
  content: "";
  position: absolute;
  left: 32px;
  top: 4px;
  bottom: 4px;
  width: 3px;
  background: var(--primary);
  border-radius: 99px;
  opacity: 0.6;
}

/* ========== 第四模块：反馈 ========== */
.feedback-card-wrapper {
  background: var(--primary-lig);
  border-radius: var(--radius-lg);
  padding: 48px;
  display: grid;
  grid-template-columns: 1fr 1.3fr;
  gap: 48px;
  align-items: center;
  box-shadow: var(--shadow-soft);
  position: relative;
  overflow: hidden;
}

.feedback-card-wrapper::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(255, 255, 255, 0.03) 1.5px, transparent 1.5px);
  background-size: 20px 20px;
  /* 降低透明度，减少干扰 */
  opacity: 0.3; 
  pointer-events: none;
}

.feedback-info {
  position: relative;
  z-index: 1;
}

.feedback-badge {
  display: inline-block;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1.5px;
  color: var(--text);
  background: rgba(255, 255, 255, 0.08);
  padding: 4px 12px;
  border-radius: 99px;
  margin-bottom: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.feedback-hero-title {
  font-size: 28px;
  font-weight: 900;
  color: var(--text);
  line-height: 1.3;
  margin: 0 0 16px 0;
  letter-spacing: -1px;
}

.feedback-hero-desc {
  font-size: 14px;
  /* 改为高对比度的半透明白色 */
  /* color: rgba(0, 0, 0, 0.9);  */
  color:var(--text);
  line-height: 1.6;
  margin: 0;
  /* 轻微阴影增强边缘清晰度 */
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1); 
  /* 提升字重 */
  font-weight: 500; 
}

.feedback-option-desc {
  font-size: 12px;
  /* 改为高对比度的半透明白色 */
  color:var(--text);
  /* color: rgba(255, 255, 255, 0.85);  */
  line-height: 1.6;
  margin: 0 0 20px 0;
  flex-grow: 1;
  /* 轻微阴影增强边缘清晰度 */
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.1); 
  /* 提升字重 */
  font-weight: 500; 
}

.feedback-forms-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  position: relative;
  z-index: 1;
}

.feedback-option-card {
  /* 提高背景不透明度，让卡片更“立”起来 */
  background: rgba(255, 255, 255, 0.3); 
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 24px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
}

.feedback-option-card:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.15);
}

.feedback-option-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.feedback-option-icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.feedback-option-icon svg {
  width: 16px;
  height: 16px;
}

.feat-icon { background: rgba(149, 215, 248, 0); color: var(--primary); }
.bug-icon { background: rgba(149, 215, 248, 0); color: var(--primary); }

.feedback-option-title {
  font-size: 14px;
  font-weight: 800;
  color: var(--text);
  margin: 0;
}

/* .feedback-option-desc {
  font-size: 12px;
  color: var(--primary-light);
  line-height: 1.6;
  margin: 0 0 20px 0;
  flex-grow: 1;
} */

.feedback-action-btn {
  width: 100%;
  padding: 10px 16px;
  border-radius: 10px;
  border: none;
  font-size: 12.5px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s;
}

.primary-action {
  background: rgba(255, 255, 255, 0.3);
  color: var(--text-main);
  font-weight: 800;
}
.primary-action:hover {
  opacity: 0.85;
}

.secondary-action {
  background: rgba(255, 255, 255, 0.5);
  color: var(--text);
  border: 1px solid rgba(255, 255, 255, 0.12);
}
.secondary-action:hover {
  background: rgba(255, 255, 255, 0.18);
  color: white;
}

/* ========== 第五模块：快速链接 ========== */
.link-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.link-card {
  background: white;
  border-radius: var(--radius-md);
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow-soft);
  border: 1px solid var(--border-color);
  text-decoration: none;
  cursor: pointer;
}

.link-card-label {
  font-size: 14px;
  font-weight: 800;
  color: var(--text-main);
  transition: color 0.3s;
}

.link-card-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--bg-color);
  color: var(--text-light);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  flex-shrink: 0;
}
.link-card-arrow svg {
  width: 14px;
  height: 14px;
}

.link-card:hover {
  border-color: var(--primary-light);
}
.link-card:hover .link-card-label {
  color: var(--theme-text-dark);
}
.link-card:hover .link-card-arrow {
  background: var(--primary);
  color: white;
  transform: translateX(4px);
}

/* ========== 响应式 ========== */
@media (max-width: 900px) {
  .step-dashboard {
    grid-template-columns: 1fr;
  }
  .step-display-window {
    height: auto;
    padding: 24px;
  }
  .step-display-track {
    transform: none !important;
  }
  .step-display-item {
    height: auto;
  }
  .scroll-card {
    flex: 0 0 calc(50% - 12px);
  }
  .feedback-card-wrapper {
    grid-template-columns: 1fr;
    padding: 32px;
  }
}

@media (max-width: 640px) {
  .page-container {
    padding: 30px 16px 60px;
  }
  .step-dashboard {
    padding: 16px;
  }
  .scroll-card {
    flex: 0 0 85%;
  }
  .scroll-btn {
    display: none;
  }
  .scroll-viewport {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .scroll-wrapper {
    transform: none !important;
  }
  .feedback-forms-grid {
    grid-template-columns: 1fr;
  }
  .link-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}

.guide-modal-overlay {
  position: fixed; inset: 0; z-index: 3000;
  background: rgba(0,0,0,0.4);
  display: flex; justify-content: center; align-items: center;
}
.guide-modal {
  background: white; border-radius: 16px; padding: 32px;
  max-width: 520px; width: 90vw; max-height: 80vh; overflow-y: auto;
  position: relative; box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}
.gm-close {
  position: absolute; top: 14px; right: 18px;
  width: 30px; height: 30px; border-radius: 50%;
  border: none; background: var(--bg-color); color: var(--text-light);
  font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.gm-close:hover { background: #e74c3c; color: white; }
.guide-modal h2 { font-size: 20px; font-weight: 900; margin: 0 0 16px; color: var(--text-main); }
.gm-desc { font-size: 14px; color: var(--text-light); margin-bottom: 20px; }

.version-list { display: flex; flex-direction: column; gap: 20px; }
.version-item { padding: 14px; background: var(--bg-color); border-radius: 10px; }
.ver-tag { font-weight: 900; font-size: 15px; color: var(--primary); margin-right: 12px; }
.ver-date { font-size: 12px; color: var(--text-light); }
.ver-changes { margin: 8px 0 0 18px; padding: 0; font-size: 13px; color: var(--text-light); line-height: 1.7; }

.qr-wrap { text-align: center; }
.qr-img { width: 200px; height: 200px; object-fit: contain; border-radius: 12px; border: 1px solid var(--border-color); }
.qr-hint { font-size: 13px; color: var(--text-light); margin-top: 12px; }

.rating-form { display: flex; flex-direction: column; gap: 16px; }
.rating-row { display: flex; align-items: center; justify-content: space-between; }
.rating-label { font-size: 14px; font-weight: 800; color: var(--text-main); }
.stars { display: flex; gap: 4px; }
.star { font-size: 24px; cursor: pointer; color: #ddd; transition: color 0.15s; user-select: none; }
.star:hover { color: #f1c40f; }
.star.filled { color: #f1c40f; }
.rating-comment {
  width: 100%; padding: 10px 12px; border: 1px solid var(--border-color);
  border-radius: 8px; font-size: 14px; outline: none; resize: vertical; font-family: inherit;
}
.rating-comment:focus { border-color: var(--primary); }
.rating-submit {
  padding: 12px; border: none; border-radius: 8px;
  background: var(--primary); color: #1e293b; font-size: 15px; font-weight: 900; cursor: pointer;
}
.rating-submit:disabled { opacity: 0.5; }
.rating-err { color: #e74c3c; font-size: 13px; text-align: center; }
.rating-thanks { text-align: center; padding: 30px 0; }
.thanks-icon { font-size: 48px; display: block; margin-bottom: 12px; }
.rating-thanks p { font-size: 16px; font-weight: 900; color: var(--text-main); }

/* ─── 表单弹窗通用样式 ─── */
.suggestion-form, .feedback-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  font-weight: 800;
  color: var(--text-main);
}

.required { color: #e74c3c; }
.optional { color: var(--text-light); font-weight: 500; }

.form-input, .form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  font-family: inherit;
  background: white;
  color: var(--text-main);
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-input:focus, .form-textarea:focus {
  border-color: var(--primary);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  font-family: inherit;
  background: white;
  color: var(--text-main);
  cursor: pointer;
  box-sizing: border-box;
}

.form-select:focus {
  border-color: var(--primary);
}
</style>
