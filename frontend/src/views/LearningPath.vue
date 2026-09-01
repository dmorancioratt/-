<template>
  <div class="page learning-page">
    <PageHeader title="学习路径" desc="按顺序完成，不必同时开始">
      <div class="toolbar">
        <el-button @click="router.push('/match-analysis')">返回匹配分析</el-button>
        <el-button type="primary" :loading="loading" @click="regenerate">{{ path.length ? '重新生成路径' : '生成路径' }}</el-button>
      </div>
    </PageHeader>

    <section class="learning-overview">
      <div class="goal-copy">
        <span>目标岗位</span>
        <h2>{{ report?.target_job || '尚未选择目标岗位' }}</h2>
        <p>{{ heroSummary }}</p>
      </div>
      <div class="match-number">
        <strong>{{ scoreDisplay }}</strong>
        <span>{{ scoreLabel }}</span>
      </div>
      <div class="priority-copy">
        <span>先解决</span>
        <b>{{ missingSkills[0] || '暂无待补能力' }}</b>
        <small v-if="missingSkills.length > 1">随后：{{ missingSkills.slice(1, 3).join('、') }}</small>
      </div>
    </section>

    <section class="learning-workspace">
      <aside class="weekly-panel">
        <div class="workspace-heading">
          <span>本周</span>
          <h3>只做这三件事</h3>
        </div>
        <ol class="weekly-list">
          <li v-for="(item, index) in weeklyTodos.slice(0, 3)" :key="item">
            <i>{{ index + 1 }}</i>
            <span>{{ item }}</span>
          </li>
        </ol>
        <div class="certificate-note">
          <span>建议证书</span>
          <p>{{ recommendedCertificates.length ? recommendedCertificates.slice(0, 2).map((item) => item.name).join('、') : '当前岗位没有明确证书要求' }}</p>
        </div>
      </aside>

      <div class="route-panel">
        <div class="route-heading">
          <div>
            <span>成长路线</span>
            <h3>{{ path.length }} 个阶段，逐项完成</h3>
          </div>
          <small>点击阶段查看具体任务</small>
        </div>

        <ol v-if="path.length" class="route-list">
          <li v-for="(item, index) in path" :key="`${item.stage}-${index}`" :class="{ active: activeStage === index }">
            <button type="button" class="route-row" @click="activeStage = index">
              <i>{{ String(index + 1).padStart(2, '0') }}</i>
              <span><b>{{ item.stage }}</b><small>{{ item.duration }}</small></span>
              <em aria-hidden="true">{{ activeStage === index ? '−' : '+' }}</em>
            </button>
            <div v-if="activeStage === index" class="route-detail">
              <p>{{ stageContent(item, index) }}</p>
              <dl>
                <div><dt>完成产出</dt><dd>{{ item.project }}</dd></div>
                <div><dt>开始前</dt><dd>{{ item.prerequisites?.length ? item.prerequisites.join('、') : '无需额外准备' }}</dd></div>
              </dl>
            </div>
          </li>
        </ol>
        <div v-else class="route-empty">完成一次岗位匹配后，这里会生成对应的成长路线。</div>
      </div>
    </section>

    <footer class="learning-footer">
      <small>路径保留最近一次结果，只有点击“重新生成路径”才会更新。</small>
      <div>
        <el-button @click="router.push('/resume-parser')">更新简历</el-button>
        <el-button type="primary" @click="router.push('/digital-interviewer')">练习表达</el-button>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'
import { loadPageState, savePageState } from '@/utils/pageState'

const router = useRouter()
const route = useRoute()
const path = ref<any[]>([])
const aiAnalysis = ref<any>()
const report = ref<any>()
const loading = ref(false)
const activeStage = ref(0)

const missingSkills = computed<string[]>(() => report.value?.missing_skills || [])
const recommendedCertificates = computed<any[]>(() => report.value?.job_profile?.recommended_certificates || [])
const scoreDisplay = computed(() => report.value ? `${report.value.total_score ?? 0}%` : '--')
const scoreLabel = computed(() => {
  if (!report.value) return '等待匹配'
  const score = Number(report.value?.total_score || 0)
  if (score >= 85) return '高度匹配'
  if (score >= 70) return '建议复核'
  if (score >= 55) return '可培养'
  return '需系统补强'
})
const heroSummary = computed(() => report.value
  ? (missingSkills.value.length ? `本次岗位匹配报告识别出 ${missingSkills.value.length} 项待补能力。` : '本次岗位匹配报告未识别出必备技能缺口。')
  : '请先完成一次岗位匹配，系统将根据已保存的报告生成学习路径。')
const weeklyTodos = computed(() => path.value.slice(0, 3).map((item) => item.project || item.content).filter(Boolean))

type LearningPathState = {
  path: any[]
  aiAnalysis?: any
  report?: any
}

