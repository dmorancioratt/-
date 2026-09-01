<template>
  <div class="candidate-dashboard">
    <div v-if="loading" class="cockpit-loading">正在读取你的成长数据...</div>

    <section id="career-map" class="career-hero" aria-labelledby="career-title">
      <article class="hero-card readiness-card">
        <span class="section-kicker">职业进化引擎</span>
        <p class="card-label">目标岗位</p>
        <h2>{{ targetRole }}</h2>
        <span class="role-tag">{{ latestMatch ? '已完成诊断' : '等待诊断' }}</span>

        <p class="card-label readiness-label">当前匹配度</p>
        <div class="readiness-score">
          <svg viewBox="0 0 120 120" aria-hidden="true">
            <circle class="score-track" cx="60" cy="60" r="51" />
            <circle class="score-progress" cx="60" cy="60" r="51" :style="{ strokeDashoffset: scoreOffset }" />
          </svg>
          <strong>{{ matchScore }}<small>%</small></strong>
        </div>
        <div class="score-verdict">
          <b :class="matchTagClass">{{ matchStatus }}</b>
          <span>{{ latestMatch ? '岗位准备度持续更新' : '完成匹配后自动生成' }}</span>
        </div>

        <div class="skill-summary">
          <span>核心优势</span>
          <div><i v-for="skill in ownedSkills" :key="skill">{{ skill }}</i></div>
          <span>优先补强</span>
          <div><i v-for="skill in missingSkills" :key="skill" class="gap">{{ skill }}</i></div>
        </div>
        <button class="primary-action" type="button" @click="router.push('/match-analysis')">
          {{ latestMatch ? '查看智能分析' : '开始智能分析' }} <el-icon><ArrowRight /></el-icon>
        </button>
      </article>

      <article class="journey-stage" aria-label="职业成长视频">
        <div class="video-shell" :class="{ 'video-unavailable': videoUnavailable }">
          <video v-if="!videoUnavailable" class="career-video" autoplay muted loop playsinline @error="videoUnavailable = true">
            <source src="/Digital_path_transforms_into_river_202608242002.mp4" type="video/mp4" />
          </video>
          <div v-else class="video-fallback">职业成长视频暂不可用</div>
        </div>
      </article>

      <article class="hero-card focus-card">
        <span class="section-kicker">FOCUS NOW</span>
        <h2>当前聚焦能力</h2>
        <div class="focus-skill">
          <div class="skill-icon"><el-icon><Connection /></el-icon></div>
          <div><b>{{ selectedSkill || prioritySkills[0]?.name || '岗位核心能力' }}</b><small>{{ selectedItem?.category || '待完成岗位匹配' }}</small></div>
        </div>
        <div class="focus-progress"><span :style="{ width: `${selectedItem?.score || 42}%` }"></span></div>
        <button class="plain-link" type="button" @click="router.push('/capability-evolution')">查看能力图谱 <el-icon><ArrowRight /></el-icon></button>

        <div class="recommendation">
          <span>下一步推荐</span>
          <button type="button" @click="router.push('/learning-path')">
            <el-icon><Reading /></el-icon>
            <span><b>{{ prioritySkills[0]?.name ? `开始学习 ${prioritySkills[0].name}` : '生成学习路径' }}</b><small>{{ prioritySkills[0]?.reason || '先完成岗位匹配，系统会给出优先建议' }}</small></span>
            <el-icon><ArrowRight /></el-icon>
          </button>
        </div>

        <div class="trend-box">
          <div><span>能力提升预测</span><b>+{{ predictedGain }}%</b></div>
          <svg viewBox="0 0 270 64" preserveAspectRatio="none" aria-hidden="true"><path d="M0,52 C30,48 37,54 64,44 S107,43 130,31 S178,36 198,21 S232,25 270,8" /></svg>
          <small>当前 <i></i> 30天后 <i></i> 60天后</small>
        </div>
      </article>
    </section>

    <section id="readiness" class="progress-strip" aria-label="求职准备进度">
      <button v-for="item in progressItems" :key="item.label" class="progress-card" type="button" @click="router.push(item.path)">
        <span class="progress-icon"><el-icon><component :is="item.icon" /></el-icon></span>
        <span class="progress-copy"><b>{{ item.value }}{{ item.unit }}</b><small>{{ item.label }}</small></span>
        <em>{{ item.action }} <el-icon><ArrowRight /></el-icon></em>
        <i class="progress-meter"><span :style="{ width: `${item.progress}%` }"></span></i>
      </button>
    </section>

    <section id="actions" class="overview-section action-layout">
      <article class="overview-panel actions-panel">
        <div class="panel-heading">
          <div><span class="section-kicker">THIS WEEK</span><h2>本周行动任务</h2><p>完成任务，持续提升岗位匹配度</p></div>
          <span class="panel-count">{{ nextActions.length }} 项待完成</span>
        </div>
        <div class="action-list">
          <button v-for="(action, index) in nextActions" :key="action.title" type="button" @click="router.push(action.path)">
            <b>{{ String(index + 1).padStart(2, '0') }}</b>
            <span><strong>{{ action.title }}</strong><small>{{ action.desc }}</small></span>
            <em>去完成 <el-icon><ArrowRight /></el-icon></em>
          </button>
        </div>
      </article>

      <article class="overview-panel milestones-panel">
        <div class="panel-heading"><div><span class="section-kicker">CAREER TRACE</span><h2>成长里程碑</h2><p>把能力沉淀为看得见的求职竞争力</p></div></div>
        <ol class="milestone-list">
          <li :class="{ done: (model.profile.completeness || 0) >= 70 }"><span></span><div><b>完善个人画像</b><small>让岗位建议建立在真实经历之上</small></div></li>
          <li :class="{ done: Boolean(latestResume) }"><span></span><div><b>解析并优化简历</b><small>{{ latestResume ? latestResume.source_filename : '上传第一份 PDF 或 Word 简历' }}</small></div></li>
          <li :class="{ done: Boolean(latestMatch) }"><span></span><div><b>完成目标岗位匹配</b><small>{{ latestMatch ? `${matchScore}% 准备度已生成` : '识别关键能力差距与行动建议' }}</small></div></li>
          <li :class="{ done: Boolean(latestInterview?.final_score) }"><span></span><div><b>完成模拟面试</b><small>{{ latestInterview?.final_score ? `最近得分 ${Math.round(latestInterview.final_score)} 分` : '练习真实岗位问题与表达' }}</small></div></li>
        </ol>
      </article>
    </section>

    <section id="evidence" class="overview-section evidence-layout">
      <article class="overview-panel profile-panel">
        <div class="panel-heading"><div><span class="section-kicker">PROFILE & EVIDENCE</span><h2>资料与证据</h2><p>完整资料让 AI 推荐更可信</p></div><button class="outline-button" type="button" @click="router.push('/personal-center')">完善资料</button></div>
        <div class="profile-summary">
          <el-avatar :size="62" :src="model.profile.avatar_url || undefined">{{ (model.profile.real_name || '我').slice(0, 1) }}</el-avatar>
          <div><b>个人画像完整度 <em>{{ Math.round(model.profile.completeness || 0) }}%</em></b><small>{{ model.profile.education || '学历待补充' }} · {{ model.profile.city || '城市待补充' }}</small><div class="evidence-progress"><i :style="{ width: `${model.profile.completeness || 0}%` }"></i></div></div>
        </div>
        <div class="resume-evidence">
          <span class="resume-icon"><el-icon><Document /></el-icon></span>
          <div><b>{{ latestResume?.source_filename || '尚未上传可解析简历' }}</b><small>{{ latestResume ? `最近更新 ${formatDate(latestResume.created_at)}` : '支持 PDF 与 Word，解析结果将长期保存' }}</small></div>
          <button type="button" @click="router.push('/resume-parser')">{{ latestResume ? '查看简历' : '上传简历' }}</button>
        </div>
      </article>

      <article class="overview-panel skills-panel">
        <div class="panel-heading"><div><span class="section-kicker">SKILL SIGNAL</span><h2>能力信号</h2><p>从总览进入完整的能力演化图谱</p></div><button class="outline-button" type="button" @click="router.push('/capability-evolution')">能力图谱</button></div>
        <div class="skill-cloud">
          <button v-for="item in skillItems.slice(0, 8)" :key="item.name" type="button" :class="['skill-pill', item.status, { active: selectedSkill === item.name }]" @click="focusSkill(item.name)">
            <span>{{ item.name }}</span><small>{{ item.score }}%</small>
          </button>
        </div>
        <p class="skill-footnote"><el-icon><TrendCharts /></el-icon>{{ selectedItem ? `${selectedItem.name}：${selectedItem.status === 'missing' ? '建议优先安排学习任务' : '可继续补充项目与实践证据'}` : '完成岗位匹配后，可查看更精准的能力建议。' }}</p>
      </article>
    </section>

    <!-- 底部数据状态栏：刷新操作与更新时间集中在此，顶部导航只负责区块跳转 -->
    <footer class="overview-footer">
      <div class="overview-footer__status">
        <span class="status-dot" :class="{ busy: refreshing }"></span>
        <span>{{ refreshing ? '正在重新拉取最新成长数据…' : '个人成长数据就绪' }}</span>
        <span class="footer-divider"></span>
        <span>更新于 {{ updatedLabel }}</span>
      </div>
      <button type="button" :disabled="refreshing" @click="refresh(true)">
        <el-icon :class="{ 'fa-spin': refreshing }"><Refresh /></el-icon>{{ refreshing ? '更新中' : '更新数据' }}
      </button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Aim, ArrowRight, Collection, Connection, Document, Medal, Reading, Refresh, TrendCharts } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import { formatSnapshotTime, readDashboardSnapshot, settledValue, writeDashboardSnapshot } from '@/utils/dashboardCache'
