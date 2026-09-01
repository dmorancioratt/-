<template>
  <div class="cockpit-container" :class="{ 'panel-open': activePanel }">
    <button v-if="!activePanel" class="exit-button" type="button" @click="router.push('/overview')">
      <el-icon><ArrowLeft /></el-icon><span>返回概览</span>
    </button>
    <button v-if="!activePanel" class="refresh-button" type="button" :disabled="loading" @click="loadData">
      <el-icon><Refresh /></el-icon><span>{{ loading ? '同步中' : '同步真实数据' }}</span>
    </button>

    <GrowthCockpitScene :active-module="activePanel" @focus="openPanel" />

    <aside v-if="activePanel" class="data-cabin">
      <header class="cabin-header">
        <button type="button" title="返回驾驶舱" @click="activePanel = null"><el-icon><ArrowLeft /></el-icon></button>
        <div><small>{{ activeMeta.code }}</small><h1>{{ activeMeta.title }}</h1></div>
        <span class="live-state"><i></i>{{ updatedAt ? `已同步 ${updatedAt}` : '等待同步' }}</span>
      </header>

      <div v-if="loading" class="state-panel">正在读取当前账号数据...</div>
      <div v-else-if="loadError" class="state-panel error">{{ loadError }}</div>

      <main v-else class="cabin-content">
        <template v-if="activePanel === 'radar'">
          <section class="metric-grid">
            <article><strong>{{ profileSkills.length }}</strong><span>画像技能</span></article>
            <article><strong>{{ missingSkills.length }}</strong><span>待补能力</span></article>
            <article><strong>{{ latestMatch ? `${matchScore}%` : '—' }}</strong><span>最近匹配</span></article>
          </section>
          <DataSection title="已录入技能" :empty="!profileSkills.length" empty-text="个人画像尚未录入技能">
            <div class="tag-cloud"><span v-for="skill in profileSkills" :key="skill">{{ skill }}</span></div>
          </DataSection>
          <DataSection title="岗位匹配识别的缺口" :empty="!missingSkills.length" empty-text="完成岗位匹配后生成真实技能缺口">
            <div class="tag-cloud warning"><span v-for="skill in missingSkills" :key="skill">{{ skill }}</span></div>
          </DataSection>
          <ActionButton label="进入岗位匹配" @click="router.push('/match-analysis')" />
        </template>

        <template v-else-if="activePanel === 'path'">
          <section class="hero-status">
            <small>LEARNING PATH SOURCE</small>
            <h2>{{ latestMatch?.target_job || '尚未选择目标岗位' }}</h2>
            <p>{{ latestMatch ? '学习路径基于最近一次岗位匹配报告生成。' : '当前账号还没有岗位匹配报告，不能生成真实学习路径。' }}</p>
          </section>
          <DataSection title="优先提升建议" :empty="!suggestions.length" empty-text="完成岗位匹配后，这里将展示报告中的提升建议">
            <ol class="record-list"><li v-for="(item, index) in suggestions" :key="index"><b>{{ pad(index + 1) }}</b><span>{{ item }}</span></li></ol>
          </DataSection>
          <ActionButton :label="latestMatch ? '查看完整学习路径' : '先完成岗位匹配'" @click="goLearningPath" />
        </template>

        <template v-else-if="activePanel === 'avatar'">
          <section class="profile-head">
            <div class="avatar">{{ avatarText }}</div>
            <div><small>CANDIDATE PROFILE</small><h2>{{ profile.real_name || auth.user?.display_name || auth.user?.username || '当前用户' }}</h2><p>{{ profile.target_role || '尚未设置目标岗位' }}</p></div>
          </section>
          <section class="metric-grid four">
            <article><strong>{{ Math.round(Number(profile.completeness || 0)) }}%</strong><span>资料完整度</span></article>
            <article><strong>{{ resumes.length }}</strong><span>简历记录</span></article>
            <article><strong>{{ matches.length }}</strong><span>匹配报告</span></article>
            <article><strong>{{ interviews.length }}</strong><span>面试记录</span></article>
          </section>
          <DataSection title="档案信息" :empty="false">
            <dl class="profile-fields">
              <div><dt>学校</dt><dd>{{ profile.school || '未填写' }}</dd></div><div><dt>专业</dt><dd>{{ profile.major || '未填写' }}</dd></div>
              <div><dt>学历</dt><dd>{{ profile.education || '未填写' }}</dd></div><div><dt>所在城市</dt><dd>{{ profile.city || '未填写' }}</dd></div>
            </dl>
          </DataSection>
          <ActionButton label="编辑账号资料" @click="router.push('/account-settings')" />
        </template>

        <template v-else-if="activePanel === 'ai-suggest'">
          <section class="hero-status">
            <small>REPORT-BASED ADVICE</small><h2>{{ latestMatch?.target_job || '暂无分析对象' }}</h2>
            <p>{{ verdict || 'AI 建议只展示已保存岗位匹配报告的分析结果。' }}</p>
          </section>
          <DataSection title="报告建议" :empty="!suggestions.length" empty-text="当前没有已保存的 AI 建议">
            <ol class="record-list"><li v-for="(item, index) in suggestions" :key="index"><b>{{ pad(index + 1) }}</b><span>{{ item }}</span></li></ol>
          </DataSection>
          <ActionButton label="发起新的岗位分析" @click="router.push('/match-analysis')" />
        </template>

        <template v-else-if="activePanel === 'weekly-plan'">
          <section class="hero-status neutral">
            <small>PERSISTENCE STATUS</small><h2>本周计划</h2>
            <p>当前后端尚未提供个人任务计划的持久化接口，因此不展示虚假的完成进度或学习时长。</p>
          </section>
          <DataSection title="可执行建议（来自最近匹配报告）" :empty="!suggestions.length" empty-text="完成岗位匹配后可获得真实建议">
            <ol class="record-list"><li v-for="(item, index) in suggestions" :key="index"><b>{{ pad(index + 1) }}</b><span>{{ item }}</span></li></ol>
          </DataSection>
          <ActionButton label="进入学习路径" @click="goLearningPath" />
        </template>

        <template v-else-if="activePanel === 'resource-library'">
          <section class="hero-status neutral"><small>RESOURCE API STATUS</small><h2>个人学习资源</h2><p>当前后端尚未提供个人收藏、学习进度和资源评分接口，此处不再展示示例课程、虚构耗时或完成状态。</p></section>
          <DataSection title="当前学习依据" :empty="!missingSkills.length" empty-text="完成岗位匹配后生成需要提升的真实能力项">
            <div class="tag-cloud warning"><span v-for="skill in missingSkills" :key="skill">{{ skill }}</span></div>
          </DataSection>
          <ActionButton label="打开学习路径" @click="goLearningPath" />
        </template>

        <template v-else-if="activePanel === 'timeline'">
          <section class="metric-grid"><article><strong>{{ activityEvents.length }}</strong><span>真实活动记录</span></article><article><strong>{{ resumes.length }}</strong><span>简历</span></article><article><strong>{{ matches.length + interviews.length }}</strong><span>分析与面试</span></article></section>
          <DataSection title="成长记录" :empty="!activityEvents.length" empty-text="当前账号尚无简历、匹配或面试记录">
            <ol class="timeline-list"><li v-for="item in activityEvents" :key="`${item.type}-${item.id}`"><time>{{ formatDate(item.date) }}</time><b>{{ item.title }}</b><span>{{ item.detail }}</span></li></ol>
          </DataSection>
        </template>
      </main>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onMounted, ref } from 'vue'
