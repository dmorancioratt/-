<template>
  <Transition name="mission-cabin" appear>
    <section
      ref="shell"
      class="mission-cabin"
      :class="`mission-cabin--${config.visual}`"
      :style="themeStyle"
      :aria-label="config.title"
      tabindex="-1"
      @keydown.esc="emit('close')"
    >
      <div class="mission-cabin__veil" aria-hidden="true"></div>
      <div class="mission-cabin__grid" aria-hidden="true"></div>

      <header class="mission-header">
        <button class="mission-back" type="button" @click="emit('close')">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m14.5 5-7 7 7 7" /></svg>
          <span>返回驾驶舱</span>
        </button>

        <div class="mission-identity">
          <span class="mission-code">{{ config.code }}</span>
          <span class="mission-rule"></span>
          <div>
            <small>{{ config.english }}</small>
            <strong>{{ config.title }}</strong>
          </div>
        </div>

        <div class="mission-signal"><i></i><span>{{ config.status }}</span></div>
      </header>

      <div class="mission-layout">
        <aside class="mission-brief">
          <div class="mission-section-label"><span>01</span> MISSION BRIEF</div>
          <p class="mission-eyebrow">{{ config.eyebrow }}</p>
          <h1>{{ config.hero }}</h1>
          <p class="mission-summary">{{ config.summary }}</p>

          <div class="mission-progress-row">
            <div class="mission-progress" :style="progressStyle" role="progressbar" :aria-valuenow="config.progress" aria-valuemin="0" aria-valuemax="100">
              <div><strong>{{ config.progress }}</strong><span>%</span><small>{{ config.progressLabel }}</small></div>
            </div>
            <div class="mission-outcome">
              <span>EXPECTED OUTCOME</span>
              <p>{{ config.outcome }}</p>
            </div>
          </div>

          <div class="mission-metrics">
            <article v-for="metric in config.metrics" :key="metric.label">
              <span>{{ metric.label }}</span>
              <strong>{{ metric.value }}</strong>
              <small>{{ metric.delta }}</small>
            </article>
          </div>
        </aside>

        <main class="mission-visual" :aria-label="`${config.title}主视觉`">
          <div class="mission-section-label"><span>02</span> LIVE SYSTEM VIEW</div>

          <div class="visual-stage">
            <template v-if="config.visual === 'radar'">
              <div class="orbit-map">
                <div class="orbit-map__ring orbit-map__ring--one"></div>
                <div class="orbit-map__ring orbit-map__ring--two"></div>
                <div class="orbit-map__core"><small>CAPABILITY</small><strong>{{ config.progress }}</strong><span>LIVE SCORE</span></div>
                <button
                  v-for="(node, index) in config.nodes"
                  :key="node.id"
                  class="orbit-node"
                  :class="[`is-${node.state}`, { selected: selectedNode.id === node.id }]"
                  :style="orbitNodeStyle(index, config.nodes.length)"
                  type="button"
                  :aria-label="`${node.label} ${node.value}分`"
                  @click="selectNode(node.id)"
                >
                  <span>{{ node.short }}</span><b>{{ node.value }}</b>
                </button>
              </div>
            </template>

            <template v-else-if="config.visual === 'path'">
              <div class="route-map">
                <svg viewBox="0 0 760 260" preserveAspectRatio="none" aria-hidden="true">
                  <defs><linearGradient id="missionRoute" x1="0" x2="1"><stop stop-color="var(--mission-accent)"/><stop offset="1" stop-color="var(--mission-soft)"/></linearGradient></defs>
                  <path d="M36 184 C126 184 116 78 226 96 S332 210 424 166 S548 62 724 86" />
                  <path class="route-map__active" d="M36 184 C126 184 116 78 226 96 S332 210 424 166" />
                </svg>
                <button
                  v-for="(node, index) in config.nodes"
                  :key="node.id"
                  class="route-node"
                  :class="[`is-${node.state}`, { selected: selectedNode.id === node.id }]"
                  :style="routeNodeStyle(index)"
                  type="button"
                  @click="selectNode(node.id)"
                >
                  <span>{{ node.short }}</span><b>{{ node.label }}</b><small>{{ node.meta }}</small>
                </button>
              </div>
            </template>

            <template v-else-if="config.visual === 'profile'">
              <div class="profile-map">
                <div class="profile-avatar" aria-hidden="true">
                  <i class="profile-avatar__ring profile-avatar__ring--one"></i>
                  <i class="profile-avatar__ring profile-avatar__ring--two"></i>
                  <div class="profile-avatar__head"></div>
                  <div class="profile-avatar__body"></div>
                  <span>SB-2026-017</span>
                </div>
                <div class="profile-signals">
                  <button v-for="node in config.nodes" :key="node.id" type="button" :class="{ selected: selectedNode.id === node.id }" @click="selectNode(node.id)">
                    <span>{{ node.short }}</span><div><b>{{ node.label }}</b><small>{{ node.meta }}</small></div><strong>{{ node.value }}%</strong>
                  </button>
                </div>
              </div>
            </template>

            <template v-else-if="config.visual === 'resources'">
              <div class="resource-map">
                <button
                  v-for="(node, index) in config.nodes"
                  :key="node.id"
                  type="button"
                  :class="[`is-${node.state}`, { selected: selectedNode.id === node.id }]"
                  @click="selectNode(node.id)"
                >
                  <span class="resource-map__index">0{{ index + 1 }}</span>
                  <span class="resource-map__type">{{ node.short }}</span>
                  <b>{{ node.label }}</b>
                  <small>{{ node.meta }}</small>
                  <i><span :style="{ width: `${node.value}%` }"></span></i>
                  <em>QUALITY {{ node.value }}</em>
                </button>
              </div>
            </template>

            <template v-else-if="config.visual === 'ai'">
              <div class="ai-map">
                <div class="ai-map__halo ai-map__halo--one"></div>
                <div class="ai-map__halo ai-map__halo--two"></div>
                <div class="ai-map__core"><span>AI</span><b>DECISION</b><small>{{ config.progress }}% CONFIDENCE</small></div>
                <button
                  v-for="(node, index) in config.nodes"
                  :key="node.id"
                  type="button"
                  :class="{ selected: selectedNode.id === node.id }"
                  :style="aiNodeStyle(index)"
                  @click="selectNode(node.id)"
                ><span>{{ node.short }}</span><b>{{ node.value }}</b><small>{{ node.label }}</small></button>
              </div>
              <div class="ai-context-strip" aria-label="AI 决策真实数据概览">
                <article v-for="item in aiInsights" :key="item.label">
                  <span>{{ item.label }}</span>
                  <strong>{{ item.value }}</strong>
                  <small>{{ item.detail }}</small>
                </article>
              </div>
            </template>

            <template v-else-if="config.visual === 'calendar'">
              <div class="calendar-map">
                <button
                  v-for="node in config.nodes"
                  :key="node.id"
                  type="button"
                  :class="[`is-${node.state}`, { selected: selectedNode.id === node.id }]"
                  @click="selectNode(node.id)"
                >
                  <span>{{ node.short }}</span><b>{{ node.label }}</b><i><em :style="{ height: `${Math.max(node.value, 8)}%` }"></em></i><small>{{ node.meta }}</small>
                </button>
              </div>
            </template>

            <template v-else>
              <div class="achievement-map">
                <div class="achievement-map__rail"></div>
                <button
                  v-for="(node, index) in config.nodes"
                  :key="node.id"
                  type="button"
                  :class="[`is-${node.state}`, { selected: selectedNode.id === node.id }]"
                  @click="selectNode(node.id)"
                >
                  <span>0{{ index + 1 }}</span><i>{{ node.short }}</i><b>{{ node.label }}</b><small>{{ node.meta }}</small>
                </button>
              </div>
            </template>

            <div class="visual-readout" aria-live="polite">
              <span>{{ selectedNode.short }} / {{ selectedNode.state.toUpperCase() }}</span>
              <strong>{{ selectedNode.label }}</strong>
              <p>{{ selectedNode.meta }}</p>
              <b>{{ selectedNode.value }}<small>/100</small></b>
            </div>
          </div>
        </main>

        <aside class="mission-actions">
          <div class="mission-section-label"><span>03</span> ACTION RAIL</div>
          <div class="mission-action-head"><span>下一步任务</span><strong>{{ completedTasks }}/{{ tasks.length }}</strong></div>
          <div class="mission-task-list">
            <button v-for="task in tasks" :key="task.id" type="button" :class="{ done: task.done }" @click="toggleTask(task.id)">
              <i><svg v-if="task.done" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 4 4L19 7" /></svg></i>
              <span><b>{{ task.title }}</b><small>{{ task.meta }}</small></span>
            </button>
            <div v-if="!tasks.length" class="mission-task-empty">
              <span>当前账号尚无学习任务</span>
              <ol>
                <li><b>01</b><span>完成岗位匹配<small>生成真实匹配报告</small></span></li>
                <li><b>02</b><span>识别能力缺口<small>读取画像技能证据</small></span></li>
                <li><b>03</b><span>生成学习任务<small>进度保存到当前账号</small></span></li>
              </ol>
            </div>
          </div>

          <div class="mission-task-progress"><span :style="{ width: `${taskProgress}%` }"></span></div>

          <div class="mission-evidence">
            <span>AI DECISION BASIS</span>
            <ul><li v-for="item in config.evidence" :key="item">{{ item }}</li></ul>
          </div>

          <button class="mission-primary" type="button" @click="launchPrimaryAction">
            <span>{{ actionState || config.primaryAction }}</span>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-5-5 5 5-5 5" /></svg>
          </button>
        </aside>
      </div>

      <footer class="mission-footer">
        <span><i></i> LIVE DATA · CURRENT ACCOUNT</span>
        <span>{{ props.suggestions.length ? 'AI REASONING TRACE AVAILABLE' : 'WAITING FOR MATCH ANALYSIS' }}</span>
        <span>MISSION PROGRESS {{ taskProgress }}%</span>
      </footer>
    </section>
  </Transition>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { missionCabins, type MissionCabinId, type MissionNode } from './missionCabinData'