async function load(force = false) {
  loading.value = true
  try {
    let reportId = Number(route.query.reportId || 0)
    if (!reportId) {
      const history = await api.matchAnalysisHistory()
      reportId = Number(history?.[0]?.report_id || 0)
    }
    if (!reportId) {
      report.value = undefined
      path.value = []
      ElMessage.warning('请先完成一次匹配分析，再生成对应的学习路径')
      return
    }
    const pageKey = `learning-path:${reportId}`
    const pageCache = loadPageState<LearningPathState>(pageKey)
    if (!force && pageCache?.path?.length) {
      report.value = pageCache.report || await api.matchAnalysisDetail(reportId)
      path.value = pageCache.path
      aiAnalysis.value = pageCache.aiAnalysis
      return
    }
    report.value = await api.matchAnalysisDetail(reportId)
    const response = await api.learningPath(reportId)
    const rows = Array.isArray(response) ? response : response.items
    path.value = enrichPath(rows || [])
    activeStage.value = 0
    aiAnalysis.value = Array.isArray(response) ? undefined : response.ai_analysis
    savePageState<LearningPathState>(pageKey, {
      path: path.value,
      aiAnalysis: aiAnalysis.value,
      report: report.value
    })
    if (force) ElMessage.success('学习路径已重新生成')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '学习路径生成失败')
  } finally {
    loading.value = false
  }
}

function regenerate() {
  return load(true)
}

function stageContent(item: any, index: number) {
  const skill = missingSkills.value[index]
  const content = String(item?.content || '')
  const duplicatePrefix = skill ? `${skill}：${skill}：` : ''
  return duplicatePrefix && content.startsWith(duplicatePrefix)
    ? content.slice(skill.length + 1)
    : content
}

function enrichPath(rows: any[]) {
  if (!missingSkills.value.length) return rows
  return rows.map((item, index) => {
    const skill = missingSkills.value[index]
    const content = String(item.content || '')
    return {
      ...item,
      content: skill && !content.startsWith(`${skill}：`) ? `${skill}：${content}` : content
    }
  })
}

onMounted(() => load(false))

watch(() => route.query.reportId, (next, previous) => {
  if (next !== previous) load(false)
})
</script>

<style scoped>
.learning-page {
  --panel: rgba(3, 28, 36, .30);
  --edge: rgba(34, 247, 255, .11);
  --cyan: #22f7ff;
  --teal: #00c9d2;
  --amber: #ffb65c;
  display: grid;
  gap: 16px;
  color: #e7f1f4;
}

.panel {
  border: 1px solid var(--edge);
  border-radius: 20px;
  background: linear-gradient(145deg, rgba(4, 46, 54, .28), rgba(2, 20, 24, .32));
  backdrop-filter: blur(26px) saturate(1.18);
  box-shadow: 0 8px 28px rgba(0, 14, 18, 0.10);
}

/* ===== Overview / Hero ===== */
.learning-overview {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 190px minmax(230px, .55fr);
  min-height: 158px;
  overflow: hidden;
  border: 1px solid var(--edge);
  border-radius: 20px;
  background: linear-gradient(145deg, rgba(4, 46, 54, .28), rgba(2, 20, 24, .32));
  backdrop-filter: blur(26px) saturate(1.18);
  box-shadow: 0 8px 28px rgba(0, 14, 18, 0.10);
}

.goal-copy,
.match-number,
.priority-copy {
  display: flex;
  justify-content: center;
  flex-direction: column;
  padding: 24px 28px;
}

.match-number {
  align-items: center;
  border-right: 1px solid rgba(34, 247, 255, .10);
  border-left: 1px solid rgba(34, 247, 255, .10);
  text-align: center;
}

.goal-copy > span,
.priority-copy > span,
.workspace-heading > span,
.route-heading span,
.certificate-note > span {
  color: var(--teal);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.10em;
}

.goal-copy h2 {
  margin: 7px 0 8px;
  color: #f0f7f8;
  font-size: 27px;
  letter-spacing: 0;
  font-weight: 700;
}

.goal-copy p {
  max-width: 650px;
  margin: 0;
  color: #8aaeb3;
  font-size: 13px;
  line-height: 1.65;
}

.match-number strong {
  color: var(--cyan);
  font-size: 42px;
  line-height: 1;
  font-weight: 900;
  text-shadow: 0 0 10px rgba(34, 247, 255, .24);
}

.match-number span {
  margin-top: 10px;
  color: #8aaeb3;
  font-size: 12px;
}

.priority-copy b {
  margin-top: 7px;
  color: #f0f6f7;
  font-size: 20px;
  font-weight: 700;
}

.priority-copy small {
  margin-top: 9px;
  color: #849aa5;
  font-size: 11px;
  line-height: 1.5;
}

/* ===== Workspace ===== */
.learning-workspace {
  display: grid;
  grid-template-columns: 330px minmax(0, 1fr);
  overflow: hidden;
  border: 1px solid var(--edge);
  border-radius: 20px;
  background: linear-gradient(145deg, rgba(4, 46, 54, .28), rgba(2, 20, 24, .32));
  backdrop-filter: blur(26px) saturate(1.18);
  box-shadow: 0 8px 28px rgba(0, 14, 18, 0.10);
}

