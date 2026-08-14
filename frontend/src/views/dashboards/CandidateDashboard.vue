<template>
  <div class="cockpit candidate-dashboard">
    <div v-if="loading" class="cockpit-loading">正在读取你的成长数据...</div>

    <header class="cockpit-heading">
      <div class="cockpit-heading__copy">
        <span class="cockpit-eyebrow">我的求职进度</span>
        <h1>{{ greeting }}，{{ candidateHeadline }}</h1>
        <p>目标岗位：{{ targetRole }}。先看准备度和本周任务，再按需要进入完整报告、学习路径与能力图谱。</p>
      </div>
      <div class="cockpit-heading__actions">
        <span class="cockpit-updated">更新于 {{ updatedLabel }}</span>
        <button class="cockpit-button" type="button" :disabled="refreshing" @click="refresh(true)">
          <el-icon><Refresh /></el-icon>{{ refreshing ? '更新中' : '更新数据' }}
        </button>
      </div>
    </header>

    <section class="life-tree-stage">
      <LifeTreeScene
        :items="skillItems"
        :selected="selectedSkill"
        :target-role="targetRole"
        @select="selectSkill"
      />

      <div class="tree-readiness">
        <span class="brief-label">职业生命树 · {{ targetRole }}</span>
        <div class="score-line">
          <strong>{{ latestMatch ? Math.round(latestMatch.total_score || 0) : '--' }}</strong>
          <small v-if="latestMatch">% 准备度</small>
        </div>
        <span class="status-pill" :class="matchTagClass">{{ matchStatus }}</span>
        <h2>{{ latestMatch ? latestMatch.verdict || verdictText : '先确定目标岗位，让生命树开始生长' }}</h2>
        <p>{{ verdictDescription }}</p>
        <button class="primary-action" type="button" @click="router.push('/match-analysis')">
          {{ latestMatch ? '查看匹配报告' : '开始岗位匹配' }}
          <el-icon><ArrowRight /></el-icon>
        </button>
      </div>

      <div class="tree-controls">
        <label for="skill-focus">聚焦一项能力</label>
        <el-select id="skill-focus" v-model="selectedSkill" filterable placeholder="搜索技能" @change="focusSkill">
          <el-option v-for="item in skillItems" :key="item.name" :label="item.name" :value="item.name" />
        </el-select>
        <div v-if="selectedItem" class="selected-skill">
          <span :class="selectedItem.status">{{ selectedItem.category }}</span>
          <b>{{ selectedItem.name }}</b>
          <small>{{ selectedItem.status === 'missing' ? '目标岗位缺口，建议优先加入学习路径。' : selectedItem.status === 'growing' ? '正在成长，继续补充练习与项目证据。' : '已有能力证据，可继续强化成果表达。' }}</small>
        </div>
      </div>

      <div class="tree-priorities">
        <div class="tree-priorities__head">
          <span>下一批生长节点</span>
          <button type="button" @click="router.push('/learning-path')">学习路径 <el-icon><ArrowRight /></el-icon></button>
        </div>
        <button
          v-for="(item, index) in prioritySkills"
          :key="item.name"
          class="tree-priority"
          type="button"
          @click="focusSkill(item.name)"
        >
          <i>{{ index + 1 }}</i><span><b>{{ item.name }}</b><small>{{ item.reason }}</small></span>
        </button>
        <p v-if="!prioritySkills.length">{{ latestMatch ? '岗位核心技能已基本覆盖，下一步强化项目成果。' : '完成岗位匹配后，这里会显示最值得优先提升的技能。' }}</p>
      </div>

      <div class="tree-legend" aria-label="生命树节点图例">
        <span><i class="mastered"></i>已有证据</span>
        <span><i class="growing"></i>正在成长</span>
        <span><i class="missing"></i>岗位缺口</span>
      </div>
    </section>

    <section class="progress-strip" aria-label="求职资料概览">
      <button v-for="item in progressItems" :key="item.label" type="button" @click="router.push(item.path)">
        <el-icon><component :is="item.icon" /></el-icon>
        <span><b>{{ item.value }}{{ item.unit }}</b><small>{{ item.label }}</small></span>
        <em>{{ item.action }}</em>
        <i class="progress-meter"><span :style="{ width: `${item.progress}%` }"></span></i>
      </button>
    </section>

    <section class="workbench-grid">
      <article class="cockpit-panel weekly-panel">
        <div class="cockpit-panel__head">
          <div><div class="cockpit-panel__title">本周行动</div><p>按对求职结果的影响排序</p></div>
          <span class="cockpit-tag">{{ nextActions.length }} 项</span>
        </div>
        <div class="weekly-list">
          <button v-for="(action, index) in nextActions" :key="action.title" type="button" @click="router.push(action.path)">
            <span class="check-box">{{ index + 1 }}</span>
            <span><b>{{ action.title }}</b><small>{{ action.desc }}</small></span>
            <span class="do-now">去完成</span>
          </button>
        </div>
      </article>

      <article class="cockpit-panel evidence-panel">
        <div class="cockpit-panel__head"><div><div class="cockpit-panel__title">资料与证据</div><p>资料越完整，岗位建议越可靠</p></div></div>
        <div class="evidence-summary">
          <div class="profile-identity">
            <el-avatar :size="48" :src="model.profile.avatar_url || undefined">{{ (model.profile.real_name || '我').slice(0, 1) }}</el-avatar>
            <span><b>个人画像 {{ Math.round(model.profile.completeness || 0) }}%</b><small>{{ model.profile.education || '学历待补充' }} · {{ model.profile.city || '城市待补充' }}</small></span>
          </div>
          <div class="evidence-progress"><i :style="{ width: `${model.profile.completeness || 0}%` }"></i></div>
          <div class="resume-row">
            <el-icon><Document /></el-icon>
            <span><b>{{ latestResume?.source_filename || '还没有已解析简历' }}</b><small>{{ latestResume ? `最近更新 ${formatDate(latestResume.created_at)}` : '上传 PDF 或 Word 后会保留解析记录' }}</small></span>
          </div>
          <div class="evidence-actions">
            <button type="button" @click="router.push('/personal-center')">完善画像</button>
            <button type="button" @click="router.push('/resume-parser')">{{ latestResume ? '查看简历' : '上传简历' }}</button>
          </div>
        </div>
      </article>
    </section>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Aim, ArrowRight, Collection, Document, Medal, Refresh } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import LifeTreeScene, { type LifeTreeItem } from '@/components/dashboard/LifeTreeScene.vue'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import { formatSnapshotTime, readDashboardSnapshot, settledValue, writeDashboardSnapshot } from '@/utils/dashboardCache'