const props = withDefaults(defineProps<{
  moduleId: MissionCabinId
  liveTasks?: any[]
  liveResources?: any[]
  suggestions?: string[]
  profileSkills?: string[]
  matchScore?: number
}>(), {
  liveTasks: () => [],
  liveResources: () => [],
  suggestions: () => [],
  profileSkills: () => [],
  matchScore: 0,
})
const emit = defineEmits<{
  close: []
  primary: [payload: { id: MissionCabinId; route: string }]
  toggleTask: [task: any]
}>()

const shell = ref<HTMLElement | null>(null)
const aiInsights = computed(() => [
  { label: '最近匹配', value: props.matchScore ? `${props.matchScore}%` : '未生成', detail: '岗位匹配报告' },
  { label: '画像技能', value: String(props.profileSkills.length), detail: '当前账号技能证据' },
  { label: '学习任务', value: `${props.liveTasks.filter((item: any) => item.status === 'completed').length}/${props.liveTasks.length}`, detail: '后端持久化进度' },
  { label: '提升建议', value: String(props.suggestions.length), detail: props.suggestions[0] || '等待匹配分析' },
])
const config = computed(() => {
  const base = missionCabins[props.moduleId]
  const isPlan = props.moduleId === 'weekly-plan'
  const isResources = props.moduleId === 'resource-library'
  const placeholder: MissionNode = { id: 'empty', label: '暂无真实数据', short: 'WAIT', value: 0, state: 'active', meta: '完成岗位匹配后自动生成' }
  let nodes: MissionNode[] = props.moduleId === 'ai-suggest' ? [
    { id: 'match', label: '岗位匹配报告', short: 'JOB', value: props.matchScore, state: props.matchScore ? 'done' : 'active', meta: props.matchScore ? `最近匹配 ${props.matchScore}%` : '等待生成匹配报告' },
    { id: 'skills', label: '画像技能证据', short: 'SKILL', value: Math.min(100, props.profileSkills.length * 10), state: props.profileSkills.length ? 'done' : 'next', meta: `已同步 ${props.profileSkills.length} 项技能` },
    { id: 'tasks', label: '学习任务进度', short: 'TASK', value: props.liveTasks.length ? Math.round(props.liveTasks.filter((item: any) => item.status === 'completed').length / props.liveTasks.length * 100) : 0, state: props.liveTasks.length ? 'active' : 'next', meta: `当前 ${props.liveTasks.length} 项后端任务` },
    { id: 'advice', label: '报告提升建议', short: 'ADVICE', value: Math.min(100, props.suggestions.length * 25), state: props.suggestions.length ? 'active' : 'next', meta: props.suggestions[0] || '等待匹配分析' },
  ] : [placeholder]
  if (isResources && props.liveResources.length) {
    nodes = props.liveResources.slice(0, 6).map((item: any, index: number) => ({
        id: String(item.id), label: item.title, short: 'LIVE', value: Math.round(Number(item.progress || 0)),
        state: item.progress >= 100 ? 'done' as const : index === 0 ? 'active' as const : 'next' as const,
        meta: `匹配报告 #${item.source_report_id || '-'}`,
      }))
  } else if (isPlan && props.liveTasks.length) {
    nodes = props.liveTasks.slice(0, 6).map((item: any, index: number) => ({
      id: String(item.id), label: item.title, short: 'TASK', value: item.status === 'completed' ? 100 : 0,
      state: item.status === 'completed' ? 'done' as const : index === 0 ? 'active' as const : 'next' as const,
      meta: item.description || '当前账号学习任务',
    }))
  } else if (props.moduleId === 'radar' && props.profileSkills.length) {
    nodes = props.profileSkills.slice(0, 6).map((name, index) => ({
      id: `skill-${index}`, label: name, short: 'SKILL', value: 100,
      state: index === 0 ? 'active' as const : 'done' as const, meta: '当前账号画像技能',
    }))
  } else if (props.moduleId === 'ai-suggest' && props.suggestions.length) {
    nodes = props.suggestions.slice(0, 4).map((text, index) => ({
      id: `suggestion-${index}`, label: `建议 ${index + 1}`, short: 'AI', value: props.matchScore,
      state: index === 0 ? 'active' as const : 'next' as const, meta: text,
    }))
  }
  const tasks = props.liveTasks.length
    ? props.liveTasks.map((item: any) => ({ id: String(item.id), title: item.title, meta: item.description || '当前账号学习任务', done: item.status === 'completed', source: item }))
    : []
  const liveProgress = isPlan && props.liveTasks.length
    ? Math.round(props.liveTasks.filter((item: any) => item.status === 'completed').length / props.liveTasks.length * 100)
    : isResources && props.liveResources.length
      ? Math.round(props.liveResources.reduce((sum: number, item: any) => sum + Number(item.progress || 0), 0) / props.liveResources.length)
      : props.matchScore
  const hasLiveData = Boolean(props.matchScore || props.profileSkills.length || props.liveTasks.length || props.liveResources.length || props.suggestions.length)
  const completedCount = props.liveTasks.filter((item: any) => item.status === 'completed').length
  return {
    ...base,
    status: `${props.profileSkills.length + props.liveTasks.length + props.liveResources.length} LIVE RECORDS`,
    hero: props.suggestions[0] || (hasLiveData ? `当前账号已同步 ${props.profileSkills.length} 项技能、${props.liveTasks.length} 项任务和 ${props.liveResources.length} 个学习专题。` : '当前账号尚未生成本模块所需数据。'),
    summary: props.suggestions[1] || (props.matchScore ? `最近岗位匹配得分 ${props.matchScore}%，所有业务数据均来自当前账号。` : '当前账号暂无可用于本模块的业务记录。'),
    progress: liveProgress,
    progressLabel: isPlan ? '任务完成度' : isResources ? '资源完成度' : props.matchScore ? '最近匹配度' : '数据完整度',
    outcome: props.suggestions[1] || (props.liveTasks.length ? `已完成 ${completedCount} / ${props.liveTasks.length} 项后端学习任务，完成状态会持续保存。` : '完成岗位匹配后，这里会生成可执行建议和学习任务。'),
    primaryAction: props.liveTasks.length ? base.primaryAction : '完成岗位匹配并生成任务',
    route: props.liveTasks.length ? base.route : '/match-analysis',
    metrics: [
      { label: '画像技能', value: String(props.profileSkills.length), delta: '当前账号' },
      { label: '学习任务', value: String(props.liveTasks.length), delta: '后端记录' },
      { label: '学习专题', value: String(props.liveResources.length), delta: '后端记录' },
    ],
    nodes,
    tasks,
    evidence: props.profileSkills.length ? props.profileSkills.slice(0, 6) : ['当前账号暂无画像技能'],
  }
})
const tasks = ref(config.value.tasks.map(task => ({ ...task })))
const selectedNodeId = ref(config.value.nodes.find(node => node.state === 'active')?.id || config.value.nodes[0].id)
const actionState = ref('')

