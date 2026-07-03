import api from './index'

export interface PaletteColor {
  color_no: string
  hex: string
  R: number
  G: number
  B: number
}

export interface PaletteResponse {
  artkal: PaletteColor[]
  hama: PaletteColor[]
  perler: PaletteColor[]
}

export type GridColor = string | null

export interface GenerateParams {
  file: File
  grid_size: number
  color_count: number
  algorithm: string
}

export interface GenerateResponse {
  task_id: string
  grid_data: GridColor[][]
  preview_base64: string
  width: number
  height: number
  beads_count: number
}

export async function fetchPalette(): Promise<PaletteResponse> {
  const { data } = await api.get<PaletteResponse>('/generator/palette')
  return data
}

export async function generatePattern(params: GenerateParams): Promise<GenerateResponse> {
  const form = new FormData()
  form.append('file', params.file)
  form.append('grid_size', String(params.grid_size))
  form.append('color_count', String(params.color_count))
  form.append('algorithm', params.algorithm)
  const { data } = await api.post<GenerateResponse>('/generator/generate', form)
  return data
}
