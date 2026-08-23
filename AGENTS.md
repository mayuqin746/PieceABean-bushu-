# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

拼豆 PieceABean — Perler bead pattern generator and sharing platform. Users upload an image, the app pixelates it and maps colors to real bead brand palettes (Artkal, Hama, Perler), producing a grid-based bead blueprint.

## Development Commands

### Backend (Python/FastAPI)

```bash
cd backend
# Install
pip install -r requirements.txt

# Run dev server
uvicorn app.main:app --reload --port 8000

# Run single test
pytest tests/ -k test_name

# Run all tests
pytest
```

### Frontend (Vue 3 / TypeScript / Vite)

```bash
cd frontend
# Install
npm install

# Dev server (default port 5173)
npm run dev

# Type-check + build
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

## Architecture

### Backend (`backend/`)

FastAPI app with SQLAlchemy ORM over MySQL/TiDB, JWT auth, and Pillow-based image processing.

```
backend/
├── app/
│   ├── main.py              # App factory, CORS (dynamic origins via BACKEND_CORS_ORIGINS), static file serving, route registration
│   ├── core/
│   │   ├── config.py        # Pydantic Settings: DB, JWT, CORS, file upload limits — reads from .env
│   │   ├── database.py      # SQLAlchemy engine/session — auto-detects TiDB for SSL, provides get_db() dependency
│   │   └── security.py      # bcrypt password hashing, JWT create/decode (python-jose)
│   ├── models/              # SQLAlchemy ORM models: User, Pattern, Favorite (M2M join), UserPattern, Rating
│   ├── schemas/             # Pydantic request/response schemas (PatternResponse prepends STATIC_BASE_URL)
│   ├── routers/
│   │   ├── users.py         # /api/v1/users: register, login, profile CRUD, favorites, saved patterns
│   │   ├── patterns.py      # /api/v1/patterns: gallery list/search (MySQL JSON_CONTAINS for color filter), detail, random, favorite toggle
│   │   ├── generator.py     # /api/v1/generator: image upload → RGBA/alpha preservation → BOX area grid sampling → nullable grid + base64 preview; optional API quantization remains available
│   │   ├── admin.py         # /api/v1/admin: thumbnail + blueprint upload (600×600 white-background compression)
│   │   ├── palette.py       # /api/v1/palette: serve brand palette JSON
│   │   └── ratings.py       # /api/v1/ratings: user-submitted 4-dimension ratings with aggregated stats
│   ├── palette/
│   │   ├── data.py          # ARTKAL_COLORS (224 entries from ColorNo-RGB-Brand.xlsx), HAMA_COLORS, PERLER_COLORS (empty placeholders)
│   │   └── utils.py         # Weighted RGB color distance (perceptual weights: 0.299R + 0.587G + 0.114B), closest-color finder
│   └── api/deps.py          # FastAPI dependencies: get_current_user (required JWT), get_optional_user
├── scripts/
│   └── import_patterns.py   # Batch import patterns from filesystem, with --watch mode for live folder scanning
└── .env.example             # Template for .env configuration
```

Key details:
- **Database**: MySQL/TiDB — DATABASE_URL env var overrides the `.env` config. TiDB connections auto-enable `ssl_mode=VERIFY_IDENTITY`.
- **Auth flow**: Register → bcrypt hash → login returns JWT → Bearer token on all authenticated requests. `get_optional_user` allows mixed public/authenticated views (e.g., gallery shows `is_favorited` only for logged-in users).
- **Current workspace pipeline**: Two-stage: (1) the frontend submits `color_count=0`, so the backend preserves RGBA transparency and samples the image to the requested grid with BOX area averaging; low-alpha cells are returned as `null`; (2) the frontend can clear edge-connected light backgrounds, apply a locked one-cell black/white/empty outline, strictly reduce the palette, remove isolated one/two-cell regions, and optionally map to a bead brand. The backend still exposes optional `ADAPTIVE`/mediancut/octree quantization for direct API callers, but the workspace does not execute it.
- **Image processing**: Generator endpoint is entirely in-memory (no disk writes). Admin upload persists thumbnails+blueprints to `D:\Desktop\pieceabean-data\patterns\` with UUID filenames.
- **Static file serving**: `/static/patterns/{subdir}/{filename}` serves from the local patterns directory. The `PatternResponse` schema prepends `STATIC_BASE_URL` to relative paths — update `STATIC_BASE_URL` when changing deployment URLs.

### Frontend (`frontend/`)

Vue 3 Composition API + TypeScript + Vite + Pinia + Vue Router.

```
frontend/src/
├── main.ts                 # App bootstrap: Vue → Pinia → Router → mount
├── App.vue                 # Root component with theme switching
├── router/index.ts         # Routes: Home, Workspace, PatternDetail, Gallery, Guide, Profile, Search, Admin
├── stores/
│   ├── auth.ts             # JWT token + user profile store (localStorage persistence)
│   └── theme.ts            # 3-theme toggle: blue (default), pink, purple — sets data-theme attribute
├── api/
│   ├── index.ts            # Axios instance with baseURL from VITE_API_BASE_URL, Bearer token interceptor
│   ├── generator.ts        # POST multipart upload for image→pattern generation, GET palette
│   ├── patterns.ts         # Gallery list/detail/random, favorite toggle
│   └── auth.ts             # Register, login, profile CRUD
├── composables/
│   └── useColorMapping.ts  # Client-side CIEDE2000-based color merging + optional brand mapping, producing mapped grid and color/bead statistics
├── components/common/      # Reusable components: GridPreview, GridDetailModal, ExportModal, BlindBoxModal, ColorBoxModal, FloatingPet, LoginModal, NavHeader
└── views/                  # Page-level components: Home, Workspace, Gallery, PatternDetail, Guide, Profile, SearchResults, AdminLogin, AdminUpload
```

Key details:
- **API base URL**: Set by `VITE_API_BASE_URL` env var. Dev default is `/api/v1` (Vite proxy). Production is `https://pieceabean-backend.onrender.com/api/v1` (see `.env.production`).
- **Color processing on frontend**: The workspace defaults to a strict 16-color budget including the locked outline color. `useColorMapping` merges colors using CIEDE2000 plus lightness/chroma/hue/saturation/color-family penalties, then removes configurable one/two-cell connected components by merging them into the strongest compatible neighbor. With strict mode disabled, merging may stop slightly above the target to avoid perceptually incompatible combinations. No-brand output uses `C1`, `C2`, ... labels; brand output uses palette color numbers and aggregated bead counts.
- **Static assets**: Banner images and decorative assets live in `src/assets/images/banner/` organized by theme color (blue/pink/purple). Public assets for the dist build are in `public/`.
- **Production deployment**: Frontend on Vercel, backend on Render. CORS allows `*.vercel.app` via regex.

## Environment Variables

### Backend (`.env`)
| Variable | Purpose |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | MySQL/TiDB connection |
| `DATABASE_URL` | Full connection string — overrides the above when set (used for TiDB) |
| `SECRET_KEY` | JWT signing key |
| `BACKEND_CORS_ORIGINS` | Comma-separated additional CORS origins |

### Frontend (`.env*`)
| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | Backend API base URL (default `/api/v1` for dev proxy) |