type CandidateModel = { summary: any; profile: any; resumes: any[]; matches: any[]; matchDetail: any; interviews: any[]; market: any }
const emptyModel: CandidateModel = { summary: {}, profile: {}, resumes: [], matches: [], matchDetail: {}, interviews: [], market: {} }

const auth = useAuthStore()
const router = useRouter()
const model = ref<CandidateModel>({ ...emptyModel })
const loading = ref(false)
const refreshing = ref(false)
const updatedAt = ref('')
const selectedSkill = ref('')
const cacheKey = computed(() => `sr-dashboard:candidate:${auth.user?.id || auth.user?.username || 'default'}`)

const greeting = computed(() => model.value.profile.real_name || auth.user?.display_name || '你好')
const targetRole = computed(() => model.value.profile.target_role || model.value.matches[0]?.target_job || '尚未选择')
const latestResume = computed(() => model.value.resumes[0])
const latestMatch = computed(() => model.value.matches[0])
const latestInterview = computed(() => model.value.interviews.find((item) => item.status === 'completed') || model.value.interviews[0])
const updatedLabel = computed(() => formatSnapshotTime(updatedAt.value))
const candidateHeadline = computed(() => !latestMatch.value ? '先完成第一次岗位匹配' : prioritySkills.value.length ? `距离目标岗位还有 ${prioritySkills.value.length} 个优先项` : '核心能力已经覆盖，开始强化证据')
const matchStatus = computed(() => !latestMatch.value ? '待分析' : latestMatch.value.total_score >= 80 ? '准备充分' : latestMatch.value.total_score >= 60 ? '提升后可投' : '需要补强')
const matchTagClass = computed(() => !latestMatch.value ? 'warning' : latestMatch.value.total_score >= 80 ? 'success' : latestMatch.value.total_score >= 60 ? 'warning' : 'danger')
const verdictText = computed(() => latestMatch.value?.total_score >= 80 ? '已具备较好的岗位竞争力' : latestMatch.value?.total_score >= 60 ? '补齐关键差距后再投递' : '建议先完成一轮系统提升')
const verdictDescription = computed(() => {
  if (!latestMatch.value) return '选择一份简历或个人画像，再选择目标岗位，系统会保留你的分析结果。'
  const count = model.value.matchDetail.missing_skills?.length || 0
  return count ? `当前识别到 ${count} 项必备能力差距，优先处理右侧前三项。` : '岗位必备技能已基本覆盖，建议强化项目成果和面试表达。'
})

