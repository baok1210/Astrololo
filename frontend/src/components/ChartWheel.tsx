import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

const W = 480, H = 480, R = 210, INNER_R = 40

const SIGN_SYMBOLS: Record<string, string> = {
  aries: '♈', taurus: '♉', gemini: '♊', cancer: '♋',
  leo: '♌', virgo: '♍', libra: '♎', scorpio: '♏',
  sagittarius: '♐', capricorn: '♑', aquarius: '♒', pisces: '♓',
}

const PLANET_SYMBOLS: Record<string, string> = {
  sun: '☉', moon: '☽', mercury: '☿', venus: '♀', mars: '♂',
  jupiter: '♃', saturn: '♄', uranus: '♅', neptune: '♆', pluto: '♇',
  chiron: '⚷', ceres: '⚳', pallas: '⚴', juno: '⚵', vesta: '⚶',
  lilith: '⚸', north_node: '☊', south_node: '☋',
}

const SIGN_COLORS: Record<string, string> = {
  fire: '#e74c3c', earth: '#27ae60', air: '#f1c40f', water: '#3498db',
}

interface Planet {
  name: string
  longitude: number
  sign: string
  house: number
  aspects?: any[]
}

interface FixedStar {
  name: string
  name_en: string
  name_vi: string
  longitude: number
  sign: string
  magnitude: number
}

interface ChartData {
  planets: Planet[]
  houses: any[]
  ascendant: number
  aspects?: any[]
  part_of_fortune?: { longitude: number; sign: string; sign_vi?: string; house?: number }
  fixed_stars?: FixedStar[]
}

