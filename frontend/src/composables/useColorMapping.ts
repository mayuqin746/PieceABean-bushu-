import { ref, computed, watch } from 'vue'
import type { GridColor, PaletteColor, PaletteResponse } from '@/api/generator'

export interface MappedCell {
  hex: GridColor
  color_no: string | null
  text_color: 'black' | 'white'
}

export interface BrandStat {
  color_no: string
  hex: string
  count: number
}

export interface ColorProcessingOptions {
  targetColorCount: number
  strictColorLimit: boolean
  cleanupMaxRegionSize: number
  lockedColors?: string[]
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

function degToRad(deg: number): number {
  return deg * Math.PI / 180
}

function radToDeg(rad: number): number {
  return rad * 180 / Math.PI
}

function normalizeHue(deg: number): number {
  return (deg + 360) % 360
}

function deltaE2000(a: [number, number, number], b: [number, number, number]): number {
  const [l1, a1, b1] = a
  const [l2, a2, b2] = b
  const c1 = Math.sqrt(a1 ** 2 + b1 ** 2)
  const c2 = Math.sqrt(a2 ** 2 + b2 ** 2)
  const cAvg = (c1 + c2) / 2
  const cAvg7 = cAvg ** 7
  const g = 0.5 * (1 - Math.sqrt(cAvg7 / (cAvg7 + 25 ** 7)))
  const a1p = (1 + g) * a1
  const a2p = (1 + g) * a2
  const c1p = Math.sqrt(a1p ** 2 + b1 ** 2)
  const c2p = Math.sqrt(a2p ** 2 + b2 ** 2)
  const h1p = c1p === 0 ? 0 : normalizeHue(radToDeg(Math.atan2(b1, a1p)))
  const h2p = c2p === 0 ? 0 : normalizeHue(radToDeg(Math.atan2(b2, a2p)))
  const dLp = l2 - l1
  const dCp = c2p - c1p
  let dhp = h2p - h1p
  if (c1p * c2p === 0) {
    dhp = 0
  } else if (dhp > 180) {
    dhp -= 360
  } else if (dhp < -180) {
    dhp += 360
  }
  const dHp = 2 * Math.sqrt(c1p * c2p) * Math.sin(degToRad(dhp / 2))
  const lAvg = (l1 + l2) / 2
  const cAvgP = (c1p + c2p) / 2
  let hAvgP = h1p + h2p
  if (c1p * c2p === 0) {
    hAvgP = h1p + h2p
  } else if (Math.abs(h1p - h2p) > 180) {
    hAvgP = h1p + h2p < 360 ? (h1p + h2p + 360) / 2 : (h1p + h2p - 360) / 2
  } else {
    hAvgP = (h1p + h2p) / 2
  }
  const t =
    1 -
    0.17 * Math.cos(degToRad(hAvgP - 30)) +
    0.24 * Math.cos(degToRad(2 * hAvgP)) +
    0.32 * Math.cos(degToRad(3 * hAvgP + 6)) -
    0.20 * Math.cos(degToRad(4 * hAvgP - 63))
  const dTheta = 30 * Math.exp(-(((hAvgP - 275) / 25) ** 2))
  const rC = 2 * Math.sqrt((cAvgP ** 7) / (cAvgP ** 7 + 25 ** 7))
  const sL = 1 + (0.015 * ((lAvg - 50) ** 2)) / Math.sqrt(20 + ((lAvg - 50) ** 2))
  const sC = 1 + 0.045 * cAvgP
  const sH = 1 + 0.015 * cAvgP * t
  const rT = -Math.sin(degToRad(2 * dTheta)) * rC
  return Math.sqrt(
    (dLp / sL) ** 2 +
      (dCp / sC) ** 2 +
      (dHp / sH) ** 2 +
      rT * (dCp / sC) * (dHp / sH)
  )
}

function hueDistance(a: [number, number, number], b: [number, number, number]): number {
  const ha = normalizeHue(Math.atan2(a[2], a[1]) * 180 / Math.PI)
  const hb = normalizeHue(Math.atan2(b[2], b[1]) * 180 / Math.PI)
  const diff = Math.abs(ha - hb)
  return Math.min(diff, 360 - diff)
}

function rgbToHsl(r: number, g: number, b: number): [number, number, number] {
  const rn = r / 255
  const gn = g / 255
  const bn = b / 255
  const max = Math.max(rn, gn, bn)
  const min = Math.min(rn, gn, bn)
  const l = (max + min) / 2
  if (max === min) return [0, 0, l]
  const d = max - min
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
  let h = 0
  if (max === rn) h = (gn - bn) / d + (gn < bn ? 6 : 0)
  if (max === gn) h = (bn - rn) / d + 2
  if (max === bn) h = (rn - gn) / d + 4
  return [h * 60, s, l]
}

type ColorFamily =
  | 'white'
  | 'black'
  | 'gray'
  | 'dirty-green'
  | 'skin'
  | 'pink'
  | 'red'
  | 'orange'
  | 'yellow'
  | 'green'
  | 'cyan'
  | 'blue'
  | 'purple'
  | 'brown'
  | 'dark-hair'

interface ColorProfile {
  lab: [number, number, number]
  saturation: number
  chroma: number
  family: ColorFamily
}

const colorProfileCache = new Map<string, ColorProfile>()

function buildColorProfile(color: PaletteColor): ColorProfile {
  const lab = rgbToLab(color.R, color.G, color.B)
  const [hue, saturation] = rgbToHsl(color.R, color.G, color.B)
  const chroma = Math.sqrt(lab[1] ** 2 + lab[2] ** 2)
  const l = lab[0]
  const isWarm = hue >= 8 && hue <= 62
  const isPink = (hue >= 330 || hue <= 12) && saturation >= 0.16 && l >= 42
  const isSkin = isWarm && saturation >= 0.10 && saturation <= 0.58 && l >= 52 && l <= 92 && color.R >= color.B + 10
  const isDirtyGreen = hue >= 70 && hue <= 155 && saturation >= 0.08 && saturation <= 0.34 && l >= 28 && l <= 78

  let family: ColorFamily
  if (l >= 88 && saturation <= 0.18) family = 'white'
  else if (l <= 18) family = 'black'
  else if (l <= 34 && saturation <= 0.34 && color.R >= color.G - 8 && color.G >= color.B - 16) family = 'dark-hair'
  else if (isSkin) family = 'skin'
  else if (isPink) family = 'pink'
  else if (saturation <= 0.10 || chroma <= 8) family = 'gray'
  else if (isDirtyGreen) family = 'dirty-green'
  else if (hue < 12 || hue >= 345) family = 'red'
  else if (hue < 45) family = 'orange'
  else if (hue < 70) family = 'yellow'
  else if (hue < 165) family = 'green'
  else if (hue < 205) family = 'cyan'
  else if (hue < 270) family = 'blue'
  else if (hue < 330) family = 'purple'
  else family = 'brown'

  return { lab, saturation, chroma, family }
}

function getColorProfile(color: PaletteColor): ColorProfile {
  const key = color.hex || `${color.R},${color.G},${color.B}`
  const cached = colorProfileCache.get(key)
  if (cached) return cached
  const profile = buildColorProfile(color)
  colorProfileCache.set(key, profile)
  return profile
}

function profilesCompatible(a: ColorProfile, b: ColorProfile): boolean {
  if (a.family === b.family) return true
  const families = new Set([a.family, b.family])
  if (families.has('white')) return false
  if (families.has('black')) return a.lab[0] < 28 && b.lab[0] < 28
  if (families.has('skin')) return families.has('orange') || families.has('pink') || families.has('brown')
  if (families.has('pink')) return families.has('red') || families.has('purple') || families.has('skin')
  if (families.has('dirty-green')) return families.has('green') && Math.abs(a.lab[0] - b.lab[0]) <= 10
  if (families.has('gray')) return Math.max(a.saturation, b.saturation) <= 0.16 && Math.abs(a.lab[0] - b.lab[0]) <= 14
  if (families.has('dark-hair')) return families.has('brown') || families.has('black')
  return hueDistance(a.lab, b.lab) <= 28 && Math.abs(a.lab[0] - b.lab[0]) <= 16
}

function mergeCost(a: PaletteColor, b: PaletteColor): number {
  const profileA = getColorProfile(a)
  const profileB = getColorProfile(b)
  const dist = deltaE2000(profileA.lab, profileB.lab)
  const lightnessDiff = Math.abs(profileA.lab[0] - profileB.lab[0])
  const chromaDiff = Math.abs(profileA.chroma - profileB.chroma)
  const hueDiff = hueDistance(profileA.lab, profileB.lab)
  const huePenalty = Math.min(profileA.chroma, profileB.chroma) < 8 ? 0 : hueDiff * 0.14
  const saturationPenalty = Math.abs(profileA.saturation - profileB.saturation) * 8
  const familyPenalty = profilesCompatible(profileA, profileB) ? 0 : 34
  const grayGreenPenalty =
    [profileA.family, profileB.family].includes('dirty-green') &&
    [profileA.family, profileB.family].some(f => f === 'gray' || f === 'skin' || f === 'pink' || f === 'white')
      ? 28
      : 0
  return dist + lightnessDiff * 0.42 + chromaDiff * 0.08 + huePenalty + saturationPenalty + familyPenalty + grayGreenPenalty
}

function brandMappingCost(target: ColorProfile, candidate: ColorProfile): number {
  const base = deltaE2000(target.lab, candidate.lab)
  const lightnessDiff = Math.abs(target.lab[0] - candidate.lab[0])
  const hueDiff = hueDistance(target.lab, candidate.lab)
  const chromaDiff = Math.abs(target.chroma - candidate.chroma)
  let penalty = lightnessDiff * 0.22 + chromaDiff * 0.06

  if (target.chroma >= 12 && candidate.chroma >= 8) penalty += hueDiff * 0.10
  if (!profilesCompatible(target, candidate)) penalty += 18
  if (target.family === 'skin') {
    if (!['skin', 'orange', 'pink', 'brown'].includes(candidate.family)) penalty += 28
    if (candidate.family === 'dirty-green' || candidate.family === 'gray') penalty += 42
    if (candidate.lab[0] < target.lab[0] - 18) penalty += 12
  }
  if (target.family === 'pink') {
    if (!['pink', 'red', 'purple', 'skin'].includes(candidate.family)) penalty += 30
    if (candidate.family === 'gray' || candidate.family === 'dirty-green' || candidate.family === 'brown') penalty += 38
  }
  if (target.family === 'white') {
    if (candidate.family !== 'white' && candidate.family !== 'gray') penalty += 35
    if (candidate.lab[0] < 82) penalty += 20
    if (candidate.saturation > 0.20) penalty += 20
  }
  if (target.family === 'dark-hair' || target.family === 'black') {
    if (!['dark-hair', 'black', 'brown', 'gray'].includes(candidate.family)) penalty += 28
    if (candidate.family === 'green' || candidate.family === 'blue' || candidate.family === 'dirty-green') penalty += 30
  }
  if (target.family === 'dirty-green' && candidate.family !== 'dirty-green' && candidate.family !== 'green') {
    penalty += 16
  }
  if (target.family === 'gray' && candidate.saturation > 0.26) {
    penalty += 18
  }

  return base + penalty
}

function findClosest(targetHex: string, palette: PaletteColor[]): PaletteColor | null {
  if (palette.length === 0) return null
  const target = getColorProfile(paletteColorFromHex(targetHex))
  let best = palette[0]
  let bestDist = Infinity
  for (const c of palette) {
    const candidate = getColorProfile(c)
    const dist = brandMappingCost(target, candidate)
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

interface RawColorStat {
  key: string
  hex: string
  count: number
  color: PaletteColor
}

function maxAllowedMergeCost(targetCount: number): number {
  if (targetCount >= 32) return 8.5
  if (targetCount >= 24) return 10.5
  if (targetCount >= 16) return 13
  if (targetCount >= 12) return 15
  return 17
}

function paletteColorFromHex(hex: string, colorNo = hex): PaletteColor {
  const [R, G, B] = hexToRgb(hex)
  return {
    color_no: colorNo,
    hex,
    R,
    G,
    B,
  }
}

function buildRawColorStats(grid: GridColor[][]): Record<string, RawColorStat> {
  const stats: Record<string, RawColorStat> = {}
  for (const row of grid) {
    for (const hex of row) {
      if (!hex) continue
      if (!stats[hex]) {
        stats[hex] = {
          key: hex,
          hex,
          count: 0,
          color: paletteColorFromHex(hex),
        }
      }
      stats[hex].count++
    }
  }
  return stats
}

function buildRawSimilarityMergeMap(
  stats: Record<string, RawColorStat>,
  targetCount: number,
  strictLimit: boolean,
  lockedColors: Set<string>
): Record<string, string> {
  const colors = Object.values(stats).sort((a, b) => b.count - a.count)
  if (targetCount <= 0 || colors.length <= targetCount) {
    return Object.fromEntries(colors.map(c => [c.key, c.key]))
  }

  const maxSeeds = Math.min(colors.length, Math.max(targetCount * 8, 96))
  const lockedEntries = colors.filter(c => lockedColors.has(c.key))
  const unlockedEntries = colors.filter(c => !lockedColors.has(c.key))
  const seedEntries = [
    ...lockedEntries,
    ...unlockedEntries.slice(0, Math.max(0, maxSeeds - lockedEntries.length)),
  ]
  const seedKeys = new Set(seedEntries.map(c => c.key))
  const groups = seedEntries.map(c => ({
    representative: c.key,
    members: [c.key],
    count: c.count,
    locked: lockedColors.has(c.key),
  }))
  const colorByKey: Record<string, PaletteColor> = {}
  for (const c of colors) {
    colorByKey[c.key] = c.color
  }

  for (const color of colors.filter(c => !seedKeys.has(c.key))) {
    let bestGroup = groups[0]
    let bestCost = Infinity
    for (const group of groups) {
      const cost = mergeCost(color.color, colorByKey[group.representative])
      if (cost < bestCost) {
        bestCost = cost
        bestGroup = group
      }
    }
    bestGroup.members.push(color.key)
    bestGroup.count += color.count
  }

  const maxCost = maxAllowedMergeCost(targetCount)
  const lockedCount = lockedEntries.length
  const effectiveTarget = Math.max(targetCount, lockedCount)
  while (groups.length > effectiveTarget) {
    let bestI = -1
    let bestJ = -1
    let bestCost = Infinity

    for (let i = 0; i < groups.length; i++) {
      for (let j = i + 1; j < groups.length; j++) {
        if (groups[i].locked && groups[j].locked) continue
        const cost = mergeCost(colorByKey[groups[i].representative], colorByKey[groups[j].representative])
        if (cost < bestCost) {
          bestCost = cost
          bestI = i
          bestJ = j
        }
      }
    }

    if (bestI < 0 || bestJ < 0) break
    if (!strictLimit && bestCost > maxCost && groups.length <= effectiveTarget * 1.25) break

    const a = groups[bestI]
    const b = groups[bestJ]
    const keep = a.locked ? a : b.locked ? b : a.count >= b.count ? a : b
    const drop = keep === a ? b : a
    keep.members.push(...drop.members)
    keep.count += drop.count
    groups.splice(groups.indexOf(drop), 1)
  }

  const mergeMap: Record<string, string> = {}
  for (const group of groups) {
    for (const member of group.members) {
      mergeMap[member] = group.representative
    }
  }
  return mergeMap
}

function applyMergeMap(
  grid: GridColor[][],
  mergeMap: Record<string, string>
): GridColor[][] {
  return grid.map(row => row.map(hex => hex ? (mergeMap[hex] || hex) : null))
}

const REGION_NEIGHBORS = [
  [-1, 0],
  [1, 0],
  [0, -1],
  [0, 1],
] as const

function cleanupSmallRegions(
  grid: GridColor[][],
  maxRegionSize: number,
  lockedColors: Set<string>
): GridColor[][] {
  if (maxRegionSize <= 0 || grid.length === 0) return grid.map(row => [...row])

  const height = grid.length
  const width = grid[0]?.length || 0
  const visited = Array.from({ length: height }, () => Array(width).fill(false))
  const output = grid.map(row => [...row])

  for (let startY = 0; startY < height; startY++) {
    for (let startX = 0; startX < width; startX++) {
      const color = grid[startY][startX]
      if (!color || visited[startY][startX]) continue

      const component: [number, number][] = []
      const queue: [number, number][] = [[startX, startY]]
      visited[startY][startX] = true

      for (let index = 0; index < queue.length; index++) {
        const [x, y] = queue[index]
        component.push([x, y])
        for (const [dx, dy] of REGION_NEIGHBORS) {
          const nx = x + dx
          const ny = y + dy
          if (nx < 0 || nx >= width || ny < 0 || ny >= height) continue
          if (visited[ny][nx] || grid[ny][nx] !== color) continue
          visited[ny][nx] = true
          queue.push([nx, ny])
        }
      }

      if (component.length > maxRegionSize || lockedColors.has(color)) continue

      const neighborCounts = new Map<string, number>()
      for (const [x, y] of component) {
        for (const [dx, dy] of REGION_NEIGHBORS) {
          const nx = x + dx
          const ny = y + dy
          if (nx < 0 || nx >= width || ny < 0 || ny >= height) continue
          const neighbor = grid[ny][nx]
          if (!neighbor || neighbor === color) continue
          neighborCounts.set(neighbor, (neighborCounts.get(neighbor) || 0) + 1)
        }
      }
      if (neighborCounts.size === 0) continue

      const sourceColor = paletteColorFromHex(color)
      let replacement: string | null = null
      let bestBoundaryCount = -1
      let bestCost = Infinity
      for (const [candidate, boundaryCount] of neighborCounts) {
        const cost = mergeCost(sourceColor, paletteColorFromHex(candidate))
        if (
          boundaryCount > bestBoundaryCount ||
          (boundaryCount === bestBoundaryCount && cost < bestCost)
        ) {
          replacement = candidate
          bestBoundaryCount = boundaryCount
          bestCost = cost
        }
      }

      if (replacement) {
        for (const [x, y] of component) output[y][x] = replacement
      }
    }
  }

  return output
}

export function useColorMapping() {
  const selectedBrand = ref<string>('')
  const palette = ref<PaletteResponse>({
    artkal: [],
    hama: [],
    perler: [],
  })
  const gridData = ref<GridColor[][]>([])
  const processedGrid = ref<GridColor[][]>([])
  const mappedGrid = ref<MappedCell[][]>([])
  const brandStats = ref<BrandStat[]>([])
  const targetColorCount = ref(0)
  const strictColorLimit = ref(true)
  const cleanupMaxRegionSize = ref(1)
  const lockedColors = ref<Set<string>>(new Set())

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

  function setGridData(data: GridColor[][]) {
    gridData.value = data
    computeMapping()
  }

  function setProcessing(
    data: GridColor[][],
    options: ColorProcessingOptions
  ) {
    gridData.value = data
    targetColorCount.value = Math.max(0, Math.floor(options.targetColorCount || 0))
    strictColorLimit.value = options.strictColorLimit
    cleanupMaxRegionSize.value = Math.max(0, Math.min(2, Math.floor(options.cleanupMaxRegionSize || 0)))
    lockedColors.value = new Set(options.lockedColors || [])
    computeMapping()
  }

  function setBrand(brand: string) {
    selectedBrand.value = brand
  }

  function setTargetColorCount(count: number) {
    targetColorCount.value = Math.max(0, Math.floor(count || 0))
    computeMapping()
  }

  function computeMapping() {
    const gd = gridData.value
    const brandPalette = getPalette()
    console.log('[computeMapping] grid:', gd.length, 'rows, brandPalette:', brandPalette.length)

    if (gd.length === 0) {
      processedGrid.value = []
      mappedGrid.value = []
      brandStats.value = []
      return
    }

    const targetCount = targetColorCount.value
    const rawStats = buildRawColorStats(gd)
    const rawMergeMap = targetCount > 0
      ? buildRawSimilarityMergeMap(
          rawStats,
          targetCount,
          strictColorLimit.value,
          lockedColors.value
        )
      : Object.fromEntries(Object.keys(rawStats).map(key => [key, key]))
    const mergedGrid = applyMergeMap(gd, rawMergeMap)
    const cleanedGrid = cleanupSmallRegions(
      mergedGrid,
      cleanupMaxRegionSize.value,
      lockedColors.value
    )
    processedGrid.value = cleanedGrid
    const mergedRawStats: Record<string, { color_no: string; hex: string; count: number }> = {}

    for (const row of cleanedGrid) {
      for (const hex of row) {
        if (!hex) continue
        if (!mergedRawStats[hex]) {
          mergedRawStats[hex] = { color_no: hex, hex, count: 0 }
        }
        mergedRawStats[hex].count++
      }
    }

    if (brandPalette.length === 0) {
      const sortedRawStats = Object.values(mergedRawStats).sort((a, b) => b.count - a.count)
      const rawLabelByHex = Object.fromEntries(
        sortedRawStats.map((stat, index) => [stat.hex, `C${index + 1}`])
      )
      const rawGrid: MappedCell[][] = []
      for (let y = 0; y < cleanedGrid.length; y++) {
        const row: MappedCell[] = []
        for (let x = 0; x < cleanedGrid[y].length; x++) {
          const hex = cleanedGrid[y][x]
          if (!hex) {
            row.push({ hex: null, color_no: null, text_color: 'black' })
            continue
          }
          const rgb = hexToRgb(hex)
          const lum = luminance(rgb[0], rgb[1], rgb[2])
          row.push({
            hex,
            color_no: rawLabelByHex[hex] || null,
            text_color: lum > 128 ? 'black' : 'white',
          })
        }
        rawGrid.push(row)
      }
      mappedGrid.value = rawGrid
      brandStats.value = sortedRawStats.map(stat => ({
        color_no: rawLabelByHex[stat.hex],
        hex: stat.hex,
        count: stat.count,
      }))
      return
    }

    const paletteByNo = Object.fromEntries(brandPalette.map(c => [c.color_no, c]))
    const firstPassGrid: (PaletteColor | null)[][] = []
    const closestCache: Record<string, PaletteColor | null> = {}

    for (let y = 0; y < cleanedGrid.length; y++) {
      const row: (PaletteColor | null)[] = []
      for (let x = 0; x < cleanedGrid[y].length; x++) {
        const hex = cleanedGrid[y][x]
        if (!hex) {
          row.push(null)
          continue
        }
        if (!(hex in closestCache)) {
          closestCache[hex] = findClosest(hex, brandPalette)
        }
        const closest = closestCache[hex]
        row.push(closest)
      }
      firstPassGrid.push(row)
    }

    const statsMap: Record<string, { color_no: string; hex: string; count: number }> = {}
    const newGrid: MappedCell[][] = []

    for (let y = 0; y < cleanedGrid.length; y++) {
      const row: MappedCell[] = []
      for (let x = 0; x < cleanedGrid[y].length; x++) {
        const hex = cleanedGrid[y][x]
        if (!hex) {
          row.push({ hex: null, color_no: null, text_color: 'black' })
          continue
        }
        const firstPassColor = firstPassGrid[y][x]
        const closest = firstPassColor ? paletteByNo[firstPassColor.color_no] : null
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
    processedGrid,
    mappedGrid,
    brandStats,
    totalBeads,
    hasMapping,
    setPalette,
    setGridData,
    setProcessing,
    setBrand,
    setTargetColorCount,
  }
}