const selectedNode = computed(() => config.value.nodes.find(node => node.id === selectedNodeId.value) || config.value.nodes[0])
const completedTasks = computed(() => tasks.value.filter(task => task.done).length)
const taskProgress = computed(() => Math.round((completedTasks.value / Math.max(tasks.value.length, 1)) * 100))
const themeStyle = computed(() => ({
  '--mission-accent': config.value.accent,
  '--mission-soft': config.value.accentSoft,
  '--mission-rgb': config.value.accentRgb,
}))
const progressStyle = computed(() => ({ '--mission-progress': `${config.value.progress * 3.6}deg` }))

function resetCabin() {
  tasks.value = config.value.tasks.map(task => ({ ...task }))
  selectedNodeId.value = config.value.nodes.find(node => node.state === 'active')?.id || config.value.nodes[0].id
  actionState.value = ''
  nextTick(() => shell.value?.focus({ preventScroll: true }))
}

function selectNode(id: string) {
  selectedNodeId.value = id
}

function toggleTask(id: string) {
  const task: any = tasks.value.find(item => item.id === id)
  if (task?.source) {
    emit('toggleTask', task.source)
    task.done = !task.done
    return
  }
  actionState.value = '请先生成真实学习任务'
}

function launchPrimaryAction() {
  actionState.value = '任务已启动'
  window.setTimeout(() => emit('primary', { id: config.value.id, route: config.value.route }), 260)
}

