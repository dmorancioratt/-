<template>
  <Transition name="profile-cabin" appear>
    <section
      ref="shell"
      class="profile-cabin"
      aria-label="数字成长档案舱"
      tabindex="-1"
      @keydown.esc="emit('close')"
    >
      <div class="profile-cabin__veil" aria-hidden="true"></div>
      <div class="profile-cabin__grid" aria-hidden="true"></div>

      <div class="profile-frame">
        <header class="profile-head">
          <button class="profile-back" type="button" @click="emit('close')">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m14.5 5-7 7 7 7" /></svg>
            <span>返回驾驶舱</span>
          </button>

          <div class="profile-identity">
            <span class="profile-code">{{ cabin.code }}</span>
            <div class="profile-titles">
              <div class="profile-titles__row">
                <h1>{{ cabin.title }}</h1>
                <em>/ {{ cabin.english }}</em>
              </div>
            </div>
          </div>

          <div class="profile-head-actions">
            <span v-if="ownerName" class="profile-user">
              <i>{{ ownerName.slice(0, 1) }}</i>
              <span>你好，{{ ownerName }}</span>
              <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2" /><path d="M7 9h6M7 13h4" /></svg>
            </span>
            <button class="profile-assist" type="button" @click="emit('assist')">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l1.9 5.4L19 10l-5.1 1.6L12 17l-1.9-5.4L5 10l5.1-1.6Z" /></svg>
              AI 助理
            </button>
          </div>
        </header>

        <div class="profile-body">
          <!-- 01 任务简报 -->
          <aside class="panel-frame brief-card">
            <div class="panel-head">
              <span class="panel-head__cn">任务简报</span>
              <span class="panel-head__en">MISSION BRIEF</span>
            </div>
            <p class="brief-intro">这里是你个人成长的数字档案舱，整合多维证据，构建专属的成长数字身份。</p>

            <div class="brief-overview">
              <div class="archive-ring" role="progressbar" :aria-valuenow="profile.completeness" aria-valuemin="0" aria-valuemax="100" :style="ringStyle">
                <div><strong>{{ profile.completeness }}<i>%</i></strong><span>档案完整度</span><small>已归档</small></div>
              </div>
              <ul class="brief-facts">
                <li>
                  <small>证据总数</small>
                  <strong>{{ profile.evidenceTotal }}<em class="is-up">▲</em></strong>
                </li>
                <li>
                  <small>来源系统</small>
                  <strong>{{ profile.sourceSystems }}<em>个</em></strong>
                </li>
                <li>
                  <small>最近更新</small>
                  <strong class="fact-date">{{ profile.lastUpdated }}</strong>
                </li>
              </ul>
            </div>

            <div class="brief-tags">
              <div class="panel-subhead">
                <span class="panel-head__cn">成长标签</span>
                <span class="panel-head__en">GROWTH TAGS</span>
              </div>
              <div class="tag-cloud">
                <button
                  v-for="tag in tags"
                  :key="tag.label"
                  type="button"
                  class="tag-pill"
                  :class="`tag-pill--${tag.tone}`"
                  @click="removeTag(tag.label)"
                >{{ tag.label }}</button>
              </div>
              <button class="tag-add" type="button" @click="addTag">
                <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" /><path d="M12 8v8M8 12h8" /></svg>
                添加标签
              </button>
            </div>
          </aside>

          <!-- 02 数字身份全息 -->
          <main class="holo-stage" aria-label="数字身份全息投影">
            <div class="holo-id">
              <small>数字身份 ID</small>
              <div class="holo-id__row">
                <strong>{{ profile.identityId }}</strong>
                <button type="button" aria-label="复制数字身份ID" @click="copyIdentity">
                  <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="9" width="11" height="11" rx="2" /><path d="M5 15V6a2 2 0 0 1 2-2h9" /></svg>
                </button>
              </div>
            </div>

            <img
              class="holo-figure"
              src="/cockpit/profile-hologram.png"
              alt="数字人全息投影"
            />
          </main>

          <!-- 03 证据构成 + AI 决策依据 -->
          <aside class="right-stack">
            <div class="panel-frame evidence-card">
              <div class="panel-head">
                <span class="panel-head__cn">证据构成</span>
                <span class="panel-head__en">EVIDENCE COMPOSITION</span>
              </div>
              <div class="evidence-grid">
                <button
                  v-for="card in evidenceCards"
                  :key="card.key"
                  type="button"
                  class="evidence-item"
                  :class="{ expanded: expandedEvidence === card.key }"
                  :style="{ '--card-color': card.color, '--card-rgb': card.rgb }"
                  @click="toggleEvidence(card.key)"
                >
                  <div class="evidence-item__head">
                    <div>
                      <b>{{ card.title }}</b>
                      <small>{{ card.en }}</small>
                    </div>
                    <span class="evidence-item__icon"><svg viewBox="0 0 24 24" aria-hidden="true" v-html="card.icon" /></span>
                  </div>
                  <div class="evidence-item__meter">
                    <span class="ev-ring">
                      <svg viewBox="0 0 72 72" aria-hidden="true">
                        <circle class="ev-ring__track" cx="36" cy="36" r="30" />
                        <circle
                          class="ev-ring__value"
                          cx="36" cy="36" r="30"
                          :stroke="card.color"
                          :stroke-dasharray="`${2 * Math.PI * 30 * card.percent / 100} 999`"
                          transform="rotate(-90 36 36)"
                        />
                      </svg>
                      <b>{{ card.percent }}<i>%</i></b>
                    </span>
                    <span class="ev-count">{{ card.done }} / {{ card.total }}</span>
                  </div>
                  <span class="evidence-item__more">查看详情 <i>→</i></span>
                  <Transition name="ev-detail">
                    <ul v-if="expandedEvidence === card.key" class="evidence-item__list">
                      <li v-for="item in card.items" :key="item">{{ item }}</li>
                    </ul>
                  </Transition>
                </button>
              </div>
            </div>

            <div class="panel-frame ai-basis-card">
              <div class="panel-head">
                <span class="panel-head__cn">AI 决策依据</span>
                <span class="panel-head__en">AI DECISION BASIS</span>
              </div>
              <div class="ai-basis">
                <span class="ai-brain" aria-hidden="true">
                  <svg viewBox="0 0 24 24"><path d="M12 4a4 4 0 0 0-4 4v1a3.2 3.2 0 0 0 0 6.2V16a4 4 0 0 0 8 0v-.8a3.2 3.2 0 0 0 0-6.2V8a4 4 0 0 0-4-4Z" /><path d="M12 4v16M8.6 9.2h2M13.4 14.8h2" /></svg>
                </span>
                <ul>
                  <li v-for="row in aiBasis" :key="row.label">
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 4.5 4.5L19 7" /></svg>
                    <span>{{ row.label }}</span>
                    <b>{{ row.value }}</b>
                  </li>
                </ul>
              </div>
            </div>

            <button class="profile-cta" type="button" @click="openPersonalCenter">
              <span>完善个人档案</span>
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-5-5 5 5-5 5" /></svg>
            </button>
          </aside>

          <!-- 04 成长轨迹 -->
          <section class="panel-frame timeline-card" aria-label="成长轨迹">
            <div class="panel-head timeline-head">
              <div class="panel-head__group">
                <span class="panel-head__cn">成长轨迹</span>
                <span class="panel-head__en">GROWTH TIMELINE</span>
              </div>
              <Transition name="ev-detail" mode="out-in">
                <small key="caption" class="timeline-caption">{{ selectedTimeline.caption }}</small>
              </Transition>
            </div>

            <div class="timeline-track">
              <svg class="timeline-wave" viewBox="0 0 1000 150" preserveAspectRatio="none" aria-hidden="true">
                <defs>
                  <linearGradient id="gpWaveGrad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0" stop-color="#3f7bff" />
                    <stop offset=".55" stop-color="#59d8ff" />
                    <stop offset="1" stop-color="#9b8bff" />
                  </linearGradient>
                </defs>
                <path class="timeline-wave__halo" d="M0 110 C35 78 65 78 100 110 C150 42 250 42 300 110 C350 142 450 142 500 110 C550 42 650 42 700 110 C750 142 850 142 900 110 C935 78 965 78 1000 110" />
                <path class="timeline-wave__line" d="M0 110 C35 78 65 78 100 110 C150 42 250 42 300 110 C350 142 450 142 500 110 C550 42 650 42 700 110 C750 142 850 142 900 110 C935 78 965 78 1000 110" />
              </svg>

              <button class="timeline-arrow timeline-arrow--prev" type="button" aria-label="上一个节点" @click="stepTimeline(-1)">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m14.5 5-7 7 7 7" /></svg>
              </button>

              <div
                v-for="(node, index) in timelineNodes"
                :key="node.key"
                class="timeline-node"
                :class="{ selected: selectedTimelineIndex === index }"
                :style="{ left: `${10 + index * 20}%` }"
                type="button"
                role="button"
                tabindex="0"
                @click="selectTimeline(index)"
                @keydown.enter="selectTimeline(index)"
              >
                <div class="timeline-node__info">
                  <span class="timeline-node__icon"><svg viewBox="0 0 24 24" aria-hidden="true" v-html="node.icon" /></span>
                  <span class="timeline-node__copy">
                    <b>{{ node.title }}</b>
                    <small>{{ node.date }}</small>
                    <strong>{{ node.value }} <em>{{ node.unit }}</em></strong>
                  </span>
                </div>
                <i class="timeline-node__dot"></i>
              </div>

              <button class="timeline-arrow timeline-arrow--next" type="button" aria-label="下一个节点" @click="stepTimeline(1)">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9.5 5 7 7-7 7" /></svg>
              </button>
            </div>
          </section>
        </div>

        <!-- 05 个人档案 -->
        <div class="profile-info-entry">
          <div class="pi-divider">
            <span>个人档案</span>
            <em>PERSONAL PROFILE</em>
          </div>
          <ProfileInfoEditor />
        </div>
      </div>

      <Transition name="toast">
        <div v-if="toastText" class="profile-toast" role="status">{{ toastText }}</div>
      </Transition>
    </section>
  </Transition>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { missionCabins } from './missionCabinData'