import { ArrowLeft, Refresh } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import GrowthCockpitScene from '@/components/cockpit/GrowthCockpitScene.vue'

const router = useRouter()
const auth = useAuthStore()
const activePanel = ref<string | null>(null)
const loading = ref(false)
const loadError = ref('')
const updatedAt = ref('')
const profile = ref<any>({})
const resumes = ref<any[]>([])
const matches = ref<any[]>([])
const matchDetail = ref<any>({})
const interviews = ref<any[]>([])

const DataSection = defineComponent({
  props: { title: String, empty: Boolean, emptyText: String },
  setup(props, { slots }) { return () => h('section', { class: 'data-section' }, [h('h3', props.title), props.empty ? h('div', { class: 'empty-state' }, props.emptyText) : slots.default?.()]) }
})
const ActionButton = defineComponent({
  props: { label: String }, emits: ['click'],
  setup(props, { emit }) { return () => h('button', { class: 'primary-action', type: 'button', onClick: () => emit('click') }, [h('span', props.label), h('b', '→')]) }
})

const panelMeta: Record<string, { code: string; title: string }> = {
  radar: { code: 'SKILL GRAPH / LIVE PROFILE', title: '个人能力图谱' }, path: { code: 'LEARNING PATH / MATCH REPORT', title: '成长路径' },
  avatar: { code: 'PROFILE / CURRENT USER', title: '成长档案' }, 'ai-suggest': { code: 'AI ADVICE / SAVED REPORT', title: 'AI 分析建议' },
  'weekly-plan': { code: 'WEEK PLAN / ACCOUNT DATA', title: '本周计划' }, 'resource-library': { code: 'RESOURCE VAULT / ACCOUNT DATA', title: '学习资源库' },
  timeline: { code: 'ACTIVITY / DATABASE RECORDS', title: '成长时间线' }
}
const activeMeta = computed(() => panelMeta[activePanel.value || ''] || { code: 'COCKPIT', title: '个人驾驶舱' })
const latestMatch = computed(() => matches.value[0])
const matchScore = computed(() => Math.round(Number(latestMatch.value?.total_score || 0)))
const profileSkills = computed(() => (profile.value.skills || []).map((item: any) => typeof item === 'string' ? item : item?.name).filter(Boolean))
const missingSkills = computed(() => (matchDetail.value.missing_skills || []).filter(Boolean))
const suggestions = computed(() => {
  const ai = matchDetail.value.ai_analysis || {}
  return (ai.suggestions || matchDetail.value.suggestions || []).filter(Boolean)
})
const verdict = computed(() => matchDetail.value.ai_analysis?.verdict || latestMatch.value?.verdict || '')
const avatarText = computed(() => String(profile.value.real_name || auth.user?.display_name || auth.user?.username || '用').slice(0, 1))
const activityEvents = computed(() => [
  ...resumes.value.map((item) => ({ type: 'resume', id: item.id, date: item.created_at, title: '保存简历', detail: item.source_filename || item.name || '简历记录' })),
  ...matches.value.map((item) => ({ type: 'match', id: item.report_id, date: item.created_at, title: '完成岗位匹配', detail: `${item.target_job || '目标岗位'} · ${Math.round(Number(item.total_score || 0))} 分` })),
  ...interviews.value.map((item) => ({ type: 'interview', id: item.id, date: item.completed_at || item.updated_at || item.created_at, title: item.status === 'completed' ? '完成模拟面试' : '开始模拟面试', detail: `${item.job_name || '未命名岗位'}${item.status === 'completed' ? ` · ${Math.round(Number(item.final_score || 0))} 分` : ''}` }))
].filter((item) => item.date).sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()))