type SkillStatus = 'mastered' | 'growing' | 'missing'
type SkillItem = { name: string; score: number; category: string; status: SkillStatus }
type CandidateModel = { summary: any; profile: any; resumes: any[]; matches: any[]; matchDetail: any; interviews: any[]; market: any }
const emptyModel: CandidateModel = { summary: {}, profile: {}, resumes: [], matches: [], matchDetail: {}, interviews: [], market: {} }

const auth = useAuthStore()
const router = useRouter()
const model = ref<CandidateModel>({ ...emptyModel })
const loading = ref(false)
const refreshing = ref(false)
const videoUnavailable = ref(false)
const updatedAt = ref('')
const selectedSkill = ref('')
const cacheKey = computed(() => `sr-dashboard:candidate:${auth.user?.id || auth.user?.username || 'default'}`)
const updatedLabel = computed(() => formatSnapshotTime(updatedAt.value))

const targetRole = computed(() => model.value.profile.target_role || model.value.matches[0]?.target_job || '大模型应用工程师')
const latestResume = computed(() => model.value.resumes[0])
const latestMatch = computed(() => model.value.matches[0])
const latestInterview = computed(() => model.value.interviews.find((item) => item.status === 'completed') || model.value.interviews[0])
const matchScore = computed(() => Math.round(latestMatch.value?.total_score || 0))
const scoreOffset = computed(() => `${320 - (320 * matchScore.value) / 100}`)
const matchStatus = computed(() => !latestMatch.value ? '待分析' : matchScore.value >= 80 ? '准备充分' : matchScore.value >= 60 ? '提升后可投' : '需要补强')
const matchTagClass = computed(() => !latestMatch.value ? 'warning' : matchScore.value >= 80 ? 'success' : matchScore.value >= 60 ? 'warning' : 'danger')
const predictedGain = computed(() => Math.max(12, Math.min(36, Math.round((model.value.matchDetail.missing_skills?.length || 3) * 6 + 6))))