import ProfileInfoEditor from './ProfileInfoEditor.vue'

const emit = defineEmits<{
  close: []
  primary: [payload: { id: 'avatar'; route: string }]
  assist: []
}>()
const props = withDefaults(defineProps<{
  profileData?: Record<string, any>
  resumeCount?: number
  matchCount?: number
  interviewCount?: number
  activityEvents?: Array<{ type: string; id: string | number; date: string; title: string; detail: string }>
}>(), {
  profileData: () => ({}),
  resumeCount: 0,
  matchCount: 0,
  interviewCount: 0,
  activityEvents: () => [],
})

const shell = ref<HTMLElement | null>(null)
const toastText = ref('')
let toastTimer = 0

const cabin = missionCabins.avatar
const authStore = useAuthStore()
const ownerName = computed(() => {
  const user = authStore.user as { display_name?: string; username?: string } | null
  return user?.display_name || user?.username || ''
})

const profile = computed(() => {
  const data = props.profileData || {}
  const evidenceTotal = props.resumeCount + props.matchCount + props.interviewCount
  return {
    identityId: data.id ? `GID-${String(data.id).padStart(8, '0')}` : 'GID-PENDING',
    completeness: Math.max(0, Math.min(100, Math.round(Number(data.completeness || 0)))),
    evidenceTotal,
    sourceSystems: [props.resumeCount, props.matchCount, props.interviewCount].filter(Boolean).length,
    lastUpdated: props.activityEvents[0]?.date ? new Intl.DateTimeFormat('zh-CN').format(new Date(props.activityEvents[0].date)) : '暂无记录',
  }
})

const ringStyle = computed(() => ({ '--ring-angle': `${profile.value.completeness * 3.6}deg` }))

