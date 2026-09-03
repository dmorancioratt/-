<template>
  <section class="learning-mission" aria-label="沉浸式学习路径">
    <div class="learning-space">
      <video
        ref="backgroundVideo"
        class="learning-space__video"
        src="/learning-path/cosmic-learning-path.mp4"
        autoplay
        muted
        loop
        playsinline
        preload="auto"
        @playing="videoBlocked = false"
      ></video>
      <div class="learning-space__wash" aria-hidden="true"></div>
      <div class="learning-space__stars" aria-hidden="true"></div>

      <button class="learning-back" type="button" @click="emit('close')">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m14.5 5-7 7 7 7" /></svg>
        <span>返回驾驶舱</span>
      </button>

      <button class="learning-sound" type="button" :aria-label="videoMuted ? '打开背景声音' : '关闭背景声音'" @click="toggleSound">
        <svg v-if="videoMuted" viewBox="0 0 24 24" aria-hidden="true"><path d="M11 5 6 9H3v6h3l5 4V5Zm5 4 5 6m0-6-5 6" /></svg>
        <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="M11 5 6 9H3v6h3l5 4V5Zm4 3a5 5 0 0 1 0 8m3-11a9 9 0 0 1 0 14" /></svg>
      </button>

      <button v-if="videoBlocked" class="video-unlock" type="button" @click="resumeBackground">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 7 8 5-8 5V7Z" /></svg>
        播放动态星轨
      </button>

      <div class="path-planner">
        <header class="planner-head">
          <div class="planner-eyebrow"><span>AI CAREER ROUTE</span><i></i><b>知识图谱实时规划</b></div>
          <div class="planner-title-row">
            <div><small>目标岗位</small><h2>{{ targetJob || '尚未选择目标岗位' }}</h2></div>
            <button class="replan-button" type="button" @click="replanRoute">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h11a5 5 0 0 1 5 5v0a5 5 0 0 1-5 5H8"/><path d="m8 13-4 4 4 4M16 3l4 4-4 4"/></svg>
              {{ routeMode === '稳健成长' ? '切换冲刺路线' : '切换稳健路线' }}
            </button>
          </div>
          <div class="planner-metrics">
            <span><small>当前岗位匹配</small><strong>{{ matchScore }}%</strong></span>
            <span><small>规划策略</small><strong>{{ routeMode }}</strong></span>
            <span><small>预计达成</small><strong>{{ routeEstimate }}</strong></span>
          </div>
        </header>

        <div class="stage-map" aria-label="AI 岗位成长路径" :style="{ '--route-progress': routeProgress }">
          <svg class="career-route" viewBox="0 0 1000 760" preserveAspectRatio="none" aria-hidden="true">
            <defs>
              <linearGradient id="careerRouteGradient" x1="0" y1="1" x2="1" y2="0">
                <stop offset="0" stop-color="#16dbf2" />
                <stop offset=".55" stop-color="#0aa9b4" />
                <stop offset="1" stop-color="#55dfff" />
              </linearGradient>
              <filter id="careerRouteGlow"><feGaussianBlur stdDeviation="8" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
            </defs>
            <path id="careerRoutePath" class="route-line route-line--halo" d="M145 625 C225 565 260 485 340 470 S465 610 550 570 S650 405 700 345 S800 235 855 165" />
            <path class="route-line route-line--base" d="M145 625 C225 565 260 485 340 470 S465 610 550 570 S650 405 700 345 S800 235 855 165" />
            <path class="route-line route-line--progress" pathLength="100" d="M145 625 C225 565 260 485 340 470 S465 610 550 570 S650 405 700 345 S800 235 855 165" />
            <circle class="route-particle route-particle--one" r="5"><animateMotion dur="6s" repeatCount="indefinite"><mpath href="#careerRoutePath" /></animateMotion></circle>
            <circle class="route-particle route-particle--two" r="3"><animateMotion dur="6s" begin="-3s" repeatCount="indefinite"><mpath href="#careerRoutePath" /></animateMotion></circle>
          </svg>

          <button
            v-for="(stage, index) in stages"
            :key="stage.id"
            class="route-node"
            :class="{ active: selectedStageIndex === index, started: startedStages.has(stage.id), 'label-left': stage.labelSide === 'left' }"
            :style="routeNodeStyle(stage)"
            type="button"
            :aria-label="`查看成长里程碑 ${stage.id} ${stage.mapTitle}`"
            @click="selectStage(index)"
          >
            <span class="route-node__core"><small>0{{ stage.id }}</small><strong>{{ stage.nodeCode }}</strong></span>
            <span class="route-node__copy">
              <em>{{ stage.nodeTag }}</em>
              <strong>{{ stage.mapTitle }}</strong>
              <small>{{ stage.mapSubtitle }}</small>
              <span class="route-node__skills"><i v-for="skill in stage.skillTags" :key="skill">{{ skill }}</i></span>
            </span>
          </button>
        </div>

        <footer class="planner-foot">
          <span><i></i> 当前账号 {{ tasks.length }} 项学习任务 · {{ resources.length }} 个能力专题</span>
          <strong>{{ suggestions.length ? suggestions[0] : '路径随真实匹配报告动态更新' }}</strong>
        </footer>
      </div>
    </div>

    <aside class="learning-console">
      <div class="console-topline">
        <span>{{ currentStage.kicker }}</span>
        <strong>MILESTONE {{ phaseNumber }} / 05</strong>
      </div>

      <div class="console-hero">
        <div>
          <h1>{{ currentStage.title }}</h1>
          <p>{{ currentStage.description }}</p>
        </div>
        <div class="mastery-ring" :style="masteryStyle" role="progressbar" :aria-valuenow="currentStage.mastery" aria-valuemin="0" aria-valuemax="100">
          <div><strong>{{ currentStage.mastery }}%</strong><span>路径完成度</span></div>
        </div>
      </div>

      <div class="stage-stats">
        <article><span>能力簇</span><strong>{{ currentStage.domain }}</strong></article>
        <article><span>关键任务</span><strong>{{ currentStage.tasks }} 个</strong></article>
        <article><span>建议周期</span><strong>{{ currentStage.duration }}</strong></article>
      </div>

      <div class="phase-switcher" aria-label="切换成长里程碑">
        <button
          v-for="(stage, index) in stages"
          :key="`phase-${stage.id}`"
          type="button"
          :class="{ active: selectedStageIndex === index, started: startedStages.has(stage.id) }"
          :aria-label="`切换到成长里程碑 ${stage.id} ${stage.mapTitle}`"
          @click="selectStage(index)"
        >{{ stage.id }}</button>
      </div>

      <div class="resource-heading">
        <h2>AI 推荐任务包</h2>
        <button class="start-stage" type="button" :class="{ active: startedStages.has(currentStage.id) }" @click="startCurrentStage">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 4c3-1 5 0 6 1 1 1 2 3 1 6l-4 4-4-4 1-7Z"/><path d="m13 11-5 5m1-3-4 1-2 5 5-2 1-4Zm7 3 3 3" /></svg>
          {{ startedStages.has(currentStage.id) ? '任务执行中' : '启动里程碑' }}
        </button>
      </div>

      <div class="resource-list">
        <article v-for="(resource, index) in currentStage.resources" :key="resource.title" tabindex="0" @click="openResource(resource, resource.kind)" @keydown.enter="openResource(resource, resource.kind)">
          <span class="resource-index">{{ String(index + 1).padStart(2, '0') }}</span>
          <div class="resource-copy"><strong>{{ resource.title }}</strong><small>{{ resource.typeLabel }}</small></div>
          <div class="resource-actions">
            <button type="button" :aria-label="`阅读 ${resource.title}`" @click.stop="openResource(resource, 'document')">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21.5v-16Z"/><path d="M4 19a2.5 2.5 0 0 1 2.5-2.5H20" /></svg>
            </button>
            <button type="button" :aria-label="`播放 ${resource.title}`" @click.stop="openResource(resource, 'video')">
              <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m10 8 6 4-6 4V8Z" /></svg>
            </button>
          </div>
        </article>
      </div>

      <div class="console-nav">
        <button type="button" :disabled="selectedStageIndex === 0" @click="goPrevious">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m14.5 5-7 7 7 7" /></svg>上个里程碑
        </button>
        <span>{{ currentStage.mapTitle }} · {{ currentStage.goal }}</span>
        <button type="button" :disabled="selectedStageIndex === stages.length - 1" @click="goNext">
          下个里程碑<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9.5 5 7 7-7 7" /></svg>
        </button>
      </div>
    </aside>

    <Transition name="toast">
      <div v-if="toastText" class="learning-toast" role="status">{{ toastText }}</div>
    </Transition>

    <Transition name="resource-dialog">
      <div v-if="resourcePreview" class="resource-dialog" role="dialog" aria-modal="true" :aria-label="resourcePreview.resource.title" @click.self="closeResource">
        <section>
          <header>
            <div><span>MILESTONE {{ currentStage.id }} TASK</span><h2>{{ resourcePreview.resource.title }}</h2></div>
            <button type="button" aria-label="关闭资源预览" @click="closeResource"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18" /></svg></button>
          </header>
          <video v-if="resourcePreview.mode === 'video'" src="/learning-path/cosmic-learning-path.mp4" controls autoplay playsinline></video>
          <div v-else class="document-preview">
            <span>{{ resourcePreview.resource.typeLabel }}</span>
            <h3>{{ resourcePreview.resource.summaryTitle }}</h3>
            <p>{{ resourcePreview.resource.summary }}</p>
            <ul><li v-for="point in resourcePreview.resource.points" :key="point">{{ point }}</li></ul>
          </div>
          <footer>
            <span>预计学习 {{ resourcePreview.resource.time }}</span>
            <button type="button" @click="addToPlan(resourcePreview.resource)">加入本周计划</button>
          </footer>
        </section>
      </div>
    </Transition>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