export default function ChartWheel({ chartData }: { chartData: ChartData }) {
  const ref = useRef<SVGSVGElement>(null)
  const planets = chartData?.planets || []
  const houses = chartData?.houses || []
  const aspects = chartData?.aspects || []
  const ascendant = chartData?.ascendant || 0
  const pof = chartData?.part_of_fortune
  const fixedStars = chartData?.fixed_stars || []

  useEffect(() => {
    if (!ref.current) return
    const svg = d3.select(ref.current)
    svg.selectAll('*').remove()
    const g = svg.append('g').attr('transform', `translate(${W / 2},${H / 2})`)

    // Zodiac sign arcs
    const arcGen = d3.arc()
      .innerRadius(R - 30)
      .outerRadius(R)

    const signs = ['aries','taurus','gemini','cancer','leo','virgo','libra','scorpio','sagittarius','capricorn','aquarius','pisces']
    const elements = ['fire','earth','air','water','fire','earth','air','water','fire','earth','air','water']

    signs.forEach((s, i) => {
      const startAngle = (i * 30 - 90) * Math.PI / 180
      const endAngle = ((i + 1) * 30 - 90) * Math.PI / 180
      const elem = elements[i]
      g.append('path')
        .attr('d', arcGen({ startAngle, endAngle } as any))
        .attr('fill', SIGN_COLORS[elem])
        .attr('fill-opacity', 0.15)
        .attr('stroke', '#ccc').attr('stroke-width', 0.5)

      // Sign label
      const midAngle = (startAngle + endAngle) / 2
      const labelR = R - 42
      g.append('text')
        .attr('x', labelR * Math.cos(midAngle))
        .attr('y', labelR * Math.sin(midAngle))
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'central')
        .attr('font-size', '16')
        .attr('fill', '#555')
        .text(SIGN_SYMBOLS[s])
    })

    // Degree ticks
    for (let i = 0; i < 360; i += 5) {
      const angle = (i - 90) * Math.PI / 180
      const isMajor = i % 30 === 0
      const r1 = isMajor ? R - 30 : R - 25
      const r2 = R - 18
      g.append('line')
        .attr('x1', r1 * Math.cos(angle))
        .attr('y1', r1 * Math.sin(angle))
        .attr('x2', r2 * Math.cos(angle))
        .attr('y2', r2 * Math.sin(angle))
        .attr('stroke', isMajor ? '#999' : '#ddd')
        .attr('stroke-width', isMajor ? 1.5 : 0.5)
    }

    // House cusps and numbers
    if (houses.length > 0) {
      houses.forEach((h: any, i: number) => {
        const deg = h.cusp_degree || (i * 30)
        const angle = (deg - 90) * Math.PI / 180
        const r1 = R - 30, r2 = R + 15
        g.append('line')
          .attr('x1', r1 * Math.cos(angle))
          .attr('y1', r1 * Math.sin(angle))
          .attr('x2', r2 * Math.cos(angle))
          .attr('y2', r2 * Math.sin(angle))
          .attr('stroke', '#666').attr('stroke-width', 1.5)

        // House numbers
        const numR = R + 10
        g.append('text')
          .attr('x', numR * Math.cos(angle))
          .attr('y', numR * Math.sin(angle))
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'central')
          .attr('font-size', '9')
          .attr('fill', '#333')
          .attr('font-weight', 'bold')
          .text(i + 1)
      })
    }

    // Outer ring border
    g.append('circle')
      .attr('r', R + 15)
      .attr('fill', 'none')
      .attr('stroke', '#999')
      .attr('stroke-width', 1)

    g.append('circle')
      .attr('r', R - 30)
      .attr('fill', 'none')
      .attr('stroke', '#ccc')
      .attr('stroke-width', 0.5)

    // Hemisphere labels (N/S/E/W)
    const hlR = R + 26
    const hemis = [
      { label: 'S', angle: -90 },  // South = bottom of chart
      { label: 'N', angle: 90 },   // North = top
      { label: 'E', angle: 0 },    // East = right (Ascendant side)
      { label: 'W', angle: 180 },  // West = left (Descendant side)
    ]
    hemis.forEach(({ label, angle }) => {
      const a = (angle - 90) * Math.PI / 180
      g.append('text')
        .attr('x', hlR * Math.cos(a))
        .attr('y', hlR * Math.sin(a))
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'central')
        .attr('font-size', '11')
        .attr('font-weight', 'bold')
        .attr('fill', '#888')
        .text(label)
    })

    // Inner rings
    g.append('circle')
      .attr('r', INNER_R)
      .attr('fill', '#f9f6f0')
      .attr('stroke', '#ccc')

    // Aspect lines
    if (aspects.length > 0) {
      const aspColors: Record<string, string> = {
        conjunction: '#333', sextile: '#27ae60', square: '#e74c3c',
        trine: '#3498db', opposition: '#e67e22', quincunx: '#95a5a6',
      }
      aspects.slice(0, 30).forEach((a: any) => {
        const p1 = planets.find((p: Planet) => p.name === a.planet1)
        const p2 = planets.find((p: Planet) => p.name === a.planet2)
        if (!p1 || !p2) return
        const a1 = (p1.longitude - 90) * Math.PI / 180
        const a2 = (p2.longitude - 90) * Math.PI / 180
        const r1 = R - 32, r2 = R - 32
        g.append('line')
          .attr('x1', r1 * Math.cos(a1))
          .attr('y1', r1 * Math.sin(a1))
          .attr('x2', r2 * Math.cos(a2))
          .attr('y2', r2 * Math.sin(a2))
          .attr('stroke', aspColors[a.aspect_type] || '#999')
          .attr('stroke-width', 1.5)
          .attr('stroke-opacity', 0.4)
          .attr('stroke-dasharray', a.aspect_type === 'trine' ? '' : a.aspect_type === 'sextile' ? '4,4' : '')
      })
    }

    // Planet positions
    const planetR = R - 32
    planets.forEach((p: Planet, i: number) => {
      const angle = (p.longitude - 90) * Math.PI / 180
      const x = planetR * Math.cos(angle)
      const y = planetR * Math.sin(angle)

      const color = i === 0 ? '#e67e22' : i === 1 ? '#95a5a6' : '#555'

      // Dot
      g.append('circle')
        .attr('cx', x).attr('cy', y)
        .attr('r', 4)
        .attr('fill', color)
        .attr('stroke', '#fff')
        .attr('stroke-width', 1.5)

      // Symbol label with offset to prevent overlap
      const offsetAngle = i % 2 === 0 ? 0.15 : -0.15
      const labelR2 = planetR - 16
      const lx = labelR2 * Math.cos(angle + offsetAngle)
      const ly = labelR2 * Math.sin(angle + offsetAngle)

      g.append('text')
        .attr('x', lx).attr('y', ly)
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'central')
        .attr('font-size', '11')
        .attr('fill', color)
        .attr('font-weight', 'bold')
        .text(PLANET_SYMBOLS[p.name] || p.name[0].toUpperCase())
    })

    // Ascendant marker (AS)
    const ascAngle = (ascendant - 90) * Math.PI / 180
    const ascR = R + 20
    g.append('text')
      .attr('x', ascR * Math.cos(ascAngle))
      .attr('y', ascR * Math.sin(ascAngle))
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('font-size', '12')
      .attr('fill', '#e74c3c')
      .attr('font-weight', 'bold')
      .text('AS')

    // Part of Fortune marker (⊕)
    if (pof) {
      const pofAngle = (pof.longitude - 90) * Math.PI / 180
      const pofR = R - 32
      g.append('circle')
        .attr('cx', pofR * Math.cos(pofAngle))
        .attr('cy', pofR * Math.sin(pofAngle))
        .attr('r', 5)
        .attr('fill', '#f0c040')
        .attr('stroke', '#c8a030')
        .attr('stroke-width', 1.5)
      g.append('text')
        .attr('x', (pofR - 14) * Math.cos(pofAngle))
        .attr('y', (pofR - 14) * Math.sin(pofAngle))
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'central')
        .attr('font-size', '10')
        .attr('fill', '#c8a030')
        .attr('font-weight', 'bold')
        .text('⊕')
    }

    // Fixed Stars (★ dots with magnitude-based sizing)
    const starR = R - 32
    fixedStars.forEach((fs: FixedStar) => {
      const fsAngle = (fs.longitude - 90) * Math.PI / 180
      const size = Math.max(2, Math.min(5, 5 - (fs.magnitude || 3) * 0.8))
      g.append('circle')
        .attr('cx', starR * Math.cos(fsAngle))
        .attr('cy', starR * Math.sin(fsAngle))
        .attr('r', size)
        .attr('fill', '#a070d0')
        .attr('stroke', '#fff')
        .attr('stroke-width', 0.8)
        .attr('opacity', 0.8)
      g.append('text')
        .attr('x', (starR + 8) * Math.cos(fsAngle))
        .attr('y', (starR + 8) * Math.sin(fsAngle))
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'central')
        .attr('font-size', '6')
        .attr('fill', '#a070d0')
        .attr('opacity', 0.7)
        .text('★')
    })

    // Center label
    g.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('font-size', '9')
      .attr('fill', '#999')
      .text('Astrololo')

  }, [chartData])

  return (
    <div style={{ textAlign: 'center' }}>
      <svg ref={ref} width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ maxWidth: '100%', height: 'auto' }} />
    </div>
  )
}