type TagTone = 'cyan' | 'blue' | 'plain'
type GrowthTag = { label: string; tone: TagTone }
const tags = computed<GrowthTag[]>(() => (props.profileData.skills || []).map((item: any, index: number) => ({
  label: typeof item === 'string' ? item : item?.name,
  tone: (['cyan', 'blue', 'plain'] as TagTone[])[index % 3],
})).filter((item: GrowthTag) => item.label))
const tagSuggestions = ['产品思维', '全栈视野', '跨领域协作', '技术布道者']

function addTag() {
  const next = tagSuggestions.shift()
  if (!next) {
    showToast('AI 正在挖掘更多专属标签，稍后再来看看')
    return
  }
  showToast(`请在个人资料中添加标签「${next}」`)
}

function removeTag(label: string) {
  showToast(`请在个人资料中管理标签「${label}」`)
}

type EvidenceCard = {
  key: string
  title: string
  en: string
  percent: number
  done: number
  total: number
  color: string
  rgb: string
  icon: string
  items: string[]
}

const evidenceCards = computed<EvidenceCard[]>(() => [
  {
    key: 'course', title: '个人简历', en: 'RESUME RECORDS', percent: props.resumeCount ? 100 : 0, done: props.resumeCount, total: props.resumeCount,
    color: '#4ed8ff', rgb: '78, 216, 255',
    icon: '<circle cx="12" cy="9" r="5" /><path d="m9 13-2 8 5-3 5 3-2-8" />',
    items: props.resumeCount ? [`当前账号已保存 ${props.resumeCount} 份简历`] : ['当前账号尚未保存简历'],
  },
  {
    key: 'project', title: '岗位匹配', en: 'MATCH REPORTS', percent: props.matchCount ? 100 : 0, done: props.matchCount, total: props.matchCount,
    color: '#258dff', rgb: '37, 141, 255',
    icon: '<path d="m12 3 9 5-9 5-9-5Z" /><path d="m5 12.5-2 1.5 9 5 9-5-2-1.5" /><path d="m5 17-2 1.5 9 5 9-5-2-1.5" />',
    items: props.matchCount ? [`当前账号已生成 ${props.matchCount} 份匹配报告`] : ['当前账号尚未生成匹配报告'],
  },
  {
    key: 'skill', title: '画像技能', en: 'PROFILE SKILLS', percent: Math.min(100, (props.profileData.skills || []).length * 10), done: (props.profileData.skills || []).length, total: (props.profileData.skills || []).length,
    color: '#58e6ff', rgb: '88, 230, 255',
    icon: '<path d="M12 2.5 20.5 7v10L12 21.5 3.5 17V7Z" /><path d="M12 7.5a4.5 4.5 0 1 1 0 9 4.5 4.5 0 0 1 0-9Z" />',
    items: (props.profileData.skills || []).map((item: any) => typeof item === 'string' ? item : item?.name).filter(Boolean),
  },
  {
    key: 'job', title: '面试记录', en: 'INTERVIEW RECORDS', percent: props.interviewCount ? 100 : 0, done: props.interviewCount, total: props.interviewCount,
    color: '#6d8dff', rgb: '109, 141, 255',
    icon: '<path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5H4.5L6.8 17A8.5 8.5 0 1 1 21 11.5Z" /><path d="M9 10.5h6M9 14h4" />',
    items: props.interviewCount ? [`当前账号已有 ${props.interviewCount} 条面试记录`] : ['当前账号尚无面试记录'],
  },
])

const expandedEvidence = ref<string | null>(null)

function toggleEvidence(key: string) {
  expandedEvidence.value = expandedEvidence.value === key ? null : key
}

const aiBasis = computed(() => [
  { label: '已保存简历', value: String(props.resumeCount) },
  { label: '岗位匹配报告', value: String(props.matchCount) },
  { label: '面试记录', value: String(props.interviewCount) },
])

type TimelineNode = {
  key: string
  title: string
  date: string
  value: string
  unit: string
  caption: string
  icon: string
}

const fallbackTimelineIcon = '<rect x="3" y="5" width="18" height="14" rx="2" /><path d="M7 9h6M7 13h4" />'
const timelineNodes = computed<TimelineNode[]>(() => {
  const nodes = props.activityEvents.slice(0, 5).reverse().map((event, index) => ({
    key: `${event.type}-${event.id}`, title: event.title,
    date: new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: '2-digit' }).format(new Date(event.date)),
    value: String(index + 1), unit: '记录', caption: event.detail, icon: fallbackTimelineIcon,
  }))
  return nodes.length ? nodes : [{ key: 'empty', title: '暂无成长记录', date: '等待同步', value: '0', unit: '记录', caption: '完成简历、岗位匹配或面试后将在这里形成真实轨迹', icon: fallbackTimelineIcon }]
})
/*
  {
    key: 'course', title: '课程学习', date: '2024.09', value: '136', unit: '证书',
    caption: '2024.09 起 136 张课程证书完成归档，奠定理论基础',
    icon: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21.5v-16Z" /><path d="M4 19a2.5 2.5 0 0 1 2.5-2.5H20" />',
  },
  {
    key: 'assess', title: '技能测评', date: '2024.12', value: '78', unit: '评测',
    caption: '78 次技能评测持续校准能力坐标，短板自动进入计划',
    icon: '<circle cx="12" cy="9" r="5" /><path d="m9 13-2 8 5-3 5 3-2-8" />',
  },
  {
    key: 'project', title: '项目实践', date: '2025.03', value: '108', unit: '作品',
    caption: '108 件项目作品沉淀为可验证的工程证据链',
    icon: '<path d="m8 8-4 4 4 4" /><path d="m16 8 4 4-4 4" /><path d="m13 5-2 14" />',
  },
  {
    key: 'job', title: '岗位反馈', date: '2025.06', value: '46', unit: '反馈',
    caption: '46 条岗位反馈回流档案，匹配度每周自动刷新',
    icon: '<path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5H4.5L6.8 17A8.5 8.5 0 1 1 21 11.5Z" />',
  },
  {
    key: 'ability', title: '能力卡片', date: '2025.08', value: '12', unit: '能力',
    caption: '12 张能力卡片生成数字身份，可一键导出展示',
    icon: '<rect x="3" y="5" width="18" height="14" rx="2" /><path d="M7 9h6M7 13h4" />',
  },
]
*/

