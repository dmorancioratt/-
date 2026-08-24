// 城市 → 省份映射 / 经纬度 + 候选人聚合工具
// 用于 HR 大屏：把候选人按城市聚合到省份维度，做中国地图填色。

export const CITY_TO_PROVINCE: Record<string, string> = {
  北京: '北京市', 天津: '天津市', 上海: '上海市', 重庆: '重庆市',
  广州: '广东省', 深圳: '广东省', 东莞: '广东省', 佛山: '广东省', 珠海: '广东省', 惠州: '广东省',
  杭州: '浙江省', 宁波: '浙江省', 温州: '浙江省', 嘉兴: '浙江省', 绍兴: '浙江省', 金华: '浙江省',
  南京: '江苏省', 苏州: '江苏省', 无锡: '江苏省', 常州: '江苏省', 南通: '江苏省',
  成都: '四川省', 绵阳: '四川省',
  武汉: '湖北省', 宜昌: '湖北省',
  西安: '陕西省',
  长沙: '湖南省',
  青岛: '山东省', 济南: '山东省', 烟台: '山东省', 潍坊: '山东省',
  厦门: '福建省', 福州: '福建省', 泉州: '福建省',
  合肥: '安徽省', 郑州: '河南省', 石家庄: '河北省', 太原: '山西省', 沈阳: '辽宁省', 大连: '辽宁省',
  昆明: '云南省', 贵阳: '贵州省', 南宁: '广西壮族自治区', 海口: '海南省', 兰州: '甘肃省',
  银川: '宁夏回族自治区', 西宁: '青海省', 乌鲁木齐: '新疆维吾尔自治区',
  呼和浩特: '内蒙古自治区', 哈尔滨: '黑龙江省', 长春: '吉林省', 拉萨: '西藏自治区'
}

export const CITY_COORDS: Record<string, [number, number]> = {
  北京: [116.4074, 39.9042], 天津: [117.2010, 39.0842], 上海: [121.4737, 31.2304],
  广州: [113.2644, 23.1291], 深圳: [114.0579, 22.5431], 杭州: [120.1535, 30.2874],
  成都: [104.0657, 30.6594], 南京: [118.7969, 32.0603], 武汉: [114.3055, 30.5928],
  西安: [108.9398, 34.3416], 长沙: [112.9388, 28.2278], 青岛: [120.3826, 36.0671],
  济南: [117.1201, 36.6512], 苏州: [120.5853, 31.2989], 厦门: [118.0894, 24.4798],
  福州: [119.2965, 26.0745], 合肥: [117.2272, 31.8206], 郑州: [113.6253, 34.7466],
  沈阳: [123.4315, 41.8057], 大连: [121.6147, 38.9140], 昆明: [102.8329, 24.8801],
  重庆: [106.5516, 29.5630], 宁波: [121.6220, 29.8683], 东莞: [113.7518, 23.0207],
  佛山: [113.1216, 23.0218]
}

export type ProvinceCount = { name: string; value: number }

export function aggregateByProvince(candidates: any[]): ProvinceCount[] {
  const map = new Map<string, number>()
  for (const c of candidates || []) {
    const city = c?.profile?.city
    if (!city) continue
    const province = CITY_TO_PROVINCE[city]
    if (!province) continue
    map.set(province, (map.get(province) || 0) + 1)
  }
  return Array.from(map.entries())
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
}

export function topProvinces(provinces: ProvinceCount[], n = 5): ProvinceCount[] {
  return provinces.slice(0, n)
}

export type Hotspot = { name: string; value: [number, number, number] }

export function hotspotsFromProvinces(provinces: ProvinceCount[], n = 5): Hotspot[] {
  const result: Hotspot[] = []
  for (const p of provinces.slice(0, n)) {
    for (const city of Object.keys(CITY_COORDS)) {
      if (CITY_TO_PROVINCE[city] === p.name) {
        result.push({ name: city, value: [CITY_COORDS[city][0], CITY_COORDS[city][1], p.value] })
        break
      }
    }
  }
  return result
}

export type SkillFreq = { names: string[]; demand: number[]; supply: number[] }

const MOCK_SKILL_FILL = ['云原生', '板块管理', '机器学习', '数据可视化', 'Docker', '安全合规', 'Python', 'SQL', 'Linux', '数据分析']
const TARGET_SKILL_COUNT = 10

export function aggregateSkillDemand(jobs: any[], candidates: any[], graph?: { nodes?: any[]; edges?: any[] } | null): SkillFreq {
  const demandMap = new Map<string, number>()
  for (const job of jobs || []) {
    const req = job?.requirements || {}
    const required = Array.isArray(req.required_skills) ? req.required_skills : []
    const preferred = Array.isArray(req.preferred_skills) ? req.preferred_skills : []
    for (const s of required) {
      if (typeof s === 'string' && s.trim()) demandMap.set(s, (demandMap.get(s) || 0) + 2)
    }
    for (const s of preferred) {
      if (typeof s === 'string' && s.trim()) demandMap.set(s, (demandMap.get(s) || 0) + 1)
    }
  }
  if (demandMap.size === 0 && graph) {
    for (const n of graph?.nodes || []) {
      if (n?.type === 'skill' || n?.node_type === 'skill' || n?.kind === 'skill') {
        const name = n.name || n.label
        if (name) demandMap.set(name, (demandMap.get(name) || 0) + 1)
      }
    }
  }

  const supplyMap = new Map<string, number>()
  for (const c of candidates || []) {
    const skills = c?.profile?.skills || c?.latest_resume?.skills || []
    for (const s of skills) {
      if (typeof s === 'string' && s.trim()) {
        supplyMap.set(s, (supplyMap.get(s) || 0) + 1)
      } else if (s?.name) {
        supplyMap.set(s.name, (supplyMap.get(s.name) || 0) + 1)
      }
    }
  }

  // 真实数据按需求频次降序
  const realNames = Array.from(demandMap.entries())
    .sort((a, b) => b[1] - a[1])
    .map(([n]) => n)

  // 不足 10 个时用 mock 补齐
  const realSet = new Set(realNames)
  const fillNames = MOCK_SKILL_FILL.filter((n) => !realSet.has(n))
  const names = [...realNames, ...fillNames].slice(0, TARGET_SKILL_COUNT)

  const demand = names.map((n) => demandMap.get(n) || 0)
  const supply = names.map((n) => supplyMap.get(n) || 0)
  return { names, demand, supply }
}

export type EmergingItem = { name: string; count: number; percent: number; color: string }

const EMERGING_PALETTE = ['#1e3a8a', '#1d4ed8', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe']

export function aggregateEmergingByCategory(emerging: any[]): EmergingItem[] {
  if (!emerging?.length) return []
  const map = new Map<string, number>()
  for (const e of emerging) {
    const cat = e?.category || e?.domain || e?.job_name || '其他'
    map.set(cat, (map.get(cat) || 0) + 1)
  }
  const total = Array.from(map.values()).reduce((a, b) => a + b, 0) || 1
  const sorted = Array.from(map.entries()).sort((a, b) => b[1] - a[1])
  return sorted.slice(0, 5).map(([name, count], i) => ({
    name, count,
    percent: Math.round((count / total) * 100),
    color: EMERGING_PALETTE[i % EMERGING_PALETTE.length]
  }))
}
