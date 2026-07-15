import { useState } from 'react'
import { getSynastry, BirthData, SynastryResponse, SectionItem } from '../api'
import ChartWheel from './ChartWheel'
import AspectTable from './AspectTable'
import InterpretationView from './InterpretationView'

const LOCATIONS = [
  { label: '📍 Hà Nội, Việt Nam', lat: 21.03, lng: 105.85, tz: 7 },
  { label: '📍 TP. Hồ Chí Minh', lat: 10.82, lng: 106.63, tz: 7 },
  { label: '📍 Đà Nẵng', lat: 16.05, lng: 108.22, tz: 7 },
  { label: '📍 New York, USA', lat: 40.71, lng: -74.01, tz: -4 },
  { label: '📍 London, UK', lat: 51.51, lng: -0.13, tz: 1 },
  { label: '📍 Tokyo, Nhật Bản', lat: 35.68, lng: 139.69, tz: 9 },
  { label: '📍 Sydney, Úc', lat: -33.87, lng: 151.21, tz: 11 },
]

function PersonForm({ person, onChange, label, lang }: { person: any; onChange: (p: any) => void; label: string; lang: 'vi' | 'en' }) {
  const t = (vi: string, en: string) => lang === 'vi' ? vi : en
  const inputStyle: React.CSSProperties = { width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc', fontSize: 13, boxSizing: 'border-box' }
  const ls: React.CSSProperties = { fontSize: 12, color: '#555', marginBottom: 2, display: 'block' }
  function applyLocation(e: React.ChangeEvent<HTMLSelectElement>) {
    const loc = LOCATIONS.find(l => l.label === e.target.value)
    if (loc) { onChange({ ...person, lat: loc.lat, lng: loc.lng, tz: loc.tz }) }
  }
  const currentLoc = LOCATIONS.find(l => l.lat === person.lat && l.lng === person.lng && l.tz === person.tz)
  return (
    <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 16 }}>
      <h4 style={{ margin: '0 0 12px', color: '#6b3a3a', fontSize: 14 }}>{label}</h4>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
        <div style={{ gridColumn: 'span 2' }}><label style={ls}>{t('Họ Tên', 'Name')}</label><input value={person.name} onChange={e => onChange({ ...person, name: e.target.value })} style={inputStyle} /></div>
        <div><label style={ls}>{t('Năm', 'Year')}</label><input type="number" value={person.year} onChange={e => onChange({ ...person, year: +e.target.value })} style={inputStyle} /></div>
        <div><label style={ls}>{t('Tháng', 'Month')}</label><input type="number" min={1} max={12} value={person.month} onChange={e => onChange({ ...person, month: +e.target.value })} style={inputStyle} /></div>
        <div><label style={ls}>{t('Ngày', 'Day')}</label><input type="number" min={1} max={31} value={person.day} onChange={e => onChange({ ...person, day: +e.target.value })} style={inputStyle} /></div>
        <div><label style={ls}>{t('Giờ', 'Hour')}</label><input type="number" min={0} max={23} value={person.hour} onChange={e => onChange({ ...person, hour: +e.target.value })} style={inputStyle} /></div>
        <div><label style={ls}>{t('Phút', 'Minute')}</label><input type="number" min={0} max={59} value={person.minute} onChange={e => onChange({ ...person, minute: +e.target.value })} style={inputStyle} /></div>
        <div style={{ gridColumn: 'span 2' }}><label style={ls}>{t('🌍 Vị trí', '🌍 Location')}</label>
          <select value={currentLoc?.label || ''} onChange={applyLocation} style={{ ...inputStyle, background: '#fff' }}>
            <option value="" disabled>{t('-- Chọn thành phố --', '-- Select city --')}</option>
            {LOCATIONS.map(l => <option key={l.label} value={l.label}>{l.label}</option>)}
          </select>
        </div>
        <div><label style={ls}>{t('Vĩ Độ', 'Latitude')}</label><input type="number" step={0.01} value={person.lat} onChange={e => onChange({ ...person, lat: +e.target.value })} style={inputStyle} /></div>
        <div><label style={ls}>{t('Kinh Độ', 'Longitude')}</label><input type="number" step={0.01} value={person.lng} onChange={e => onChange({ ...person, lng: +e.target.value })} style={inputStyle} /></div>
        <div><label style={ls}>{t('Múi Giờ', 'Time Zone')}</label><input type="number" value={person.tz} onChange={e => onChange({ ...person, tz: +e.target.value })} style={inputStyle} /></div>
      </div>
    </div>
  )
}