type ResourceKind = 'document' | 'video' | 'lab'

type StageResource = {
  title: string
  kind: ResourceKind
  typeLabel: string
  time: string
  summaryTitle: string
  summary: string
  points: string[]
}

type LearningStage = {
  id: number
  kicker: string
  mapTitle: string
  mapSubtitle: string
  title: string
  description: string
  mastery: number
  domain: string
  tasks: number
  duration: string
  goal: string
  color: string
  rgb: string
  left: string
  top: string
  nodeCode: string
  nodeTag: string
  skillTags: string[]
  labelSide: 'left' | 'right'
  resources: StageResource[]
}

const emit = defineEmits<{ close: [] }>()
const props = withDefaults(defineProps<{
  targetJob?: string
  matchScore?: number
  suggestions?: string[]
  tasks?: any[]
  resources?: any[]
}>(), {
  targetJob: '',
  matchScore: 0,
  suggestions: () => [],
  tasks: () => [],
  resources: () => [],
})
const targetJob = computed(() => props.targetJob)
const matchScore = computed(() => Math.max(0, Math.min(100, Number(props.matchScore || 0))))
const suggestions = computed(() => props.suggestions)
const tasks = computed(() => props.tasks)
const resources = computed(() => props.resources)
const backgroundVideo = ref<HTMLVideoElement | null>(null)
const videoMuted = ref(true)
const videoBlocked = ref(false)
const selectedStageIndex = ref(0)
const startedStages = ref(new Set<number>())
const resourcePreview = ref<{ resource: StageResource; mode: 'document' | 'video' } | null>(null)
const toastText = ref('')
const routeMode = ref<'稳健成长' | '冲刺就业'>('稳健成长')
let toastTimer = 0

