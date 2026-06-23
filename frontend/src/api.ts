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
  cross_aspects: any[]
  cross_aspect_count: number
  harmonious_aspects: number
  challenging_aspects: number
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