const selectedTimelineIndex = ref(0)
const selectedTimeline = computed(() => timelineNodes.value[selectedTimelineIndex.value] || timelineNodes.value[0])

function selectTimeline(index: number) {
  selectedTimelineIndex.value = index
}

function stepTimeline(direction: -1 | 1) {
  const next = selectedTimelineIndex.value + direction
  if (next >= 0 && next < timelineNodes.value.length) selectedTimelineIndex.value = next
}

async function copyIdentity() {
  try {
    await navigator.clipboard.writeText(profile.value.identityId)
    showToast('数字身份 ID 已复制')
  } catch {
    showToast('复制失败，请手动选择复制')
  }
}

function openPersonalCenter() {
  const entry = document.querySelector<HTMLElement>('.profile-info-entry')
  if (entry) {
    entry.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } else {
    emit('primary', { id: 'avatar', route: '/personal-center' })
  }
}

function showToast(message: string) {
  window.clearTimeout(toastTimer)
  toastText.value = message
  toastTimer = window.setTimeout(() => { toastText.value = '' }, 2200)
}

onMounted(() => shell.value?.focus({ preventScroll: true }))
onBeforeUnmount(() => window.clearTimeout(toastTimer))
</script>

<style scoped>
.profile-cabin {
  position: fixed;
  inset: 0;
  z-index: 140;
  overflow-y: auto;
  overflow-x: hidden;
  color: #eefaff;
  font-family: "Bahnschrift", "Microsoft YaHei", "Noto Sans SC", sans-serif;
  outline: none;
}

.profile-cabin::-webkit-scrollbar { width: 8px; }
.profile-cabin::-webkit-scrollbar-thumb { border-radius: 8px; background: rgba(88, 200, 255, .32); }
.profile-cabin::-webkit-scrollbar-track { background: transparent; }