const stages: LearningStage[] = [
  {
    id: 1, kicker: 'AI 岗位路径 · 起点', mapTitle: '岗位定位', mapSubtitle: '锁定目标 / 解析需求', title: '目标岗位解码 / 建立能力坐标',
    description: '从招聘岗位知识图谱中解析真实需求，结合个人画像锁定目标岗位与核心能力差距。', mastery: 18, domain: '岗位知识图谱', tasks: 3, duration: '1 周', goal: '完成目标岗位画像',
    color: '#18dcf5', rgb: '24, 220, 245', left: '14.5%', top: '82%', nodeCode: 'START', nodeTag: '目标锚点', skillTags: ['岗位画像', '差距诊断'], labelSide: 'right',
    resources: [
      { title: 'AI 算法工程师岗位画像', kind: 'document', typeLabel: '岗位报告', time: '12 分钟', summaryTitle: '看清目标岗位的能力结构', summary: '聚合岗位职责、技能要求和成长趋势，形成可执行的岗位画像。', points: ['核心技能权重', '常见学历与经验要求', '岗位发展方向'] },
      { title: '招聘需求趋势解读', kind: 'video', typeLabel: '趋势视频', time: '10 分钟', summaryTitle: '岗位市场正在需要什么', summary: '基于行业招聘数据观察 AI 岗位需求与技能热度变化。', points: ['高频技能变化', '行业需求分布', '薪资与经验关联'] },
      { title: '个人能力基线测评', kind: 'lab', typeLabel: 'AI 测评', time: '20 分钟', summaryTitle: '建立当前能力坐标', summary: '通过结构化测评生成个人能力基线，为后续路径规划提供依据。', points: ['知识掌握度', '项目经验强度', '岗位能力差距'] },
    ],
  },
  {
    id: 2, kicker: 'AI 岗位路径 · 补强', mapTitle: '能力补强', mapSubtitle: '补齐差距 / 核心技能', title: '核心技能筑基 / 缩小岗位差距',
    description: '依据岗位技能权重与个人薄弱项，优先补齐 Python、机器学习和数据处理等高价值能力。', mastery: 42, domain: 'Python·机器学习', tasks: 4, duration: '3 周', goal: '补齐 3 项核心差距',
    color: '#38d7e8', rgb: '56, 215, 232', left: '34%', top: '62%', nodeCode: 'SKILL', nodeTag: '能力引擎', skillTags: ['Python', 'ML'], labelSide: 'right',
    resources: [
      { title: 'Python 工程化训练营', kind: 'lab', typeLabel: '技能实训', time: '40 分钟', summaryTitle: '把基础语法升级为工程能力', summary: '围绕真实数据任务训练代码结构、调试和工程规范。', points: ['模块化开发', '异常与日志', '代码质量检查'] },
      { title: '机器学习核心算法图谱', kind: 'video', typeLabel: '知识图谱', time: '25 分钟', summaryTitle: '串联算法与应用场景', summary: '用知识图谱理解常见算法之间的关系和岗位应用边界。', points: ['监督与无监督学习', '模型选择逻辑', '评估指标体系'] },
      { title: 'SQL 与数据处理实战', kind: 'document', typeLabel: '实战指南', time: '30 分钟', summaryTitle: '补齐数据处理高频要求', summary: '针对招聘高频场景完成数据查询、清洗和指标分析。', points: ['多表关联', '窗口函数', '数据质量处理'] },
    ],
  },
  {
    id: 3, kicker: 'AI 岗位路径 · 实战', mapTitle: '项目实战', mapSubtitle: '真实任务 / 证据沉淀', title: '项目能力验证 / 生成成长证据',
    description: '把已掌握技能放进真实项目情境，用可验证的代码、指标和成果证明岗位胜任力。', mastery: 67, domain: '项目实践', tasks: 3, duration: '4 周', goal: '完成可展示项目',
    color: '#0aa9b4', rgb: '37, 141, 255', left: '55%', top: '74%', nodeCode: 'BUILD', nodeTag: '项目跃迁', skillTags: ['项目证据', '协作'], labelSide: 'right',
    resources: [
      { title: '岗位技能知识图谱构建', kind: 'lab', typeLabel: '核心项目', time: '6 小时', summaryTitle: '把技能关系转化为可用产品', summary: '完成岗位、技能、课程三类实体建模与可视化分析。', points: ['图谱数据建模', '关系抽取与清洗', '可视化交互'] },
      { title: 'AI 项目评审清单', kind: 'video', typeLabel: '评审指南', time: '18 分钟', summaryTitle: '用企业标准检查项目', summary: '从业务价值、技术深度和可解释性三个维度评估项目。', points: ['问题定义', '技术方案', '量化结果'] },
      { title: 'GitHub 作品集包装', kind: 'document', typeLabel: '作品集', time: '35 分钟', summaryTitle: '让项目证据可被快速理解', summary: '将代码、数据、演示和结果组织为专业作品集。', points: ['README 叙事', '架构与演示图', '成果指标'] },
    ],
  },
  {
    id: 4, kicker: 'AI 岗位路径 · 验收', mapTitle: '岗位验收', mapSubtitle: '模拟面试 / 能力复测', title: '岗位能力验收 / 更新匹配画像',
    description: '通过岗位化测评和 AI 模拟面试检验技术表达、问题解决和项目解释能力。', mastery: 84, domain: '测评与面试', tasks: 3, duration: '2 周', goal: '岗位匹配达到 85%',
    color: '#377dff', rgb: '55, 125, 255', left: '70%', top: '45%', nodeCode: 'CHECK', nodeTag: '岗位闸门', skillTags: ['技术面', '复测'], labelSide: 'left',
    resources: [
      { title: '算法岗技术面试题库', kind: 'document', typeLabel: '岗位题库', time: '30 分钟', summaryTitle: '覆盖高频技术考点', summary: '根据目标岗位能力图谱生成个性化技术面试题。', points: ['算法与数据结构', '机器学习原理', '项目深挖问题'] },
      { title: 'AI 模拟面试', kind: 'lab', typeLabel: '智能测评', time: '25 分钟', summaryTitle: '在真实压力下练表达', summary: 'AI 面试官根据回答动态追问并生成结构化反馈。', points: ['表达清晰度', '技术准确度', '问题分析过程'] },
      { title: '能力差距复测报告', kind: 'video', typeLabel: '诊断报告', time: '15 分钟', summaryTitle: '验证路径带来的能力变化', summary: '对比起点画像与当前能力证据，更新岗位匹配度。', points: ['能力增量', '剩余差距', '冲刺建议'] },
    ],
  },
  {
    id: 5, kicker: 'AI 岗位路径 · 转化', mapTitle: '求职冲刺', mapSubtitle: '精准投递 / 成果转化', title: '求职成果交付 / 打通岗位出口',
    description: '把能力图谱中的成长证据转化为简历、作品集和精准岗位机会，形成完整就业闭环。', mastery: 96, domain: '就业转化', tasks: 3, duration: '持续优化', goal: '完成岗位转化',
    color: '#55dfff', rgb: '85, 223, 255', left: '85.5%', top: '21.5%', nodeCode: 'GOAL', nodeTag: '目标抵达', skillTags: ['岗位机会', '成果转化'], labelSide: 'left',
    resources: [
      { title: '岗位机会雷达', kind: 'lab', typeLabel: '智能匹配', time: '15 分钟', summaryTitle: '从海量岗位中找到高匹配机会', summary: '综合技能、项目和偏好生成优先投递清单。', points: ['岗位匹配评分', '发展潜力', '投递优先级'] },
      { title: '简历技能证据优化', kind: 'document', typeLabel: '简历助手', time: '25 分钟', summaryTitle: '让每项技能都有证据', summary: '把项目成果和能力提升转化为可量化的简历表达。', points: ['成果量化', '关键词对齐', '项目亮点提炼'] },
      { title: '面试复盘与路径迭代', kind: 'video', typeLabel: '成长复盘', time: '18 分钟', summaryTitle: '让每次面试反哺成长路径', summary: '记录面试反馈并自动更新能力差距与后续任务。', points: ['问题归因', '证据补强', '路径动态重排'] },
    ],
  },
]

