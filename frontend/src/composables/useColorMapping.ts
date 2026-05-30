import { ref, computed, watch } from 'vue'
import type { PaletteColor, PaletteResponse } from '@/api/generator'

export interface MappedCell {
  hex: string
  color_no: string | null
  text_color: 'black' | 'white'
}

export interface BrandStat {
  color_no: string
  hex: string
  count: number
}

function hexToRgb(hex: string): [number, number, number] {
  return [
    parseInt(hex.slice(1, 3), 16),
    parseInt(hex.slice(3, 5), 16),
    parseInt(hex.slice(5, 7), 16),
  ]
}

const XN = 0.95047
const YN = 1.00000
const ZN = 1.08883

function srgbToLinear(c: number): number {
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
}

function labF(t: number): number {
  const delta = 6 / 29
  return t > delta ** 3 ? t ** (1 / 3) : t / (3 * delta ** 2) + 4 / 29
}

function rgbToLab(r: number, g: number, b: number): [number, number, number] {
  const rLin = srgbToLinear(r / 255)
  const gLin = srgbToLinear(g / 255)
  const bLin = srgbToLinear(b / 255)

  const x = rLin * 0.4124564 + gLin * 0.3575761 + bLin * 0.1804375
  const y = rLin * 0.2126729 + gLin * 0.7151522 + bLin * 0.0721750
  const z = rLin * 0.0193339 + gLin * 0.1191920 + bLin * 0.9503041

  const fx = labF(x / XN)
  const fy = labF(y / YN)
  const fz = labF(z / ZN)

  return [
    116 * fy - 16,
    500 * (fx - fy),
    200 * (fy - fz),
  ]
}

function colorDistance(a: [number, number, number], b: [number, number, number]): number {
  return Math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)
}

function findClosest(targetHex: string, palette: PaletteColor[]): PaletteColor | null {
  if (palette.length === 0) return null
  const targetRgb = hexToRgb(targetHex)
  const targetLab = rgbToLab(targetRgb[0], targetRgb[1], targetRgb[2])
  let best = palette[0]
  let bestDist = Infinity
  for (const c of palette) {
    const candLab = rgbToLab(c.R, c.G, c.B)
    const dist = colorDistance(targetLab, candLab)
    if (dist < bestDist) {
      bestDist = dist
      best = c
    }
  }
  return best
}

function luminance(r: number, g: number, b: number): number {
  return 0.299 * r + 0.587 * g + 0.114 * b
}

export function useColorMapping() {
  const selectedBrand = ref<string>('')
  const palette = ref<PaletteResponse>({
    artkal: [],
    hama: [],
    perler: [],
  })
  const gridData = ref<string[][]>([])
  const mappedGrid = ref<MappedCell[][]>([])
  const brandStats = ref<BrandStat[]>([])

  const hasMapping = computed(() => brandStats.value.length > 0)

  const totalBeads = computed(() =>
    brandStats.value.reduce((sum, s) => sum + s.count, 0)
  )

  function getPalette(): PaletteColor[] {
    const key = selectedBrand.value as keyof PaletteResponse
    const result = palette.value[key] || []
    console.log('[getPalette] brand:', selectedBrand.value, 'key:', key, 'size:', result.length)
    return result
  }

  function setPalette(data: PaletteResponse) {
    palette.value = data
    console.log('[setPalette] palette artkal size:', data.artkal.length)
    computeMapping()
  }

  function setGridData(data: string[][]) {
    gridData.value = data
    computeMapping()
  }

  function setBrand(brand: string) {
    selectedBrand.value = brand
  }

  function computeMapping() {
    const gd = gridData.value
    const brandPalette = getPalette()
    console.log('[computeMapping] grid:', gd.length, 'rows, brandPalette:', brandPalette.length)

    if (gd.length === 0) {
      mappedGrid.value = []
      brandStats.value = []
      return
    }

    if (brandPalette.length === 0) {
      const rawGrid: MappedCell[][] = []
      for (let y = 0; y < gd.length; y++) {
        const row: MappedCell[] = []
        for (let x = 0; x < gd[y].length; x++) {
          row.push({ hex: gd[y][x], color_no: null, text_color: 'black' })
        }
        rawGrid.push(row)
      }
      mappedGrid.value = rawGrid
      brandStats.value = []
      return
    }

    const statsMap: Record<string, { color_no: string; hex: string; count: number }> = {}
    const newGrid: MappedCell[][] = []

    for (let y = 0; y < gd.length; y++) {
      const row: MappedCell[] = []
      for (let x = 0; x < gd[y].length; x++) {
        const hex = gd[y][x]
        const closest = brandPalette.length > 0 ? findClosest(hex, brandPalette) : null
        const displayHex = closest ? closest.hex : hex
        const rgb = hexToRgb(displayHex)
        const lum = luminance(rgb[0], rgb[1], rgb[2])
        const textColor: 'black' | 'white' = lum > 128 ? 'black' : 'white'
        const colorNo = closest ? closest.color_no : null

        row.push({ hex: displayHex, color_no: colorNo, text_color: textColor })

        if (colorNo) {
          if (!statsMap[colorNo]) {
            statsMap[colorNo] = { color_no: colorNo, hex: closest!.hex, count: 0 }
          }
          statsMap[colorNo].count++
        }
      }
      newGrid.push(row)
    }

    mappedGrid.value = newGrid
    brandStats.value = Object.values(statsMap).sort((a, b) => b.count - a.count)
  }

  watch(selectedBrand, (newVal) => {
    console.log('[watch] selectedBrand changed to:', newVal)
    computeMapping()
  })

  return {
    selectedBrand,
    palette,
    gridData,
    mappedGrid,
    brandStats,
    totalBeads,
    hasMapping,
    setPalette,
    setGridData,
    setBrand,
  }
}
