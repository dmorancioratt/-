export type MissionCabinId =
  | 'resource-library'
  | 'radar'
  | 'path'
  | 'avatar'
  | 'ai-suggest'
  | 'weekly-plan'
  | 'timeline'

export type MissionNodeState = 'done' | 'active' | 'next' | 'locked'

export type MissionNode = {
  id: string
  label: string
  short: string
  value: number
  state: MissionNodeState
  meta: string
}

export type MissionTask = {
  id: string
  title: string
  meta: string
  done: boolean
}

export type MissionCabinConfig = {
  id: MissionCabinId
  visual: 'radar' | 'path' | 'profile' | 'resources' | 'ai' | 'calendar' | 'achievements'
  code: string
  english: string
  title: string
  status: string
  eyebrow: string
  hero: string
  summary: string
  accent: string
  accentSoft: string
  accentRgb: string
  progress: number
  progressLabel: string
  outcome: string
  primaryAction: string
  route: string
  metrics: Array<{ label: string; value: string; delta: string }>
  nodes: MissionNode[]
  tasks: MissionTask[]
  evidence: string[]
}

export const missionCabins: Record<MissionCabinId, MissionCabinConfig> = {
  'resource-library': {
    id: 'resource-library',
    visual: 'resources',
    code: '01',
    english: 'RESOURCE VAULT',
    title: '学习资源任务舱',
    status: '04 CURATED SOURCES',
    eyebrow: '当前资源策略',
    hero: '先完成一个可演示的 RAG 项目，再扩展理论深度。',
    summary: '系统已按阅读、实战、交付三段式筛选资源，避免课程堆积，把每一份材料都绑定到作品产出。',
    accent: '#58e6ff',
    accentSoft: '#67b8ff',
    accentRgb: '88, 230, 255',
    progress: 25,
    progressLabel: '资源完成度',
    outcome: '完成后生成 1 个项目证据，并提升 RAG 能力可信度。',
    primaryAction: '进入完整学习路径',
    route: '/learning-path',
    metrics: [
      { label: '精选资源', value: '04', delta: '去重后' },
      { label: '预计投入', value: '11h', delta: '本周' },
      { label: '交付成果', value: '01', delta: '可展示' },
    ],
    nodes: [
      { id: 'doc', label: 'LangChain 官方文档', short: 'DOC', value: 92, state: 'done', meta: '阅读 · 45 分钟' },
      { id: 'course', label: 'RAG 原理到实战', short: 'VID', value: 88, state: 'active', meta: '课程 · 3.5 小时' },
      { id: 'project', label: '企业知识库问答', short: 'LAB', value: 96, state: 'next', meta: '项目 · 6 小时' },
      { id: 'paper', label: 'RAG 经典论文', short: 'PDF', value: 84, state: 'locked', meta: '论文 · 50 分钟' },
    ],
    tasks: [
      { id: 'r1', title: '完成向量检索笔记', meta: '45 分钟', done: true },
      { id: 'r2', title: '复现基础 RAG 链路', meta: '2.5 小时', done: false },
      { id: 'r3', title: '提交项目演示链接', meta: '本周日', done: false },
    ],
    evidence: ['岗位需求映射：RAG / 向量检索 / LangChain', '资源质量分 ≥ 84', '最终产出可进入成长档案'],
  },
  radar: {
    id: 'radar',
    visual: 'radar',
    code: '04',
    english: 'SKILL GRAPH',
    title: '能力图谱任务舱',
    status: '08 DIMENSIONS ONLINE',
    eyebrow: 'AI 能力诊断',
    hero: '补齐 RAG 与工程化能力，岗位匹配度可从 72% 推进到 87%。',
    summary: '你的算法基础已经形成优势，当前瓶颈集中在知识增强、服务部署和复杂任务编排。',
    accent: '#57dfff',
    accentSoft: '#7b6dff',
    accentRgb: '87, 223, 255',
    progress: 74,
    progressLabel: '综合能力值',
    outcome: '完成三项补强任务后，预计超过 81% 的同阶段候选人。',
    primaryAction: '打开完整能力图谱',
    route: '/skill-graph',
    metrics: [
      { label: '优势能力', value: '05', delta: '+1 本月' },
      { label: '关键缺口', value: '03', delta: '需补强' },
      { label: '岗位匹配', value: '72%', delta: '+14%' },
    ],
    nodes: [
      { id: 'python', label: 'Python 工程', short: 'PY', value: 88, state: 'done', meta: '超过 86% 同学' },
      { id: 'ml', label: '机器学习', short: 'ML', value: 82, state: 'done', meta: '核心优势能力' },
      { id: 'dl', label: '深度学习', short: 'DL', value: 76, state: 'active', meta: '持续增长中' },
      { id: 'rag', label: 'RAG 知识增强', short: 'RG', value: 62, state: 'active', meta: '岗位高频要求' },
      { id: 'deploy', label: '模型部署', short: 'OP', value: 54, state: 'next', meta: '缺口优先级 P1' },
      { id: 'agent', label: 'Agent 编排', short: 'AG', value: 48, state: 'locked', meta: '下一阶段能力' },
    ],
    tasks: [
      { id: 's1', title: '完成 RAG 检索评估实验', meta: '+6 能力值', done: false },
      { id: 's2', title: '部署一个推理 API', meta: '+5 能力值', done: false },
      { id: 's3', title: '补充项目性能证据', meta: '+4 可信度', done: true },
    ],
    evidence: ['来自 3 个项目与 6 次测评', '对齐 AI 算法工程师能力基线', '最近一次更新：今天 09:42'],
  },
  path: {
    id: 'path',
    visual: 'path',
    code: '02',
    english: 'LEARNING PATH',
    title: '职业航线任务舱',
    status: 'STAGE 04 / 06',
    eyebrow: '当前航线',
    hero: '你已经越过基础学习区，下一站是可交付的 RAG 项目。',
    summary: '路径会根据岗位需求和你的完成速度动态重排。当前最短路线不是继续看课，而是完成一项项目交付。',
    accent: '#69f0d2',
    accentSoft: '#657bff',
    accentRgb: '105, 240, 210',
    progress: 58,
    progressLabel: '航线进度',
    outcome: '预计 4 周后进入 Agent 项目阶段，岗位匹配度提升 15%。',
    primaryAction: '继续当前学习任务',
    route: '/learning-path',
    metrics: [
      { label: '已完成', value: '03', delta: '阶段' },
      { label: '当前任务', value: 'RAG', delta: 'P0' },
      { label: '抵达目标', value: '8周', delta: '-2周' },
    ],
    nodes: [
      { id: 'p1', label: 'Python', short: '01', value: 100, state: 'done', meta: '入门基础' },
      { id: 'p2', label: '机器学习', short: '02', value: 100, state: 'done', meta: '核心算法' },
      { id: 'p3', label: '深度学习', short: '03', value: 100, state: 'done', meta: '进阶应用' },
      { id: 'p4', label: 'RAG 项目', short: '04', value: 58, state: 'active', meta: '当前阶段' },
      { id: 'p5', label: 'Agent 开发', short: '05', value: 0, state: 'next', meta: '下一阶段' },
      { id: 'p6', label: 'AI 算法工程师', short: 'GO', value: 0, state: 'locked', meta: '目标岗位' },
    ],
    tasks: [
      { id: 'p1t', title: '理解向量检索评估指标', meta: '今天 · 40 分钟', done: true },
      { id: 'p2t', title: '完成知识库切片实验', meta: '明天 · 90 分钟', done: false },
      { id: 'p3t', title: '录制项目演示视频', meta: '周日 · 30 分钟', done: false },
    ],
    evidence: ['依据 14 个目标岗位实时重排', '路径难度与每周 8 小时时间预算匹配', '已避免 2 门重复课程'],
  },
  avatar: {
    id: 'avatar',
    visual: 'profile',
    code: '03',
    english: 'GROWTH PROFILE',
    title: '数字成长档案舱',
    status: 'IDENTITY VERIFIED',
    eyebrow: '能力身份摘要',
    hero: '你的个人标签正在从“课程学习者”转向“AI 项目交付者”。',
    summary: '成长档案把课程、项目、测评和岗位能力关联起来，形成可向评委与企业解释的能力证据链。',
    accent: '#8e9cff',
    accentSoft: '#58e6ff',
    accentRgb: '142, 156, 255',
    progress: 81,
    progressLabel: '档案可信度',
    outcome: '再补充 1 项部署证据，即可生成 AI 算法工程师能力名片。',
    primaryAction: '查看个人中心',
    route: '/personal-center',
    metrics: [
      { label: '能力标签', value: '18', delta: '+3' },
      { label: '项目证据', value: '06', delta: '已验证' },
      { label: '成长等级', value: 'L4', delta: '探索者' },
    ],
    nodes: [
      { id: 'a1', label: '课程证书', short: 'CR', value: 92, state: 'done', meta: '8 项已验证' },
      { id: 'a2', label: '项目作品', short: 'PJ', value: 81, state: 'active', meta: '6 项有效证据' },
      { id: 'a3', label: '技能测评', short: 'EX', value: 76, state: 'active', meta: '最近提升 9%' },
      { id: 'a4', label: '岗位反馈', short: 'HR', value: 64, state: 'next', meta: '2 次模拟反馈' },
    ],
    tasks: [
      { id: 'a1t', title: '补充项目性能指标', meta: '证据完整度 +8%', done: false },
      { id: 'a2t', title: '更新本月成长总结', meta: '约 10 分钟', done: false },
      { id: 'a3t', title: '验证课程证书', meta: '已完成', done: true },
    ],
    evidence: ['证据覆盖课程、项目、测评、反馈', '6 项记录已通过来源校验', '能力身份可导出为展示报告'],
  },
  'ai-suggest': {
    id: 'ai-suggest',
    visual: 'ai',
    code: '05',
    english: 'AI COMPANION',
    title: 'AI 决策任务舱',
    status: 'REASONING ONLINE',
    eyebrow: '此刻最优行动',
    hero: '暂停新增课程，把本周时间集中到 RAG 项目交付。',
    summary: 'AI 综合岗位热度、能力缺口和时间预算后，判断项目证据比继续积累课程更能提升你的竞争力。',
    accent: '#c18cff',
    accentSoft: '#5ce5ff',
    accentRgb: '193, 140, 255',
    progress: 87,
    progressLabel: '建议置信度',
    outcome: '执行建议可在 7 天内形成 1 项作品证据，预计匹配度提升 8%。',
    primaryAction: '采纳并生成计划',
    route: '/learning-path',
    metrics: [
      { label: '岗位信号', value: '14', delta: '实时' },
      { label: '缺口权重', value: 'P0', delta: 'RAG' },
      { label: '时间预算', value: '8h', delta: '可完成' },
    ],
    nodes: [
      { id: 'i1', label: '岗位需求', short: 'JOB', value: 91, state: 'done', meta: '14 个目标岗位' },
      { id: 'i2', label: '能力缺口', short: 'GAP', value: 88, state: 'active', meta: 'RAG 优先级最高' },
      { id: 'i3', label: '学习节奏', short: 'TIME', value: 82, state: 'active', meta: '本周可投入 8h' },
      { id: 'i4', label: '行动收益', short: 'GAIN', value: 86, state: 'next', meta: '预计提升 8%' },
    ],
    tasks: [
      { id: 'i1t', title: '锁定本周 RAG 项目', meta: '立即', done: false },
      { id: 'i2t', title: '自动拆解为 3 个任务', meta: 'AI 生成', done: false },
      { id: 'i3t', title: '同步到计划日历', meta: '等待确认', done: false },
    ],
    evidence: ['建议参考 14 个目标岗位', '已排除重复学习内容', '置信度 87%，可查看完整依据'],
  },
  'weekly-plan': {
    id: 'weekly-plan',
    visual: 'calendar',
    code: '06',
    english: 'MISSION CALENDAR',
    title: '本周任务编排舱',
    status: 'WEEK 35 ACTIVE',
    eyebrow: '本周作战节奏',
    hero: '本周只保留三件高价值任务，确保周日产生可展示成果。',
    summary: '计划按精力峰值和任务依赖自动排序。深度任务安排在高专注时段，零碎学习集中处理。',
    accent: '#52ddff',
    accentSoft: '#69f0d2',
    accentRgb: '82, 221, 255',
    progress: 42,
    progressLabel: '本周完成度',
    outcome: '完成全部任务可获得 1 个项目里程碑，并解锁“知识增强实践者”。',
    primaryAction: '打开完整计划',
    route: '/learning-path',
    metrics: [
      { label: '关键任务', value: '03', delta: '已聚焦' },
      { label: '时间预算', value: '8h', delta: '剩余 5h' },
      { label: '连续学习', value: '12d', delta: '+1' },
    ],
    nodes: [
      { id: 'mon', label: '周一', short: 'MON', value: 100, state: 'done', meta: '检索指标' },
      { id: 'tue', label: '周二', short: 'TUE', value: 100, state: 'done', meta: '切片实验' },
      { id: 'wed', label: '周三', short: 'WED', value: 50, state: 'active', meta: 'RAG 链路' },
      { id: 'thu', label: '周四', short: 'THU', value: 0, state: 'next', meta: '接口部署' },
      { id: 'fri', label: '周五', short: 'FRI', value: 0, state: 'next', meta: '效果评估' },
      { id: 'sat', label: '周六', short: 'SAT', value: 0, state: 'locked', meta: '演示优化' },
      { id: 'sun', label: '周日', short: 'SUN', value: 0, state: 'locked', meta: '成果提交' },
    ],
    tasks: [
      { id: 'w1', title: '完成基础 RAG 链路', meta: '今天 20:00 · 2h', done: true },
      { id: 'w2', title: '加入检索效果评估', meta: '周五 · 2h', done: false },
      { id: 'w3', title: '录制 90 秒演示', meta: '周日 · 1h', done: false },
    ],
    evidence: ['计划基于每周 8 小时预算', '高专注任务安排在晚间', '完成状态会回写成长档案'],
  },
  timeline: {
    id: 'timeline',
    visual: 'achievements',
    code: '07',
    english: 'ACHIEVEMENT VAULT',
    title: '成长里程碑任务舱',
    status: '09 BADGES SECURED',
    eyebrow: '下一枚关键徽章',
    hero: '再完成一次可验证部署，即可解锁“AI 工程实践者”。',
    summary: '成就不记录点击和观看时长，只记录能够证明能力增长的项目、测评与真实反馈。',
    accent: '#ffc86b',
    accentSoft: '#ff7ca8',
    accentRgb: '255, 200, 107',
    progress: 76,
    progressLabel: '徽章解锁进度',
    outcome: '新徽章将同步到成长档案，并成为岗位匹配的工程化证据。',
    primaryAction: '查看能力演化时间线',
    route: '/capability-evolution',
    metrics: [
      { label: '已获徽章', value: '09', delta: '+2 本月' },
      { label: '稀有成就', value: '03', delta: 'TOP 12%' },
      { label: '成长积分', value: '860', delta: '+120' },
    ],
    nodes: [
      { id: 't1', label: 'Python 起航者', short: 'PY', value: 100, state: 'done', meta: '2026.03 解锁' },
      { id: 't2', label: '算法探索者', short: 'ML', value: 100, state: 'done', meta: '2026.05 解锁' },
      { id: 't3', label: '深度学习实践者', short: 'DL', value: 100, state: 'done', meta: '2026.07 解锁' },
      { id: 't4', label: '知识增强构建者', short: 'RG', value: 76, state: 'active', meta: '当前冲刺' },
      { id: 't5', label: 'AI 工程实践者', short: 'OP', value: 0, state: 'next', meta: '等待部署证据' },
    ],
    tasks: [
      { id: 't1t', title: '完成线上推理接口', meta: '解锁条件 1/2', done: false },
      { id: 't2t', title: '提交性能对比结果', meta: '解锁条件 2/2', done: false },
      { id: 't3t', title: '验证深度学习项目', meta: '上一徽章', done: true },
    ],
    evidence: ['徽章仅由可验证证据触发', '每枚徽章关联岗位能力标签', '成长积分不受学习时长灌水影响'],
  },
}

export function isMissionCabinId(value: string): value is MissionCabinId {
  return value in missionCabins
}