function pad(value: number) { return String(value).padStart(2, '0') }
function formatDate(value: string) { return value ? new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(value)) : '时间未知' }
function openPanel(id: string) { if (panelMeta[id]) activePanel.value = id }
function goLearningPath() { latestMatch.value?.report_id ? router.push({ path: '/learning-path', query: { reportId: String(latestMatch.value.report_id) } }) : router.push('/match-analysis') }
async function loadData() {
  loading.value = true; loadError.value = ''
  try {
    const [p, r, m, i] = await Promise.all([api.myProfile(), api.resumes(), api.matchAnalysisHistory(), api.interviewSessions()])
    profile.value = p || {}; resumes.value = r || []; matches.value = m || []; interviews.value = i || []
    matchDetail.value = matches.value[0]?.report_id ? await api.matchAnalysisDetail(matches.value[0].report_id) : {}
    updatedAt.value = new Intl.DateTimeFormat('zh-CN', { hour: '2-digit', minute: '2-digit' }).format(new Date())
  } catch (error: any) { loadError.value = error?.response?.data?.detail || '个人数据加载失败，请检查后端服务' }
  finally { loading.value = false }
}
onMounted(loadData)
</script>

<style scoped>
.cockpit-container { position: fixed; inset: 0; overflow: hidden; background: #020817; color: #e9faff; font-family: "Microsoft YaHei", sans-serif; }
.exit-button,.refresh-button { position: fixed; z-index: 40; top: 22px; display: inline-flex; align-items: center; gap: 8px; border: 1px solid rgba(105, 216, 255, .38); border-radius: 7px; padding: 10px 14px; color: #dff9ff; background: rgba(3, 22, 54, .82); font: inherit; font-size: 12px; cursor: pointer; backdrop-filter: blur(12px); }
.exit-button { left: 22px; }.refresh-button { right: 22px; }.refresh-button:disabled { opacity: .55; cursor: wait; }
.data-cabin { position: fixed; z-index: 50; inset: 3.5vh 3vw; display: grid; grid-template-rows: auto 1fr; overflow: hidden; border: 1px solid rgba(85, 218, 255, .48); border-radius: 8px; background: radial-gradient(circle at 20% 0, rgba(19, 95, 178, .25), transparent 38%), rgba(2, 13, 35, .96); box-shadow: 0 26px 90px rgba(0, 0, 0, .65), inset 0 0 60px rgba(34, 128, 215, .08); backdrop-filter: blur(18px); }
.cabin-header { display: grid; grid-template-columns: 42px 1fr auto; align-items: center; gap: 14px; border-bottom: 1px solid rgba(66, 176, 235, .24); padding: 17px 22px; }
.cabin-header button { display: grid; width: 38px; height: 38px; place-items: center; border: 1px solid rgba(80, 209, 255, .34); border-radius: 5px; color: #71e6ff; background: rgba(20, 92, 162, .2); cursor: pointer; }
.cabin-header small,.profile-head small,.hero-status small { color: #56dfff; font: 700 9px Consolas, monospace; letter-spacing: 1.5px; }.cabin-header h1 { margin: 4px 0 0; font-size: 19px; letter-spacing: 0; }
.live-state { color: #7ea6c1; font-size: 10px; }.live-state i { display: inline-block; width: 6px; height: 6px; margin-right: 7px; border-radius: 50%; background: #48e3b5; box-shadow: 0 0 9px #48e3b5; }
.cabin-content { width: min(1120px, calc(100% - 40px)); margin: 0 auto; padding: 28px 0 40px; overflow-y: auto; }
.state-panel { display: grid; place-items: center; color: #86aac3; }.state-panel.error { color: #ff98aa; }
.metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }.metric-grid.four { grid-template-columns: repeat(4, 1fr); }.metric-grid article { min-height: 105px; display: grid; place-content: center; border: 1px solid rgba(67, 184, 244, .23); border-radius: 6px; text-align: center; background: rgba(6, 39, 82, .5); }.metric-grid strong { color: #64e6ff; font: 800 29px Consolas, monospace; }.metric-grid span { margin-top: 8px; color: #82a6c0; font-size: 11px; }
.data-section { margin-top: 15px; border: 1px solid rgba(66, 171, 230, .2); border-radius: 6px; padding: 20px; background: rgba(4, 29, 65, .56); }.data-section h3 { margin: 0 0 16px; font-size: 14px; }.empty-state { min-height: 80px; display: grid; place-items: center; color: #7195af; font-size: 11px; }
.tag-cloud { display: flex; flex-wrap: wrap; gap: 8px; }.tag-cloud span { border: 1px solid rgba(77, 214, 255, .3); border-radius: 4px; padding: 7px 10px; color: #a8eaff; background: rgba(20, 103, 173, .17); font-size: 11px; }.tag-cloud.warning span { border-color: rgba(255, 181, 85, .28); color: #ffd095; background: rgba(125, 75, 16, .15); }
.hero-status { border-left: 3px solid #58dcff; padding: 10px 0 10px 20px; }.hero-status.neutral { border-left-color: #ffbc62; }.hero-status h2 { margin: 8px 0; font-size: 25px; }.hero-status p { max-width: 760px; margin: 0; color: #86a9c2; font-size: 12px; line-height: 1.8; }
.record-list,.timeline-list { display: grid; gap: 8px; margin: 0; padding: 0; list-style: none; }.record-list li { display: grid; grid-template-columns: 35px 1fr; align-items: center; gap: 10px; border-bottom: 1px solid rgba(64, 151, 208, .13); padding: 10px 0; }.record-list b { color: #52dfff; font: 700 11px Consolas, monospace; }.record-list span { color: #c5dfef; font-size: 12px; line-height: 1.6; }
.profile-head { display: flex; align-items: center; gap: 18px; margin-bottom: 18px; }.avatar { display: grid; width: 76px; height: 76px; place-items: center; border: 1px solid #65e4ff; border-radius: 50%; color: #eaffff; background: radial-gradient(circle, #1763a7, #071a3b); box-shadow: 0 0 25px rgba(68, 210, 255, .28); font-size: 28px; }.profile-head h2 { margin: 5px 0; }.profile-head p { margin: 0; color: #86aac4; font-size: 12px; }
.profile-fields { display: grid; grid-template-columns: 1fr 1fr; gap: 0; margin: 0; }.profile-fields div { display: grid; grid-template-columns: 90px 1fr; border-bottom: 1px solid rgba(72, 153, 207, .13); padding: 11px 0; }.profile-fields dt { color: #749ab5; font-size: 11px; }.profile-fields dd { margin: 0; font-size: 12px; }
.timeline-list li { display: grid; grid-template-columns: 110px 150px 1fr; gap: 14px; border-bottom: 1px solid rgba(67, 153, 211, .14); padding: 13px 0; }.timeline-list time { color: #6bdfff; font: 10px Consolas, monospace; }.timeline-list b { font-size: 12px; }.timeline-list span { color: #82a5bd; font-size: 11px; }
.primary-action { display: flex; align-items: center; justify-content: space-between; width: 100%; margin-top: 15px; border: 1px solid rgba(76, 219, 255, .48); border-radius: 6px; padding: 14px 18px; color: #effdff; background: linear-gradient(90deg, rgba(23, 137, 219, .55), rgba(34, 91, 206, .42)); font: inherit; font-size: 12px; cursor: pointer; }.primary-action:hover { border-color: #7deaff; filter: brightness(1.12); }
@media (max-width: 700px) { .data-cabin { inset: 10px; }.cabin-content { width: calc(100% - 24px); padding-top: 18px; }.metric-grid,.metric-grid.four { grid-template-columns: 1fr 1fr; }.cabin-header { grid-template-columns: 38px 1fr; }.live-state { display: none; }.timeline-list li { grid-template-columns: 1fr; gap: 5px; }.profile-fields { grid-template-columns: 1fr; } }
</style>