function categoryFor(name: string) {
  if (/Python|Java|SQL|RAG|模型|算法|前端|后端|数据/.test(name)) return '专业技能'
  if (/沟通|表达|协作|项目|需求/.test(name)) return '通用能力'
  if (/Docker|Kubernetes|Linux|Git|部署/.test(name)) return '工程实践'
  return '岗位能力'
}

const prioritySkills = computed(() => (model.value.matchDetail.missing_skills || []).slice(0, 3).map((name: string, index: number) => ({
  name,
  category: categoryFor(name),
  reason: index === 0 ? '目标岗位必备，建议本周优先开始' : index === 1 ? '会直接影响项目完成度和面试回答' : '补齐后可提高岗位能力覆盖率'
})))

const progressItems = computed(() => [
  { label: '个人画像', value: Math.round(model.value.profile.completeness || 0), unit: '%', progress: Math.round(model.value.profile.completeness || 0), action: '完善资料', path: '/personal-center', icon: Collection },
  { label: '已解析简历', value: model.value.resumes.length, unit: ' 份', progress: Math.min(100, model.value.resumes.length * 50), action: '管理简历', path: '/resume-parser', icon: Document },
  { label: '岗位匹配', value: Math.round(latestMatch.value?.total_score || 0), unit: '%', progress: Math.round(latestMatch.value?.total_score || 0), action: '查看分析', path: '/match-analysis', icon: Aim },
  { label: '最近面试', value: Math.round(latestInterview.value?.final_score || 0), unit: ' 分', progress: Math.round(latestInterview.value?.final_score || 0), action: '继续练习', path: '/digital-interviewer', icon: Medal }
])

const skillItems = computed<LifeTreeItem[]>(() => {
  const owned = (model.value.profile.skills || []).map((skill: any, index: number) => ({
    name: typeof skill === 'string' ? skill : skill.name, score: Math.max(62, 92 - index * 4),
    category: categoryFor(typeof skill === 'string' ? skill : skill.name), status: index < 4 ? 'mastered' as const : 'growing' as const
  })).filter((item: LifeTreeItem) => item.name)
  const missing = (model.value.matchDetail.missing_skills || []).map((name: string, index: number) => ({ name, score: 34 + index * 3, category: categoryFor(name), status: 'missing' as const }))
  const fallback = ['Python', 'SQL', 'RAG', '项目管理', 'Docker', '模型部署'].map((name, index) => ({ name, score: 86 - index * 6, category: categoryFor(name), status: index < 4 ? 'mastered' as const : 'growing' as const }))
  const unique = new Map<string, LifeTreeItem>()
  ;(([...owned, ...missing].length ? [...owned, ...missing] : fallback)).forEach((item) => { if (!unique.has(item.name)) unique.set(item.name, item) })
  return [...unique.values()].slice(0, 18)
})