.profile-cabin__veil,
.profile-cabin__grid { position: absolute; inset: 0; pointer-events: none; }
.profile-cabin__veil {
  background:
    radial-gradient(circle at 50% 40%, rgba(34, 108, 210, .2), transparent 46%),
    radial-gradient(circle at 12% 108%, rgba(37, 141, 255, .14), transparent 40%),
    linear-gradient(180deg, #041022 0%, #061831 48%, #030c1d 100%);
}
.profile-cabin__grid {
  opacity: .16;
  background-image:
    linear-gradient(rgba(96, 190, 255, .18) 1px, transparent 1px),
    linear-gradient(90deg, rgba(96, 190, 255, .13) 1px, transparent 1px);
  background-size: 52px 52px;
  mask-image: radial-gradient(circle at 50% 42%, #000 8%, transparent 78%);
}

.profile-frame {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  height: auto;
  min-height: 100%;
  padding: 14px clamp(16px, 1.6vw, 30px) 16px;
}

/* ============ 头部 ============ */
.profile-head { display: flex; align-items: center; gap: 18px; padding-bottom: 12px; }
.profile-back {
  display: inline-flex; flex-shrink: 0; align-items: center; gap: 9px;
  border: 1px solid rgba(90, 200, 255, .4); border-radius: 9px; padding: 10px 15px;
  background: rgba(6, 24, 48, .7); color: #cdeeff; font: inherit; font-size: 13px;
  cursor: pointer; backdrop-filter: blur(8px); transition: .22s ease;
}
.profile-back svg { width: 18px; fill: none; stroke: #4fd8ff; stroke-width: 1.9; transition: transform .22s ease; }
.profile-back:hover { border-color: #4fd8ff; color: #fff; box-shadow: 0 0 18px rgba(79, 216, 255, .25); }
.profile-back:hover svg { transform: translateX(-4px); }

.profile-identity { display: flex; flex: 1; align-items: center; gap: 14px; min-width: 0; }
.profile-code {
  display: grid; place-items: center; width: 46px; height: 46px; flex-shrink: 0;
  border: 1px solid rgba(110, 226, 255, .75); border-radius: 10px;
  background: linear-gradient(150deg, rgba(64, 190, 255, .28), rgba(24, 84, 190, .18));
  box-shadow: 0 0 20px rgba(66, 190, 255, .3), inset 0 0 14px rgba(96, 210, 255, .2);
  color: #dff6ff; font-size: 19px; font-weight: 800; letter-spacing: .04em;
  clip-path: polygon(22% 0, 100% 0, 100% 78%, 78% 100%, 0 100%, 0 22%);
}
.profile-titles__row { display: flex; align-items: baseline; gap: 10px; }
.profile-titles h1 {
  margin: 0; font-size: clamp(21px, 1.75vw, 30px); font-weight: 800; letter-spacing: .06em;
  background: linear-gradient(100deg, #ffffff 30%, #9fdfff 100%);
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.profile-titles em { color: #6d90a8; font-size: 12px; font-style: normal; letter-spacing: .2em; }

.profile-head-actions { display: flex; flex-shrink: 0; align-items: center; gap: 10px; }
.profile-user {
  display: inline-flex; align-items: center; gap: 9px;
  border: 1px solid rgba(110, 190, 255, .32); border-radius: 999px; padding: 6px 14px 6px 7px;
  background: rgba(8, 26, 54, .72); color: #d8ecfa; font-size: 13px;
}
.profile-user i {
  display: grid; place-items: center; width: 30px; height: 30px; border-radius: 50%;
  background: linear-gradient(140deg, #58e6ff, #7c6dff); color: #041224; font-size: 13px; font-weight: 800; font-style: normal;
}
.profile-user svg { width: 17px; fill: none; stroke: #7fa8c4; stroke-width: 1.6; }
.profile-assist {
  display: inline-flex; align-items: center; gap: 8px;
  border: 1px solid rgba(120, 220, 255, .45); border-radius: 999px; padding: 10px 18px;
  background: linear-gradient(120deg, rgba(64, 190, 255, .2), rgba(124, 109, 255, .16));
  color: #e2f6ff; font: inherit; font-size: 13px; font-weight: 700; cursor: pointer; transition: .22s ease;
}
.profile-assist svg { width: 16px; fill: none; stroke: #6ee2ff; stroke-width: 1.6; }
.profile-assist:hover { border-color: #6ee2ff; box-shadow: 0 0 20px rgba(94, 220, 255, .35); transform: translateY(-1px); }

/* ============ 主体网格 ============ */
.profile-body {
  display: grid;
  grid-template-columns: minmax(300px, 26%) minmax(0, 1fr) minmax(330px, 29%);
  grid-template-rows: minmax(0, 1fr) auto;
  gap: 14px;
  min-height: 640px;
}

/* ============ 个人信息录入 ============ */
.profile-info-entry { border-top: 1px solid rgba(96, 186, 255, .18); padding-top: 18px; }
.pi-divider { display: flex; align-items: baseline; gap: 12px; margin-bottom: 16px; padding-left: 12px; }
.pi-divider::before { content: ""; width: 4px; height: 15px; align-self: center; border-radius: 2px; background: linear-gradient(180deg, #58e6ff, #7c6dff); box-shadow: 0 0 8px rgba(88, 230, 255, .8); }
.pi-divider span { color: #ecf7ff; font-size: 16px; font-weight: 800; letter-spacing: .06em; }
.pi-divider em { color: #5f7f95; font-size: 10px; font-style: normal; letter-spacing: .2em; }

.panel-frame {
  position: relative;
  border: 1px solid rgba(96, 186, 255, .26);
  border-radius: 14px;
  background:
    radial-gradient(120% 60% at 18% -10%, rgba(78, 190, 255, .09), transparent 55%),
    linear-gradient(165deg, rgba(13, 34, 70, .78), rgba(6, 16, 38, .88));
  box-shadow: 0 18px 44px rgba(1, 7, 20, .45), inset 0 1px 0 rgba(190, 235, 255, .08);
  padding: 16px 18px;
  backdrop-filter: blur(10px);
}
.panel-frame::before,
.panel-frame::after { content: ""; position: absolute; width: 16px; height: 16px; pointer-events: none; opacity: .85; }
.panel-frame::before { top: -1px; left: -1px; border-top: 2px solid #6fe4ff; border-left: 2px solid #6fe4ff; border-top-left-radius: 14px; filter: drop-shadow(0 0 6px rgba(80, 210, 255, .7)); }
.panel-frame::after { right: -1px; bottom: -1px; border-right: 2px solid #6fe4ff; border-bottom: 2px solid #6fe4ff; border-bottom-right-radius: 14px; filter: drop-shadow(0 0 6px rgba(80, 210, 255, .7)); }

.panel-head { display: flex; align-items: baseline; gap: 9px; }
.panel-head__group { display: flex; align-items: baseline; gap: 9px; }
.panel-head__cn { position: relative; padding-left: 12px; color: #ecf7ff; font-size: 15px; font-weight: 800; letter-spacing: .08em; }
.panel-head__cn::before { content: ""; position: absolute; top: 50%; left: 0; width: 4px; height: 13px; border-radius: 2px; background: linear-gradient(180deg, #58e6ff, #7c6dff); box-shadow: 0 0 8px rgba(88, 230, 255, .8); transform: translateY(-50%); }
.panel-head__en { color: #5f7f95; font-size: 9px; letter-spacing: .2em; }

/* ============ 任务简报 ============ */
.brief-card { grid-column: 1; grid-row: 1; display: flex; flex-direction: column; min-height: 0; overflow-y: auto; overflow-x: hidden; }
.brief-card::-webkit-scrollbar { width: 4px; }
.brief-card::-webkit-scrollbar-thumb { border-radius: 4px; background: rgba(88, 200, 255, .3); }
.brief-intro { margin: 12px 0 0; color: #93aec2; font-size: 12.5px; line-height: 1.8; }

.brief-overview { display: flex; align-items: center; gap: 18px; margin-top: 18px; margin-bottom: auto; }
.archive-ring {
  --ring-angle: 331.2deg;
  position: relative; display: grid; place-items: center; width: 132px; height: 132px; flex-shrink: 0;
  border-radius: 50%;
  background: conic-gradient(#4fd8ff var(--ring-angle), rgba(78, 190, 255, .12) 0);
  box-shadow: 0 0 32px rgba(64, 190, 255, .22);
}
.archive-ring::before { content: ""; grid-area: 1 / 1; width: 108px; height: 108px; border-radius: 50%; background: radial-gradient(circle, rgba(10, 30, 62, .96) 62%, rgba(8, 22, 48, .96)); border: 1px solid rgba(96, 190, 255, .3); }
.archive-ring div { grid-area: 1 / 1; position: relative; text-align: center; }
.archive-ring strong { display: block; color: #fff; font-size: 33px; line-height: 1; text-shadow: 0 0 18px rgba(79, 216, 255, .6); }
.archive-ring strong i { color: #4fd8ff; font-size: 15px; font-style: normal; font-weight: 700; }
.archive-ring span { display: block; margin-top: 6px; color: #8fb2c8; font-size: 10.5px; }
.archive-ring small { display: block; margin-top: 2px; color: #58d8a8; font-size: 9px; letter-spacing: .12em; }

.brief-facts { flex: 1; display: flex; flex-direction: column; gap: 12px; margin: 0; padding: 0; list-style: none; }
.brief-facts li { border-left: 2px solid rgba(79, 216, 255, .35); padding-left: 12px; }
.brief-facts small { display: block; color: #6d8ea6; font-size: 10px; letter-spacing: .1em; }
.brief-facts strong { display: block; margin-top: 3px; color: #4fd8ff; font-size: 21px; line-height: 1.1; }
.brief-facts li:nth-child(n+2) strong { color: #e8f6ff; }
.brief-facts em { margin-left: 4px; color: #7fa4bc; font-size: 11px; font-style: normal; }
.brief-facts em.is-up { color: #58e6a8; font-size: 12px; }
.fact-date { font-size: 17px !important; letter-spacing: .04em; }

.brief-tags { display: flex; flex-direction: column; margin-top: 18px; border-top: 1px solid rgba(96, 186, 255, .16); padding-top: 14px; }
.panel-subhead { display: flex; align-items: baseline; gap: 9px; }
.tag-cloud { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 13px; }
.tag-pill {
  border: 1px solid rgba(104, 196, 255, .3); border-radius: 7px; padding: 6px 11px;
  background: rgba(12, 32, 64, .6); color: #a9d4ee; font: inherit; font-size: 11.5px; cursor: pointer;
  transition: .2s ease;
}
.tag-pill:hover { border-color: rgba(140, 230, 255, .7); color: #fff; transform: translateY(-1px); }
.tag-pill--cyan { border-color: rgba(88, 220, 255, .5); color: #8ce6ff; }
.tag-pill--blue { border-color: rgba(37, 141, 255, .48); background: rgba(37, 103, 219, .14); color: #c5ddff; }
.tag-add {
  display: inline-flex; align-self: flex-end; align-items: center; gap: 7px; margin-top: 13px;
  border: 0; background: transparent; color: #6fc8ec; font: inherit; font-size: 12px; cursor: pointer;
}
.tag-add svg { width: 15px; fill: none; stroke: #6fc8ec; stroke-width: 1.6; }
.tag-add:hover { color: #a5e6ff; } .tag-add:hover svg { stroke: #a5e6ff; }

/* ============ 中央全息 ============ */
.holo-stage {
  grid-column: 2; grid-row: 1;
  position: relative; min-height: 0;
  border: 1px solid rgba(96, 186, 255, .2); border-radius: 14px;
  background:
    radial-gradient(58% 42% at 50% 66%, rgba(46, 140, 255, .16), transparent 72%),
    linear-gradient(180deg, rgba(6, 18, 40, .5), rgba(4, 12, 30, .68));
  overflow: hidden;
}
.holo-stage::before {
  content: ""; position: absolute; inset: 0; opacity: .1; pointer-events: none;
  background-image: linear-gradient(rgba(96, 190, 255, .35) 1px, transparent 1px);
  background-size: 100% 30px;
  mask-image: linear-gradient(180deg, transparent 4%, #000 30%, #000 78%, transparent);
}
.holo-id { position: absolute; z-index: 3; top: 16px; left: 50%; text-align: center; transform: translateX(-50%); }
.holo-id small { display: block; color: #8fd4f2; font-size: 12px; letter-spacing: .3em; text-shadow: 0 0 14px rgba(88, 214, 255, .6); }
.holo-id__row { display: inline-flex; align-items: center; gap: 9px; margin-top: 5px; }
.holo-id strong { color: #fff; font-size: clamp(15px, 1.25vw, 21px); letter-spacing: .08em; white-space: nowrap; text-shadow: 0 0 22px rgba(94, 220, 255, .55); }
.holo-id button {
  display: grid; place-items: center; width: 26px; height: 26px;
  border: 1px solid rgba(120, 214, 255, .45); border-radius: 7px; background: rgba(10, 30, 60, .7); cursor: pointer;
}
.holo-id button svg { width: 14px; fill: none; stroke: #7fd8ff; stroke-width: 1.7; }
.holo-id button:hover { border-color: #7fd8ff; box-shadow: 0 0 12px rgba(96, 214, 255, .4); }

.holo-figure {
  position: absolute; left: 50%; top: 53%;
  height: 96%; max-width: none;
  object-fit: contain;
  mix-blend-mode: screen;
  -webkit-mask-image: radial-gradient(92% 86% at 50% 50%, #000 58%, transparent 90%);
  mask-image: radial-gradient(92% 86% at 50% 50%, #000 58%, transparent 90%);
  pointer-events: none; user-select: none;
  animation: holo-drift 7s ease-in-out infinite;
}

/* ============ 右侧证据构成 ============ */
.right-stack { grid-column: 3; grid-row: 1 / 3; display: flex; flex-direction: column; gap: 14px; min-height: 0; }
.evidence-card { display: flex; flex-direction: column; min-height: 0; flex: 1; }
.evidence-grid { display: grid; grid-template-columns: 1fr 1fr; grid-auto-rows: 1fr; gap: 10px; margin-top: 12px; flex: 1; min-height: 0; }
.evidence-item {
  position: relative; display: flex; flex-direction: column; overflow: hidden;
  border: 1px solid rgba(var(--card-rgb), .32); border-radius: 11px; padding: 12px;
  background: linear-gradient(150deg, rgba(var(--card-rgb), .12), rgba(6, 16, 38, .86) 52%);
  color: inherit; font: inherit; text-align: left; cursor: pointer;
  transition: border-color .22s ease, transform .22s ease, box-shadow .22s ease;
}
.evidence-item:hover, .evidence-item.expanded { border-color: rgba(var(--card-rgb), .8); transform: translateY(-2px); box-shadow: 0 12px 26px rgba(1, 8, 22, .45), 0 0 18px rgba(var(--card-rgb), .2); }
.evidence-item__head { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
.evidence-item__head b { display: block; color: #f0f9ff; font-size: 14px; letter-spacing: .04em; }
.evidence-item__head small { display: block; margin-top: 3px; color: rgba(var(--card-rgb), .85); font-size: 8px; letter-spacing: .14em; }
.evidence-item__icon { display: grid; place-items: center; width: 34px; height: 34px; flex-shrink: 0; border: 1px solid rgba(var(--card-rgb), .45); border-radius: 9px; background: rgba(var(--card-rgb), .12); }
.evidence-item__icon svg { width: 18px; fill: none; stroke: var(--card-color); stroke-width: 1.6; }
.evidence-item__meter { display: flex; align-items: center; gap: 12px; margin-top: 12px; }
.ev-ring { position: relative; display: grid; place-items: center; width: 64px; height: 64px; flex-shrink: 0; }
.ev-ring svg { width: 100%; height: 100%; }
.ev-ring__track { fill: none; stroke: rgba(255, 255, 255, .08); stroke-width: 6; }
.ev-ring__value { fill: none; stroke-width: 6; stroke-linecap: round; filter: drop-shadow(0 0 5px rgba(var(--card-rgb), .8)); }
.ev-ring b { position: absolute; color: #fff; font-size: 15px; }
.ev-ring b i { color: var(--card-color); font-size: 9px; font-style: normal; }
.ev-count { color: #a8c4d8; font-size: 13px; letter-spacing: .06em; }
.evidence-item__more { margin-top: auto; padding-top: 10px; color: rgba(var(--card-rgb), .95); font-size: 11px; }
.evidence-item__more i { font-style: normal; transition: transform .2s ease; }
.evidence-item:hover .evidence-item__more i, .evidence-item.expanded .evidence-item__more i { transform: translateX(3px); }
.evidence-item__list { position: absolute; z-index: 3; inset: auto 0 0 0; margin: 0; padding: 10px 12px; list-style: none; border-top: 1px solid rgba(var(--card-rgb), .3); background: linear-gradient(180deg, rgba(5, 14, 32, .96), rgba(8, 22, 48, .98)); }
.evidence-item__list li { position: relative; padding: 4px 0 4px 13px; color: #c3dcea; font-size: 10.5px; line-height: 1.45; }
.evidence-item__list li::before { content: ""; position: absolute; top: 9.5px; left: 0; width: 5px; height: 5px; border-radius: 1px; background: var(--card-color); box-shadow: 0 0 7px rgba(var(--card-rgb), .8); }
.ev-detail-enter-active, .ev-detail-leave-active { transition: opacity .22s ease, transform .22s ease; }
.ev-detail-enter-from, .ev-detail-leave-to { opacity: 0; transform: translateY(8px); }

/* ============ AI 决策依据 ============ */
.ai-basis-card { flex-shrink: 0; }
.ai-basis { display: flex; align-items: center; gap: 16px; margin-top: 12px; }
.ai-brain { display: grid; place-items: center; width: 74px; height: 74px; flex-shrink: 0; border: 1px solid rgba(150, 140, 255, .4); border-radius: 14px; background: radial-gradient(circle at 50% 40%, rgba(124, 109, 255, .24), rgba(10, 20, 46, .9) 72%); box-shadow: 0 0 24px rgba(124, 109, 255, .2); }
.ai-brain svg { width: 40px; fill: none; stroke: #58e6ff; stroke-width: 1.5; filter: drop-shadow(0 0 8px rgba(70, 215, 255, .55)); }
.ai-basis ul { flex: 1; display: flex; flex-direction: column; gap: 9px; margin: 0; padding: 0; list-style: none; }
.ai-basis li { display: flex; align-items: center; gap: 9px; }
.ai-basis li svg { width: 14px; flex-shrink: 0; fill: none; stroke: #58e6a8; stroke-width: 2.2; filter: drop-shadow(0 0 5px rgba(88, 230, 168, .6)); }
.ai-basis li span { color: #a8c2d6; font-size: 12px; white-space: nowrap; }
.ai-basis li::after { content: ""; flex: 1; border-bottom: 1px dashed rgba(120, 170, 210, .25); }
.ai-basis li b { color: #fff; font-size: 14px; letter-spacing: .03em; }

.profile-cta {
  display: flex; align-items: center; justify-content: center; gap: 12px; flex-shrink: 0;
  border: 1px solid rgba(140, 200, 255, .75); border-radius: 13px; padding: 15px;
  background: linear-gradient(100deg, rgba(64, 150, 255, .4), rgba(124, 109, 255, .38) 55%, rgba(64, 190, 255, .4));
  box-shadow: 0 0 26px rgba(84, 160, 255, .3), inset 0 1px 0 rgba(230, 246, 255, .3);
  color: #fff; font: inherit; font-size: 16px; font-weight: 800; letter-spacing: .28em;
  cursor: pointer; transition: .22s ease;
}
.profile-cta svg { width: 20px; fill: none; stroke: currentColor; stroke-width: 2; transition: transform .22s ease; }
.profile-cta:hover { box-shadow: 0 0 38px rgba(96, 180, 255, .55); transform: translateY(-2px); }
.profile-cta:hover svg { transform: translateX(4px); }

/* ============ 成长轨迹 ============ */
.timeline-card { grid-column: 1 / 3; grid-row: 2; padding-bottom: 12px; }
.timeline-head { justify-content: space-between; }
.timeline-caption { color: #6fc8ec; font-size: 11px; letter-spacing: .04em; }

.timeline-track { position: relative; height: clamp(128px, 16.5vh, 158px); margin-top: 4px; }
.timeline-wave { position: absolute; inset: 0; width: 100%; height: 100%; }
.timeline-wave__halo { fill: none; stroke: rgba(88, 170, 255, .16); stroke-width: 7; }
.timeline-wave__line { fill: none; stroke: url(#gpWaveGrad); stroke-width: 2.2; filter: drop-shadow(0 0 6px rgba(88, 190, 255, .55)); }

.timeline-node {
  position: absolute; top: 0; bottom: 0; z-index: 3; width: 17%;
  border: 0; padding: 0; background: transparent; color: inherit; font: inherit;
  cursor: pointer; transform: translateX(-50%);
}
.timeline-node__info {
  position: relative; z-index: 3; display: flex; align-items: center; gap: 9px;
  border: 1px solid rgba(104, 196, 255, .26); border-radius: 11px; padding: 8px 10px;
  background: linear-gradient(140deg, rgba(13, 34, 68, .92), rgba(6, 16, 38, .9));
  transition: border-color .22s ease, box-shadow .22s ease, transform .22s ease;
}
.timeline-node__icon { display: grid; place-items: center; width: 34px; height: 34px; flex-shrink: 0; border: 1px solid rgba(110, 214, 255, .5); border-radius: 9px; background: rgba(64, 180, 255, .13); }
.timeline-node__icon svg { width: 17px; fill: none; stroke: #6ee2ff; stroke-width: 1.7; }
.timeline-node__copy { display: flex; flex-direction: column; min-width: 0; }
.timeline-node__copy b { color: #ecf7ff; font-size: 12.5px; letter-spacing: .04em; }
.timeline-node__copy small { margin-top: 1px; color: #6d8ea6; font-size: 9.5px; letter-spacing: .08em; }
.timeline-node__copy strong { margin-top: 2px; color: #59d8ff; font-size: 12px; }
.timeline-node__copy em { color: #8fb2c8; font-size: 9.5px; font-style: normal; }
.timeline-node__dot {
  position: absolute; z-index: 2; top: 73.3%; left: 50%; width: 11px; height: 11px;
  border: 2px solid #6ee2ff; border-radius: 50%; background: #06152e;
  box-shadow: 0 0 12px rgba(88, 210, 255, .8); transform: translate(-50%, -50%);
}
.timeline-node::after { content: ""; position: absolute; top: 58px; bottom: 27%; left: 50%; width: 1px; background: linear-gradient(180deg, rgba(110, 226, 255, .5), rgba(110, 226, 255, .08)); }
.timeline-node:hover .timeline-node__info, .timeline-node.selected .timeline-node__info { border-color: rgba(110, 226, 255, .8); box-shadow: 0 0 20px rgba(80, 200, 255, .28); transform: translateY(-2px); }
.timeline-node.selected .timeline-node__dot { background: #6ee2ff; box-shadow: 0 0 18px rgba(110, 226, 255, 1); }
.timeline-node.selected .timeline-node__icon { background: rgba(110, 226, 255, .9); }
.timeline-node.selected .timeline-node__icon svg { stroke: #041528; }

.timeline-arrow {
  position: absolute; z-index: 4; top: 50%; display: grid; place-items: center; width: 30px; height: 30px;
  border: 1px solid rgba(104, 196, 255, .35); border-radius: 50%; background: rgba(8, 24, 50, .85);
  color: #7fd0f0; cursor: pointer; transform: translateY(-50%); transition: .2s ease;
}
.timeline-arrow svg { width: 15px; fill: none; stroke: currentColor; stroke-width: 2; }
.timeline-arrow:hover { border-color: #6ee2ff; color: #fff; box-shadow: 0 0 14px rgba(88, 210, 255, .4); }
.timeline-arrow--prev { left: -6px; } .timeline-arrow--next { right: -6px; }

/* ============ 提示 ============ */
.profile-toast {
  position: fixed; z-index: 220; bottom: 30px; left: 50%;
  border: 1px solid rgba(88, 214, 255, .5); border-radius: 8px; padding: 12px 20px;
  background: rgba(4, 19, 38, .95); color: #e9fbff; font-size: 13px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, .36), 0 0 22px rgba(88, 214, 255, .16);
  transform: translateX(-50%);
}
.toast-enter-active, .toast-leave-active { transition: .25s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translate(-50%, 14px); }

/* ============ 动画 ============ */
@keyframes holo-drift { 0%, 100% { transform: translate(-50%, -50%); } 50% { transform: translate(-50%, calc(-50% - 8px)); } }

.profile-cabin-enter-active, .profile-cabin-leave-active { transition: opacity .4s ease; }
.profile-cabin-enter-active .profile-head { transition: opacity .5s ease, transform .55s cubic-bezier(.2, .8, .2, 1); }
.profile-cabin-enter-active .brief-card, .profile-cabin-enter-active .right-stack { transition: opacity .55s ease .08s, transform .6s cubic-bezier(.2, .8, .2, 1) .08s; }
.profile-cabin-enter-active .holo-stage { transition: opacity .55s ease .14s, transform .62s cubic-bezier(.2, .8, .2, 1) .14s; }
.profile-cabin-enter-active .timeline-card { transition: opacity .55s ease .2s, transform .6s cubic-bezier(.2, .8, .2, 1) .2s; }
.profile-cabin-enter-from { opacity: 0; }
.profile-cabin-enter-from .profile-head { opacity: 0; transform: translateY(-26px); }
.profile-cabin-enter-from .brief-card { opacity: 0; transform: translateX(-32px); }
.profile-cabin-enter-from .holo-stage { opacity: 0; transform: scale(.96); }
.profile-cabin-enter-from .right-stack { opacity: 0; transform: translateX(32px); }
.profile-cabin-enter-from .timeline-card { opacity: 0; transform: translateY(30px); }
.profile-cabin-leave-to { opacity: 0; }

/* ============ 响应式 ============ */
@media (max-width: 1500px) {
  .profile-body { grid-template-columns: minmax(280px, 27%) minmax(0, 1fr) minmax(300px, 30%); }
}

@media (max-width: 1180px) {
  .profile-cabin { overflow-y: auto; }
  .profile-frame { height: auto; min-height: 100%; }
  .profile-body { grid-template-columns: 1fr; grid-template-rows: auto; }
  .brief-card, .holo-stage, .right-stack, .timeline-card { grid-column: auto; grid-row: auto; }
  .holo-stage { height: 540px; }
  .brief-card { overflow: visible; }
  .profile-user span { display: none; }
}

@media (max-width: 640px) {
  .profile-head { flex-wrap: wrap; gap: 10px; }
  .profile-identity { order: 3; flex-basis: 100%; }
  .profile-code { width: 38px; height: 38px; font-size: 15px; }
  .profile-titles h1 { font-size: 20px; }
  .holo-stage { height: 460px; }
  .evidence-grid { grid-template-columns: 1fr; }
  .timeline-track { height: auto; padding: 4px 0 10px; }
  .timeline-wave { display: none; }
  .timeline-node { position: static; width: 100%; transform: none; margin-top: 10px; }
  .timeline-node::after, .timeline-node__dot { display: none; }
  .timeline-arrow { display: none; }
  .profile-cta { letter-spacing: .14em; }
}

@media (prefers-reduced-motion: reduce) {
  .profile-cabin *, .profile-cabin *::before, .profile-cabin *::after {
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
  }
}
</style>
