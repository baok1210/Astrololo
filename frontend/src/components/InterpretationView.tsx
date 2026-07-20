import { SectionData, SectionItem } from '../api'

const SECTION_TITLES: Record<string, [string, string]> = {
  executive_summary: ['Tổng Quan Lá Số', 'Chart Overview'],
  synthesis: ['Tổng Hợp Đa Yếu Tố', 'Multi-Factor Synthesis'],
  part_of_fortune: ['Phần Tài Lộc', 'Part of Fortune'],
  dispositor: ['Chuỗi Chủ Tinh', 'Dispositor Chain'],
  pattern: ['Cấu Hình Đặc Biệt', 'Aspect Patterns'],
  combination: ['Kết Hợp Sao-Cung-Nhà', 'Planet-Sign-House'],
  house_placement: ['Bảng Vị Trí & Ý Nghĩa Nhà', 'House Placement Table'],
  house_distribution: ['Phân Bố Hành Tinh Theo Nhà', 'Planet Distribution by House'],
  dignity: ['Sức Mạnh Hành Tinh', 'Planetary Dignities'],
  element: ['Cân Bằng Nguyên Tố', 'Element Balance'],
  quality: ['Phân Bố Năng Lượng Hoàng Đạo', 'Zodiacal Energy Distribution'],
  planet_in_sign: ['Hành Tinh Trong Cung', 'Planets in Signs'],
  planet_in_house: ['Hành Tinh Trong Nhà', 'Planets in Houses'],
  house_cusp: ['Ý Nghĩa Đỉnh Nhà', 'House Cusp Meanings'],
  aspect: ['Các Góc Chiếu', 'Aspects'],
  aspect_synthesis: ['Tổng Hợp Góc Chiếu Theo Hành Tinh', 'Per-Planet Aspect Synthesis'],
  midpoints: ['Trung Điểm', 'Midpoints'],
  transit: ['Quá Cảnh Hành Tinh', 'Planetary Transits'],
  sun_moon: ['Kết Hợp Mặt Trời - Mặt Trăng', 'Sun-Moon Combination'],
  dominant_planet: ['Hành Tinh Nổi Bật', 'Dominant Planet'],
  fixed_stars: ['Sao Cố Định', 'Fixed Stars'],
  moon_sign: ['Mặt Trăng — Cảm Xúc & Nội Tâm', 'Moon — Emotions & Inner World'],
  life_area: ['14 Khía Cạnh Cuộc Sống', '14 Life Areas'],
  aspect_group: ['Nhóm Góc Chiếu', 'Aspect Groups'],
  encyclopedia: ['Bách Khoa Chiêm Tinh', 'Astrology Encyclopedia'],
}

const SECTION_COLORS: Record<string, string> = {
  synthesis: '#e0d0c0', dignity: '#e8d5c4', element: '#c4d8e8',
  planet_in_sign: '#d4e8c4', planet_in_house: '#e8e4c4',
  aspect: '#e8c4d4', aspect_synthesis: '#e0c4d4', pattern: '#d5c4e8', dispositor: '#c4e8d8',
  part_of_fortune: '#f5e6c8', combination: '#f0d8c4', house_placement: '#c8d4e8',
  house_distribution: '#d0e0e0', quality: '#e0d8d0', house_cusp: '#d8d0e0',
  midpoints: '#f0e0c0', transit: '#d0e8f0', sun_moon: '#f0e8d0', dominant_planet: '#f0d8d0',
  fixed_stars: '#d0c0e0',
}