const selectedItem = computed(() => skillItems.value.find((item) => item.name === selectedSkill.value) || skillItems.value[0])
const nextActions = computed(() => {
  const firstGap = prioritySkills.value[0]?.name
  return [
    latestMatch.value
      ? { title: firstGap ? `开始学习 ${firstGap}` : '整理一个岗位相关项目', desc: firstGap ? '先完成基础学习和一个可展示的小任务' : '写清职责、过程和量化结果', path: '/learning-path' }
      : { title: '完成第一次岗位匹配', desc: '选定目标岗位，找到最值得优先提升的能力', path: '/match-analysis' },
    { title: latestResume.value ? '补充简历中的成果证据' : '上传并解析第一份简历', desc: latestResume.value ? '把项目结果写成可验证的数据和产出' : '支持 PDF 和 Word，解析历史会长期保留', path: '/resume-parser' },
    { title: '进行一次模拟面试', desc: '用真实岗位问题练习表达，结束后查看总评分', path: '/digital-interviewer' }
  ]
})

function selectSkill(item: LifeTreeItem) { selectedSkill.value = item.name }
function focusSkill(value: string) { selectedSkill.value = value }
function formatDate(value: string) { return value ? new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(value)) : '时间未知' }

async function refresh(force = false) {
  if (!force) {
    const cached = readDashboardSnapshot<CandidateModel>(cacheKey.value)
    if (cached) { model.value = cached.data; updatedAt.value = cached.updatedAt; selectedSkill.value = skillItems.value[0]?.name || ''; return }
  }
  loading.value = !force
  refreshing.value = force
  try {
    const results = await Promise.allSettled([api.overview(), api.myProfile(), api.resumes(), api.matchAnalysisHistory(), api.interviewSessions(), api.marketSnapshot()])
    const matches = settledValue(results[3], [] as any[])
    let matchDetail: any = {}
    if (matches[0]?.report_id) { try { matchDetail = await api.matchAnalysisDetail(matches[0].report_id) } catch { matchDetail = {} } }
    const next: CandidateModel = { summary: settledValue(results[0], {}), profile: settledValue(results[1], {}), resumes: settledValue(results[2], []), matches, matchDetail, interviews: settledValue(results[4], []), market: settledValue(results[5], {}) }
    const snapshot = writeDashboardSnapshot(cacheKey.value, next)
    model.value = snapshot.data; updatedAt.value = snapshot.updatedAt; selectedSkill.value = skillItems.value[0]?.name || ''
    if (force) ElMessage.success('个人成长数据已更新')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '个人成长数据加载失败')
  } finally { loading.value = false; refreshing.value = false }
}

onMounted(() => refresh(false))
</script>

