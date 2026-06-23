import { useState } from 'react'
import { getNatal, getNatalRaw, getAIInterpretation, BirthData, NatalResponse, AIResponse } from '../api'
import ChartWheel from './ChartWheel'
import InterpretationView from './InterpretationView'

export default function NatalPanel({ lang }: { lang: 'vi' | 'en' }) {
  const t = (vi: string, en: string) => lang === 'vi' ? vi : en
  const [name, setName] = useState('')
  const [year, setYear] = useState(new Date().getFullYear() - 25)
  const [month, setMonth] = useState(6)
  const [day, setDay] = useState(15)
  const [hour, setHour] = useState(12)
  const [minute, setMinute] = useState(0)
  const [lat, setLat] = useState(21.03)
  const [lng, setLng] = useState(105.85)
  const [tz, setTz] = useState(7)
  const [loading, setLoading] = useState(false)
  const [useAI, setUseAI] = useState(false)
  const [showEsoteric, setShowEsoteric] = useState(true)
  const [houseSystem, setHouseSystem] = useState('placidus')
  const [nodeType, setNodeType] = useState('mean')
  const [result, setResult] = useState<NatalResponse | null>(null)
  const [rawData, setRawData] = useState<any>(null)
  const [aiResult, setAIResult] = useState<AIResponse | null>(null)
  const [error, setError] = useState('')

  const getData = (): BirthData => ({
    name: name.trim(), year, month, day, hour, minute,
    latitude: lat, longitude: lng,
    timezone_str: `Etc/GMT${tz >= 0 ? '-' : '+'}${Math.abs(tz)}`,
    house_system: houseSystem,
    node_type: nodeType,
    lang,
    esoteric: showEsoteric,
  })

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) { setError(t('Vui lòng nhập họ tên.', 'Please enter your name.')); return }
    setLoading(true); setError(''); setResult(null); setRawData(null); setAIResult(null)
    try {
      const data = getData()
      const [interp, raw] = await Promise.all([getNatal(data), getNatalRaw(data)])
      setResult(interp)
      setRawData(raw)
      if (useAI) {
        const ai = await getAIInterpretation(data)
        setAIResult(ai)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || t('Lỗi kết nối đến máy chủ.', 'Connection error.'))
    } finally { setLoading(false) }
  }

  const planets = rawData?.planets
  const houses = rawData?.houses
  const aspects = rawData?.aspects
  const hasChart = planets && houses

  const LOCATIONS = [
    { label: '📍 Hà Nội, Việt Nam', lat: 21.03, lng: 105.85, tz: 7 },
    { label: '📍 TP. Hồ Chí Minh', lat: 10.82, lng: 106.63, tz: 7 },
    { label: '📍 Đà Nẵng', lat: 16.05, lng: 108.22, tz: 7 },
    { label: '📍 Hải Phòng', lat: 20.84, lng: 106.69, tz: 7 },
    { label: '📍 Cần Thơ', lat: 10.04, lng: 105.78, tz: 7 },
    { label: '📍 New York, USA', lat: 40.71, lng: -74.01, tz: -4 },
    { label: '📍 London, UK', lat: 51.51, lng: -0.13, tz: 1 },
    { label: '📍 Tokyo, Nhật Bản', lat: 35.68, lng: 139.69, tz: 9 },
    { label: '📍 Sydney, Úc', lat: -33.87, lng: 151.21, tz: 11 },
    { label: '📍 Paris, Pháp', lat: 48.86, lng: 2.35, tz: 2 },
    { label: '📍 Berlin, Đức', lat: 52.52, lng: 13.41, tz: 2 },
    { label: '📍 Seoul, Hàn Quốc', lat: 37.57, lng: 126.98, tz: 9 },
  ]

  const inputStyle: React.CSSProperties = { width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc', fontSize: 13, boxSizing: 'border-box' }
  const labelStyle: React.CSSProperties = { fontSize: 12, color: '#555', marginBottom: 2, display: 'block' }

  function applyLocation(e: React.ChangeEvent<HTMLSelectElement>) {
    const loc = LOCATIONS.find(l => l.label === e.target.value)
    if (loc) { setLat(loc.lat); setLng(loc.lng); setTz(loc.tz) }
  }

  const currentLoc = LOCATIONS.find(l => l.lat === lat && l.lng === lng && l.tz === tz)

  return (
    <div>
      <form onSubmit={handleSubmit} style={{ background: '#fff', padding: 20, borderRadius: 8, boxShadow: '0 1px 4px rgba(0,0,0,0.08)', marginBottom: 20 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
          <div style={{ gridColumn: 'span 3' }}>
            <label style={labelStyle}>{t('Họ Tên', 'Name')} *</label>
            <input value={name} onChange={e => setName(e.target.value)} placeholder={t('Nguyễn Văn A', 'John Doe')} style={inputStyle} />
          </div>
          <div><label style={labelStyle}>{t('Năm', 'Year')}</label><input type="number" value={year} onChange={e => setYear(+e.target.value)} style={inputStyle} /></div>
          <div><label style={labelStyle}>{t('Tháng', 'Month')}</label><input type="number" min={1} max={12} value={month} onChange={e => setMonth(+e.target.value)} style={inputStyle} /></div>
          <div><label style={labelStyle}>{t('Ngày', 'Day')}</label><input type="number" min={1} max={31} value={day} onChange={e => setDay(+e.target.value)} style={inputStyle} /></div>
          <div><label style={labelStyle}>{t('Giờ (0-23)', 'Hour (0-23)')}</label><input type="number" min={0} max={23} value={hour} onChange={e => setHour(+e.target.value)} style={inputStyle} /></div>
          <div><label style={labelStyle}>{t('Phút', 'Minute')}</label><input type="number" min={0} max={59} value={minute} onChange={e => setMinute(+e.target.value)} style={inputStyle} /></div>
          <div><label style={labelStyle}>{t('Múi Giờ (UTC+?)', 'Time Zone (UTC+?)')}</label><input type="number" value={tz} onChange={e => setTz(+e.target.value)} style={inputStyle} /></div>
          <div style={{ gridColumn: 'span 2' }}>
            <label style={labelStyle}>{t('🌍 Vị trí (chọn thành phố)', '🌍 Location (select city)')}</label>
            <select value={currentLoc?.label || ''} onChange={applyLocation} style={{ ...inputStyle, background: '#fff' }}>
              <option value="" disabled>{t('-- Chọn thành phố --', '-- Select city --')}</option>
              {LOCATIONS.map(l => <option key={l.label} value={l.label}>{l.label}</option>)}
            </select>
          </div>
          <div style={{ display: 'flex', gap: 6 }}>
            <div style={{ flex: 1 }}><label style={labelStyle}>{t('Vĩ Độ', 'Latitude')}</label><input type="number" step={0.01} value={lat} onChange={e => setLat(+e.target.value)} style={inputStyle} /></div>
            <div style={{ flex: 1 }}><label style={labelStyle}>{t('Kinh Độ', 'Longitude')}</label><input type="number" step={0.01} value={lng} onChange={e => setLng(+e.target.value)} style={inputStyle} /></div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 12 }}>
          <div style={{ flex: 0.35 }}>
            <label style={labelStyle}>{t('Hệ Thống Nhà', 'House System')}</label>
            <select value={houseSystem} onChange={e => setHouseSystem(e.target.value)} style={{ ...inputStyle, background: '#fff' }}>
              <option value="placidus">Placidus</option>
              <option value="koch">Koch</option>
              <option value="whole_sign">Whole Sign</option>
              <option value="equal">Equal</option>
              <option value="regiomontanus">Regiomontanus</option>
              <option value="campanus">Campanus</option>
              <option value="porphyry">Porphyry</option>
            </select>
          </div>
          <div style={{ flex: 0.25 }}>
            <label style={labelStyle}>{t('Nút', 'Node')}</label>
            <select value={nodeType} onChange={e => setNodeType(e.target.value)} style={{ ...inputStyle, background: '#fff' }}>
              <option value="mean">Mean</option>
              <option value="true">True</option>
            </select>
          </div>
          <label style={{ fontSize: 13, color: '#555', display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
            <input type="checkbox" checked={useAI} onChange={e => setUseAI(e.target.checked)} />
            {t('AI Luận giải mở rộng', 'Extended AI Reading')}
          </label>
          <label style={{ fontSize: 13, color: '#555', display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
            <input type="checkbox" checked={showEsoteric} onChange={e => setShowEsoteric(e.target.checked)} />
            {t('Chiêm tinh Nội môn', 'Esoteric Astrology')}
          </label>
          <button type="submit" disabled={loading} style={{ flex: 1, padding: 10, background: '#6b3a3a', color: '#fff', border: 'none', borderRadius: 6, fontSize: 14, cursor: 'pointer' }}>
            {loading ? t('Đang tính toán...', 'Calculating...') : t('Tra cứu Lá Số', 'View Chart')}
          </button>
        </div>
      </form>

      {error && <div style={{ background: '#fdd', padding: 12, borderRadius: 6, marginBottom: 16, fontSize: 13 }}>{error}</div>}

      {hasChart && <ChartWheel chartData={rawData} />}

      {result && <InterpretationView sections={result.interpretation} overall={result.overall} lang={lang} />}

      {aiResult && aiResult.success && (
        <div style={{ background: '#f0f4ff', borderRadius: 8, padding: 16, marginTop: 16, border: '1px solid #c4d4f0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <h3 style={{ margin: 0, fontSize: 15, color: '#2c3e50' }}>{t('AI Luận Giải Mở Rộng', 'Extended AI Reading')}</h3>
            <span style={{ fontSize: 10, color: '#888' }}>Model: {aiResult.model}</span>
          </div>
          <p style={{ whiteSpace: 'pre-wrap', color: '#333', lineHeight: 1.6, fontSize: 13 }}>{aiResult.text}</p>

          {aiResult.syntheses && aiResult.syntheses.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <h4 style={{ fontSize: 13, color: '#2c3e50', marginBottom: 8 }}>{t('Tổng Hợp Từng Hành Tinh', 'Per-Planet Synthesis')}</h4>
              {aiResult.syntheses.map((s: any) => (
                <div key={s.planet} style={{ marginBottom: 8, padding: 8, background: '#e8edf5', borderRadius: 6 }}>
                  <strong style={{ fontSize: 12, color: '#4a2c2a' }}>{s.planet_name}</strong>
                  <p style={{ margin: '4px 0 0', fontSize: 12, color: '#444', lineHeight: 1.5 }}>{s.text}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