function categoryFor(name: string) {
  if (/Python|Java|SQL|RAG|模型|算法|前端|后端|数据/.test(name)) return '专业技能'
  if (/沟通|表达|协作|项目|需求/.test(name)) return '通用能力'
  if (/Docker|Kubernetes|Linux|Git|部署/.test(name)) return '工程实践'
  return '岗位能力'
}

const prioritySkills = computed<Array<{ name: string; category: string; reason: string }>>(() => (model.value.matchDetail.missing_skills || []).slice(0, 3).map((name: string, index: number) => ({
  name,
  category: categoryFor(name),
  reason: index === 0 ? '目标岗位必备，建议本周优先开始' : index === 1 ? '会直接影响项目完成度和面试回答' : '补齐后可提高岗位能力覆盖率'
})))
const ownedSkills = computed(() => (model.value.profile.skills || []).map((item: any) => typeof item === 'string' ? item : item.name).filter(Boolean).slice(0, 3).length ? (model.value.profile.skills || []).map((item: any) => typeof item === 'string' ? item : item.name).filter(Boolean).slice(0, 3) : ['Python 开发', '逻辑思维', '数据分析'])
const missingSkills = computed(() => prioritySkills.value.map((item) => item.name).length ? prioritySkills.value.map((item) => item.name) : ['RAG 工程化', 'Agent 协同', '项目落地经验'])
const skillItems = computed<SkillItem[]>(() => {
  const owned = (model.value.profile.skills || []).map((skill: any, index: number) => ({ name: typeof skill === 'string' ? skill : skill.name, score: Math.max(62, 92 - index * 4), category: categoryFor(typeof skill === 'string' ? skill : skill.name), status: (index < 4 ? 'mastered' : 'growing') as SkillStatus })).filter((item: SkillItem) => item.name)
  const missing = (model.value.matchDetail.missing_skills || []).map((name: string, index: number) => ({ name, score: 34 + index * 3, category: categoryFor(name), status: 'missing' as SkillStatus }))
  const fallback = ['Python', 'SQL', 'RAG', '项目管理', 'Docker', '模型部署'].map((name, index) => ({ name, score: 86 - index * 6, category: categoryFor(name), status: (index < 4 ? 'mastered' : 'growing') as SkillStatus }))
  const unique = new Map<string, SkillItem>()
  ;(([...owned, ...missing].length ? [...owned, ...missing] : fallback)).forEach((item) => { if (!unique.has(item.name)) unique.set(item.name, item) })
  return [...unique.values()].slice(0, 12)
})
const selectedItem = computed(() => skillItems.value.find((item) => item.name === selectedSkill.value) || skillItems.value[0])
const nextActions = computed(() => {
  const firstGap = prioritySkills.value[0]?.name
  return [
    latestMatch.value ? { title: firstGap ? `开始学习 ${firstGap}` : '整理一个岗位相关项目', desc: firstGap ? '先完成基础学习和一个可展示的小任务' : '写清职责、过程和量化结果', path: '/learning-path' } : { title: '完成第一次岗位匹配', desc: '选定目标岗位，找到最值得优先提升的能力', path: '/match-analysis' },
    { title: latestResume.value ? '补充简历中的成果证据' : '上传并解析第一份简历', desc: latestResume.value ? '把项目结果写成可验证的数据和产出' : '支持 PDF 和 Word，解析历史会长期保留', path: '/resume-parser' },
    { title: '进行一次模拟面试', desc: '用真实岗位问题练习表达，结束后查看总评分', path: '/digital-interviewer' }
  ]
})
const progressItems = computed(() => [
  { label: '个人资料完整度', value: Math.round(model.value.profile.completeness || 0), unit: '%', progress: Math.round(model.value.profile.completeness || 0), action: '完善资料', path: '/personal-center', icon: Collection },
  { label: '进行中任务', value: nextActions.value.length, unit: ' 项', progress: Math.min(100, nextActions.value.length * 25), action: '查看任务', path: '/learning-path', icon: Document },
  { label: '简历优化进度', value: Math.min(100, Math.round((model.value.profile.completeness || 0) * .8 + (latestResume.value ? 20 : 0))), unit: '%', progress: Math.min(100, Math.round((model.value.profile.completeness || 0) * .8 + (latestResume.value ? 20 : 0))), action: '去优化', path: '/resume-parser', icon: Aim },
  { label: '面试模拟得分', value: Math.round(latestInterview.value?.final_score || 0), unit: ' 分', progress: Math.round(latestInterview.value?.final_score || 0), action: '去练习', path: '/digital-interviewer', icon: Medal }
])

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
    model.value = snapshot.data
    updatedAt.value = snapshot.updatedAt
    selectedSkill.value = skillItems.value[0]?.name || ''
    if (force) ElMessage.success('个人成长数据已更新')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '个人成长数据加载失败')
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

onMounted(() => refresh(false))
</script>