<style scoped>
.candidate-dashboard { max-width: 1600px; margin: 0 auto; }
.life-tree-stage { position: relative; height: 650px; overflow: hidden; margin-bottom: 14px; border: 1px solid rgba(78,200,255,.15); border-radius: 12px; background: rgba(5, 30, 70, 0.25); box-shadow: 0 8px 30px rgba(0,10,40,.12); backdrop-filter: blur(6px); }
.life-tree-stage > .life-tree { position: absolute; inset: 0; }
.tree-readiness, .tree-controls, .tree-priorities { position: absolute; z-index: 2; border-left: 2px solid rgba(70,213,247,.72); padding: 13px 14px; background: rgba(8, 40, 85, 0.45); box-shadow: 0 6px 20px rgba(0,10,35,.12); backdrop-filter: blur(8px); }
.tree-readiness { top: 18px; left: 18px; width: min(294px, calc(100% - 36px)); }
.tree-controls { top: 18px; right: 18px; width: 276px; }
.tree-priorities { right: 18px; bottom: 18px; width: 300px; }
.brief-label { color: #70dcfa; font-size: 12px; font-weight: 800; }
.score-line { display: flex; align-items: baseline; gap: 6px; margin-top: 12px; }
.score-line strong { color: #f7fdff; font-size: 48px; line-height: .95; }
.score-line small { color: #a4bfd2; font-size: 13px; }
.status-pill { display: inline-block; margin-top: 10px; border-radius: 5px; padding: 5px 9px; color: #ffd094; background: rgba(118,71,14,.32); font-size: 11px; font-weight: 800; }
.status-pill.success { color: #73f1d4; background: rgba(14,104,86,.3); }.status-pill.danger { color: #ff9db0; background: rgba(118,26,45,.3); }
.tree-readiness h2 { margin: 11px 0 6px; color: #f3fbff; font-size: 17px; line-height: 1.35; }
.tree-readiness p { margin: 0 0 15px; color: #94b2c9; font-size: 12px; line-height: 1.65; }
.primary-action { display: inline-flex; align-items: center; gap: 8px; min-height: 42px; border: 0; border-radius: 8px; padding: 0 17px; color: #fff; background: #1676bd; font: inherit; font-size: 13px; font-weight: 800; cursor: pointer; }
.tree-controls > label { display: block; margin-bottom: 9px; color: #78def6; font-size: 11px; font-weight: 800; }
.tree-controls .el-select { width: 100%; }
.selected-skill { margin-top: 11px; }
.selected-skill span, .selected-skill b, .selected-skill small { display: block; }
.selected-skill span { color: #45a9ff; font-size: 10px; }.selected-skill span.mastered { color: #39e3cf; }.selected-skill span.missing { color: #ffc16c; }
.selected-skill b { margin-top: 4px; color: #eefaff; font-size: 15px; }
.selected-skill small { margin-top: 5px; color: #7d9db6; font-size: 11px; line-height: 1.5; }
.tree-priorities__head { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 8px; }
.tree-priorities__head > span { color: #e8faff; font-size: 12px; font-weight: 800; }
.tree-priorities__head button { display: inline-flex; align-items: center; gap: 4px; border: 0; padding: 4px 0; color: #75def8; background: transparent; font: inherit; font-size: 10px; cursor: pointer; }
.tree-priority { display: grid; grid-template-columns: 23px minmax(0,1fr); align-items: center; gap: 9px; width: 100%; border: 0; border-top: 1px solid rgba(70,156,206,.13); padding: 8px 0; color: inherit; background: transparent; font: inherit; text-align: left; cursor: pointer; }
.tree-priority:hover b { color: #67e5ff; }.tree-priority i { display: grid; place-items: center; width: 21px; height: 21px; border: 1px solid rgba(255,178,76,.48); border-radius: 50%; color: #ffc06b; font-size: 10px; font-style: normal; }
.tree-priority b, .tree-priority small { display: block; }.tree-priority b { color: #eefaff; font-size: 12px; }.tree-priority small { overflow: hidden; margin-top: 3px; color: #7898b1; font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }
.tree-priorities > p { margin: 8px 0 0; color: #88a9bf; font-size: 11px; line-height: 1.6; }
.tree-legend { position: absolute; z-index: 2; bottom: 18px; left: 18px; display: flex; flex-wrap: wrap; gap: 12px; color: #82a5bc; font-size: 10px; }
.tree-legend span { display: inline-flex; align-items: center; gap: 6px; }.tree-legend i { width: 7px; height: 7px; border-radius: 50%; }.tree-legend .mastered { background: #27e5d0; box-shadow: 0 0 8px rgba(39,229,208,.75); }.tree-legend .growing { background: #43a6ff; box-shadow: 0 0 8px rgba(67,166,255,.75); }.tree-legend .missing { background: #ffb24c; box-shadow: 0 0 8px rgba(255,178,76,.75); }
.progress-strip { display: grid; grid-template-columns: repeat(4,minmax(0,1fr)); gap: 10px; margin-bottom: 14px; }
.progress-strip button { position: relative; display: grid; grid-template-columns: 30px minmax(0,1fr) auto; align-items: center; gap: 10px; min-height: 78px; overflow: hidden; border: 1px solid rgba(78,200,255,.15); border-radius: 10px; padding: 12px 14px 16px; color: inherit; background: rgba(8, 42, 92, 0.3); font: inherit; text-align: left; cursor: pointer; }.progress-strip button:hover { border-color: rgba(71,215,255,.3); background: rgba(12, 55, 115, 0.4); }.progress-strip .el-icon { color: #42d5fa; font-size: 22px; }.progress-strip b,.progress-strip small { display: block; }.progress-strip b { color: #f3fbff; font-size: 18px; }.progress-strip small { margin-top: 3px; color: #7f9eb6; font-size: 11px; }.progress-strip em { color: #78dff7; font-size: 11px; font-style: normal; }.progress-meter { position: absolute; right: 0; bottom: 0; left: 0; height: 3px; background: rgba(65,128,170,.13); }.progress-meter span { display: block; height: 100%; background: #36c6e8; transform-origin: left; animation: candidate-bar-enter .75s ease-out both; }
@keyframes candidate-bar-enter { from { transform: scaleX(0); } }
.workbench-grid { display: grid; grid-template-columns: minmax(0,1.5fr) minmax(330px,.7fr); gap: 14px; margin-bottom: 14px; }.weekly-list { display: grid; gap: 9px; padding: 5px 16px 17px; }.weekly-list button { display: grid; grid-template-columns: 32px minmax(0,1fr) auto; align-items: center; gap: 12px; min-height: 64px; border: 1px solid rgba(70,158,216,.12); border-radius: 9px; padding: 10px 12px; color: inherit; background: rgba(10, 48, 95, 0.28); font: inherit; text-align: left; cursor: pointer; }.weekly-list button:hover { border-color: rgba(65,210,255,.25); background: rgba(15, 60, 115, 0.4); }.check-box { display: grid; place-items: center; width: 30px; height: 30px; border: 1px solid rgba(77,210,248,.4); border-radius: 7px; color: #83e7ff; font-weight: 900; }.weekly-list b,.weekly-list small { display: block; }.weekly-list b { color: #ecfaff; font-size: 14px; }.weekly-list small { margin-top: 5px; color: #7d9db6; font-size: 12px; }.do-now { color: #83e7ff; font-size: 12px; font-weight: 800; }
.evidence-summary { padding: 6px 16px 17px; }.profile-identity,.resume-row { display: flex; align-items: center; gap: 11px; }.profile-identity b,.profile-identity small,.resume-row b,.resume-row small { display: block; }.profile-identity b,.resume-row b { color: #eafaff; font-size: 13px; }.profile-identity small,.resume-row small { margin-top: 5px; color: #7898b1; font-size: 11px; }.evidence-progress { height: 5px; margin: 14px 0 17px; overflow: hidden; border-radius: 5px; background: rgba(79,133,171,.2); }.evidence-progress i { display: block; height: 100%; background: #36d7ff; }.resume-row { border-top: 1px solid rgba(75,157,209,.15); padding-top: 15px; }.resume-row > .el-icon { color: #49d7ff; font-size: 24px; }.resume-row span { min-width: 0; }.resume-row b { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }.evidence-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 17px; }.evidence-actions button { min-height: 36px; border: 1px solid rgba(63,202,255,.3); border-radius: 7px; color: #bdeffc; background: rgba(13,91,157,.23); font: inherit; font-size: 12px; font-weight: 800; cursor: pointer; }
@media (max-width: 1180px) { .progress-strip { grid-template-columns:repeat(2,1fr); }.workbench-grid { grid-template-columns:1fr; } }
@media (max-width: 760px) {
  .life-tree-stage { height: 1080px; border-radius: 8px; }
  .tree-readiness, .tree-controls, .tree-priorities { right: 12px; left: 12px; width: auto; padding: 12px 13px; }
  .tree-readiness { top: 12px; }
  .tree-readiness .score-line { margin-top: 7px; }.tree-readiness .score-line strong { font-size: 40px; }.tree-readiness h2 { margin-top: 9px; font-size: 16px; }.tree-readiness p { margin-bottom: 10px; }.tree-readiness .primary-action { min-height: 36px; }
  .tree-controls { top: 270px; }
  .tree-priorities { bottom: 46px; }
  .tree-legend { right: 12px; bottom: 15px; left: 12px; justify-content: center; }
  .progress-strip { grid-template-columns: 1fr 1fr; }.progress-strip button { grid-template-columns: 26px minmax(0,1fr); }.progress-strip em { display: none; }
}
</style>
