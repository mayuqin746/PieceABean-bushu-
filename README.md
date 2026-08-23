# 🧩 拼豆 PieceABean

**拼豆图纸在线生成与分享平台** —— 上传一张图片，自动生成像素化拼豆图纸，匹配真实品牌色板，一键导出施工蓝图。

---

## 📖 目录

- [项目简介](#-项目简介)
- [核心功能](#-核心功能)
- [技术架构](#-技术架构)
- [项目结构](#-项目结构)
- [数据模型](#-数据模型)
- [API 接口](#-api-接口)
- [颜色处理流程](#-颜色处理流程)
- [本地开发](#-本地开发)
- [部署](#-部署)
- [环境变量](#-环境变量)

---

## 🎯 项目简介

拼豆（Perler Bead / Hama Bead / Fuse Bead）是一种将彩色塑料珠排列在钉板上、加热融合成型的手工艺术。**PieceABean** 是一个全栈 Web 应用，让用户：

1. 上传任意图片
2. 自动像素化并降色到目标色数
3. 将每个像素匹配到真实品牌拼豆色板（Artkal / Hama / Perler）
4. 生成带色号标注的网格图纸
5. 统计每种颜色所需珠子数量
6. 分享、收藏、评价图纸

### 应用场景

- 🎨 手工爱好者制作拼豆图案
- 🖼️ 将照片、插画、Logo 转化为拼豆作品
- 📊 批量管理、浏览和分享图纸
- 🛍️ 按色号采购珠子（精确知道每种颜色需要多少颗）

---

## ✨ 核心功能

### 🧠 图片 → 拼豆图纸 引擎
| 功能 | 说明 |
|---|---|
| **像素网格化** | 后端使用 BOX 面积采样将上传图片缩放为目标网格，减少高反差边缘产生的额外过渡色；透明区域保留为空格 |
| **前端颜色归并** | 工作台默认严格限制为 16 色，可设 0 ~ 64 个目标颜色/色号；归并代价综合 CIEDE2000、明度、色度、色相和颜色族 |
| **拼豆结构优化** | 支持连通浅色背景留空、固定黑/白/留空轮廓，以及单格/双格孤立杂色清理 |
| **品牌色板映射** | 前端将归并后的颜色匹配到真实品牌色板，输出真实色号 + 十六进制色值；不选品牌时使用 `C1`、`C2`… 自定义编号 |
| **配色卡输出** | 精确统计每种颜色珠子需求量（按数量降序） |
| **预览图生成** | 工作台渲染最终映射网格；后端接口同时返回带网格边框的原始颜色 PNG（base64） |

### 👥 用户系统
- JWT 注册/登录（bcrypt 密码哈希）
- 个人中心：头像、简介编辑
- 收藏图纸（多对多关联）
- 在线保存生成的作品（UserPattern）

### 🖼️ 图纸图鉴
- 分类浏览（系列、主题分类）
- 模糊搜索（标题、描述）
- 按颜色筛选（JSON_CONTAINS 查询）
- 随机图纸（收藏暂存池机制）
- 图纸详情：网格预览 + 统计数据

### 🎲 趣味互动
- **盲盒抽图**：每日 3 次随机抽图纸（前端 localStorage 限流）
- **色彩占卜**：每日 3 次随机颜色抽签
- **浮动宠物**：页面角落的交互式吉祥物

### ⭐ 评分与反馈
- 四维度评分系统：UI 设计、布局体验、功能完整度、整体体验（1-5 分）
- 用户建议箱（Suggestion）
- 用户反馈通道（Feedback）：Bug 报告 / 建议 / 其他
- 常见问题 FAQ 系统

### 🛠️ 管理后台
- 管理员 JWT 登录
- 图纸上传：上传缩略图 + 蓝图，自动压缩为 600×600 白色背景 JPEG
- 元数据编辑（标题、分类、系列、描述、色板）

### 🎨 前端体验
- 三色主题切换（蓝色默认 / 粉色 / 紫色），CSS 变量驱动
- 沉浸式工作台（全屏无干扰布局）
- 响应式设计（桌面 + 平板 + 手机）
- 页面过渡动画（fade + translate）

---

## 🏗️ 技术架构

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend (Vercel)                      │
│  Vue 3 + TypeScript + Vite + Pinia + Vue Router + Axios  │
│  背景/轮廓/空间清理 + CIEDE2000 归并 + 色号映射             │
└──────────────────┬───────────────────────────────────────┘
                   │  HTTPS + Bearer JWT
                   ▼
┌──────────────────────────────────────────────────────────┐
│                  Backend (Render)                         │
│  Python 3 / FastAPI                                       │
│  Pillow 图片解码、透明蒙版保留、BOX 面积采样与原始预览        │
│  JWT 鉴权 (python-jose + bcrypt)                          │
└──────────────────┬───────────────────────────────────────┘
                   │  SQLAlchemy ORM
                   ▼
┌──────────────────────────────────────────────────────────┐
│              MySQL / TiDB 数据库                           │
│  8 张数据表：users, patterns, favorites, user_patterns,   │
│  ratings, suggestions, feedbacks, faqs                    │
└──────────────────────────────────────────────────────────┘
```

### 技术选型

| 层 | 技术 | 说明 |
|---|---|---|
| **前端框架** | Vue 3.4 (Composition API) | `<script setup>` + TypeScript |
| **构建工具** | Vite 5 | 开发热更新 + 生产构建 |
| **路由** | Vue Router 4 | History 模式，懒加载路由 |
| **状态管理** | Pinia 2 | auth store（JWT 持久化）、theme store（CSS 变量切换） |
| **HTTP 客户端** | Axios | 请求/响应拦截器，自动附加 Bearer Token |
| **后端框架** | FastAPI | 异步 Python，自动 OpenAPI 文档 |
| **ORM** | SQLAlchemy 2.0 | Declarative Mapped 模型 |
| **图片处理** | Pillow (PIL) | 图片解码、透明蒙版保留、BOX 面积采样；生成接口保留可选量化能力 |
| **颜色归并与映射** | TypeScript（浏览器端） | 固定轮廓、连通背景清理、小色块空间清理、严格颜色预算、CIEDE2000 归并和品牌映射 |
| **鉴权** | JWT (python-jose) | HS256 算法，1440 分钟过期 |
| **密码哈希** | bcrypt (passlib) | 注册时哈希，登录时验证 |
| **数据库** | MySQL / TiDB | 自动检测 TiDB → 启用 SSL VERIFY_IDENTITY |
| **部署** | Vercel (前端) + Render (后端) | CORS 支持 `*.vercel.app` |

---

## 📁 项目结构

```
PieceABean/
├── README.md                    # 项目文档（本文件）
├── CLAUDE.md                    # AI 助手指南
├── backend/
│   ├── requirements.txt         # Python 依赖
│   ├── .env.example             # 环境变量模板
│   ├── tests/                   # 测试用例
│   └── app/
│       ├── main.py              # 应用入口：FastAPI 工厂、CORS、路由注册、静态文件
│       ├── api/
│       │   └── deps.py          # FastAPI 依赖注入：get_current_user, get_optional_user
│       ├── core/
│       │   ├── config.py        # Pydantic Settings：DB/JWT/CORS/上传配置
│       │   ├── database.py      # SQLAlchemy 引擎/会话工厂（TiDB SSL 自动检测）
│       │   └── security.py      # bcrypt 密码哈希 + JWT 创建/解码
│       ├── models/
│       │   ├── user.py          # 用户表
│       │   ├── pattern.py       # 图纸表（含 JSON 色板字段）
│       │   ├── favorite.py      # 收藏关联表（M2M）
│       │   ├── user_pattern.py  # 用户保存的图纸
│       │   ├── rating.py        # 四维度评分表
│       │   ├── suggestion.py    # 用户建议
│       │   ├── feedback.py      # 用户反馈
│       │   └── faq.py           # FAQ 问答
│       ├── schemas/             # Pydantic 请求/响应模型
│       ├── routers/
│       │   ├── users.py         # /api/v1/users: 注册、登录、个人信息、收藏、保存图纸
│       │   ├── patterns.py      # /api/v1/patterns: 图鉴列表/搜索/筛选/详情/随机/收藏
│       │   ├── generator.py     # /api/v1/generator: 图片上传→透明蒙版→BOX 网格采样→网格+预览
│       │   ├── admin.py         # /api/v1/admin: 后台图纸上传（缩略图+蓝图）
│       │   ├── palette.py       # /api/v1/palette: 品牌色板数据
│       │   ├── ratings.py       # /api/v1/ratings: 用户评分提交+聚合统计
│       │   ├── suggestions.py   # /api/v1/suggestions: 用户建议
│       │   ├── feedbacks.py     # /api/v1/feedbacks: 用户反馈
│       │   └── faqs.py          # /api/v1/faqs: FAQ 列表
│       ├── palette/
│       │   ├── data.py          # ARTKAL_COLORS（224 色）、HAMA_COLORS、PERLER_COLORS
│       │   └── utils.py         # 加权 RGB 颜色距离 + 最近色查找
│       └── scripts/
│           └── import_patterns.py  # 批量导入图纸 + --watch 文件监控模式
│
└── frontend/
    ├── package.json             # Node 依赖
    ├── vite.config.ts           # Vite 配置（别名 @、代理 /api→后端）
    ├── vercel.json              # Vercel SPA 路由重写
    ├── tsconfig.json            # TypeScript 配置
    ├── .env.production          # 生产环境 API 地址
    ├── env.d.ts                 # 类型声明
    └── src/
        ├── main.ts              # 应用启动：Vue→Pinia→Router→挂载
        ├── App.vue              # 根组件：布局、主题切换、弹窗管理、盲盒/色盒逻辑
        ├── api/
        │   ├── index.ts         # Axios 实例（baseURL、Bearer Token 拦截器）
        │   ├── auth.ts          # 注册、登录、个人信息 CRUD
        │   ├── generator.ts     # 图片上传生成、色板获取
        │   └── patterns.ts      # 图鉴列表/详情/随机/收藏
        ├── stores/
        │   ├── auth.ts          # JWT + 用户信息（localStorage 持久化）
        │   └── theme.ts         # 三色主题切换（blue/pink/purple）
        ├── composables/
        │   └── useColorMapping.ts  # CIELAB 色彩空间映射引擎
        ├── components/
        │   └── common/          # GridPreview, GridDetailModal, ExportModal,
        │                        # BlindBoxModal, ColorBoxModal, FloatingPet,
        │                        # LoginModal, NavHeader
        ├── views/
        │   ├── Home.vue         # 首页
        │   ├── Workspace.vue    # 工作台（上传→生成→预览→导出）
        │   ├── Gallery.vue      # 图鉴浏览
        │   ├── PatternDetail.vue # 图纸详情
        │   ├── Guide.vue        # 新手指南
        │   ├── Profile.vue      # 个人中心
        │   ├── SearchResults.vue # 搜索结果
        │   ├── AdminLogin.vue   # 管理员登录
        │   └── AdminUpload.vue  # 图纸上传
        ├── router/
        │   └── index.ts         # 路由配置（9 条路由）
        └── assets/
            ├── styles/          # CSS 变量、基础样式
            └── images/banner/   # 主题化 Banner 图片（blue/pink/purple）
```

---

## 🗄️ 数据模型

### ER 关系图

```
┌──────────┐       ┌──────────────┐       ┌───────────┐
│   User   │──1:N──│   Pattern    │──M:N──│   User    │
│          │       │  (owner_id)  │       │ (favorites)│
│          │──1:N──│ UserPattern  │       └───────────┘
│          │──1:N──│   Rating     │
│          │──1:N──│  Suggestion  │
│          │──1:N──│  Feedback    │
└──────────┘       └──────────────┘
```

### 数据表详解

#### `users` — 用户
| 字段 | 类型 | 说明 |
|---|---|---|
| id | INT (PK) | 自增主键 |
| username | VARCHAR(50) UNIQUE | 用户名 |
| email | VARCHAR(120) UNIQUE | 邮箱 |
| hashed_password | VARCHAR(255) | bcrypt 哈希密码 |
| avatar_url | VARCHAR(512) | 头像 URL |
| bio | TEXT | 个人简介 |
| created_at | DATETIME | 注册时间 |

#### `patterns` — 图纸
| 字段 | 类型 | 说明 |
|---|---|---|
| id | INT (PK) | 自增主键 |
| title | VARCHAR(200) | 图纸标题 |
| description | TEXT | 描述 |
| category | VARCHAR(50) | 分类（索引） |
| series | VARCHAR(100) | 系列名 |
| colors | JSON | 色板数据（color_no → hex → count） |
| thumbnail_url | VARCHAR(512) | 缩略图路径 |
| blueprint_url | VARCHAR(512) | 蓝图路径 |
| grid_data | JSON | 网格数据 |
| width / height | INT | 网格尺寸 |
| beads_count | INT | 总珠子数 |
| views / likes | INT | 浏览/点赞数 |
| is_public | BOOL | 是否公开 |
| owner_id | FK → users.id | 作者 |

#### `favorites` — 收藏（多对多中间表）
| 字段 | 类型 | 说明 |
|---|---|---|
| user_id | FK → users.id | 用户 ID（联合主键） |
| pattern_id | FK → patterns.id | 图纸 ID（联合主键） |
| created_at | DATETIME | 收藏时间 |

#### `user_patterns` — 用户保存的图纸
| 字段 | 类型 | 说明 |
|---|---|---|
| id | INT (PK) | 自增主键 |
| user_id | FK → users.id | 所属用户 |
| title | VARCHAR(200) | 标题 |
| category | VARCHAR(50) | 分类 |
| colors | JSON | 色板 |
| grid_data | JSON | 网格数据 |
| width / height | INT | 尺寸 |
| beads_count | INT | 珠子总数 |

#### `ratings` — 评分
| 字段 | 类型 | 说明 |
|---|---|---|
| id | INT (PK) | 自增主键 |
| user_id | FK → users.id | 评分用户 |
| score_ui | INT | UI 设计分 |
| score_layout | INT | 布局体验分 |
| score_feature | INT | 功能完整度分 |
| score_ux | INT | 整体体验分 |
| comment | TEXT | 文字评价 |

#### `suggestions` — 建议
| 字段 | 类型 | 说明 |
|---|---|---|
| id | INT (PK) | 自增主键 |
| title | VARCHAR(200) | 建议标题 |
| content | TEXT | 建议内容 |
| contact | VARCHAR(200) | 联系方式 |

#### `feedbacks` — 反馈
| 字段 | 类型 | 说明 |
|---|---|---|
| id | INT (PK) | 自增主键 |
| type | VARCHAR(20) | 类型：bug / suggestion / other |
| content | TEXT | 反馈内容 |
| contact | VARCHAR(200) | 联系方式 |

#### `faqs` — 常见问题
| 字段 | 类型 | 说明 |
|---|---|---|
| id | INT (PK) | 自增主键 |
| question | VARCHAR(500) | 问题 |
| answer | TEXT | 答案 |
| sort_order | INT | 排序 |
| is_visible | BOOL | 是否展示 |

---

## 🌐 API 接口

### RESTful API 总览

所有接口前缀：`/api/v1`

#### 🔐 用户模块 `users`
| 方法 | 路径 | 认证 | 说明 |
|---|---|---|---|
| POST | `/users/register` | 无 | 注册 |
| POST | `/users/login` | 无 | 登录 → 返回 JWT |
| GET | `/users/me` | Bearer | 获取个人信息 |
| PUT | `/users/me` | Bearer | 更新个人信息 |
| GET | `/users/me/favorites` | Bearer | 我的收藏 |
| POST | `/users/me/favorites/{pattern_id}` | Bearer | 添加收藏 |
| DELETE | `/users/me/favorites/{pattern_id}` | Bearer | 取消收藏 |
| GET | `/users/me/patterns` | Bearer | 我保存的图纸 |
| POST | `/users/me/patterns` | Bearer | 保存图纸 |
| DELETE | `/users/me/patterns/{id}` | Bearer | 删除保存的图纸 |

#### 🖼️ 图纸模块 `patterns`
| 方法 | 路径 | 认证 | 说明 |
|---|---|---|---|
| GET | `/patterns` | 可选 | 图鉴列表（分页、搜索、分类筛选、颜色过滤） |
| GET | `/patterns/{id}` | 可选 | 图纸详情（含 is_favorited 状态） |
| GET | `/patterns/random` | 可选 | 随机一张图纸 |

#### 🛠️ 生成器 `generator`
| 方法 | 路径 | 认证 | 说明 |
|---|---|---|---|
| POST | `/generator/generate` | 无 | 上传图片 → 生成图纸（multipart/form-data） |
| GET | `/generator/palette` | 无 | 获取三大品牌色板数据 |

**`POST /generator/generate` 请求参数：**

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| file | File | 必填 | 图片文件（JPG/PNG/WebP/BMP） |
| grid_size | int | 29 | 最长边网格尺寸（10-200；工作台 UI 为 15-200） |
| color_count | int | 0 | 目标颜色数（0=不降色，最大64） |
| algorithm | string | "kmeans" | 量化算法：kmeans / mediancut / octree |

> 当前工作台固定提交 `color_count=0`，所以不会调用后端的三种量化实现；`algorithm` 仍提交为 `kmeans` 以满足接口参数，但此时不参与计算。后端量化能力仅供直接调用接口时选用。

**响应示例：**
```json
{
  "task_id": "a1b2c3d4e5f6...",
  "grid_data": [["#FF0000", "#00FF00"], ["#0000FF", "#FFFFFF"]],
  "preview_base64": "iVBORw0KGgo...",
  "width": 29,
  "height": 20,
  "beads_count": 580
}
```

#### 📊 评分模块 `ratings`
| 方法 | 路径 | 认证 | 说明 |
|---|---|---|---|
| POST | `/ratings` | Bearer | 提交评分 |
| GET | `/ratings/stats` | 无 | 获取聚合评分统计 |

#### 💡 建议与反馈
| 方法 | 路径 | 认证 | 说明 |
|---|---|---|---|
| POST | `/suggestions` | 无 | 提交建议 |
| POST | `/feedbacks` | 无 | 提交反馈 |
| GET | `/faqs` | 无 | 获取 FAQ 列表 |

#### 🔧 管理后台 `admin`
| 方法 | 路径 | 认证 | 说明 |
|---|---|---|---|
| POST | `/admin/login` | 无 | 管理员登录 |
| POST | `/admin/patterns` | Bearer (Admin) | 上传图纸（thumb + blueprint） |
| GET | `/admin/patterns` | Bearer (Admin) | 图纸列表管理 |

---

## 🎨 颜色处理流程

这是整个平台最核心的技术链路。当前工作台采用“后端网格采样 + 前端颜色归并与色板映射”的两阶段流程：

### 阶段一：后端 —— 图片 → 原始颜色网格

```
用户上传图片
    │
    ▼
[1] 格式处理：统一转换为 RGBA，保留透明蒙版
    │
    ▼
[2] 像素化：BOX 面积采样到目标网格尺寸（保持宽高比）
    └── 避免 LANCZOS 在黑色轮廓等高反差边缘产生振铃和额外过渡色
    │
    ▼
[3] 当前工作台提交 color_count=0：跳过后端颜色量化
    └── 直接调用 API 且 color_count > 0 时，仍可选：
        ├── Pillow Image.ADAPTIVE（参数名 kmeans）
        ├── Pillow MEDIANCUT
        └── Pillow FASTOCTREE
    │
    ▼
[4] 网格提取：有效像素 → #RRGGBB；低透明度像素 → null 空格
    │
    ▼
[5] 预览生成：绘制带 1px 灰色边框的棋盘格 PNG → base64 编码
    │
    ▼
[6] 返回：grid_data + preview_base64 + 元数据
```

### 阶段二：前端 —— 原始颜色网格 → 颜色归并 → 图纸

```
后端返回 grid_data（hex 色值网格）
    │
    ▼
[1] 背景与轮廓：
    ├── 可将与画布边缘连通的近白背景设为空格
    ├── 根据空格边界生成固定一格黑色/白色轮廓
    └── 也可选择透明/留空边缘或关闭轮廓
    │
    ▼
[2] 统计原始颜色及其格子数量；固定轮廓色加入锁定集合
    │
    ▼
[3] 若设置目标颜色数：
    ├── sRGB → 线性 RGB → CIEXYZ → CIELAB（D65）
    ├── 使用 CIEDE2000，并叠加明度、色度、色相、饱和度和颜色族惩罚
    ├── 优先保留高频代表色，迭代合并相近颜色
    └── 默认严格限制颜色总数，锁定轮廓不会被普通颜色吞并
    │
    ▼
[4] 空间清理：
    └── 按四邻域查找单格/双格孤立色块，合并到接触最多且色差最小的相邻区域
    │
    ▼
[5] 若未选择品牌色板：
    └── 使用归并后的代表色，按数量生成 C1、C2… 自定义编号
    │
    ▼
[6] 若选择品牌色板：
    ├── 对每个代表色计算 CIEDE2000
    ├── 叠加明度、色度、色相及颜色族兼容性惩罚
    └── 选择综合代价最低的品牌颜色 → 真实色号（如 "MF3"）
    │
    ▼
[7] 计算亮度 → 决定文字颜色（黑/白）确保可读性
    │
    ▼
[8] 输出：
    ├── mappedGrid[][]：{ hex, color_no, text_color }
    └── brandStats[]：{ color_no, hex, count } 按数量降序
```

工作台默认启用“严格限制颜色总数”，目标数量包含固定轮廓色。关闭严格限制后，算法会优先避免强行合并感知差异过大的颜色，因此最终颜色数可能略高于设定值。

### 品牌色板数据

| 品牌 | 颜色数量 | 数据来源 | 状态 |
|---|---|---|---|
| **Artkal** | 224 色 | ColorNo-RGB-Brand.xlsx | ✅ 可用 |
| **Hama** | 待补充 | — | ⏳ 空占位 |
| **Perler** | 待补充 | — | ⏳ 空占位 |

### 色差算法对比

| 算法 | 使用场景 | 精度 |
|---|---|---|
| **CIEDE2000 + 特征惩罚**（前端） | 相似色归并、最终色板匹配 | 高 —— 兼顾感知色差、明度、色度、色相和颜色族 |
| **加权 RGB 距离**（后端 util） | `palette/utils.py` 备用工具 | 较低 —— 0.299R + 0.587G + 0.114B |

---

## 🚀 本地开发

### 环境要求

- **Python** ≥ 3.10
- **Node.js** ≥ 18
- **MySQL** ≥ 5.7（或 TiDB）

### 1. 克隆仓库

```bash
git clone <repo-url>
cd PieceABean
```

### 2. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入数据库连接信息和 JWT 密钥

# 启动开发服务器（自动建表 + 热重载）
uvicorn app.main:app --reload --port 8000
```

API 文档自动生成：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173

开发模式下 Vite 自动将 `/api` 和 `/static` 请求代理到 `http://localhost:8000`。

### 4. 运行测试

```bash
# 后端测试
cd backend
pytest                              # 全部测试
pytest tests/ -k test_name          # 指定测试

# 前端类型检查 + 构建
cd frontend
npm run build                       # vue-tsc 类型检查 + vite build
npm run lint                        # ESLint 检查
```

---

## 📦 部署

### 前端：Vercel

```
Frontend (Vue SPA)
    │
    ├── 构建命令：npm run build
    ├── 输出目录：dist
    ├── SPA 路由：vercel.json rewrites /* → /index.html
    └── 环境变量：VITE_API_BASE_URL=https://pieceabean-backend.onrender.com/api/v1
```

### 后端：Render

```
Backend (FastAPI)
    │
    ├── 启动命令：uvicorn app.main:app --host 0.0.0.0 --port $PORT
    ├── 环境变量：DATABASE_URL（TiDB 连接字符串）、SECRET_KEY、BACKEND_CORS_ORIGINS
    └── CORS 配置：自动允许 *.vercel.app 域名
```

### CORS 策略

```python
# 允许的域名来源
origins = [
    "http://localhost:5173",       # 本地开发
    "http://127.0.0.1:5173",
]
# + BACKEND_CORS_ORIGINS 环境变量（逗号分隔的附加域名）

# 正则匹配所有 Vercel 预览部署
allow_origin_regex = r"https://.*\.vercel\.app"
```

---

## 🔧 环境变量

### 后端 `.env`

| 变量 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `DB_HOST` | str | localhost | 数据库主机 |
| `DB_PORT` | int | 3306 | 数据库端口 |
| `DB_USER` | str | root | 数据库用户 |
| `DB_PASSWORD` | str | — | 数据库密码 |
| `DB_NAME` | str | pieceabean | 数据库名称 |
| `DATABASE_URL` | str | — | 完整连接字符串（设置后覆盖上述五项，用于 TiDB） |
| `SECRET_KEY` | str | — | JWT 签名密钥（生产环境务必修改） |
| `ALGORITHM` | str | HS256 | JWT 签名算法 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | 1440 | Token 过期时间（分钟） |
| `APP_NAME` | str | 拼豆 PieceABean | 应用名称 |
| `DEBUG` | bool | true | 调试模式 |
| `BACKEND_CORS_ORIGINS` | str | — | 额外 CORS 域名（逗号分隔） |
| `STATIC_BASE_URL` | str | http://localhost:8000 | 静态文件基础 URL |
| `MAX_UPLOAD_SIZE_MB` | int | 10 | 上传文件大小限制（MB） |

### 前端 `.env*`

| 变量 | 文件 | 默认值 | 说明 |
|---|---|---|---|
| `VITE_API_BASE_URL` | `.env` | `/api/v1` | 开发模式 API 地址（Vite 代理） |
| `VITE_API_BASE_URL` | `.env.production` | `https://pieceabean-backend.onrender.com/api/v1` | 生产模式 API 地址 |

---

## 📄 许可证

待定

---

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

---

> 🧩 **拼豆 PieceABean** —— 让每一张图片都变成可以动手制作的拼豆艺术品