function SynastryInterpretation({ items }: { items: any[] }) {
  if (!items || items.length === 0) return null
  return (
    <div style={{ marginBottom: 16 }}>
      {items.map((item, i) => (
        <div key={i} style={{ background: '#fff', padding: 12, borderRadius: 6, marginBottom: 8, border: '1px solid #e0d8d0' }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#4a2c2a', marginBottom: 4 }}>{item.title}</div>
          <div style={{ fontSize: 12, color: '#555', lineHeight: 1.5 }}>{item.text?.slice(0, 300)}</div>
        </div>
      ))}
    </div>
  )
}

export default function SynastryPanel({ lang }: { lang: 'vi' | 'en' }) {
  const t = (vi: string, en: string) => lang === 'vi' ? vi : en
  const [p1, setP1] = useState({ name: 'Người 1', year: 1990, month: 1, day: 1, hour: 12, minute: 0, lat: 21.03, lng: 105.85, tz: 7 })
  const [p2, setP2] = useState({ name: 'Người 2', year: 1992, month: 7, day: 20, hour: 14, minute: 30, lat: 10.82, lng: 106.63, tz: 7 })
  const [houseSystem, setHouseSystem] = useState('placidus')
  const [nodeType, setNodeType] = useState('mean')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<SynastryResponse | null>(null)
  const [error, setError] = useState('')
  const [tab, setTab] = useState<'overlap' | 'composite'>('overlap')

  function toBirthData(p: any): BirthData {
    return { name: p.name, year: p.year, month: p.month, day: p.day, hour: p.hour, minute: p.minute, latitude: p.lat, longitude: p.lng, timezone_str: `Etc/GMT${p.tz >= 0 ? '-' : '+'}${Math.abs(p.tz)}`, house_system: houseSystem, node_type: nodeType, lang }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!p1.name.trim() || !p2.name.trim()) { setError(t('Vui lòng nhập tên cả hai người.', 'Please enter both names.')); return }
    setLoading(true); setError(''); setResult(null)
    try {
      const res = await getSynastry(toBirthData(p1), toBirthData(p2))
      setResult(res)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || t('Lỗi kết nối.', 'Connection error.'))
    } finally { setLoading(false) }
  }

  const p1ChartRaw = result?.person1 ? { planets: result.person1.planets, houses: result.person1.houses, ascendant: result.person1.ascendant, aspects: [] } : null
  const p2ChartRaw = result?.person2 ? { planets: result.person2.planets, houses: result.person2.houses, ascendant: result.person2.ascendant, aspects: [] } : null

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
          <PersonForm person={p1} onChange={setP1} label={t('Người Thứ Nhất', 'Person 1')} lang={lang} />
          <PersonForm person={p2} onChange={setP2} label={t('Người Thứ Hai', 'Person 2')} lang={lang} />
        </div>

        <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
          <div style={{ flex: 0.35 }}>
            <label style={{ fontSize: 12, color: '#555', marginBottom: 2, display: 'block' }}>{t('Hệ Thống Nhà', 'House System')}</label>
            <select value={houseSystem} onChange={e => setHouseSystem(e.target.value)} style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc', fontSize: 13, background: '#fff' }}>
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
            <label style={{ fontSize: 12, color: '#555', marginBottom: 2, display: 'block' }}>{t('Nút', 'Node')}</label>
            <select value={nodeType} onChange={e => setNodeType(e.target.value)} style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc', fontSize: 13, background: '#fff' }}>
              <option value="mean">Mean</option>
              <option value="true">True</option>
            </select>
          </div>
        </div>

        <button type="submit" disabled={loading} style={{ width: '100%', padding: 10, background: '#6b3a3a', color: '#fff', border: 'none', borderRadius: 6, fontSize: 14, cursor: 'pointer', marginBottom: 20 }}>
          {loading ? t('Đang tính toán...', 'Calculating...') : t('Xem Tương Hợp', 'View Synastry')}
        </button>
      </form>

      {error && <div style={{ background: '#fdd', padding: 12, borderRadius: 6, marginBottom: 16, fontSize: 13 }}>{error}</div>}

      {result && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
            <div>
              <ChartWheel chartData={p1ChartRaw!} />
              {result.person1?.interpretation?.sections && (
                <InterpretationView sections={result.person1.interpretation.sections} lang={lang} />
              )}
            </div>
            <div>
              <ChartWheel chartData={p2ChartRaw!} />
              {result.person2?.interpretation?.sections && (
                <InterpretationView sections={result.person2.interpretation.sections} lang={lang} />
              )}
            </div>
          </div>

          <div style={{ background: '#fff', padding: 16, borderRadius: 8, marginBottom: 16, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
              <button onClick={() => setTab('overlap')} style={{ flex: 1, padding: 8, border: 'none', borderRadius: 6, fontSize: 13, cursor: 'pointer', background: tab === 'overlap' ? '#6b3a3a' : '#eee', color: tab === 'overlap' ? '#fff' : '#555' }}>{t('Góc Chiếu (Overlap)', 'Aspects (Overlap)')}</button>
              <button onClick={() => setTab('composite')} disabled={!result.composite} style={{ flex: 1, padding: 8, border: 'none', borderRadius: 6, fontSize: 13, cursor: 'pointer', background: tab === 'composite' ? '#6b3a3a' : '#eee', color: tab === 'composite' ? '#fff' : '#555', opacity: result.composite ? 1 : 0.5 }}>{t('Lá Số Chung (Composite)', 'Composite Chart')}</button>
            </div>
            {tab === 'overlap' ? (
              <div>
                <h3 style={{ margin: '0 0 4px', fontSize: 15, color: '#4a2c2a' }}>{t('Tổng Quan Tương Hợp', 'Synastry Overview')}</h3>
                {result.compatibility_score !== undefined && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '8px 0' }}>
                    <div style={{ position: 'relative', width: 64, height: 64 }}>
                      <svg width={64} height={64} viewBox="0 0 64 64">
                        <circle cx={32} cy={32} r={28} fill="none" stroke="#eee" strokeWidth={6} />
                        <circle cx={32} cy={32} r={28} fill="none" stroke="#6b3a3a" strokeWidth={6}
                          strokeDasharray={`${(result.compatibility_score / 100) * 175.9} 175.9`}
                          strokeLinecap="round" transform="rotate(-90 32 32)" />
                      </svg>
                      <span style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 15, fontWeight: 'bold', color: '#4a2c2a' }}>
                        {result.compatibility_score}
                      </span>
                    </div>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 600, color: '#4a2c2a' }}>{result.compatibility_label}</div>
                      <div style={{ fontSize: 12, color: '#888' }}>{t('Điểm tương hợp', 'Compatibility score')}</div>
                    </div>
                  </div>
                )}
                {result.summary && <p style={{ fontSize: 13, color: '#555', marginTop: 8 }}>{lang === 'vi' ? result.summary.vi : result.summary.en}</p>}
                {lang === 'en' && result.compatibility_text && (
                  <p style={{ fontSize: 12, color: '#666', marginTop: 8, lineHeight: 1.5, whiteSpace: 'pre-line' }}>{result.compatibility_text}</p>
                )}
                <p style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
                  {result.cross_aspect_count} {t('góc chiếu', 'aspects')} · {result.harmonious_aspects} {t('thuận', 'harmonious')} · {result.challenging_aspects} {t('nghịch', 'challenging')}
                </p>
              </div>
            ) : (
              result.composite && (
                <div>
                  <h3 style={{ margin: '0 0 8px', fontSize: 15, color: '#4a2c2a' }}>{t('Lá Số Chung (Composite)', 'Composite Chart')}</h3>
                  <p style={{ fontSize: 12, color: '#666', marginBottom: 12 }}>{t('Lá số được tính từ điểm giữa (midpoint) của hai lá số — thể hiện bản chất mối quan hệ.', 'Chart computed from the midpoint of both charts — the relationship\'s own nature.')}</p>
                  <ChartWheel chartData={{ planets: result.composite.planets, houses: result.composite.houses, ascendant: result.composite.ascendant, aspects: result.composite.aspects || [] }} />
                  {result.composite.interpretation?.sections && (
                    <InterpretationView sections={result.composite.interpretation.sections} lang={lang} />
                  )}
                </div>
              )
            )}
          </div>

          {result.cross_interpretation && result.cross_interpretation.length > 0 && (
            <div style={{ marginBottom: 16 }}>
              <h3 style={{ margin: '0 0 12px', fontSize: 14, color: '#4a2c2a' }}>{t('Luận Giải Góc Chiếu', 'Aspect Interpretation')}</h3>
              <SynastryInterpretation items={result.cross_interpretation} />
            </div>
          )}

          {result.cross_aspects && result.cross_aspects.length > 0 && (
            <AspectTable aspects={result.cross_aspects} title={t('Góc Chiếu Giữa Hai Lá Số', 'Cross Aspects')} />
          )}
        </div>
      )}
    </div>
  )
}
