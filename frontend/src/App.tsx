import { useState } from 'react'
import ErrorBoundary from './components/ErrorBoundary'
import NatalPanel from './components/NatalPanel'
import TransitPanel from './components/TransitPanel'
import SynastryPanel from './components/SynastryPanel'

type Tab = 'natal' | 'transit' | 'synastry'

const TABS: { key: Tab; label: string; label_en: string; icon: string }[] = [
  { key: 'natal', label: 'Lá Số Cá Nhân', label_en: 'Natal Chart', icon: '☉' },
  { key: 'transit', label: 'Quá Cảnh', label_en: 'Transits', icon: '♄' },
  { key: 'synastry', label: 'Tương Hợp', label_en: 'Synastry', icon: '♀♂' },
]

export default function App() {
  const [tab, setTab] = useState<Tab>('natal')
  const [lang, setLang] = useState<'vi' | 'en'>('vi')

  const t = (vi: string, en: string) => lang === 'vi' ? vi : en

  return (
    <ErrorBoundary>
      <div style={{ 
        maxWidth: 960, 
        margin: '0 auto', 
        padding: 20, 
        fontFamily: 'Segoe UI, system-ui, sans-serif', 
        background: '#f5f0eb', 
        minHeight: '100vh'
      }}>
        <header style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 8 }}>
            <button onClick={() => setLang(lang === 'vi' ? 'en' : 'vi')} style={{
              padding: '4px 14px', borderRadius: 12, border: '1px solid #b5653e',
              background: lang === 'vi' ? '#b5653e' : '#fff',
              color: lang === 'vi' ? '#fff' : '#b5653e',
              fontSize: 12, fontWeight: 600, cursor: 'pointer',
            }}>
              {lang === 'vi' ? 'EN' : 'VI'}
            </button>
          </div>
          <h1 style={{ color: '#4a2c2a', margin: 0, fontSize: 28, letterSpacing: 4 }}>ASTROLO<span style={{ color: '#b5653e' }}>LO</span></h1>
          <p style={{ color: '#888', margin: '4px 0 0', fontSize: 12 }}>{t('Chiêm Tinh Học Hiện Đại', 'Modern Astrology')}</p>
        </header>

        <div style={{ 
          display: 'flex', 
          gap: 4, 
          marginBottom: 24, 
          background: '#e8ddd0', 
          borderRadius: 8, 
          padding: 4 
        }}>
          {TABS.map(tabDef => (
            <button
              key={tabDef.key}
              onClick={() => setTab(tabDef.key)}
              style={{
                flex: 1, 
                padding: '10px 8px', 
                border: 'none', 
                borderRadius: 6,
                background: tab === tabDef.key ? '#6b3a3a' : 'transparent',
                color: tab === tabDef.key ? '#fff' : '#4a2c2a',
                fontSize: 13, 
                fontWeight: tab === tabDef.key ? 600 : 400,
                cursor: 'pointer', 
                transition: 'all 0.2s',
              }}
            >
              {lang === 'vi' ? tabDef.label : tabDef.label_en}
            </button>
          ))}
        </div>

        {tab === 'natal' && <NatalPanel lang={lang} />}
        {tab === 'transit' && <TransitPanel lang={lang} />}
        {tab === 'synastry' && <SynastryPanel lang={lang} />}
      </div>
    </ErrorBoundary>
  )
}