const currentStage = computed(() => {
  const base = stages[selectedStageIndex.value]
  const liveResources: StageResource[] = props.resources.slice(0, 3).map((item: any) => ({
    title: item.title,
    kind: 'document',
    typeLabel: '真实学习专题',
    time: `进度 ${Math.round(Number(item.progress || 0))}%`,
    summaryTitle: item.title,
    summary: `该专题由匹配报告 #${item.source_report_id || '-'} 的技能差距生成。`,
    points: [`当前进度 ${Math.round(Number(item.progress || 0))}%`, '进度将保存到当前账号'],
  }))
  return {
    ...base,
    title: props.targetJob ? `${props.targetJob} / ${base.mapTitle}` : base.title,
    description: props.suggestions[selectedStageIndex.value] || base.description,
    mastery: props.matchScore || base.mastery,
    tasks: props.tasks.length || base.tasks,
    resources: liveResources.length ? liveResources : base.resources,
  }
})
const phaseNumber = computed(() => String(currentStage.value.id).padStart(2, '0'))
const routeEstimate = computed(() => routeMode.value === '稳健成长' ? '10 周' : '7 周')
const routeProgress = computed(() => `${Math.max(4, selectedStageIndex.value / (stages.length - 1) * 100)}`)
const masteryStyle = computed(() => ({
  '--mastery-angle': `${currentStage.value.mastery * 3.6}deg`,
  '--stage-color': currentStage.value.color,
  '--stage-rgb': currentStage.value.rgb,
}))

function routeNodeStyle(stage: LearningStage) {
  return {
    left: stage.left,
    top: stage.top,
    '--stage-color': stage.color,
    '--stage-rgb': stage.rgb,
  }
}

function selectStage(index: number) {
  selectedStageIndex.value = index
  showToast(`已定位成长里程碑 ${stages[index].id} · ${stages[index].mapTitle}`)
}

function replanRoute() {
  routeMode.value = routeMode.value === '稳健成长' ? '冲刺就业' : '稳健成长'
  showToast(`AI 已切换为“${routeMode.value}”规划策略，预计 ${routeEstimate.value} 达成目标岗位`)
}

function startCurrentStage() {
  const next = new Set(startedStages.value)
  if (next.has(currentStage.value.id)) {
    showToast(`${currentStage.value.mapTitle}任务正在执行中`)
  } else {
    next.add(currentStage.value.id)
    startedStages.value = next
    showToast(`已启动成长里程碑 ${currentStage.value.id} · ${currentStage.value.mapTitle}`)
  }
}

function openResource(resource: StageResource, mode: ResourceKind) {
  resourcePreview.value = { resource, mode: mode === 'video' ? 'video' : 'document' }
}

function closeResource() {
  resourcePreview.value = null
}

function addToPlan(resource: StageResource) {
  closeResource()
  showToast(`“${resource.title}”已加入本周计划`)
}

function goPrevious() {
  if (selectedStageIndex.value > 0) selectStage(selectedStageIndex.value - 1)
}

function goNext() {
  if (selectedStageIndex.value < stages.length - 1) selectStage(selectedStageIndex.value + 1)
}

function showToast(message: string) {
  window.clearTimeout(toastTimer)
  toastText.value = message
  toastTimer = window.setTimeout(() => { toastText.value = '' }, 2200)
}

async function resumeBackground() {
  try {
    await backgroundVideo.value?.play()
    videoBlocked.value = false
  } catch {
    videoBlocked.value = true
  }
}

async function toggleSound() {
  if (!backgroundVideo.value) return
  videoMuted.value = !videoMuted.value
  backgroundVideo.value.muted = videoMuted.value
  await resumeBackground()
  showToast(videoMuted.value ? '背景声音已关闭' : '背景声音已打开')
}

onMounted(async () => {
  await resumeBackground()
})

onBeforeUnmount(() => window.clearTimeout(toastTimer))
</script>

