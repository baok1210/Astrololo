const PLANET_NAMES_VI: Record<string, string> = {
  sun: 'Mặt Trời', moon: 'Mặt Trăng', mercury: 'Sao Thủy', venus: 'Sao Kim', mars: 'Sao Hỏa',
  jupiter: 'Sao Mộc', saturn: 'Sao Thổ', uranus: 'Sao Thiên Vương', neptune: 'Sao Hải Vương', pluto: 'Sao Diêm Vương',
  chiron: 'Chiron', ceres: 'Ceres', pallas: 'Pallas', juno: 'Juno', vesta: 'Vesta', lilith: 'Lilith',
  north_node: 'La Hầu', south_node: 'Kế Hầu',
}

const ASPECT_NAMES: Record<string, string> = {
  conjunction: 'Hội', opposition: 'Xung', trine: 'Tam Hợp', square: 'Vuông',
  sextile: 'Lục Hợp', quincunx: 'Bát Xung', semisextile: 'Nửa Lục Hợp',
  semisquare: 'Bán Vuông', sesquiquadrate: 'Rưỡi Vuông',
}

const ASPECT_COLORS: Record<string, string> = {
  conjunction: '#333', sextile: '#27ae60', square: '#e74c3c',
  trine: '#3498db', opposition: '#e67e22', quincunx: '#95a5a6',
  semisextile: '#1abc9c', semisquare: '#e91e63', sesquiquadrate: '#9b59b6',
}

function pname(key: string): string {
  return PLANET_NAMES_VI[key] || key
}

export default function AspectTable({ aspects, title }: { aspects: any[]; title?: string }) {
  if (!aspects || aspects.length === 0) return null

  return (
    <div style={{ background: '#fff', borderRadius: 8, marginBottom: 16, boxShadow: '0 1px 4px rgba(0,0,0,0.08)', overflow: 'hidden' }}>
      {title && <div style={{ background: '#e8c4d4', padding: '10px 16px' }}><h3 style={{ margin: 0, fontSize: 15, color: '#333' }}>{title}</h3></div>}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ background: '#f5f0eb' }}>
              <th style={{ padding: '8px 10px', textAlign: 'left' }}>Hành Tinh 1</th>
              <th style={{ padding: '8px 10px', textAlign: 'left' }}>Hành Tinh 2</th>
              <th style={{ padding: '8px 10px', textAlign: 'left' }}>Góc Chiếu</th>
              <th style={{ padding: '8px 10px', textAlign: 'left' }}>Orb</th>
              <th style={{ padding: '8px 10px', textAlign: 'left' }}>Loại</th>
            </tr>
          </thead>
          <tbody>
            {aspects.map((a, i) => {
              const nature = a.nature || a.type || 'neutral'
              const orbVal = a.orb_formatted || (a.orb ? a.orb.toFixed(1) + '°' : '')
              const isHar = nature === 'harmonious'
              const isCha = nature === 'challenging'
              return (
                <tr key={i} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '6px 10px' }}>{pname(a.planet1)}</td>
                  <td style={{ padding: '6px 10px' }}>{pname(a.planet2)}</td>
                  <td style={{ padding: '6px 10px', fontWeight: 600, color: ASPECT_COLORS[a.aspect_type] || '#333' }}>
                    {a.aspect_name_vi || ASPECT_NAMES[a.aspect_type] || a.aspect_type}
                  </td>
                  <td style={{ padding: '6px 10px' }}>{orbVal}</td>
                  <td style={{ padding: '6px 10px' }}>
                    <span style={{
                      display: 'inline-block', padding: '2px 8px', borderRadius: 10, fontSize: 11,
                      background: isHar ? '#d4edda' : isCha ? '#f8d7da' : '#ffeaa8',
                      color: isHar ? '#155724' : isCha ? '#721c24' : '#856404',
                    }}>
                      {isHar ? 'Thuận' : isCha ? 'Nghịch' : 'Trung'}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