export default function InterpretationView({
  sections, overall, lang = 'vi',
}: {
  sections?: SectionData[]
  overall?: string
  lang?: string
}) {
  const t = (vi: string, en: string) => lang === 'vi' ? vi : en
  const idx = lang === 'vi' ? 0 : 1
  if (!sections || sections.length === 0) return null

  return (
    <div>
      {overall && (
        <div style={{ background: '#fff', padding: 16, borderRadius: 8, marginBottom: 16, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
          <h3 style={{ margin: '0 0 8px', color: '#4a2c2a' }}>
            {lang === 'vi' ? 'Nhận Định Tổng Quan' : 'Overall Interpretation'}
          </h3>
          <p style={{ whiteSpace: 'pre-wrap', color: '#333', lineHeight: 1.6 }}>{overall}</p>
        </div>
      )}

      {sections.map((section) => {
        const titlePair = SECTION_TITLES[section.category]
        const title = titlePair ? titlePair[idx] : section.title
        const bg = SECTION_COLORS[section.category] || '#f5f0eb'
        const items = section.items || []

        return (
          <div key={section.category} style={{ background: '#fff', borderRadius: 8, marginBottom: 12, boxShadow: '0 1px 4px rgba(0,0,0,0.08)', overflow: 'hidden' }}>
            <div style={{ background: bg, padding: '10px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: 15, color: '#333' }}>{title}</h3>
              {items.length > 0 && <span style={{ fontSize: 11, color: '#888' }}>{items.length} {t('mục', 'items')}</span>}
            </div>
            <div style={{ padding: 12 }}>
              {section.category === 'house_placement' ? (
                <HousePlacementTable items={items as (SectionItem & { metadata: NonNullable<SectionItem['metadata']> })[]} lang={lang} />
              ) : (
                items.map((item, i) => {
                  const m = item.metadata as any
                  const score = (m && typeof m.score === 'number') ? m.score : item.score
                  const isLife = section.category === 'life_area'
                  return (
                  <div key={i} style={{ marginBottom: i < items.length - 1 ? 10 : 0, paddingBottom: i < items.length - 1 ? 10 : 0, borderBottom: i < items.length - 1 ? '1px solid #eee' : 'none' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 8 }}>
                      {item.title && <strong style={{ fontSize: 13, color: '#555', display: 'block', marginBottom: 4 }}>{item.title}</strong>}
                      {isLife && score !== undefined && (
                        <span style={{ fontSize: 12, fontWeight: 600, padding: '2px 8px', borderRadius: 10, background: score >= 70 ? '#27ae60' : score >= 50 ? '#f39c12' : score >= 30 ? '#e67e22' : '#e74c3c', color: '#fff', whiteSpace: 'nowrap' }}>{score}/100</span>
                      )}
                    </div>
                    {item.text && <p style={{ margin: 0, fontSize: 13, color: '#444', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{item.text}</p>}
                    {Array.isArray((item as any).evidence) && (item as any).evidence.length > 0 && (
                      <div style={{ marginTop: 6, display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                        {((item as any).evidence as string[]).map((ev, ei) => (
                          <span key={ei} style={{ fontSize: 11, padding: '2px 7px', borderRadius: 8, background: '#eef2f7', color: '#3a5a7a', border: '1px solid #d6e0ea' }}>📍 {ev}</span>
                        ))}
                      </div>
                    )}
                    {!isLife && score !== 0 && <span style={{ fontSize: 11, color: score > 0 ? '#27ae60' : '#e74c3c' }}>Score: {score > 0 ? '+' : ''}{score}</span>}
                  </div>
                  )
                })
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function HousePlacementTable({ items, lang = 'vi' }: {
  items: (SectionItem & { metadata: NonNullable<SectionItem['metadata']> })[]
  lang?: string
}) {
  const t = (vi: string, en: string) => lang === 'vi' ? vi : en
  const TH: React.CSSProperties = {
    padding: '6px 10px', fontSize: 11, fontWeight: 600, color: '#555',
    background: '#f0eef0', borderBottom: '2px solid #ddd', textAlign: 'left',
    position: 'sticky', top: 0,
  }
  const TD: React.CSSProperties = {
    padding: '6px 10px', fontSize: 12, color: '#444', borderBottom: '1px solid #e8e4e8',
    verticalAlign: 'top',
  }

  return (
    <div style={{ overflowX: 'auto', maxHeight: 480, overflowY: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: 500 }}>
        <thead>
          <tr>
            <th style={{ ...TH, width: 30 }}>#</th>
            <th style={TH}>{t('Đỉnh nhà', 'Cusp')}</th>
            <th style={{ ...TH, width: 55 }}>{t('Góc', 'Angle')}</th>
            <th style={TH}>{t('Hành tinh / Điểm', 'Bodies')}</th>
          </tr>
        </thead>
        <tbody>
          {items.map(item => {
            const m = item.metadata
            const planets = m.planets || []
            const angleLabel = m.angle_label || ''
            const isEmpty = m.is_empty
            return (
              <tr key={m.house} style={{ background: isEmpty ? '#fafafa' : '#fff' }}>
                <td style={{ ...TD, fontWeight: 600, color: '#666', textAlign: 'center' }}>
                  H{m.house}
                </td>
                <td style={TD}>
                  <span style={{ fontWeight: 500, color: '#333' }}>{m.cusp_degree_dms}</span>
                  {' '}{lang === 'vi' ? m.cusp_sign_vi : m.cusp_sign_en}
                </td>
                <td style={{ ...TD, textAlign: 'center', color: '#8a6e4b', fontWeight: 500 }}>
                  {angleLabel}
                </td>
                <td style={TD}>
                  {isEmpty ? (
                    <span style={{ color: '#999', fontStyle: 'italic' }}>—</span>
                  ) : (
                    <div>
                      {planets.map((p: any, i: number) => (
                        <div key={p.name} style={{
                          display: 'inline-block',
                          marginRight: 4, marginBottom: 2,
                          padding: '2px 6px',
                          borderRadius: 4,
                          fontSize: 11,
                          background: p.dignity_label === 'rulership' ? '#d4e8c4'
                            : p.dignity_label === 'exaltation' ? '#c4d8e8'
                            : p.dignity_label === 'detriment' ? '#e8c4c4'
                            : p.dignity_label === 'fall' ? '#e8d4c4'
                            : '#f0eef0',
                          color: '#333',
                          cursor: 'pointer',
                        }}>
                          {lang === 'vi' ? p.name_vi : p.name_en}
                          <span style={{ color: '#888', marginLeft: 2 }}>
                            ({p.position_dms} {lang === 'vi' ? p.sign_vi : p.sign_en}{p.is_retrograde ? ' ℞' : ''})
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
