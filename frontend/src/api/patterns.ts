import api from './index'

export interface PatternItem {
  id: number
  title: string
  description: string | null
  category: string
  series: string | null
  colors: string[] | null
  thumbnail_url: string | null
  blueprint_url: string | null
  width: number
  height: number
  beads_count: number
  views: number
  likes: number
  owner_id: number | null
  is_public: boolean
  is_favorited: boolean
  created_at: string
}

export interface PatternListResponse {
  total: number
  items: PatternItem[]
}

export async function fetchPatterns(params: {
  category?: string
  series?: string
  color?: string
  keyword?: string
  sort?: string
  page?: number
  page_size?: number
}) {
  const { data } = await api.get<PatternListResponse>('/patterns/', { params })
  return data
}

export async function fetchPatternDetail(id: number) {
  const { data } = await api.get<PatternItem>(`/patterns/${id}`)
  return data
}

export async function fetchRandomPattern(): Promise<PatternItem> {
  const { data } = await api.get<PatternItem>('/patterns/random')
  return data
}

export async function fetchCategories() {
  const { data } = await api.get<{ categories: string[] }>('/patterns/categories')
  return data.categories
}

export async function toggleFavorite(patternId: number) {
  const { data } = await api.post<{ favorited: boolean }>(`/patterns/${patternId}/favorite`)
  return data
}

export interface UserPatternItem {
  id: number
  user_id: number
  title: string
  category: string
  colors: string[] | null
  grid_data: string[][] | null
  width: number
  height: number
  beads_count: number
  created_at: string
}

export async function fetchMyPatterns(category?: string) {
  const params: Record<string, string> = {}
  if (category && category !== '全部') params.category = category
  const { data } = await api.get<UserPatternItem[]>('/users/me/patterns', { params })
  return data
}

export async function deleteUserPattern(id: number) {
  await api.delete(`/users/me/patterns/${id}`)
}

export async function fetchMyFavorites() {
  const { data } = await api.get<PatternItem[]>('/users/me/favorites')
  return data
}

export async function saveMyPattern(params: {
  title: string
  category: string
  colors: string[]
  grid_data: string[][]
  width: number
  height: number
  beads_count: number
}) {
  const { data } = await api.post<UserPatternItem>('/users/me/patterns', params)
  return data
}