function orbitNodeStyle(index: number, total: number) {
  const angle = (Math.PI * 2 * index) / total - Math.PI / 2
  const radius = 39
  return { left: `${50 + Math.cos(angle) * radius}%`, top: `${50 + Math.sin(angle) * radius}%` }
}

function routeNodeStyle(index: number) {
  const positions = [
    { left: '3%', top: '63%' }, { left: '18%', top: '25%' }, { left: '35%', top: '52%' },
    { left: '52%', top: '57%' }, { left: '69%', top: '18%' }, { left: '87%', top: '26%' },
  ]
  return positions[index] || positions[positions.length - 1]
}

function aiNodeStyle(index: number) {
  const positions = [
    { left: '6%', top: '18%' }, { right: '5%', top: '20%' }, { left: '8%', bottom: '16%' }, { right: '7%', bottom: '15%' },
  ]
  return positions[index] || positions[0]
}

watch(() => props.moduleId, resetCabin)
onMounted(resetCabin)
</script>

<style scoped>
.mission-cabin {
  --mission-accent: #52ddff;
  --mission-soft: #0aa9b4;
  --mission-rgb: 88, 230, 255;
  position: fixed;
  inset: 0;
  z-index: 120;
  display: grid;
  grid-template-rows: 74px minmax(0, 1fr) 34px;
  overflow: hidden;
  color: #effbff;
  font-family: "Bahnschrift", "Microsoft YaHei", sans-serif;
  outline: none;
}