<style scoped>
.learning-mission {
  position: fixed;
  inset: 0;
  z-index: 140;
  display: grid;
  grid-template-columns: minmax(0, 1.92fr) minmax(500px, 1fr);
  gap: 0;
  padding: 10px 12px;
  overflow: hidden;
  background: #061122;
  color: #f4f7fb;
  font-family: "Microsoft YaHei", "Noto Sans SC", sans-serif;
}

.learning-space,
.learning-console { position: relative; min-width: 0; min-height: 0; overflow: hidden; }
.learning-space { border: 1px solid rgba(46, 169, 221, .32); border-radius: 20px 0 0 20px; background: #061426; }
.learning-space__video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.learning-space__wash { position: absolute; inset: 0; background: linear-gradient(90deg, rgba(2, 11, 27, .16), rgba(3, 15, 34, .08) 48%, rgba(3, 12, 29, .38)), linear-gradient(180deg, rgba(1, 8, 19, .12), transparent 42%, rgba(2, 9, 22, .18)); }
.learning-space__stars { position: absolute; inset: 0; opacity: .28; background-image: radial-gradient(circle, rgba(150, 226, 255, .9) 0 1px, transparent 1.4px); background-size: 46px 46px; mask-image: linear-gradient(180deg, #000, transparent 84%); pointer-events: none; }

.learning-back,
.learning-sound,
.video-unlock { position: absolute; z-index: 8; border: 1px solid rgba(59, 213, 248, .44); background: rgba(3, 15, 34, .74); color: #daf8ff; backdrop-filter: blur(12px); cursor: pointer; }
.learning-back { top: 20px; left: 22px; display: flex; align-items: center; gap: 8px; border-radius: 9px; padding: 10px 14px; font: inherit; font-size: 13px; }
.learning-back svg,.learning-sound svg,.video-unlock svg { width: 19px; fill: none; stroke: #1ed7f4; stroke-width: 1.9; }
.learning-back:hover,.learning-sound:hover { border-color: #17d8f3; background: rgba(8, 42, 67, .84); }
.learning-sound { right: 20px; bottom: 18px; display: grid; place-items: center; width: 42px; height: 42px; border-radius: 50%; }
.video-unlock { top: 50%; left: 50%; display: flex; align-items: center; gap: 9px; border-radius: 8px; padding: 12px 18px; transform: translate(-50%, -50%); font: inherit; }

.path-planner { position: absolute; inset: 0; z-index: 3; overflow: hidden; }
.planner-head { position: absolute; z-index: 7; top: 84px; left: 28px; width: min(470px, 44%); border-left: 2px solid #17d9f3; padding: 2px 0 2px 18px; }
.planner-eyebrow { display: flex; align-items: center; gap: 9px; color: #a9bdce; font: 700 9px/1 Bahnschrift, Consolas, sans-serif; letter-spacing: .14em; }
.planner-eyebrow span { color: #20def5; }.planner-eyebrow i { width: 28px; height: 1px; background: rgba(32, 222, 245, .54); }.planner-eyebrow b { font-weight: 500; }
.planner-title-row { display: flex; align-items: flex-end; justify-content: space-between; gap: 18px; margin-top: 13px; }
.planner-title-row small { color: #8ba1b5; font-size: 11px; }.planner-title-row h2 { margin: 5px 0 0; color: #f5fcff; font-size: clamp(24px, 2vw, 34px); line-height: 1; letter-spacing: -.02em; text-shadow: 0 0 24px rgba(41, 215, 244, .16); }
.replan-button { display: flex; flex-shrink: 0; align-items: center; gap: 7px; border: 1px solid rgba(38, 216, 243, .36); border-radius: 7px; padding: 9px 11px; background: rgba(3, 22, 42, .72); color: #b9f5ff; font: inherit; font-size: 10px; cursor: pointer; backdrop-filter: blur(10px); transition: .22s ease; }
.replan-button svg { width: 15px; fill: none; stroke: #29dcf5; stroke-width: 1.7; }.replan-button:hover { border-color: #20dff5; background: rgba(10, 59, 79, .78); box-shadow: 0 0 22px rgba(25, 216, 242, .18); transform: translateY(-2px); }
.planner-metrics { display: flex; gap: 8px; margin-top: 16px; }
.planner-metrics > span { min-width: 104px; border: 1px solid rgba(122, 217, 237, .13); border-radius: 6px; padding: 9px 11px; background: linear-gradient(135deg, rgba(5, 29, 53, .72), rgba(4, 18, 38, .48)); backdrop-filter: blur(8px); }
.planner-metrics small,.planner-metrics strong { display: block; }.planner-metrics small { color: #738da3; font-size: 9px; }.planner-metrics strong { margin-top: 5px; color: #effcff; font: 700 14px/1 Bahnschrift, "Microsoft YaHei", sans-serif; }

.stage-map { --route-progress: 4; position: absolute; inset: 155px 0 62px; }
.career-route { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }
.route-line { fill: none; stroke-linecap: round; stroke-linejoin: round; vector-effect: non-scaling-stroke; }
.route-line--halo { stroke: rgba(55, 204, 243, .15); stroke-width: 24; filter: url(#careerRouteGlow); }
.route-line--base { stroke: rgba(170, 222, 240, .28); stroke-width: 2; stroke-dasharray: 3 9; }
.route-line--progress { stroke: url(#careerRouteGradient); stroke-width: 5; stroke-dasharray: var(--route-progress) 100; filter: url(#careerRouteGlow); transition: stroke-dasharray .65s cubic-bezier(.2,.75,.2,1); }
.route-particle { fill: #dffcff; filter: url(#careerRouteGlow); }.route-particle--two { fill: #55dfff; }
.route-node {
  --stage-color: #18dcf5;
  --stage-rgb: 24, 220, 245;
  --node-anchor: 34px;
  position: absolute;
  z-index: 4;
  display: flex;
  align-items: center;
  gap: 11px;
  border: 0;
  padding: 0;
  background: transparent;
  color: #f5fbff;
  text-align: left;
  cursor: pointer;
  transform: translate(calc(var(--node-anchor) * -1), -50%);
  transform-origin: var(--node-anchor) 50%;
  transition: transform .28s ease, filter .28s ease;
}
.route-node.label-left { flex-direction: row-reverse; text-align: right; transform: translate(calc(-100% + var(--node-anchor)), -50%); transform-origin: calc(100% - var(--node-anchor)) 50%; }
.route-node:hover,.route-node.active { z-index: 6; transform: translate(calc(var(--node-anchor) * -1), -50%) scale(1.055); filter: drop-shadow(0 12px 22px rgba(0,0,0,.35)); }
.route-node.label-left:hover,.route-node.label-left.active { transform: translate(calc(-100% + var(--node-anchor)), -50%) scale(1.055); }
.route-node__core { position: relative; display: grid; width: 68px; height: 68px; flex: 0 0 68px; place-items: center; align-content: center; border: 1px solid var(--stage-color); border-radius: 50%; background: radial-gradient(circle, rgba(var(--stage-rgb), .24), rgba(3, 20, 42, .88) 62%); box-shadow: 0 0 0 7px rgba(var(--stage-rgb), .06), 0 0 24px rgba(var(--stage-rgb), .28), inset 0 0 18px rgba(var(--stage-rgb), .12); transition: .28s ease; }
.route-node__core::before,.route-node__core::after { position: absolute; border: 1px solid rgba(var(--stage-rgb), .32); border-radius: 50%; content: ""; }.route-node__core::before { inset: -8px; border-style: dashed; animation: routeOrbit 9s linear infinite; }.route-node__core::after { top: -5px; left: 50%; width: 8px; height: 8px; border: 0; background: var(--stage-color); box-shadow: 0 0 12px var(--stage-color); transform: translateX(-50%); }
.route-node__core small { color: rgba(228, 249, 255, .6); font: 700 9px/1 Bahnschrift, sans-serif; letter-spacing: .12em; }.route-node__core strong { margin-top: 5px; color: var(--stage-color); font: 800 11px/1 Bahnschrift, sans-serif; letter-spacing: .08em; }
.route-node__copy { position: relative; display: flex; width: 174px; flex-direction: column; border: 1px solid rgba(var(--stage-rgb), .22); border-radius: 8px; padding: 10px 12px; background: linear-gradient(110deg, rgba(4, 23, 47, .88), rgba(5, 18, 39, .58)); box-shadow: inset 0 1px rgba(255,255,255,.04); backdrop-filter: blur(10px); }
.route-node__copy::before { position: absolute; top: 50%; right: 100%; width: 11px; height: 1px; background: var(--stage-color); opacity: .65; content: ""; }.route-node.label-left .route-node__copy::before { right: auto; left: 100%; }
.route-node__copy > em { color: var(--stage-color); font: normal 700 8px/1 Bahnschrift, "Microsoft YaHei", sans-serif; letter-spacing: .13em; }.route-node__copy > strong { margin-top: 6px; font-size: 16px; line-height: 1.1; }.route-node__copy > small { margin-top: 5px; color: #91a7ba; font-size: 9px; letter-spacing: .05em; }
.route-node__skills { display: flex; gap: 5px; margin-top: 8px; }.route-node.label-left .route-node__skills { justify-content: flex-end; }.route-node__skills i { border: 1px solid rgba(var(--stage-rgb), .2); border-radius: 3px; padding: 3px 5px; color: rgba(213, 244, 250, .7); font: normal 8px/1 "Microsoft YaHei", sans-serif; }
.route-node:hover .route-node__core,.route-node.active .route-node__core { background: radial-gradient(circle, rgba(var(--stage-rgb), .46), rgba(3, 20, 42, .9) 66%); box-shadow: 0 0 0 10px rgba(var(--stage-rgb), .08), 0 0 34px rgba(var(--stage-rgb), .5), inset 0 0 22px rgba(var(--stage-rgb), .22); }
.route-node.active .route-node__copy { border-color: rgba(var(--stage-rgb), .72); background: linear-gradient(110deg, rgba(var(--stage-rgb), .2), rgba(4, 18, 39, .82)); }.route-node.started .route-node__core::after { background: #70f2b3; box-shadow: 0 0 13px #70f2b3; }
.planner-foot { position: absolute; right: 24px; bottom: 20px; left: 28px; z-index: 5; display: flex; align-items: center; justify-content: space-between; border-top: 1px solid rgba(111, 210, 233, .15); padding-top: 12px; color: #7893a8; font: 600 9px/1 Bahnschrift, "Microsoft YaHei", sans-serif; letter-spacing: .07em; }.planner-foot span { display: flex; align-items: center; gap: 8px; }.planner-foot i { width: 6px; height: 6px; border-radius: 50%; background: #49efbc; box-shadow: 0 0 10px #49efbc; }.planner-foot strong { color: #9eb3c3; font-weight: 600; }
@keyframes routeOrbit { to { transform: rotate(360deg); } }

.learning-console {
  border: 1px solid rgba(0, 203, 236, .56);
  border-radius: 20px;
  margin-left: -1px;
  padding: clamp(28px, 2.35vw, 48px) clamp(28px, 2.1vw, 44px) 24px;
  overflow-y: auto;
  background: radial-gradient(circle at 82% 8%, rgba(0, 161, 202, .12), transparent 33%), linear-gradient(150deg, rgba(4, 14, 31, .98), rgba(4, 19, 38, .97));
  box-shadow: -25px 0 60px rgba(0, 0, 0, .3);
}
.learning-console::before { content: ""; position: absolute; inset: 0; opacity: .13; background-image: linear-gradient(rgba(41, 204, 235, .12) 1px, transparent 1px), linear-gradient(90deg, rgba(41, 204, 235, .1) 1px, transparent 1px); background-size: 44px 44px; pointer-events: none; }
.learning-console > * { position: relative; z-index: 1; }
.learning-console::-webkit-scrollbar { width: 5px; }.learning-console::-webkit-scrollbar-thumb { border-radius: 4px; background: rgba(29, 208, 240, .38); }
.console-topline { display: flex; align-items: center; justify-content: space-between; color: #04d8f5; font-family: Georgia, "Microsoft YaHei", serif; font-size: 13px; font-weight: 700; letter-spacing: .08em; }
.console-topline strong { font-size: 12px; letter-spacing: .13em; }
.console-hero { display: grid; grid-template-columns: 1fr 126px; align-items: center; gap: 20px; margin-top: 34px; }
.console-hero h1 { margin: 0; font-size: clamp(30px, 2.25vw, 44px); line-height: 1.16; letter-spacing: -.035em; }
.console-hero p { max-width: 520px; margin: 15px 0 0; color: #98a6bb; font-size: 15px; line-height: 1.75; }
.mastery-ring { display: grid; place-items: center; width: 122px; aspect-ratio: 1; border-radius: 50%; background: conic-gradient(var(--stage-color) var(--mastery-angle), rgba(var(--stage-rgb), .1) 0); box-shadow: 0 0 28px rgba(var(--stage-rgb), .13); }
.mastery-ring::before { content: ""; grid-area: 1/1; width: 116px; aspect-ratio: 1; border-radius: 50%; background: #07162c; }
.mastery-ring div { grid-area: 1/1; position: relative; text-align: center; }.mastery-ring strong { display: block; font-family: Georgia, serif; font-size: 27px; }.mastery-ring span { display: block; margin-top: 8px; color: #8695aa; font-size: 12px; }

.stage-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 13px; margin-top: 28px; }
.stage-stats article { border: 1px solid rgba(122, 153, 183, .15); border-radius: 10px; padding: 17px 16px; background: linear-gradient(135deg, rgba(255,255,255,.055), rgba(255,255,255,.018)); }.stage-stats span { display: block; color: #728197; font-size: 12px; }.stage-stats strong { display: block; margin-top: 12px; color: #eef4fa; font-size: 17px; }
.phase-switcher { position: relative; display: flex; justify-content: space-between; margin: 30px 8px 0; }.phase-switcher::before { content: ""; position: absolute; top: 50%; right: 4%; left: 4%; height: 1px; background: linear-gradient(90deg, #0dd8f4, #0aa9b4 52%, #55dfff); }.phase-switcher button { position: relative; z-index: 1; display: grid; place-items: center; width: 47px; height: 47px; border: 1px solid rgba(39, 205, 236, .42); border-radius: 50%; background: #07162c; color: #d6e0eb; font: inherit; font-size: 16px; cursor: pointer; transition: .25s ease; }.phase-switcher button:nth-child(3),.phase-switcher button:nth-child(n+4) { border-color: rgba(55, 160, 255, .55); }.phase-switcher button:hover,.phase-switcher button.active { border-color: #11d8f4; background: #12d7f2; color: #041221; box-shadow: 0 0 22px rgba(18, 215, 242, .65); transform: scale(1.06); }.phase-switcher button.started::after { content: ""; position: absolute; top: -3px; right: -1px; width: 8px; height: 8px; border-radius: 50%; background: #52ddff; box-shadow: 0 0 8px #52ddff; }
.resource-heading { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-top: 29px; }.resource-heading h2 { margin: 0; font-size: 18px; }.start-stage { display: flex; align-items: center; gap: 8px; border: 0; border-radius: 9px; padding: 12px 16px; background: linear-gradient(135deg, #10c8ee, #0aa9b4); color: #03111f; font: inherit; font-size: 13px; font-weight: 800; cursor: pointer; box-shadow: 0 12px 28px rgba(2, 183, 224, .18); }.start-stage svg { width: 19px; fill: none; stroke: currentColor; stroke-width: 1.8; }.start-stage:hover { transform: translateY(-2px); box-shadow: 0 16px 32px rgba(2, 197, 235, .3); }.start-stage.active { background: linear-gradient(135deg, #55dfff, #0aa9b4); }
.resource-list { display: flex; flex-direction: column; gap: 11px; margin-top: 15px; }.resource-list article { display: grid; grid-template-columns: 34px 1fr auto; align-items: center; gap: 8px; border: 1px solid rgba(100, 127, 159, .17); border-radius: 10px; padding: 12px 13px; background: rgba(4, 12, 28, .62); cursor: pointer; transition: .22s ease; }.resource-list article:hover,.resource-list article:focus { border-color: rgba(18, 215, 242, .48); background: rgba(9, 27, 49, .84); outline: none; transform: translateX(-3px); }.resource-index { color: #08d7f4; font-family: Georgia, serif; font-size: 13px; font-weight: 700; }.resource-copy { display: flex; min-width: 0; flex-direction: column; }.resource-copy strong { overflow: hidden; font-size: 13px; text-overflow: ellipsis; white-space: nowrap; }.resource-copy small { margin-top: 5px; color: #7f8da1; font-size: 11px; }.resource-actions { display: flex; gap: 7px; }.resource-actions button { display: grid; place-items: center; width: 36px; height: 36px; border: 1px solid rgba(121, 146, 178, .18); border-radius: 8px; background: rgba(255,255,255,.04); color: #b8c9d9; cursor: pointer; }.resource-actions button:hover { border-color: #13d7f2; color: #13d7f2; background: rgba(16, 193, 229, .09); }.resource-actions svg { width: 19px; fill: none; stroke: currentColor; stroke-width: 1.7; }
.console-nav { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 12px; margin-top: 18px; border-top: 1px solid rgba(95, 125, 155, .14); padding-top: 14px; }.console-nav button { display: flex; align-items: center; gap: 5px; border: 0; background: transparent; color: #8da1b6; font: inherit; font-size: 11px; cursor: pointer; }.console-nav button:hover:not(:disabled) { color: #13d7f2; }.console-nav button:disabled { opacity: .3; cursor: not-allowed; }.console-nav svg { width: 15px; fill: none; stroke: currentColor; stroke-width: 1.8; }.console-nav span { overflow: hidden; color: #63768b; font-size: 10px; text-align: center; text-overflow: ellipsis; white-space: nowrap; }

.learning-toast { position: fixed; z-index: 220; bottom: 28px; left: 50%; border: 1px solid rgba(18, 215, 242, .5); border-radius: 8px; padding: 12px 20px; background: rgba(4, 19, 38, .95); color: #e9fbff; box-shadow: 0 15px 40px rgba(0,0,0,.36), 0 0 25px rgba(18,215,242,.15); transform: translateX(-50%); font-size: 13px; }
.toast-enter-active,.toast-leave-active { transition: .25s ease; }.toast-enter-from,.toast-leave-to { opacity: 0; transform: translate(-50%, 15px); }
.resource-dialog { position: fixed; inset: 0; z-index: 210; display: grid; place-items: center; padding: 24px; background: rgba(1, 7, 18, .78); backdrop-filter: blur(14px); }.resource-dialog > section { width: min(680px, 92vw); overflow: hidden; border: 1px solid rgba(21, 214, 243, .44); border-radius: 15px; background: linear-gradient(145deg, #07172e, #050e20); box-shadow: 0 30px 90px rgba(0,0,0,.52); }.resource-dialog header { display: flex; align-items: flex-start; justify-content: space-between; border-bottom: 1px solid rgba(100, 132, 164, .15); padding: 22px 24px; }.resource-dialog header span { color: #11d7f2; font-size: 10px; letter-spacing: .13em; }.resource-dialog h2 { margin: 7px 0 0; font-size: 22px; }.resource-dialog header button { display: grid; place-items: center; width: 36px; height: 36px; border: 1px solid rgba(137, 163, 190, .2); border-radius: 8px; background: rgba(255,255,255,.035); color: #c8d5e1; cursor: pointer; }.resource-dialog header svg { width: 18px; fill: none; stroke: currentColor; stroke-width: 1.8; }.resource-dialog video { display: block; width: 100%; max-height: 360px; background: #020817; }.document-preview { padding: 28px 30px 24px; }.document-preview > span { color: #10d8f3; font-size: 11px; }.document-preview h3 { margin: 12px 0 8px; font-size: 22px; }.document-preview p { margin: 0; color: #96a7ba; font-size: 14px; line-height: 1.7; }.document-preview ul { display: grid; gap: 10px; margin: 22px 0 0; padding: 0; list-style: none; }.document-preview li { position: relative; border-left: 2px solid #10d8f3; padding-left: 13px; color: #d1dde7; font-size: 13px; }.resource-dialog footer { display: flex; align-items: center; justify-content: space-between; border-top: 1px solid rgba(100, 132, 164, .15); padding: 16px 24px; }.resource-dialog footer span { color: #71869a; font-size: 12px; }.resource-dialog footer button { border: 0; border-radius: 8px; padding: 10px 15px; background: #10c9e9; color: #04111e; font: inherit; font-size: 12px; font-weight: 800; cursor: pointer; }.resource-dialog-enter-active,.resource-dialog-leave-active { transition: opacity .25s ease; }.resource-dialog-enter-active > section,.resource-dialog-leave-active > section { transition: transform .28s ease; }.resource-dialog-enter-from,.resource-dialog-leave-to { opacity: 0; }.resource-dialog-enter-from > section,.resource-dialog-leave-to > section { transform: scale(.96) translateY(12px); }

@media (max-width: 1180px) {
  .learning-mission { grid-template-columns: minmax(0, 1.35fr) minmax(470px, 1fr); }.planner-head { width: 52%; }.route-node { --node-anchor: 30px; }.route-node__copy { width: 145px; }.route-node__skills { display: none; }.route-node__core { width: 60px; height: 60px; flex-basis: 60px; }.console-hero { grid-template-columns: 1fr 104px; }.mastery-ring { width: 102px; }.mastery-ring::before { width: 96px; }.stage-stats article { padding: 13px 11px; }
}
@media (max-width: 900px) {
  .learning-mission { position: absolute; display: block; padding: 8px; overflow-y: auto; }.learning-space { height: 700px; border-radius: 18px 18px 0 0; }.learning-console { min-height: 720px; margin: -1px 0 0; border-radius: 0 0 18px 18px; }.planner-head { width: min(470px, calc(100% - 56px)); }.stage-map { top: 160px; }.route-node__copy { width: 155px; }
}
@media (max-width: 620px) {
  .learning-space { height: 820px; }.planner-head { top: 82px; left: 18px; width: calc(100% - 36px); padding-left: 13px; }.planner-title-row { align-items: flex-start; }.planner-title-row h2 { font-size: 25px; }.planner-metrics > span { min-width: 0; flex: 1; padding: 8px; }.planner-metrics small { font-size: 8px; }.planner-metrics strong { font-size: 12px; }.replan-button { max-width: 120px; }.stage-map { inset: 220px 0 62px; }.route-node { --node-anchor: 24px; gap: 7px; }.route-node__copy { width: 122px; padding: 8px; }.route-node__copy > strong { font-size: 13px; }.route-node__copy > small { font-size: 8px; }.route-node__core { width: 48px; height: 48px; flex-basis: 48px; }.route-node__core::before { inset: -5px; }.planner-foot { right: 16px; left: 16px; }.planner-foot strong { display: none; }.learning-console { padding: 24px 18px; }.console-hero { grid-template-columns: 1fr; }.mastery-ring { position: absolute; top: 58px; right: 0; width: 86px; }.mastery-ring::before { width: 80px; }.mastery-ring strong { font-size: 21px; }.console-hero h1 { max-width: calc(100% - 95px); font-size: 28px; }.stage-stats { gap: 7px; }.stage-stats strong { font-size: 13px; }.resource-heading { align-items: flex-start; }.start-stage { padding: 10px 11px; font-size: 11px; }.resource-actions button { width: 32px; height: 32px; }.console-nav span { display: none; }.console-nav { grid-template-columns: 1fr 1fr; }.console-nav button:last-child { justify-self: end; }
}
@media (prefers-reduced-motion: reduce) { .learning-mission * { scroll-behavior: auto !important; transition-duration: .01ms !important; } }
</style>
