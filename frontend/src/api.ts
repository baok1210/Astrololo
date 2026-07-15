import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1' })

export interface BirthData {
  name: string; year: number; month: number; day: number
  hour: number; minute: number; latitude: number; longitude: number
  timezone_str?: string; house_system?: string; node_type?: string; lang?: string
  esoteric?: boolean
}

export interface NatalResponse {
  summary: any
  interpretation: SectionData[]
  overall: string
}

export interface SectionItem {
  title: string
  text: string
  score: number
  tags: string[]
  metadata?: Record<string, any>
}

export interface SectionData {
  category: string
  title: string
  items: SectionItem[]
}

export interface TransitResponse {
  natal: any
  transit: any & { interpretation?: { sections: SectionData[] } }
  transit_date: string
  transit_planets: any[]
  transit_aspects: any[]
  aspect_count: number
  transit_interpretation?: {
    overview: string
    sections: SectionData[]
    per_planet: any[]
  }
}

export interface SynastryResponse {
  person1: any
  person2: any
  composite?: any
  cross_aspects: any[]
  cross_aspect_count: number
  harmonious_aspects: number
  challenging_aspects: number
  compatibility_score: number
  compatibility_label: string
  compatibility_text?: string
  cross_interpretation?: SectionItem[]
  summary?: { vi: string; en: string }
}

export interface AISynthesis {
  planet: string
  planet_name: string
  text: string
}

export interface AIResponse {
  text: string
  model: string
  success: boolean
  error?: string
  syntheses?: AISynthesis[]
}

export interface ChartResponse {
  success: boolean
  data: any
}

export async function getNatal(data: BirthData): Promise<NatalResponse> {
  const res = await api.post('/interpret', { ...data, lang: data.lang || 'vi' })
  return res.data.data
}

export async function getNatalRaw(data: BirthData): Promise<any> {
  const res = await api.post('/natal', { ...data, lang: data.lang || 'vi' })
  return res.data.data
}

export async function getTransit(data: BirthData & { transit_year: number; transit_month: number; transit_day: number }): Promise<TransitResponse> {
  const res = await api.post('/transit', { ...data })
  return res.data.data
}

export async function getSynastry(p1: BirthData, p2: BirthData): Promise<SynastryResponse> {
  const body: any = {}
  for (const [k, v] of Object.entries(p1)) {
    if (k === 'timezone_str') body[`person1_timezone`] = v
    else body[`person1_${k}`] = v
  }
  for (const [k, v] of Object.entries(p2)) {
    if (k === 'timezone_str') body[`person2_timezone`] = v
    else body[`person2_${k}`] = v
  }
  body.house_system = p1.house_system || 'placidus'
  body.node_type = p1.node_type || 'mean'
  body.lang = p1.lang || 'vi'
  const res = await api.post('/synastry', body)
  return res.data.data
}

export async function getAIInterpretation(data: BirthData): Promise<AIResponse> {
  const res = await api.post('/interpret/ai', { ...data })
  return res.data.data
}

export async function getConstants(): Promise<any> {
  const res = await api.get('/constants')
  return res.data.data
}

export async function getHealth(): Promise<any> {
  const res = await api.get('/health')
  return res.data
}

export interface DailyResponse {
  daily: {
    date: string
    headline: string
    aspect_picks: {
      transit_planet: string
      transit_planet_label: string
      aspect: string
      to_natal_planet: string
      to_natal_sign: string
      orb?: number
      nature: string
    }[]
  }
}

export async function getDaily(data: BirthData): Promise<DailyResponse> {
  const res = await api.post('/daily', { ...data, lang: data.lang || 'vi' })
  return res.data.data
}

export interface CityGeo {
  name: string
  lat: number
  lng: number
  country: string
  tz: string
}

export async function geocodeCity(query: string): Promise<CityGeo[]> {
  // Free, no-key Nominatim (OpenStreetMap) geocoding.
  try {
    const url = `https://nominatim.openstreetmap.org/search?format=json&limit=6&accept-language=vi&q=${encodeURIComponent(query)}`
    const res = await fetch(url, { headers: { 'Accept': 'application/json' } })
    const arr = await res.json()
    return (arr || []).map((r: any) => ({
      name: r.display_name || r.name,
      lat: parseFloat(r.lat),
      lng: parseFloat(r.lon),
      country: (r.address && (r.address.country || r.address.city || '')) || '',
      tz: '',  // resolved client-side from lat/lng via Intl
    })).filter((c: CityGeo) => !isNaN(c.lat) && !isNaN(c.lng))
  } catch {
    return []
  }
}

export function tzFromCoords(lat: number, lng: number): string {
  // Approximate UTC offset from longitude: 15° per hour. Crude but avoids
  // depending on the browser's local tz, which may differ from the queried city.
  try {
    let off = Math.round(lng / 15)
    if (off > 12) off -= 24
    if (off < -12) off += 24
    return `Etc/GMT${off >= 0 ? '-' : '+'}${Math.abs(off)}`
  } catch {
    return 'UTC'
  }
}