.mission-cabin__veil,
.mission-cabin__grid { position: absolute; inset: 0; pointer-events: none; }
.mission-cabin__veil {
  background:
    linear-gradient(90deg, rgba(2, 8, 24, .97) 0%, rgba(3, 13, 34, .9) 31%, rgba(3, 12, 31, .79) 66%, rgba(2, 8, 24, .96) 100%),
    radial-gradient(circle at 51% 42%, rgba(var(--mission-rgb), .15), transparent 34%);
  backdrop-filter: blur(8px) saturate(.85);
}
.mission-cabin__grid {
  opacity: .2;
  background-image: linear-gradient(rgba(var(--mission-rgb), .16) 1px, transparent 1px), linear-gradient(90deg, rgba(var(--mission-rgb), .13) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: linear-gradient(90deg, #000, transparent 54%, #000);
}

.mission-header,
.mission-layout,
.mission-footer { position: relative; z-index: 2; }
.mission-header {
  display: grid;
  grid-template-columns: 230px 1fr 230px;
  align-items: center;
  border-bottom: 1px solid rgba(var(--mission-rgb), .28);
  padding: 0 28px;
  background: rgba(3, 12, 30, .72);
  box-shadow: 0 18px 50px rgba(0, 0, 0, .25);
}
.mission-back {
  display: inline-flex; align-items: center; gap: 10px; width: max-content;
  border: 0; padding: 10px 0; background: transparent; color: #b9d7e5; cursor: pointer; font: inherit;
}
.mission-back svg { width: 21px; fill: none; stroke: var(--mission-accent); stroke-width: 1.8; transition: transform .25s ease; }
.mission-back:hover svg { transform: translateX(-4px); }
.mission-back:hover { color: #fff; }
.mission-identity { display: flex; align-items: center; justify-content: center; gap: 13px; }
.mission-code { display: grid; place-items: center; width: 34px; height: 34px; background: var(--mission-accent); color: #03101e; font-weight: 900; }
.mission-rule { width: 46px; height: 1px; background: linear-gradient(90deg, var(--mission-accent), transparent); }
.mission-identity div { display: flex; flex-direction: column; }
.mission-identity small { color: var(--mission-accent); font-size: 10px; letter-spacing: .22em; }
.mission-identity strong { margin-top: 2px; font-size: 17px; letter-spacing: .05em; }
.mission-signal { justify-self: end; display: flex; align-items: center; gap: 9px; color: #8eafbe; font-size: 10px; letter-spacing: .12em; }
.mission-signal i { width: 7px; height: 7px; border-radius: 50%; background: var(--mission-accent); box-shadow: 0 0 14px var(--mission-accent); animation: mission-pulse 1.8s ease-in-out infinite; }

.mission-layout {
  display: grid;
  grid-template-columns: minmax(300px, 28%) minmax(480px, 1fr) minmax(286px, 24%);
  min-height: 0;
  padding: 22px 28px 18px;
}
.mission-brief,
.mission-actions { min-width: 0; }
.mission-brief { padding: 6px 28px 0 0; border-right: 1px solid rgba(var(--mission-rgb), .18); }
.mission-actions { padding: 6px 0 0 26px; border-left: 1px solid rgba(var(--mission-rgb), .18); }
.mission-visual { min-width: 0; padding: 6px 24px 0; }
.mission-section-label { display: flex; align-items: center; gap: 9px; color: #668493; font-size: 9px; letter-spacing: .2em; }
.mission-section-label::after { content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(var(--mission-rgb), .28), transparent); }
.mission-section-label span { color: var(--mission-accent); font-weight: 900; }
.mission-eyebrow { margin: 30px 0 10px; color: var(--mission-accent); font-size: 12px; font-weight: 800; letter-spacing: .12em; }
.mission-brief h1 { max-width: 430px; margin: 0; color: #f5fcff; font-size: clamp(25px, 2.1vw, 38px); line-height: 1.24; letter-spacing: -.035em; }
.mission-summary { max-width: 430px; margin: 18px 0 0; color: #91afbd; font-size: 13px; line-height: 1.75; }
.mission-progress-row { display: grid; grid-template-columns: 126px 1fr; align-items: center; gap: 18px; margin-top: 28px; }
.mission-progress { display: grid; place-items: center; width: 112px; aspect-ratio: 1; border-radius: 50%; background: conic-gradient(var(--mission-accent) var(--mission-progress), rgba(var(--mission-rgb), .09) 0); box-shadow: 0 0 34px rgba(var(--mission-rgb), .12); }
.mission-progress::before { content: ""; grid-area: 1/1; width: 88px; aspect-ratio: 1; border-radius: 50%; background: rgba(4, 14, 35, .96); border: 1px solid rgba(var(--mission-rgb), .24); }
.mission-progress div { grid-area: 1/1; position: relative; text-align: center; }
.mission-progress strong { font-size: 31px; line-height: 1; }
.mission-progress div > span { color: var(--mission-accent); font-size: 13px; }
.mission-progress small { display: block; margin-top: 5px; color: #7797a5; font-size: 9px; }
.mission-outcome { border-left: 2px solid var(--mission-accent); padding-left: 14px; }
.mission-outcome span { color: var(--mission-accent); font-size: 9px; letter-spacing: .15em; }
.mission-outcome p { margin: 7px 0 0; color: #c6dae3; font-size: 12px; line-height: 1.55; }
.mission-metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; margin-top: 28px; background: rgba(var(--mission-rgb), .16); }
.mission-metrics article { min-width: 0; padding: 14px 11px; background: rgba(4, 14, 35, .9); }
.mission-metrics span,
.mission-metrics small { display: block; overflow: hidden; color: #6d8a98; font-size: 9px; text-overflow: ellipsis; white-space: nowrap; }
.mission-metrics strong { display: block; margin: 6px 0 4px; color: #f1fbff; font-size: 20px; }
.mission-metrics small { color: var(--mission-accent); }

.visual-stage { position: relative; height: calc(100% - 28px); min-height: 430px; margin-top: 16px; overflow: hidden; border: 1px solid rgba(var(--mission-rgb), .19); background: radial-gradient(circle at 50% 45%, rgba(var(--mission-rgb), .08), transparent 40%), rgba(2, 10, 26, .36); clip-path: polygon(18px 0, 100% 0, 100% calc(100% - 18px), calc(100% - 18px) 100%, 0 100%, 0 18px); }
.visual-stage::before,
.visual-stage::after { content: ""; position: absolute; z-index: 5; width: 34px; height: 34px; border-color: var(--mission-accent); opacity: .65; pointer-events: none; }
.visual-stage::before { top: 9px; left: 9px; border-top: 1px solid; border-left: 1px solid; }
.visual-stage::after { right: 9px; bottom: 9px; border-right: 1px solid; border-bottom: 1px solid; }
.visual-readout { position: absolute; right: 18px; bottom: 17px; left: 18px; z-index: 8; display: grid; grid-template-columns: 120px minmax(120px, .8fr) 1fr 70px; align-items: center; gap: 15px; border-top: 1px solid rgba(var(--mission-rgb), .22); padding: 12px 2px 0; background: linear-gradient(180deg, transparent, rgba(2, 10, 26, .72) 34%); }
.visual-readout > span { color: var(--mission-accent); font-size: 9px; letter-spacing: .14em; }
.visual-readout strong { font-size: 13px; }
.visual-readout p { margin: 0; color: #7897a5; font-size: 11px; }
.visual-readout > b { color: var(--mission-accent); font-size: 25px; text-align: right; }
.visual-readout > b small { color: #6e8a98; font-size: 9px; }

.orbit-map { position: absolute; inset: 6% 6% 18%; }
.orbit-map__ring { position: absolute; top: 50%; left: 50%; border: 1px solid rgba(var(--mission-rgb), .24); border-radius: 50%; transform: translate(-50%, -50%); }
.orbit-map__ring--one { width: 57%; aspect-ratio: 1; }
.orbit-map__ring--two { width: 82%; aspect-ratio: 1; border-style: dashed; animation: mission-spin 28s linear infinite; }
.orbit-map__core { position: absolute; top: 50%; left: 50%; display: grid; place-items: center; width: 126px; aspect-ratio: 1; border: 1px solid var(--mission-accent); border-radius: 50%; background: radial-gradient(circle, rgba(var(--mission-rgb), .24), rgba(3, 13, 31, .96) 65%); transform: translate(-50%, -50%); box-shadow: 0 0 55px rgba(var(--mission-rgb), .24); }
.orbit-map__core small,.orbit-map__core span { color: #7795a3; font-size: 8px; letter-spacing: .12em; }
.orbit-map__core strong { color: var(--mission-accent); font-size: 38px; line-height: .8; }
.orbit-node { position: absolute; display: grid; place-items: center; width: 70px; aspect-ratio: 1; border: 1px solid rgba(var(--mission-rgb), .28); border-radius: 50%; background: rgba(4, 15, 36, .95); color: #96b3c1; transform: translate(-50%, -50%); cursor: pointer; transition: .25s ease; }
.orbit-node span { color: var(--mission-accent); font-size: 10px; }.orbit-node b { font-size: 16px; }.orbit-node:hover,.orbit-node.selected { border-color: var(--mission-accent); color: #fff; box-shadow: 0 0 30px rgba(var(--mission-rgb), .26); transform: translate(-50%, -50%) scale(1.1); }

.route-map { position: absolute; inset: 9% 4% 22%; }
.route-map svg { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }
.route-map path { fill: none; stroke: rgba(var(--mission-rgb), .15); stroke-width: 2; stroke-dasharray: 7 9; }
.route-map .route-map__active { stroke: url(#missionRoute); stroke-width: 3; stroke-dasharray: none; filter: drop-shadow(0 0 8px rgba(var(--mission-rgb), .55)); }
.route-node { position: absolute; display: flex; flex-direction: column; align-items: center; min-width: 80px; border: 0; background: transparent; color: #88a8b7; transform: translate(-50%, -50%); cursor: pointer; }
.route-node > span { display: grid; place-items: center; width: 52px; aspect-ratio: 1; border: 1px solid rgba(var(--mission-rgb), .35); background: #06152f; color: var(--mission-accent); transform: rotate(45deg); box-shadow: 0 0 20px rgba(var(--mission-rgb), .12); }
.route-node > span::first-line { transform: rotate(-45deg); }.route-node b { margin-top: 17px; color: #d7eaf2; font-size: 11px; }.route-node small { margin-top: 4px; font-size: 8px; }.route-node:hover > span,.route-node.selected > span { background: var(--mission-accent); color: #04101f; box-shadow: 0 0 32px rgba(var(--mission-rgb), .45); }

.profile-map { position: absolute; inset: 7% 7% 20%; display: grid; grid-template-columns: .9fr 1.2fr; align-items: center; gap: 8%; }
.profile-avatar { position: relative; justify-self: center; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 220px; height: 310px; border: 1px solid rgba(var(--mission-rgb), .23); background: radial-gradient(circle at 50% 36%, rgba(var(--mission-rgb), .2), transparent 48%); clip-path: polygon(14% 0, 86% 0, 100% 10%, 100% 90%, 86% 100%, 14% 100%, 0 90%, 0 10%); }
.profile-avatar__head { width: 72px; height: 88px; border-radius: 48% 48% 42% 42%; background: linear-gradient(180deg, var(--mission-accent), var(--mission-soft)); opacity: .72; filter: drop-shadow(0 0 24px rgba(var(--mission-rgb), .65)); }
.profile-avatar__body { width: 142px; height: 118px; margin-top: 5px; border-radius: 58% 58% 18% 18%; background: linear-gradient(180deg, rgba(var(--mission-rgb), .75), rgba(var(--mission-rgb), .08)); }
.profile-avatar > span { position: absolute; bottom: 16px; color: var(--mission-accent); font-size: 9px; letter-spacing: .18em; }
.profile-avatar__ring { position: absolute; border: 1px solid rgba(var(--mission-rgb), .28); border-radius: 50%; }.profile-avatar__ring--one { width: 160px; height: 160px; }.profile-avatar__ring--two { width: 205px; height: 205px; border-style: dashed; animation: mission-spin 22s linear infinite; }
.profile-signals { display: flex; flex-direction: column; gap: 8px; }
.profile-signals button { display: grid; grid-template-columns: 40px 1fr 48px; align-items: center; gap: 10px; border: 1px solid rgba(var(--mission-rgb), .14); padding: 12px; background: rgba(4, 15, 36, .62); color: #d5e7ee; text-align: left; cursor: pointer; }.profile-signals button:hover,.profile-signals button.selected { border-color: var(--mission-accent); background: rgba(var(--mission-rgb), .09); }.profile-signals button > span { color: var(--mission-accent); font-size: 10px; }.profile-signals div { display: flex; flex-direction: column; }.profile-signals b { font-size: 12px; }.profile-signals small { color: #718e9c; font-size: 9px; }.profile-signals strong { color: var(--mission-accent); font-size: 15px; text-align: right; }

.resource-map { position: absolute; inset: 7% 6% 22%; display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.resource-map button { position: relative; display: flex; flex-direction: column; align-items: flex-start; border: 1px solid rgba(var(--mission-rgb), .18); padding: 17px 18px; overflow: hidden; background: linear-gradient(135deg, rgba(var(--mission-rgb), .08), rgba(4, 15, 35, .86) 45%); color: #dbeaf0; text-align: left; cursor: pointer; clip-path: polygon(12px 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%, 0 12px); }
.resource-map button:hover,.resource-map button.selected { border-color: var(--mission-accent); transform: translateY(-2px); box-shadow: 0 14px 32px rgba(0,0,0,.22); }.resource-map__index { position: absolute; right: 14px; top: 12px; color: rgba(var(--mission-rgb), .28); font-size: 28px; font-weight: 900; }.resource-map__type { color: var(--mission-accent); font-size: 9px; letter-spacing: .17em; }.resource-map b { max-width: 80%; margin-top: 20px; font-size: 14px; }.resource-map small { margin-top: 5px; color: #718d9a; font-size: 10px; }.resource-map i { width: 100%; height: 2px; margin-top: auto; background: rgba(var(--mission-rgb), .1); }.resource-map i span { display: block; height: 100%; background: var(--mission-accent); box-shadow: 0 0 8px var(--mission-accent); }.resource-map em { margin-top: 7px; color: #6f8b98; font-size: 8px; font-style: normal; letter-spacing: .12em; }

.ai-map { position: absolute; inset: 4% 7% 35%; }
.ai-map__core { position: absolute; top: 50%; left: 50%; display: grid; place-items: center; width: 150px; aspect-ratio: 1; border: 1px solid var(--mission-accent); border-radius: 50%; background: radial-gradient(circle, rgba(var(--mission-rgb), .28), rgba(4, 12, 31, .96) 66%); transform: translate(-50%, -50%); box-shadow: 0 0 70px rgba(var(--mission-rgb), .26); }.ai-map__core span { color: #fff; font-size: 38px; font-weight: 900; }.ai-map__core b { color: var(--mission-accent); font-size: 9px; letter-spacing: .22em; }.ai-map__core small { color: #728f9d; font-size: 8px; }.ai-map__halo { position: absolute; top: 50%; left: 50%; border: 1px solid rgba(var(--mission-rgb), .24); border-radius: 50%; transform: translate(-50%,-50%); }.ai-map__halo--one { width: 270px; height: 270px; }.ai-map__halo--two { width: 380px; height: 380px; border-style: dashed; animation: mission-spin 30s linear infinite; }
.ai-map button { position: absolute; display: grid; grid-template-columns: 38px 38px; align-items: center; width: 142px; border: 1px solid rgba(var(--mission-rgb), .18); padding: 12px; background: rgba(4, 14, 34, .9); color: #d6e8ee; text-align: left; cursor: pointer; }.ai-map button:hover,.ai-map button.selected { border-color: var(--mission-accent); box-shadow: 0 0 28px rgba(var(--mission-rgb), .16); }.ai-map button span { color: var(--mission-accent); font-size: 9px; }.ai-map button b { color: #fff; font-size: 18px; text-align: right; }.ai-map button small { grid-column: 1/-1; margin-top: 5px; color: #6f8e9c; font-size: 9px; }
.ai-context-strip { position: absolute; right: 18px; bottom: 77px; left: 18px; z-index: 7; display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.ai-context-strip article { min-width: 0; border: 1px solid rgba(var(--mission-rgb), .2); padding: 11px 12px; background: rgba(4, 18, 42, .88); }
.ai-context-strip span,.ai-context-strip small { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ai-context-strip span { color: #7394a5; font-size: 8px; letter-spacing: .12em; }
.ai-context-strip strong { display: block; margin: 5px 0 3px; color: var(--mission-accent); font-size: 18px; }
.ai-context-strip small { color: #96b6c6; font-size: 9px; }

.calendar-map { position: absolute; inset: 8% 5% 22%; display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; align-items: stretch; }
.calendar-map button { display: flex; flex-direction: column; align-items: center; border: 1px solid rgba(var(--mission-rgb), .14); padding: 13px 5px 10px; background: rgba(4, 14, 34, .66); color: #8daab7; cursor: pointer; }.calendar-map button:hover,.calendar-map button.selected { border-color: var(--mission-accent); background: rgba(var(--mission-rgb), .08); }.calendar-map button > span { color: var(--mission-accent); font-size: 8px; }.calendar-map b { margin-top: 8px; color: #d9e9ef; font-size: 11px; }.calendar-map i { position: relative; flex: 1; width: 4px; min-height: 170px; margin: 14px 0; background: rgba(var(--mission-rgb), .1); }.calendar-map em { position: absolute; right: 0; bottom: 0; left: 0; min-height: 4px; background: linear-gradient(180deg, var(--mission-soft), var(--mission-accent)); box-shadow: 0 0 12px rgba(var(--mission-rgb), .55); }.calendar-map small { color: #6f8c99; font-size: 8px; line-height: 1.35; writing-mode: horizontal-tb; text-align: center; white-space: normal; word-break: break-all; hyphens: auto; min-height: 0; margin-top: 6px; max-width: 100%; }

.achievement-map { position: absolute; inset: 11% 5% 24%; display: flex; align-items: center; justify-content: space-between; gap: 10px; }.achievement-map__rail { position: absolute; top: 48%; right: 4%; left: 4%; height: 1px; background: linear-gradient(90deg, var(--mission-accent) 0 66%, rgba(var(--mission-rgb), .15) 66%); }.achievement-map button { position: relative; z-index: 2; display: flex; flex: 1; flex-direction: column; align-items: center; border: 0; background: transparent; color: #809da9; cursor: pointer; }.achievement-map button > span { color: #607d89; font-size: 9px; }.achievement-map button i { display: grid; place-items: center; width: 72px; aspect-ratio: 1; margin: 18px 0; border: 1px solid rgba(var(--mission-rgb), .28); background: #06142e; color: var(--mission-accent); font-size: 14px; font-style: normal; transform: rotate(45deg); box-shadow: 0 0 26px rgba(var(--mission-rgb), .11); }.achievement-map button b { color: #cfe2e9; font-size: 10px; }.achievement-map button small { margin-top: 4px; font-size: 8px; }.achievement-map button:hover i,.achievement-map button.selected i { border-color: var(--mission-accent); background: var(--mission-accent); color: #07111f; box-shadow: 0 0 32px rgba(var(--mission-rgb), .4); }.achievement-map button.is-locked { opacity: .42; }

.mission-action-head { display: flex; align-items: baseline; justify-content: space-between; margin-top: 27px; }.mission-action-head span { font-size: 15px; font-weight: 800; }.mission-action-head strong { color: var(--mission-accent); font-size: 12px; }.mission-task-list { display: flex; flex-direction: column; gap: 8px; margin-top: 14px; }.mission-task-list button { display: grid; grid-template-columns: 24px 1fr; align-items: center; gap: 11px; border: 1px solid rgba(var(--mission-rgb), .14); padding: 12px; background: rgba(4, 14, 34, .58); color: #d4e5eb; text-align: left; cursor: pointer; }.mission-task-list button:hover { border-color: rgba(var(--mission-rgb), .45); }.mission-task-list button > i { display: grid; place-items: center; width: 20px; height: 20px; border: 1px solid rgba(var(--mission-rgb), .4); }.mission-task-list button svg { width: 14px; fill: none; stroke: #04101e; stroke-width: 2.4; }.mission-task-list button.done > i { border-color: var(--mission-accent); background: var(--mission-accent); }.mission-task-list button.done b { color: #78949f; text-decoration: line-through; }.mission-task-list button span { display: flex; min-width: 0; flex-direction: column; }.mission-task-list button b { overflow: hidden; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }.mission-task-list button small { margin-top: 4px; color: #6d8996; font-size: 9px; }.mission-task-progress { height: 2px; margin-top: 12px; background: rgba(var(--mission-rgb), .1); }.mission-task-progress span { display: block; height: 100%; background: var(--mission-accent); box-shadow: 0 0 8px var(--mission-accent); transition: width .3s ease; }
.mission-task-empty { border: 1px solid rgba(var(--mission-rgb), .16); padding: 13px; background: rgba(4, 18, 42, .5); }
.mission-task-empty > span { color: #90afbd; font-size: 10px; }
.mission-task-empty ol { display: grid; gap: 8px; margin: 12px 0 0; padding: 0; list-style: none; }
.mission-task-empty li { display: grid; grid-template-columns: 24px 1fr; gap: 9px; align-items: center; }
.mission-task-empty li > b { color: var(--mission-accent); font: 700 9px Consolas, monospace; }
.mission-task-empty li > span { display: grid; color: #d4e8ef; font-size: 10px; }
.mission-task-empty li small { margin-top: 2px; color: #688895; font-size: 8px; }
.mission-evidence { margin-top: 26px; border-top: 1px solid rgba(var(--mission-rgb), .15); padding-top: 17px; }.mission-evidence > span { color: var(--mission-accent); font-size: 9px; letter-spacing: .16em; }.mission-evidence ul { display: flex; flex-direction: column; gap: 9px; margin: 13px 0 0; padding: 0; list-style: none; }.mission-evidence li { position: relative; padding-left: 13px; color: #7897a4; font-size: 10px; line-height: 1.45; }.mission-evidence li::before { content: ""; position: absolute; top: 6px; left: 0; width: 4px; height: 4px; background: var(--mission-accent); box-shadow: 0 0 8px var(--mission-accent); }
.mission-primary { display: flex; align-items: center; justify-content: space-between; width: 100%; margin-top: 24px; border: 1px solid var(--mission-accent); padding: 14px 16px; background: linear-gradient(90deg, rgba(var(--mission-rgb), .22), rgba(var(--mission-rgb), .07)); color: #f4fdff; font: inherit; font-size: 11px; font-weight: 800; cursor: pointer; clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 12px 100%, 0 calc(100% - 12px)); }.mission-primary:hover { background: var(--mission-accent); color: #03101f; box-shadow: 0 0 28px rgba(var(--mission-rgb), .25); }.mission-primary svg { width: 18px; fill: none; stroke: currentColor; stroke-width: 1.8; }
.mission-footer { display: flex; align-items: center; justify-content: space-between; border-top: 1px solid rgba(var(--mission-rgb), .18); padding: 0 28px; background: rgba(2, 9, 24, .8); color: #5f7c89; font-size: 8px; letter-spacing: .15em; }.mission-footer span:first-child { color: #82a0ac; }.mission-footer i { display: inline-block; width: 5px; height: 5px; margin-right: 7px; border-radius: 50%; background: #66d0e0; box-shadow: 0 0 8px #66d0e0; }

.is-done { --node-opacity: 1; }.is-next { opacity: .72; }.is-locked { opacity: .42; filter: grayscale(.3); }

.mission-cabin-enter-active,.mission-cabin-leave-active { transition: opacity .42s ease; }.mission-cabin-enter-active .mission-header,.mission-cabin-enter-active .mission-brief,.mission-cabin-enter-active .mission-visual,.mission-cabin-enter-active .mission-actions { transition: opacity .5s ease, transform .58s cubic-bezier(.2,.8,.2,1); }.mission-cabin-enter-from { opacity: 0; }.mission-cabin-enter-from .mission-header { transform: translateY(-30px); }.mission-cabin-enter-from .mission-brief { opacity: 0; transform: translateX(-34px); }.mission-cabin-enter-from .mission-visual { opacity: 0; transform: scale(.96); }.mission-cabin-enter-from .mission-actions { opacity: 0; transform: translateX(34px); }.mission-cabin-leave-to { opacity: 0; }

@keyframes mission-pulse { 50% { opacity: .4; transform: scale(.72); } }
@keyframes mission-spin { to { transform: translate(-50%,-50%) rotate(360deg); } }

@media (max-width: 1180px) {
  .mission-layout { grid-template-columns: minmax(280px, 32%) 1fr; overflow-y: auto; }
  .mission-actions { grid-column: 1 / -1; display: grid; grid-template-columns: 1fr 1.2fr 1fr; gap: 18px; border-top: 1px solid rgba(var(--mission-rgb), .18); border-left: 0; padding: 20px 0 10px; }
  .mission-actions > .mission-section-label,.mission-actions > .mission-action-head { display: none; }
  .mission-task-list { grid-column: 1 / 2; margin-top: 0; }.mission-task-progress { display: none; }.mission-evidence { grid-column: 2 / 3; margin-top: 0; padding-top: 0; border-top: 0; }.mission-primary { grid-column: 3 / 4; align-self: end; }
  .mission-visual { border-right: 0; }.visual-stage { min-height: 470px; }
}

@media (max-width: 760px) {
  .mission-cabin { grid-template-rows: 64px minmax(0, 1fr); overflow-y: auto; }
  .mission-header { position: sticky; top: 0; z-index: 20; grid-template-columns: auto 1fr auto; padding: 0 16px; }.mission-back span,.mission-rule,.mission-signal span { display: none; }.mission-identity { justify-content: flex-start; }.mission-identity small { font-size: 8px; }.mission-identity strong { font-size: 13px; }.mission-signal { width: 20px; }
  .mission-layout { display: flex; flex-direction: column; padding: 16px; overflow: visible; }.mission-brief,.mission-visual,.mission-actions { border: 0; padding: 0; }.mission-brief h1 { font-size: 27px; }.mission-progress-row { grid-template-columns: 108px 1fr; }.mission-progress { width: 98px; }.mission-metrics { margin-bottom: 24px; }
  .visual-stage { height: 520px; min-height: 520px; }.visual-readout { grid-template-columns: 1fr 64px; }.visual-readout > span,.visual-readout p { display: none; }
  .mission-actions { display: block; margin-top: 22px; padding-top: 20px; border-top: 1px solid rgba(var(--mission-rgb), .18); }.mission-actions > .mission-section-label,.mission-actions > .mission-action-head { display: flex; }.mission-task-list { margin-top: 14px; }.mission-evidence { margin-top: 22px; padding-top: 17px; border-top: 1px solid rgba(var(--mission-rgb), .15); }
  .profile-map { grid-template-columns: 1fr; overflow: auto; }.profile-avatar { display: none; }.resource-map { grid-template-columns: 1fr; overflow-y: auto; }.ai-map { bottom: 46%; }.ai-context-strip { grid-template-columns: repeat(2, 1fr); }.calendar-map { grid-template-columns: repeat(4, 1fr); overflow-y: auto; }.calendar-map i { min-height: 70px; }.achievement-map { align-items: flex-start; overflow-x: auto; }.achievement-map button { min-width: 120px; }.mission-footer { display: none; }
}

@media (prefers-reduced-motion: reduce) {
  .mission-cabin *, .mission-cabin *::before, .mission-cabin *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; scroll-behavior: auto !important; transition-duration: .01ms !important; }
}
</style>