.weekly-panel {
  padding: 26px;
  border-right: 1px solid rgba(34, 247, 255, .10);
  background: linear-gradient(145deg, rgba(4, 46, 54, .18), rgba(2, 20, 24, .22));
}

.workspace-heading h3,
.route-heading h3 {
  margin: 5px 0 0;
  color: #edf5f7;
  font-size: 18px;
  letter-spacing: 0;
  font-weight: 700;
}

.weekly-list {
  display: grid;
  gap: 0;
  margin: 24px 0 0;
  padding: 0;
  list-style: none;
}

.weekly-list li {
  display: grid;
  grid-template-columns: 24px minmax(0, 1fr);
  gap: 11px;
  padding: 15px 0;
  border-top: 1px solid rgba(34, 247, 255, .08);
}

.weekly-list i {
  display: grid;
  place-items: center;
  width: 23px;
  height: 23px;
  border: 1px solid rgba(34, 247, 255, .30);
  border-radius: 50%;
  color: var(--cyan);
  font-size: 10px;
  font-style: normal;
  font-weight: 700;
  box-shadow: 0 0 8px rgba(34, 247, 255, .12);
}

.weekly-list span {
  color: #cbdbe0;
  font-size: 13px;
  line-height: 1.6;
}

.certificate-note {
  margin-top: 20px;
  border-left: 2px solid var(--amber);
  padding-left: 11px;
}

.certificate-note > span { color: var(--amber); }

.certificate-note p {
  margin: 5px 0 0;
  color: #a9b9bf;
  font-size: 12px;
  line-height: 1.55;
}

.route-panel { min-width: 0; padding: 26px 28px; }
.route-heading {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 16px;
}
.route-heading small { color: #718a96; font-size: 11px; }

.route-list {
  margin: 0;
  padding: 0;
  border-bottom: 1px solid rgba(34, 247, 255, .08);
  list-style: none;
}

.route-list > li {
  border-top: 1px solid rgba(34, 247, 255, .08);
  transition: background 150ms ease;
}

.route-list > li.active { background: linear-gradient(90deg, rgba(4, 62, 74, .22), rgba(2, 20, 24, .16)); }

.route-row {
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr) 24px;
  align-items: center;
  gap: 13px;
  width: 100%;
  min-height: 64px;
  border: 0;
  padding: 0 14px;
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
  border-radius: 12px;
  transition: background 180ms ease;
}

.route-row:hover { background: rgba(34, 247, 255, .04); }

.route-row:focus-visible {
  outline: 2px solid rgba(34, 247, 255, .42);
  outline-offset: -2px;
}

.route-row > i {
  color: var(--cyan);
  font-size: 11px;
  font-style: normal;
  font-weight: 700;
}

.route-row > span {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  min-width: 0;
}

.route-row b { color: #dce9ed; font-size: 14px; font-weight: 700; }
.route-row small { color: #8298a3; font-size: 11px; }
.route-row em { color: var(--teal); font-size: 14px; font-style: normal; text-align: center; font-weight: 700; }

.route-detail {
  padding: 2px 52px 22px 65px;
}

.route-detail > p {
  margin: 0 0 15px;
  color: #9eb2bb;
  font-size: 13px;
  line-height: 1.7;
}

.route-detail dl {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(170px, .5fr);
  gap: 18px;
  margin: 0;
}

.route-detail dl > div {
  border-left: 2px solid rgba(34, 247, 255, .34);
  padding-left: 11px;
}

.route-detail dt { color: var(--teal); font-size: 10px; font-weight: 700; letter-spacing: 0.08em; }
.route-detail dd { margin: 5px 0 0; color: #c6d5da; font-size: 12px; line-height: 1.55; }
.route-empty { padding: 60px 20px; color: #7f97a2; text-align: center; }

/* ===== Footer ===== */
.learning-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  min-height: 58px;
  border-top: 1px solid rgba(34, 247, 255, .10);
  padding: 8px 2px 0;
}

.learning-footer > small { color: #718894; font-size: 11px; }
.learning-footer > div { display: flex; gap: 8px; }

@media (max-width: 980px) {
  .learning-overview { grid-template-columns: 1fr 150px; }
  .priority-copy { grid-column: 1 / -1; border-top: 1px solid rgba(34, 247, 255, .10); }
  .learning-workspace { grid-template-columns: 1fr; }
  .weekly-panel { border-right: 0; border-bottom: 1px solid rgba(34, 247, 255, .10); }
}

@media (max-width: 640px) {
  .learning-overview { grid-template-columns: 1fr; }
  .match-number { align-items: flex-start; border: 0; border-top: 1px solid rgba(34, 247, 255, .10); text-align: left; }
  .goal-copy, .match-number, .priority-copy, .weekly-panel, .route-panel { padding: 20px 17px; }
  .route-heading, .learning-footer { align-items: flex-start; flex-direction: column; }
  .route-row > span { align-items: flex-start; flex-direction: column; gap: 3px; }
  .route-detail { padding: 0 17px 20px 52px; }
  .route-detail dl { grid-template-columns: 1fr; }
}
</style>