<style scoped>
.candidate-dashboard { --panel: rgba(3, 28, 36, .30); --edge: rgba(34, 247, 255, .11); --cyan: #22f7ff; --text: #e5ffff; max-width: 1680px; margin: 0 auto; color: var(--text); font-family: "Microsoft YaHei", "Noto Sans SC", sans-serif; }
.cockpit-loading { position: fixed; z-index: 20; top: 18px; right: 20px; border: 1px solid var(--edge); border-radius: 999px; padding: 9px 15px; color: #9fffff; background: rgba(2, 16, 20, .36); box-shadow: 0 0 20px rgba(0, 222, 230, .10); backdrop-filter: blur(22px); font-size: 12px; }
.overview-rail { position: sticky; z-index: 5; top: 8px; display: flex; align-items: center; justify-content: center; gap: 6px; width: max-content; max-width: calc(100vw - 36px); margin: 0 auto 14px; border: 1px solid rgba(34, 247, 255, .10); border-radius: 999px; padding: 5px; background: rgba(3, 22, 28, .28); box-shadow: 0 8px 24px rgba(0, 8, 12, .11); backdrop-filter: blur(30px) saturate(1.18); }
.overview-rail a,.overview-rail button { display: inline-flex; align-items: center; gap: 5px; border: 0; border-radius: 999px; padding: 8px 12px; color: #79b3b8; background: transparent; font: inherit; font-size: 12px; text-decoration: none; cursor: pointer; }.overview-rail a:hover,.overview-rail button:hover { color: #e6ffff; background: rgba(34, 247, 255, .08); }.overview-rail button { color: #4feaff; }.overview-rail button:disabled { cursor: wait; opacity: .6; }
.career-hero { display: grid; grid-template-columns: minmax(250px, .8fr) minmax(480px, 2.15fr) minmax(260px, .84fr); min-height: 555px; overflow: hidden; border: 1px solid rgba(34, 247, 255, .11); border-radius: 20px; background: radial-gradient(circle at 50% 100%, rgba(0, 201, 210, .07), transparent 44%), rgba(2, 15, 19, .28); box-shadow: 0 24px 62px rgba(0, 10, 14, .16), inset 0 1px 0 rgba(141, 255, 255, .04); backdrop-filter: blur(26px) saturate(1.18); }
.hero-card { position: relative; z-index: 2; padding: 30px 24px; background: linear-gradient(160deg, rgba(4, 44, 54, .26), rgba(2, 18, 22, .20)); backdrop-filter: blur(26px) saturate(1.15); }.readiness-card { border-right: 1px solid rgba(34, 247, 255, .07); }.focus-card { border-left: 1px solid rgba(34, 247, 255, .07); }
.section-kicker { display: block; color: #22f7ff; font-size: 10px; font-weight: 900; letter-spacing: .14em; text-transform: uppercase; text-shadow: 0 0 8px rgba(34, 247, 255, .30); }.card-label { margin: 25px 0 8px; color: #739ea3; font-size: 12px; }.hero-card h2 { margin: 0; color: #ecffff; font-size: 21px; letter-spacing: -.04em; }.role-tag { display: inline-block; margin-top: 10px; border-radius: 5px; padding: 5px 8px; color: #7dfaff; background: rgba(34, 247, 255, .07); box-shadow: inset 0 0 0 1px rgba(34, 247, 255, .08); font-size: 11px; }.readiness-label { margin-top: 25px; }
.readiness-score { position: relative; display: grid; place-items: center; width: 138px; height: 138px; margin: 6px 0 2px; }.readiness-score svg { position: absolute; width: 100%; height: 100%; transform: rotate(-90deg); }.readiness-score circle { fill: none; stroke-width: 8; }.score-track { stroke: rgba(0, 142, 156, .24); }.score-progress { stroke: #22f7ff; stroke-linecap: round; stroke-dasharray: 320; transition: stroke-dashoffset 1s ease; filter: drop-shadow(0 0 5px rgba(34, 247, 255, .48)); }.readiness-score strong { color: #e5ffff; font-size: 47px; letter-spacing: -.07em; text-shadow: 0 0 8px rgba(34, 247, 255, .30); }.readiness-score small { margin-left: 2px; color: #9be3e8; font-size: 15px; }.score-verdict { display: grid; gap: 5px; }.score-verdict b { font-size: 17px; }.score-verdict b.success { color: #a5dcc9; text-shadow: 0 0 6px rgba(165, 220, 201, .20); }.score-verdict b.warning { color: #ffc048; }.score-verdict b.danger { color: #ff5d7d; }.score-verdict span { color: #72a0a5; font-size: 11px; }
.skill-summary { display: grid; gap: 8px; margin-top: 22px; }.skill-summary > span { color: #6ea0a5; font-size: 11px; }.skill-summary > div { display: flex; flex-wrap: wrap; gap: 6px; }.skill-summary i { border: 1px solid rgba(34, 247, 255, .22); border-radius: 5px; padding: 4px 7px; color: #8df4f9; background: rgba(0, 120, 133, .14); font-size: 10px; font-style: normal; }.skill-summary i.gap { border-color: rgba(255, 192, 72, .26); color: #ffd888; background: rgba(110, 76, 10, .18); }
.primary-action { display: inline-flex; align-items: center; justify-content: center; gap: 8px; width: 100%; min-height: 44px; margin-top: 22px; border: 1px solid rgba(34, 247, 255, .48); border-radius: 8px; color: #eaffff; background: linear-gradient(90deg, #00c9d2, #22f7ff 52%, #6ffaff); box-shadow: 0 8px 25px rgba(0, 201, 210, .28), 0 0 18px rgba(34, 247, 255, .22); font: inherit; font-size: 13px; font-weight: 800; text-shadow: 0 0 8px rgba(34, 247, 255, .35); cursor: pointer; }.primary-action:hover { filter: brightness(1.12); transform: translateY(-1px); }
.journey-stage { position: relative; display: grid; grid-template-rows: auto 1fr auto; min-width: 0; overflow: hidden; background: linear-gradient(180deg, rgba(2, 22, 28, .52), rgba(0, 12, 16, .14)); }.journey-copy { position: relative; z-index: 3; padding: 29px 34px 12px; text-align: center; }.journey-copy h1 { max-width: 700px; margin: 10px auto 8px; color: #e5ffff; font-family: "Microsoft YaHei", "Noto Sans SC", sans-serif; font-size: clamp(25px, 2.35vw, 38px); letter-spacing: -.05em; line-height: 1.25; }.journey-copy em { color: #22f7ff; font-style: normal; text-shadow: 0 0 10px rgba(34, 247, 255, .65); }.journey-copy p { margin: 0; color: #86b7bc; font-size: 13px; }.video-shell { position: relative; min-height: 332px; margin: 0 18px; overflow: hidden; border: 1px solid rgba(34, 247, 255, .14); border-radius: 12px; background: radial-gradient(ellipse at 48% 87%, rgba(34, 247, 255, .38), transparent 18%), linear-gradient(145deg, #06323a, #011216 80%); }.video-shell::after { position: absolute; inset: 0; background-image: linear-gradient(rgba(141, 255, 255, .07) 1px, transparent 1px), linear-gradient(90deg, rgba(141, 255, 255, .07) 1px, transparent 1px); background-size: 42px 42px; content: ''; opacity: .35; pointer-events: none; }.career-video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: .78; mix-blend-mode: screen; }.video-shade { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(2, 18, 22, .28), rgba(0, 12, 16, .33) 42%, rgba(0, 12, 16, .75)); }.journey-route { position: absolute; z-index: 1; top: 53%; left: 12%; width: 73%; height: 34%; border-top: 3px solid rgba(141, 255, 255, .84); border-radius: 48%; box-shadow: 0 -1px 11px rgba(34, 247, 255, .78), 0 -11px 40px rgba(34, 247, 255, .22); transform: rotate(-8deg); }.journey-route::after { position: absolute; top: -42px; right: -4%; width: 30%; height: 70px; border-top: 3px solid #ffc048; border-radius: 50%; box-shadow: 0 -1px 8px rgba(255, 192, 72, .8); content: ''; transform: rotate(17deg); }
.route-stop { position: absolute; z-index: 3; display: grid; grid-template-columns: 30px auto; column-gap: 7px; min-width: 135px; border: 1px solid rgba(34, 247, 255, .36); border-radius: 10px; padding: 8px 10px; color: #dfffff; background: rgba(3, 36, 44, .40); box-shadow: 0 0 14px rgba(34, 247, 255, .08); font: inherit; text-align: left; cursor: pointer; backdrop-filter: blur(18px) saturate(1.15); }.route-stop:hover { border-color: #8dffff; transform: translateY(-3px); }.route-stop b { grid-row: span 2; align-self: center; color: #22f7ff; font-size: 19px; text-shadow: 0 0 8px rgba(34, 247, 255, .55); }.route-stop span { font-size: 12px; font-weight: 800; }.route-stop small { margin-top: 3px; color: #7ab2b7; font-size: 10px; }.route-stop--one { bottom: 22px; left: 6%; }.route-stop--two { bottom: 42%; left: 34%; border-color: rgba(145, 210, 190, .34); }.route-stop--two b { color: #9ad8c5; text-shadow: 0 0 8px rgba(154, 216, 197, .26); }.route-stop--three { right: 12%; bottom: 19%; border-color: rgba(186, 142, 255, .48); }.route-stop--three b { color: #c19aff; text-shadow: 0 0 8px rgba(186, 142, 255, .4); }.target-beacon { position: absolute; z-index: 3; top: 20%; right: 7%; display: grid; justify-items: center; text-align: center; }.target-beacon span { display: block; width: 58px; height: 24px; border: 2px solid #22f7ff; border-radius: 50%; box-shadow: 0 0 0 8px rgba(34, 247, 255, .10), 0 0 18px rgba(34, 247, 255, .65); animation: beacon 2.7s ease-in-out infinite; }.target-beacon b { margin-top: 9px; color: #e5ffff; font-size: 13px; }.target-beacon small { margin-top: 2px; color: #79a5ab; font-size: 10px; }@keyframes beacon { 50% { transform: scale(1.19); box-shadow: 0 0 0 15px rgba(34, 247, 255, .03), 0 0 28px rgba(34, 247, 255, .78); } }
.journey-steps { position: relative; z-index: 2; display: grid; grid-template-columns: auto 1fr auto 1fr auto 1fr auto; align-items: center; gap: 7px; padding: 13px 30px 18px; color: #6c9196; font-size: 11px; text-align: center; }.journey-steps span.active { color: #22f7ff; font-weight: 800; text-shadow: 0 0 8px rgba(34, 247, 255, .6); }.journey-steps i { height: 1px; background: linear-gradient(90deg, #22f7ff, rgba(0, 201, 210, .28)); }
.focus-card { display: flex; flex-direction: column; }.focus-card h2 { margin-top: 12px; }.focus-skill { display: flex; align-items: center; gap: 11px; margin-top: 21px; border: 1px solid rgba(34, 247, 255, .13); border-radius: 10px; padding: 13px; background: rgba(4, 54, 63, .22); backdrop-filter: blur(19px) saturate(1.15); }.skill-icon { display: grid; place-items: center; width: 36px; height: 36px; border-radius: 50%; color: #22f7ff; background: rgba(0, 201, 210, .12); font-size: 20px; box-shadow: inset 0 0 12px rgba(34, 247, 255, .10); }.focus-skill b,.focus-skill small { display: block; }.focus-skill b { color: #ecffff; font-size: 14px; }.focus-skill small { margin-top: 5px; color: #76a3a8; font-size: 10px; }.focus-progress { height: 6px; margin: 13px 4px 0; overflow: hidden; border-radius: 6px; background: rgba(0, 142, 156, .14); }.focus-progress span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #00c9d2, #22f7ff); box-shadow: 0 0 9px rgba(34, 247, 255, .38); }.plain-link { display: inline-flex; align-items: center; gap: 4px; margin: 11px 0 16px; border: 0; padding: 0; color: #4feaff; background: transparent; font: inherit; font-size: 11px; font-weight: 700; cursor: pointer; }.recommendation { border-top: 1px solid rgba(34, 247, 255, .08); padding-top: 17px; }.recommendation > span { color: #6c9aa0; font-size: 12px; }.recommendation button { display: grid; grid-template-columns: 28px 1fr 15px; align-items: center; gap: 8px; width: 100%; margin-top: 9px; border: 1px solid rgba(34, 247, 255, .14); border-radius: 9px; padding: 11px; color: #a8f6fb; background: rgba(6, 62, 73, .11); backdrop-filter: blur(18px) saturate(1.12); font: inherit; text-align: left; cursor: pointer; }.recommendation button:hover { border-color: rgba(141, 255, 255, .48); }.recommendation button > .el-icon:first-child { display: grid; place-items: center; width: 28px; height: 28px; border-radius: 6px; color: #22f7ff; background: rgba(0, 201, 210, .14); }.recommendation b,.recommendation small { display: block; }.recommendation b { color: #e4ffff; font-size: 11px; }.recommendation small { margin-top: 4px; color: #759da2; font-size: 10px; line-height: 1.4; }.trend-box { margin-top: auto; border-top: 1px solid rgba(34, 247, 255, .10); padding-top: 17px; }.trend-box > div { display: flex; justify-content: space-between; color: #6c9aa0; font-size: 11px; }.trend-box b { color: #9ad8c5; font-size: 16px; text-shadow: 0 0 8px rgba(154, 216, 197, .20); }.trend-box svg { display: block; width: 100%; height: 52px; margin: 5px 0; overflow: visible; }.trend-box path { fill: none; stroke: #9ad8c5; stroke-width: 2.5; filter: drop-shadow(0 0 3px rgba(154, 216, 197, .32)); }.trend-box small { display: flex; justify-content: space-between; color: #68878c; font-size: 9px; }.trend-box i { display: inline-block; width: 5px; height: 5px; margin: 0 4px; border-radius: 50%; background: #9ad8c5; }
.progress-strip { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 15px; }.progress-card { position: relative; display: grid; grid-template-columns: 42px minmax(0, 1fr) auto; align-items: center; gap: 11px; min-height: 91px; overflow: hidden; border: 1px solid rgba(34, 247, 255, .12); border-radius: 13px; padding: 14px 16px 18px; color: inherit; background: rgba(3, 36, 44, .34); box-shadow: inset 0 1px 0 rgba(141, 255, 255, .025); font: inherit; text-align: left; cursor: pointer; backdrop-filter: blur(24px) saturate(1.15); }.progress-card:hover { border-color: rgba(141, 255, 255, .48); transform: translateY(-2px); }.progress-icon { display: grid; place-items: center; width: 41px; height: 41px; border-radius: 50%; color: #22f7ff; background: radial-gradient(circle, rgba(34, 247, 255, .24), rgba(0, 122, 131, .08)); font-size: 22px; text-shadow: 0 0 8px rgba(34, 247, 255, .44); }.progress-copy b,.progress-copy small { display: block; }.progress-copy b { color: #e5ffff; font-size: 24px; text-shadow: 0 0 6px rgba(34, 247, 255, .20); }.progress-copy small { margin-top: 5px; color: #78a4a9; font-size: 11px; }.progress-card em { display: inline-flex; align-items: center; gap: 3px; color: #4feaff; font-size: 11px; font-style: normal; white-space: nowrap; }.progress-meter { position: absolute; right: 0; bottom: 0; left: 0; height: 3px; background: rgba(0, 142, 156, .10); }.progress-meter span { display: block; height: 100%; background: linear-gradient(90deg, #00c9d2, #22f7ff); box-shadow: 0 0 7px rgba(34, 247, 255, .40); transform-origin: left; animation: progress-in 1s ease-out both; }@keyframes progress-in { from { transform: scaleX(0); } }
.overview-section { display: grid; gap: 14px; margin-top: 15px; }.action-layout { grid-template-columns: minmax(0, 1.35fr) minmax(360px, .9fr); }.evidence-layout { grid-template-columns: minmax(0, 1.15fr) minmax(380px, 1fr); }.overview-panel { border: 1px solid rgba(34, 247, 255, .11); border-radius: 14px; background: linear-gradient(145deg, rgba(4, 46, 54, .36), rgba(2, 20, 24, .38)); box-shadow: inset 0 1px 0 rgba(141, 255, 255, .025); backdrop-filter: blur(26px) saturate(1.15); }.panel-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 15px; border-bottom: 1px solid rgba(34, 247, 255, .07); padding: 21px 22px 16px; }.panel-heading h2 { margin: 5px 0 5px; color: #e5ffff; font-size: 19px; }.panel-heading p { margin: 0; color: #6e979c; font-size: 11px; }.panel-count { border-radius: 999px; padding: 6px 10px; color: #6feaff; background: rgba(0, 201, 210, .10); font-size: 11px; white-space: nowrap; }.action-list { display: grid; gap: 8px; padding: 12px 18px 18px; }.action-list button { display: grid; grid-template-columns: 34px 1fr auto; align-items: center; gap: 12px; border: 1px solid rgba(34, 247, 255, .10); border-radius: 9px; padding: 12px; color: inherit; background: rgba(3, 36, 44, .22); font: inherit; text-align: left; cursor: pointer; backdrop-filter: blur(20px) saturate(1.12); }.action-list button:hover { border-color: rgba(141, 255, 255, .44); background: rgba(6, 66, 77, .32); }.action-list button > b { display: grid; place-items: center; width: 32px; height: 32px; border: 1px solid rgba(34, 247, 255, .20); border-radius: 8px; color: #6feaff; background: rgba(0, 142, 156, .12); font-size: 12px; text-shadow: 0 0 6px rgba(34, 247, 255, .32); }.action-list strong,.action-list small { display: block; }.action-list strong { color: #e5ffff; font-size: 13px; }.action-list small { margin-top: 5px; color: #6f9499; font-size: 11px; }.action-list em { display: inline-flex; align-items: center; gap: 3px; color: #4feaff; font-size: 11px; font-style: normal; }.milestone-list { display: grid; gap: 0; margin: 0; padding: 14px 24px 19px; list-style: none; }.milestone-list li { position: relative; display: grid; grid-template-columns: 16px 1fr; gap: 11px; padding: 8px 0 14px; }.milestone-list li:not(:last-child)::after { position: absolute; top: 25px; bottom: -1px; left: 7px; width: 1px; background: rgba(0, 142, 156, .16); content: ''; }.milestone-list li > span { position: relative; z-index: 1; width: 14px; height: 14px; margin-top: 2px; border: 2px solid #3e8f94; border-radius: 50%; background: #092c33; }.milestone-list li.done > span { border-color: #9ad8c5; background: #9ad8c5; box-shadow: 0 0 6px rgba(154, 216, 197, .26); }.milestone-list b,.milestone-list small { display: block; }.milestone-list b { color: #e5ffff; font-size: 12px; }.milestone-list small { margin-top: 4px; color: #6f9398; font-size: 10px; }
.outline-button { border: 1px solid rgba(34, 247, 255, .24); border-radius: 7px; padding: 7px 11px; color: #6feaff; background: rgba(0, 142, 156, .10); backdrop-filter: blur(10px); font: inherit; font-size: 11px; cursor: pointer; }.outline-button:hover { background: rgba(0, 178, 188, .20); }.profile-summary { display: flex; align-items: center; gap: 14px; padding: 21px 23px; }.profile-summary > div { flex: 1; min-width: 0; }.profile-summary b,.profile-summary small { display: block; }.profile-summary b { color: #ecffff; font-size: 14px; }.profile-summary b em { color: #22f7ff; font-size: 18px; font-style: normal; text-shadow: 0 0 8px rgba(34, 247, 255, .36); }.profile-summary small { margin-top: 6px; color: #6f959a; font-size: 11px; }.evidence-progress { height: 6px; margin-top: 12px; overflow: hidden; border-radius: 999px; background: rgba(0, 142, 156, .14); }.evidence-progress i { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #00c9d2, #22f7ff); box-shadow: 0 0 9px rgba(34, 247, 255, .40); }.resume-evidence { display: grid; grid-template-columns: 36px 1fr auto; align-items: center; gap: 11px; margin: 0 22px 22px; border: 1px solid rgba(34, 247, 255, .13); border-radius: 9px; padding: 12px; background: rgba(3, 30, 37, .30); backdrop-filter: blur(18px) saturate(1.12); }.resume-icon { display: grid; place-items: center; width: 34px; height: 34px; border-radius: 7px; color: #22f7ff; background: rgba(0, 142, 156, .16); font-size: 18px; }.resume-evidence b,.resume-evidence small { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }.resume-evidence b { color: #e5ffff; font-size: 12px; }.resume-evidence small { margin-top: 4px; color: #6f9499; font-size: 10px; }.resume-evidence button { border: 0; padding: 6px 0; color: #4feaff; background: transparent; font: inherit; font-size: 11px; cursor: pointer; }.skill-cloud { display: flex; flex-wrap: wrap; gap: 8px; padding: 20px 22px 13px; }.skill-pill { display: inline-flex; align-items: center; gap: 6px; border: 1px solid rgba(34, 247, 255, .16); border-radius: 999px; padding: 7px 10px; color: #9fdfe5; background: rgba(5, 54, 64, .20); backdrop-filter: blur(14px) saturate(1.10); font: inherit; font-size: 11px; cursor: pointer; }.skill-pill:hover,.skill-pill.active { border-color: rgba(141, 255, 255, .55); color: #e5ffff; }.skill-pill small { color: #22f7ff; font-size: 9px; }.skill-pill.missing { border-color: rgba(255, 192, 72, .24); color: #ffd888; }.skill-pill.missing small { color: #ffc048; }.skill-footnote { display: flex; align-items: center; gap: 7px; margin: 0 22px 20px; color: #6f9499; font-size: 11px; }.skill-footnote .el-icon { color: #22f7ff; text-shadow: 0 0 6px rgba(34, 247, 255, .40); }
@media (max-width: 1250px) { .career-hero { grid-template-columns: minmax(230px, .82fr) minmax(430px, 1.7fr); }.focus-card { grid-column: span 2; display: grid; grid-template-columns: 1fr 1fr; gap: 10px 22px; border-top: 1px solid rgba(34, 247, 255, .14); border-left: 0; }.focus-card .section-kicker,.focus-card h2 { grid-column: span 2; }.focus-card h2 { margin-top: -7px; }.focus-skill,.recommendation,.trend-box { margin-top: 0; }.trend-box { padding-top: 0; border-top: 0; }.focus-card .plain-link { align-self: end; margin: 0; }.focus-card .recommendation { border-top: 0; padding-top: 0; }.action-layout,.evidence-layout { grid-template-columns: 1fr; } }
@media (max-width: 840px) { .overview-rail { justify-content: flex-start; overflow: auto; }.overview-rail a { white-space: nowrap; }.career-hero { grid-template-columns: 1fr; }.readiness-card,.focus-card { border: 0; border-bottom: 1px solid rgba(34, 247, 255, .14); }.journey-stage { min-height: 520px; order: -1; }.focus-card { grid-column: auto; display: block; }.focus-card h2 { margin-top: 12px; }.focus-card .plain-link { margin: 11px 0 16px; }.focus-card .recommendation,.trend-box { border-top: 1px solid rgba(34, 247, 255, .14); padding-top: 17px; }.progress-strip { grid-template-columns: 1fr 1fr; }.route-stop--three { right: 6%; }.target-beacon { right: 6%; }.journey-copy { padding-right: 20px; padding-left: 20px; }.video-shell { min-height: 290px; }.journey-steps { padding-right: 18px; padding-left: 18px; } }
@media (max-width: 520px) { .candidate-dashboard { margin: 0 -2px; }.overview-rail { justify-content: flex-start; width: 100%; border-radius: 11px; }.overview-rail a { display: none; }.overview-rail a:first-child,.overview-rail a:nth-child(3) { display: inline-flex; }.overview-rail button { margin-left: auto; }.hero-card { padding: 22px 18px; }.journey-copy h1 { font-size: 25px; }.journey-copy p { font-size: 11px; line-height: 1.6; }.video-shell { min-height: 295px; margin: 0 10px; }.route-stop { min-width: 0; padding: 6px 8px; }.route-stop b { font-size: 14px; }.route-stop span { font-size: 10px; }.route-stop small { display: none; }.route-stop--one { bottom: 18px; left: 4%; }.route-stop--two { bottom: 47%; left: 30%; }.route-stop--three { right: 3%; bottom: 25%; }.target-beacon { top: 14%; }.target-beacon b { max-width: 86px; font-size: 10px; }.journey-steps { gap: 4px; padding-bottom: 14px; font-size: 9px; }.progress-strip { grid-template-columns: 1fr; }.progress-card { min-height: 75px; }.panel-heading { padding: 18px 16px 14px; }.action-list { padding: 10px 12px 14px; }.action-list button { grid-template-columns: 30px 1fr; }.action-list em { display: none; }.profile-summary { padding: 17px; }.resume-evidence { grid-template-columns: 34px 1fr; margin: 0 16px 16px; }.resume-evidence button { grid-column: 2; justify-self: start; }.skill-cloud { padding: 16px 17px 10px; }.skill-footnote { margin: 0 17px 17px; } }
.journey-stage { display: block; height: 100%; min-height: 0; background: #021a20; }
.journey-stage .video-shell { height: 100%; min-height: 100%; margin: 0; border: 0; border-radius: 0; background: #021a20; }
.journey-stage .video-shell::after { display: none; }
.journey-stage .career-video { opacity: 1; mix-blend-mode: normal; }
.video-fallback { position: absolute; inset: 0; display: grid; place-items: center; color: #8fe5ea; background: radial-gradient(circle at 50% 50%, #0a5a64, #021a20 72%); font-size: 13px; }
@media (max-width: 840px) { .journey-stage { min-height: 360px; }.journey-stage .video-shell { min-height: 100%; } }
@media (max-width: 520px) { .journey-stage { min-height: 290px; }.journey-stage .video-shell { min-height: 100%; margin: 0; } }
/* ===== 底部数据状态栏：更新操作集中在页面最下方，顶部导航只负责区块跳转 ===== */
.overview-footer { display: flex; align-items: center; justify-content: space-between; gap: 14px; margin-top: 18px; border: 1px solid rgba(34,247,255,.12); border-radius: 10px; padding: 13px 18px; background: rgba(3,28,36,.42); backdrop-filter: blur(22px) saturate(1.15); }
.overview-footer__status { display: flex; align-items: center; gap: 10px; color: #77a0a5; font-size: 12px; }
.overview-footer__status .status-dot { width: 7px; height: 7px; border-radius: 50%; background: #9ad8c5; box-shadow: 0 0 6px rgba(154,216,197,.38); }
.overview-footer__status .status-dot.busy { background: #ffc048; box-shadow: 0 0 7px rgba(255,192,72,.52); animation: footer-busy 1s ease-in-out infinite; }
@keyframes footer-busy { 50% { opacity: .35; } }
.footer-divider { width: 1px; height: 12px; background: rgba(78,148,153,.20); }
.overview-footer button { display: inline-flex; align-items: center; gap: 6px; border: 1px solid rgba(34,247,255,.34); border-radius: 8px; padding: 9px 14px; color: #eaffff; background: linear-gradient(90deg, rgba(0,201,210,.16), rgba(34,247,255,.22)); box-shadow: 0 0 14px rgba(34,247,255,.11), inset 0 1px 0 rgba(141,255,255,.14); backdrop-filter: blur(14px); font: inherit; font-size: 12px; font-weight: 700; cursor: pointer; }
.overview-footer button:hover { filter: brightness(1.15); transform: translateY(-1px); }
.overview-footer button:disabled { cursor: wait; opacity: .7; }
.overview-footer .fa-spin { color: #4feaff; }
@media (max-width: 620px) { .overview-footer { flex-direction: column; align-items: flex-start; } .overview-footer button { align-self: stretch; justify-content: center; } }
</style>
