import { useState } from 'react'
import { getNatal, getTransit, BirthData, NatalResponse, TransitResponse } from '../api'
import ChartWheel from './ChartWheel'
import AspectTable from './AspectTable'
import InterpretationView from './InterpretationView'

export default function TransitPanel({ lang }: { lang: 'vi' | 'en' }) {
  const t = (vi: string, en: string) => lang === 'vi' ? vi : en
  const [name, setName] = useState('')
  const [year, setYear] = useState(1990); const [month, setMonth] = useState(1); const [day, setDay] = useState(1)
  const [hour, setHour] = useState(12); const [minute, setMinute] = useState(0)
  const [lat, setLat] = useState(21.03); const [lng, setLng] = useState(105.85); const [tz, setTz] = useState(7)
  const [houseSystem, setHouseSystem] = useState('placidus')
  const [nodeType, setNodeType] = useState('mean')
  const [ty, setTy] = useState(new Date().getFullYear())
  const [tm, setTm] = useState(new Date().getMonth() + 1)
  const [td, setTd] = useState(new Date().getDate())
  const [loading, setLoading] = useState(false)
  const [showEsoteric, setShowEsoteric] = useState(true)
  const [result, setResult] = useState<TransitResponse | null>(null)
  const [natal, setNatal] = useState<any>(null)
  const [error, setError] = useState('')

  const getBase = (): BirthData => ({
    name, year, month, day, hour, minute, latitude: lat, longitude: lng,
    timezone_str: `Etc/GMT${tz >= 0 ? '-' : '+'}${Math.abs(tz)}`,
    house_system: houseSystem, node_type: nodeType, lang,
    esoteric: showEsoteric,
  })

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) { setError(t('Vui lòng nhập họ tên.', 'Please enter your name.')); return }
    setLoading(true); setError(''); setResult(null); setNatal(null)
    try {
      const base = getBase()
      const [nat, trans] = await Promise.all([
        getNatal(base),
        getTransit({ ...base, transit_year: ty, transit_month: tm, transit_day: td }),
      ])
      setNatal(nat)
      setResult(trans)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || t('Lỗi kết nối.', 'Connection error.'))
    } finally { setLoading(false) }
  }

  const LOCATIONS = [
    { label: '📍 Hà Nội, Việt Nam', lat: 21.03, lng: 105.85, tz: 7 },
    { label: '📍 TP. Hồ Chí Minh', lat: 10.82, lng: 106.63, tz: 7 },
    { label: '📍 Đà Nẵng', lat: 16.05, lng: 108.22, tz: 7 },
    { label: '📍 New York, USA', lat: 40.71, lng: -74.01, tz: -4 },
    { label: '📍 London, UK', lat: 51.51, lng: -0.13, tz: 1 },
    { label: '📍 Tokyo, Nhật Bản', lat: 35.68, lng: 139.69, tz: 9 },
    { label: '📍 Sydney, Úc', lat: -33.87, lng: 151.21, tz: 11 },
  ]

  const inputStyle: React.CSSProperties = { width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc', fontSize: 13, boxSizing: 'border-box' }
  const labelStyle: React.CSSProperties = { fontSize: 12, color: '#555', marginBottom: 2, display: 'block' }

  function applyLocation(e: React.ChangeEvent<HTMLSelectElement>) {
    const loc = LOCATIONS.find(l => l.label === e.target.value)
    if (loc) { setLat(loc.lat); setLng(loc.lng); setTz(loc.tz) }
  }
  const currentLoc = LOCATIONS.find(l => l.lat === lat && l.lng === lng && l.tz === tz)

  const transitChartData = result?.transit ? { planets: result.transit.planets, houses: result.transit.houses, ascendant: result.transit.ascendant } : null

  return (
    <div>
      <form onSubmit={handleSubmit} style={{ background: '#fff', padding: 20, borderRadius: 8, boxShadow: '0 1px 4px rgba(0,0,0,0.08)', marginBottom: 20 }}>
        <h4 style={{ margin: '0 0 12px', color: '#4a2c2a', fontSize: 14 }}>{t('Lá Số Gốc (Natal)', 'Birth Chart (Natal)')}</h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
          <div style={{ gridColumn: 'span 3' }}>
            <label style={labelStyle}>{t('Họ Tên', 'Name')}</label>
            <input value={name} onChange={e => setName(e.target.value)} placeholder={t('Nguyễn Văn A', 'John Doe')} style={inputStyle} />
          </div>
          <div><label style={labelStyle}>{t('Năm', 'Year')}</label><input type="number" value={year} onChange={e => setYear(+e.target.value)} style={inputStyle} /></div>
          <div><label style={labelStyle}>{t('Tháng', 'Month')}</label><input type="number" min={1} max={12} value={month} onChange={e => setMonth(+e.target.value)} style={inputStyle} /></div>
          <div><label style={labelStyle}>{t('Ngày', 'Day')}</label><input type="number" min={1} max={31} value={day} onChange={e => setDay(+e.target.value)} style={inputStyle} /></div>
          <div><label style={labelStyle}>{t('Giờ', 'Hour')}</label><input type="number" min={0} max={23} value={hour} onChange={e => setHour(+e.target.value)} style={inputStyle} /></div>
          <div><label style={labelStyle}>{t('Phút', 'Minute')}</label><input type="number" min={0} max={59} value={minute} onChange={e => setMinute(+e.target.value)} style={inputStyle} /></div>
          <div><label style={labelStyle}>{t('Múi Giờ', 'Time Zone')}</label><input type="number" value={tz} onChange={e => setTz(+e.target.value)} style={inputStyle} /></div>
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

        <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
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
          <div style={{ flex: 0.2 }}>
            <label style={labelStyle}>{t('Nút', 'Node')}</label>
            <select value={nodeType} onChange={e => setNodeType(e.target.value)} style={{ ...inputStyle, background: '#fff' }}>
              <option value="mean">Mean</option>
              <option value="true">True</option>
            </select>
          </div>
          <label style={{ fontSize: 13, color: '#555', display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer', marginTop: 18 }}>
            <input type="checkbox" checked={showEsoteric} onChange={e => setShowEsoteric(e.target.checked)} />
            {t('Chiêm tinh Nội môn', 'Esoteric Astrology')}
          </label>
        </div>

        <h4 style={{ margin: '16px 0 12px', color: '#4a2c2a', fontSize: 14 }}>{t('Ngày Quá Cảnh (Transit)', 'Transit Date')}</h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
          <div><label style={labelStyle}>{t('Năm', 'Year')}</label><input type="number" value={ty} onChange={e => setTy(+e.target.value)} style={inputStyle} /></div>
          <div><label style={labelStyle}>{t('Tháng', 'Month')}</label><input type="number" min={1} max={12} value={tm} onChange={e => setTm(+e.target.value)} style={inputStyle} /></div>
          <div><label style={labelStyle}>{t('Ngày', 'Day')}</label><input type="number" min={1} max={31} value={td} onChange={e => setTd(+e.target.value)} style={inputStyle} /></div>
        </div>

        <button type="submit" disabled={loading} style={{ width: '100%', marginTop: 12, padding: 10, background: '#6b3a3a', color: '#fff', border: 'none', borderRadius: 6, fontSize: 14, cursor: 'pointer' }}>
          {loading ? t('Đang tính toán...', 'Calculating...') : t('Xem Quá Cảnh', 'View Transits')}
        </button>
      </form>

      {error && <div style={{ background: '#fdd', padding: 12, borderRadius: 6, marginBottom: 16, fontSize: 13 }}>{error}</div>}

      {result && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
          {natal && <ChartWheel chartData={natal as any} />}
          {transitChartData && <ChartWheel chartData={transitChartData as any} />}
        </div>
      )}

      {result && (
        <div style={{ background: '#fff', padding: 16, borderRadius: 8, marginBottom: 16, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
          <h3 style={{ margin: '0 0 8px', fontSize: 15, color: '#4a2c2a' }}>{t('Quá Cảnh', 'Transits')} {result.transit_date}</h3>
          <p style={{ fontSize: 12, color: '#888' }}>{result.transit_planets?.length || 0} {t('hành tinh', 'planets')} · {result.aspect_count} {t('góc chiếu', 'aspects')}</p>

          {result.transit_planets && result.transit_planets.length > 0 && (
            <div style={{ marginTop: 12, overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                <thead>
                  <tr style={{ background: '#f5f0eb' }}>
                    <th style={thStyle}>{t('Hành Tinh', 'Planet')}</th>
                    <th style={thStyle}>{t('Cung', 'Sign')}</th>
                    <th style={thStyle}>{t('Vị Trí', 'Position')}</th>
                    <th style={thStyle}>{t('Nhà', 'House')}</th>
                    <th style={thStyle}>{t('Tốc Độ', 'Speed')}</th>
                  </tr>
                </thead>
                <tbody>
                  {result.transit_planets.map((p: any) => (
                    <tr key={p.name}>
                      <td style={tdStyle}>{lang === 'vi' ? p.name_vi : p.name_en} {p.is_retrograde ? '℞' : ''}</td>
                      <td style={tdStyle}>{lang === 'vi' ? p.sign_name_vi : p.sign_name_en}</td>
                      <td style={tdStyle}>{p.position_in_sign.toFixed(2)}°</td>
                      <td style={tdStyle}>{p.house || '—'}</td>
                      <td style={tdStyle}>{p.speed > 0 ? `${p.speed.toFixed(2)}°/d` : `${(-p.speed).toFixed(2)}°/d Rx`}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {(() => {
        const natalLikeSections = result?.transit?.interpretation?.sections || []
        const transitSections = (result as any)?.transit_interpretation?.sections || []
        const allSections = [...natalLikeSections, ...transitSections]
        if (allSections.length === 0) return null
        return (
          <InterpretationView
            sections={allSections}
            overall={result?.transit?.interpretation?.overall_interpretation}
          />
        )
      })()}

      {result?.transit_aspects && result.transit_aspects.length > 0 && (
        <AspectTable aspects={result.transit_aspects} title="Góc Chiếu Transit → Natal" />
      )}
    </div>
  )
}

const thStyle: React.CSSProperties = { padding: '6px 8px', textAlign: 'left', borderBottom: '2px solid #ddd', fontSize: 11, textTransform: 'uppercase', color: '#666' }
const tdStyle: React.CSSProperties = { padding: '6px 8px', borderBottom: '1px solid #eee' }
