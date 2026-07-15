import React, { useState } from 'react'
import { getProgression, getSolarReturn, getTransit, PredictiveResponse, BirthData } from '../api'
import InterpretationView from './InterpretationView'

type Mode = 'progression' | 'solar' | 'transit'
const MODES: { key: Mode; vi: string; en: string }[] = [
  { key: 'progression', vi: 'Tiến Trình', en: 'Progressed' },
  { key: 'solar', vi: 'Solar Return', en: 'Solar Return' },
  { key: 'transit', vi: 'Transit', en: 'Transit' },
]

const inputStyle: React.CSSProperties = { padding: '8px 10px', border: '1px solid #ddd', borderRadius: 8, fontSize: 13, width: '100%', boxSizing: 'border-box' }
const labelStyle: React.CSSProperties = { fontSize: 12, color: '#666', marginBottom: 4, display: 'block' }

export default function PredictivePanel({ lang = 'vi' }: { lang?: string }) {
  const [mode, setMode] = useState<Mode>('progression')
  const [age, setAge] = useState(30)
  const [year, setYear] = useState(new Date().getFullYear() + 1)
  const [name, setName] = useState('')
  const [y, setY] = useState(1990)
  const [m, setM] = useState(6)
  const [d, setD] = useState(15)
  const [hh, setHh] = useState(10)
  const [mm, setMm] = useState(30)
  const [lat, setLat] = useState(10.8)
  const [lng, setLng] = useState(106.7)
  const [tz, setTz] = useState('Asia/Ho_Chi_Minh')
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState('')
  const [result, setResult] = useState<any>(null)

  const birth: BirthData = { name, year: y, month: m, day: d, hour: hh, minute: mm, latitude: lat, longitude: lng, timezone_str: tz, lang }

  const run = async () => {
    setLoading(true); setErr(''); setResult(null)
    try {
      if (mode === 'progression') {
        const r = await getProgression({ ...birth, age })
        setResult(r)
      } else if (mode === 'solar') {
        const r = await getSolarReturn({ ...birth, target_year: year })
        setResult(r)
      } else {
        const now = new Date()
        const r = await getTransit({ ...birth, transit_year: now.getFullYear(), transit_month: now.getMonth() + 1, transit_day: now.getDate() })
        setResult(r)
      }
    } catch (e: any) {
      setErr(e?.response?.data?.detail || String(e))
    } finally {
      setLoading(false)
    }
  }

  const t = (vi: string, en: string) => (lang === 'vi' ? vi : en)
  const chart = result?.progression || result?.solar_return || result || {}
  const interp = (chart.interpretation as any) || {}
  const sections: any[] = interp.sections || result?.sections || []
  const hasData = sections.length > 0 || (result?.aspect_interpretations?.length)

  return (
    <div>
      <div style={{ display: 'flex', gap: 6, marginBottom: 10, flexWrap: 'wrap' }}>
        {MODES.map((m) => (
          <button key={m.key} onClick={() => setMode(m.key)}
            style={{ padding: '6px 12px', borderRadius: 8, border: '1px solid #ddd',
              background: mode === m.key ? '#4a2c2a' : '#fff', color: mode === m.key ? '#fff' : '#333',
              cursor: 'pointer', fontSize: 13, fontWeight: mode === m.key ? 600 : 400 }}>
            {t(m.vi, m.en)}
          </button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(110px, 1fr))', gap: 8, marginBottom: 10 }}>
        <div><label style={labelStyle}>{t('Năm sinh', 'Year')}</label><input style={inputStyle} type="number" value={y} onChange={(e) => setY(Number(e.target.value))} /></div>
        <div><label style={labelStyle}>{t('Tháng', 'Month')}</label><input style={inputStyle} type="number" value={m} onChange={(e) => setM(Number(e.target.value))} /></div>
        <div><label style={labelStyle}>{t('Ngày', 'Day')}</label><input style={inputStyle} type="number" value={d} onChange={(e) => setD(Number(e.target.value))} /></div>
        <div><label style={labelStyle}>{t('Giờ', 'Hour')}</label><input style={inputStyle} type="number" value={hh} onChange={(e) => setHh(Number(e.target.value))} /></div>
        <div><label style={labelStyle}>{t('Phút', 'Min')}</label><input style={inputStyle} type="number" value={mm} onChange={(e) => setMm(Number(e.target.value))} /></div>
        <div><label style={labelStyle}>{t('Vĩ độ', 'Lat')}</label><input style={inputStyle} type="number" step="0.01" value={lat} onChange={(e) => setLat(Number(e.target.value))} /></div>
        <div><label style={labelStyle}>{t('Kinh độ', 'Lng')}</label><input style={inputStyle} type="number" step="0.01" value={lng} onChange={(e) => setLng(Number(e.target.value))} /></div>
        <div><label style={labelStyle}>{t('Múi giờ', 'TZ')}</label><input style={inputStyle} value={tz} onChange={(e) => setTz(e.target.value)} /></div>
      </div>

      <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 10, flexWrap: 'wrap' }}>
        {mode === 'progression' && (
          <label style={{ fontSize: 13 }}>{t('Tuổi', 'Age')}:
            <input type="number" value={age} min={1} max={100} onChange={(e) => setAge(Number(e.target.value))}
              style={{ width: 60, marginLeft: 6 }} />
          </label>
        )}
        {mode === 'solar' && (
          <label style={{ fontSize: 13 }}>{t('Năm', 'Year')}:
            <input type="number" value={year} min={1900} max={2100} onChange={(e) => setYear(Number(e.target.value))}
              style={{ width: 80, marginLeft: 6 }} />
          </label>
        )}
        <button onClick={run} disabled={loading}
          style={{ padding: '6px 16px', borderRadius: 8, border: 'none', background: '#4a2c2a',
            color: '#fff', cursor: loading ? 'wait' : 'pointer', fontSize: 13 }}>
          {loading ? t('Đang tính...', 'Calculating...') : t('Xem', 'View')}
        </button>
      </div>

      {err && <p style={{ color: '#c00', fontSize: 13 }}>{err}</p>}

      {hasData ? (
        <InterpretationView
          sections={sections}
          overall={result?.summary ? (lang === 'vi' ? result.summary.vi : result.summary.en) : ''}
          lang={lang}
        />
      ) : (
        !loading && <p style={{ fontSize: 13, color: '#888' }}>{t('Chọn loại bản đồ và nhấn Xem.', 'Pick a chart type and press View.')}</p>
      )}
    </div>
  )
}
