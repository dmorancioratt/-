<template>
  <div class="page emerging-jobs-page">
    <PageHeader title="新岗位发现" desc="基于技能增长、多源一致性、技能组合新颖度、标题稳定性和场景扩散度计算新岗位指数">
      <div class="toolbar">
        <el-tag v-if="lastUpdated" effect="plain">上次更新 {{ formatTime(lastUpdated) }}</el-tag>
        <el-button :icon="Connection" :loading="validating" @click="runCrossValidation">交叉验证</el-button>
        <el-button type="primary" :loading="loading" @click="generate(true)">
          {{ rows.length ? '更新分析' : '生成分析' }}
        </el-button>
      </div>
    </PageHeader>
    <section v-if="validationReport?.generated_at" class="validation-strip" aria-label="数据源交叉验证结果">
      <div><span>抄袭识别召回率</span><strong>{{ formatPercent(validationReport.summary?.plagiarism_recall) }}</strong><small>扰动基准 {{ validationReport.summary?.recall_sample_size || 0 }} 条</small></div>
      <div><span>近似抄袭 JD</span><strong>{{ validationReport.summary?.plagiarism_count || 0 }}</strong><small>跨源与同源近似文本</small></div>
      <div><span>过滤噪声 JD</span><strong>{{ validationReport.summary?.noise_count || 0 }}</strong><small>共核验 {{ validationReport.summary?.jd_count || 0 }} 条</small></div>
      <div><span>时间衰减半衰期</span><strong>{{ validationReport.algorithm?.time_decay_half_life_days || '—' }}</strong><small>天 · 指数衰减</small></div>
      <p>评分模型：来源可追溯性 27% · 有效率 25% · 独创率 20% · 时效性 18% · 数据覆盖 10%</p>
    </section>
    <div class="dashboard-grid">
      <!-- ===== 左栏：数据源列表 ===== -->
      <div class="col col-left">
        <div class="col-header">
          <span class="col-title">数据源列表</span>
          <el-tag size="small" round>{{ sources.length }} 个来源</el-tag>
        </div>
        <div class="source-tree-wrapper">
          <el-input
            v-model="sourceFilter"
            placeholder="搜索数据源..."
            size="small"
            clearable
            class="source-search"
          />
          <el-tree
            ref="sourceTreeRef"
            :data="sourceTree"
            :props="{ children: 'children', label: 'label' }"
            :filter-node-method="filterSourceNode"
            node-key="id"
            default-expand-all
            :expand-on-click-node="true"
          >
            <template #default="{ data }">
              <div v-if="data.isSource" class="source-tree-item">
                <div class="source-top">
                  <span class="source-name">{{ data.name }}</span>
                  <el-tag :type="trustTagType(data.trustScore)" size="small" effect="dark">
                    {{ data.trustScore != null ? `${Math.round(data.trustScore)} 分` : '待验证' }}
                  </el-tag>
                </div>
                <div class="source-meta">
                  <span class="source-updated">{{ data.updated }}</span>
                </div>
                <div class="source-bottom">
                  <span class="source-count">权重 {{ formatPercent(data.weight) }}</span>
                  <span>噪声 {{ formatPercent(data.noiseRate) }}</span>
                  <span>时效 {{ formatPercent(data.timeDecayWeight) }}</span>
                </div>
              </div>
              <span v-else class="source-group-label">{{ data.label }}</span>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- ===== 中栏：多源交叉验证及融合结果 ===== -->
      <div class="col col-mid">
        <div class="col-header">
          <span class="col-title">多源交叉验证及融合结果</span>
          <el-tag size="small" round type="info">{{ rows.length }} 个候选</el-tag>
        </div>
        <div class="job-cards">
          <div
            v-for="job in rows"
            :key="job.job_name"
            class="job-card"
            :class="{ active: current === job }"
            @click="selectCurrent(job)"
          >
            <div class="job-card-header">
              <span class="job-name">{{ job.job_name }}</span>
              <span class="job-index" :style="{ color: indexColor(job.emerging_index) }">
                {{ Math.round(job.emerging_index * 100) }}%
              </span>
            </div>
            <!-- 5维小柱状图 -->
            <div class="dim-bars">
              <div v-for="(val, key) in job.dimensions" :key="key" class="dim-bar-row">
                <span class="dim-label">{{ dimLabels[key] || key }}</span>
                <div class="dim-track">
                  <div class="dim-fill" :style="{ width: (val * 100) + '%', background: indexColor(val) }" />
                </div>
              </div>
            </div>
            <!-- 多源覆盖指示 -->
            <div class="source-dots">
              <span class="dots-label">多源覆盖：</span>
              <span
                v-for="s in sources"
                :key="s.id"
                class="source-dot"
                :class="{ covered: job.source_coverage?.includes(s.id) }"
                :title="getSourceLabel(s.id)"
              />
              <span class="coverage-text">{{ job.source_coverage?.length || 0 }}/{{ sources.length }}</span>
            </div>
            <div class="job-card-footer">
              <el-tag v-if="job.review_status === 'approved'" type="success" size="small" effect="plain">已通过</el-tag>
              <el-tag v-else type="warning" size="small" effect="plain">待审核</el-tag>
              <span class="job-skills">{{ job.related_skills.slice(0, 3).join(' · ') }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== 右栏：详细信息 ===== -->
      <div class="col col-right">
        <div class="col-header">
          <span class="col-title">详细信息</span>
        </div>
        <el-empty v-if="!current" description="选择左侧候选岗位查看详情" />
        <div v-else class="detail-panel">
          <div class="detail-hero">
            <h3 class="detail-name">{{ current.job_name }}</h3>
            <div class="detail-index-row">
              <span class="detail-index-label">新岗位指数</span>
              <span class="detail-index-val" :style="{ color: indexColor(current.emerging_index) }">
                {{ Math.round(current.emerging_index * 100) }}%
              </span>
            </div>
          </div>
          <p class="detail-def">{{ current.definition }}</p>

          <div class="detail-section">
            <h4>核心职责</h4>
            <ul><li v-for="item in current.responsibilities" :key="item">{{ item }}</li></ul>
          </div>

          <div class="detail-section">
            <h4>必备技能</h4>
            <div class="tag-row"><el-tag v-for="item in current.required_skills" :key="item" size="small">{{ item }}</el-tag></div>
          </div>

          <div class="detail-section">
            <h4>应用场景</h4>
            <div class="tag-row"><el-tag v-for="item in current.scenarios" :key="item" type="info" size="small">{{ item }}</el-tag></div>
          </div>

          <div class="detail-section">
            <h4>建议证书</h4>
            <div class="tag-row">
              <el-tag v-for="item in current.requirements?.recommended_certificates || []" :key="item.id" type="warning" size="small" effect="light">{{ item.name }}</el-tag>
              <span v-if="!current.requirements?.recommended_certificates?.length" class="text-muted">暂无明确证书建议</span>
            </div>
          </div>

          <div class="detail-section">
            <h4>证据来源</h4>
            <div class="evidence-list">
              <div v-for="item in current.evidence" :key="item.quote" class="evidence-item">
                <div class="evidence-quote">"{{ item.quote }}"</div>
                <div class="evidence-source">— {{ item.source }}</div>
              </div>
            </div>
          </div>

          <div class="detail-actions">
            <el-button :disabled="!current.job_id" @click="openGraph" size="small">能力图谱</el-button>
            <el-button type="primary" :disabled="!current.job_id" @click="startMatch" size="small">匹配分析</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 底部：数据源动态轮播 ===== -->
    <div class="source-ticker">
      <div class="ticker-label">数据源状态</div>
      <div class="ticker-track">
        <div class="ticker-inner">
          <div
            v-for="(src, i) in [...sources, ...sources]"
            :key="`ticker-${src.id}-${i}`"
            class="ticker-item"
          >
            <span class="ticker-dot" :class="{ active: src.status === 'active' }" />
            <span class="ticker-name">{{ src.name }}</span>
            <span class="ticker-divider">|</span>
            <span class="ticker-meta">{{ src.type }}</span>
            <span class="ticker-count">覆盖 {{ src.jobCount }} 岗位</span>
            <span class="ticker-time">{{ src.updated }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Connection } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'
import { loadPageState, savePageState } from '@/utils/pageState'

type EmergingJobsState = {
  rows: any[]
  currentJobName?: string
  lastUpdated?: string
}


// ===== 默认排序：新兴岗位（大模型/智能体等）置顶，传统岗位（Java/前端等）后置 =====
const EMERGING_KEYWORDS = [
  '大模型', '大语言模型', 'LLM', '智能体', 'Agent', 'AIGC', '提示工程', 'Prompt',
  '多模态', '具身智能', '数字孪生', '人工智能', '机器学习', '深度学习', '数据科学',
  '算法', '机器人', '自动驾驶', '云计算', '大数据', 'AI ',
]
const TRADITIONAL_KEYWORDS = [
  'Java', '前端', 'Web', '后端', 'PHP', '.NET', '测试', '运维', '网络工程',
  '数据库', '行政', '会计', '财务', '销售', '人事', '文员', '客服', '运营专员',
]

function jobTier(job: any): number {
  const name = String(job?.job_name || '')
  if (EMERGING_KEYWORDS.some((k) => name.includes(k))) return 0
  if (TRADITIONAL_KEYWORDS.some((k) => name.includes(k))) return 2
  return 1
}

// 层级优先（新兴 > 其他 > 传统）；同层级按新兴指数降序，再按名称排序，保证结果稳定
function sortJobsByDefault(list: any[]): any[] {
  return [...list].sort((a, b) => {
    const tierDiff = jobTier(a) - jobTier(b)
    if (tierDiff !== 0) return tierDiff
    const idxDiff = (Number(b?.emerging_index) || 0) - (Number(a?.emerging_index) || 0)
    if (idxDiff !== 0) return idxDiff
    return String(a?.job_name || '').localeCompare(String(b?.job_name || ''))
  })
}

const rows = ref<any[]>([])
const router = useRouter()
const current = ref<any>()
const loading = ref(false)
const validating = ref(false)
const lastUpdated = ref<string>()
const validationReport = ref<any>()
const sources = ref<any[]>([])
const sourceFilter = ref('')
const sourceTreeRef = ref<any>()

const sourceTree = computed(() => {
  const groups: Record<string, any[]> = {}
  sources.value.forEach((src) => {
    if (!groups[src.type]) groups[src.type] = []
    groups[src.type].push({
      id: src.id,
      label: src.name,
      isSource: true,
      ...src,
    })
  })
  return Object.entries(groups).map(([type, children]) => ({
    id: `group-${type}`,
    label: type,
    children,
  }))
})

function filterSourceNode(value: string, data: any) {
  if (!value) return true
  return data.label?.includes(value)
}

watch(sourceFilter, (val) => {
  sourceTreeRef.value?.filter(val)
})

const dimLabels: Record<string, string> = {
  skill_growth: '技能增长率',
  source_consistency: '多源一致性',
  combo_novelty: '组合新颖度',
  title_stability: '标题稳定性',
  scenario_diffusion: '场景扩散度',
}

function getSourceLabel(id: string) {
  return sources.value.find((s) => s.id === id)?.name || id
}

function applyMarketSources(snapshot: any) {
  const sourceRows = Array.isArray(snapshot?.sources) ? snapshot.sources : []
  sources.value = sourceRows.map((source: any) => {
    const id = String(source.source_key || source.id || '')
    const updatedAt = source.last_synced_at || source.published_at || source.uploaded_at
    const validation = source.metadata?.source_validation || {}
    return {
      id,
      name: source.source_name || source.publisher || id,
      type: source.data_type || source.domain || '数据源',
      status: source.status === 'archived' ? 'pending' : 'active',
      updated: updatedAt ? formatTime(updatedAt) : '—',
      jobCount: rows.value.filter((job) => job.source_key === id || job.source_coverage?.includes(id)).length,
      trustScore: validation.trust_score,
      weight: validation.weight,
      noiseRate: validation.noise_rate,
      plagiarismRate: validation.plagiarism_rate,
      timeDecayWeight: validation.time_decay_weight,
    }
  })
}

function applyValidation(report: any) {
  validationReport.value = report
  const byKey = new Map<string, any>((report?.sources || []).map((source: any) => [String(source.source_key || source.id), source]))
  const merged = sources.value.map((source) => {
    const validation: any = byKey.get(String(source.id))
    byKey.delete(String(source.id))
    return validation ? {
      ...source,
      trustScore: validation.trust_score,
      weight: validation.weight,
      noiseRate: validation.noise_rate,
      plagiarismRate: validation.plagiarism_rate,
      timeDecayWeight: validation.time_decay_weight,
    } : source
  })
  for (const [id, validation] of byKey) {
    merged.push({
      id,
      name: validation.source_name || id,
      type: '招聘 JD 数据源',
      status: 'active',
      updated: validation.validated_at ? formatTime(validation.validated_at) : '—',
      jobCount: validation.valid_jd_count || 0,
      trustScore: validation.trust_score,
      weight: validation.weight,
      noiseRate: validation.noise_rate,
      plagiarismRate: validation.plagiarism_rate,
      timeDecayWeight: validation.time_decay_weight,
    })
  }
  sources.value = merged
}

function formatPercent(value: unknown) {
  const number = Number(value)
  return Number.isFinite(number) ? `${(number * 100).toFixed(1)}%` : '—'
}

function trustTagType(score: unknown) {
  const value = Number(score)
  if (!Number.isFinite(value)) return 'info'
  if (value >= 80) return 'success'
  if (value >= 60) return 'warning'
  return 'danger'
}

async function loadValidation() {
  try {
    applyValidation(await api.sourceValidation())
  } catch {
    validationReport.value = undefined
  }
}

async function loadSourceContext() {
  try {
    applyMarketSources(await api.marketSnapshot())
  } catch {
    sources.value = []
  }
  await loadValidation()
}

async function runCrossValidation() {
  validating.value = true
  try {
    applyValidation(await api.runSourceValidation())
    ElMessage.success('数据源交叉验证完成')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '数据源交叉验证失败')
  } finally {
    validating.value = false
  }
}

function indexColor(val: number) {
  if (val >= 0.85) return '#60a5fa'
  if (val >= 0.75) return '#38bdf8'
  return '#7dd3fc'
}

function persistState() {
  savePageState<EmergingJobsState>('emerging-jobs', {
    rows: rows.value,
    currentJobName: current.value?.job_name,
    lastUpdated: lastUpdated.value
  })
}

function selectCurrent(row?: any) {
  current.value = row
  persistState()
}

function openGraph() {
  if (current.value?.job_id) router.push({ path: '/skill-graph', query: { jobId: String(current.value.job_id) } })
}

function startMatch() {
  if (current.value?.job_id) router.push({ path: '/match-analysis', query: { jobId: String(current.value.job_id) } })
}

async function generate(notify = false) {
  loading.value = true
  await loadSourceContext()
  try {
    rows.value = sortJobsByDefault(await api.emergingJobs())
    current.value = rows.value[0]
    lastUpdated.value = new Date().toISOString()
    persistState()
    if (notify) ElMessage.success('新岗位分析已更新')
  } catch (error: any) {
    rows.value = []
    current.value = undefined
    ElMessage.error(error?.response?.data?.detail || '新岗位分析生成失败')
  } finally {
    loading.value = false
  }
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
  }).format(new Date(value))
}

onMounted(async () => {
  const cached = loadPageState<EmergingJobsState>('emerging-jobs')
  const cacheMatchesCatalog = cached?.rows?.length && cached.rows.every((item) => item.job_id && item.requirements && item.authority)
  if (cacheMatchesCatalog) {
    rows.value = sortJobsByDefault(cached.rows)
    lastUpdated.value = cached.lastUpdated
    current.value = rows.value.find((item) => item.job_name === cached.currentJobName) || rows.value[0]
    await loadSourceContext()
    return
  }
  await generate()
})
</script>

<style scoped>
.validation-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0;
  margin-bottom: 12px;
  border-block: 1px solid rgba(78, 200, 255, 0.16);
  background: rgba(5, 27, 57, 0.52);
}

.validation-strip > div {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 2px 10px;
  padding: 9px 14px;
  border-right: 1px solid rgba(78, 200, 255, 0.12);
}

.validation-strip > div:last-of-type { border-right: 0; }
.validation-strip span { color: #91acc4; font-size: 11px; }
.validation-strip strong { grid-row: span 2; color: #7dd3fc; font-size: 20px; line-height: 1.4; }
.validation-strip small { color: #5f7f99; font-size: 10px; }
.validation-strip p {
  grid-column: 1 / -1;
  margin: 0;
  padding: 5px 14px;
  border-top: 1px solid rgba(78, 200, 255, 0.1);
  color: #6f91aa;
  font-size: 10px;
}

/* ===== 三栏大屏布局 ===== */
.dashboard-grid {
  display: grid;
  grid-template-columns: 280px 1fr 280px;
  gap: 16px;
  height: calc(100vh - 295px);
  min-height: 520px;
}

.col {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(78, 200, 255, 0.15);
  border-radius: 12px;
  background: rgba(8, 42, 92, 0.28);
  backdrop-filter: blur(8px);
}

.col-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(78, 200, 255, 0.12);
  flex-shrink: 0;
}

.col-title {
  font-size: 14px;
  font-weight: 600;
  color: #cbd5e1;
  letter-spacing: 0.5px;
}

/* ===== 左栏：数据源树 ===== */
.source-tree-wrapper {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 0 8px 8px;
}

.source-search {
  margin-bottom: 6px;
  flex-shrink: 0;
}

:deep(.source-tree-wrapper .el-tree) {
  flex: 1;
  overflow-y: auto;
  background: transparent;
  --el-tree-node-hover-bg-color: rgba(56, 189, 248, 0.06);
}

:deep(.source-tree-wrapper .el-tree-node__content) {
  height: auto;
  padding: 3px 0;
}

:deep(.source-tree-wrapper .el-tree-node.is-expanded > .el-tree-node__children) {
  overflow: visible;
}

.source-group-label {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  padding-left: 2px;
}

.source-tree-item {
  padding: 6px 0;
  width: 100%;
}

.source-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.source-name {
  font-size: 13px;
  font-weight: 500;
  color: #e2e8f0;
}

.source-meta {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 2px;
}

.source-updated {
  font-size: 11px;
  color: #64748b;
}

.source-bottom {
  display: flex;
  flex-wrap: wrap;
  gap: 2px 8px;
  font-size: 11px;
  color: #708ba1;
}

.source-count {
  color: #38bdf8;
}

/* 滚动条 */
:deep(.source-tree-wrapper .el-tree)::-webkit-scrollbar,
.job-cards::-webkit-scrollbar,
.detail-panel::-webkit-scrollbar {
  width: 4px;
}

:deep(.source-tree-wrapper .el-tree)::-webkit-scrollbar-thumb,
.job-cards::-webkit-scrollbar-thumb,
.detail-panel::-webkit-scrollbar-thumb {
  background: rgba(78, 200, 255, 0.2);
  border-radius: 2px;
}

/* ===== 中栏：岗位卡片 ===== */
.job-cards {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.job-card {
  padding: 12px;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(78, 200, 255, 0.08);
  cursor: pointer;
  transition: all 0.2s;
}

.job-card:hover { border-color: rgba(78, 200, 255, 0.25); }
.job-card.active { border-color: rgba(56, 189, 248, 0.5); background: rgba(56, 189, 248, 0.08); }

.job-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.job-name {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
}

.job-index {
  font-size: 18px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

/* 5维小柱状图 */
.dim-bars {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin-bottom: 8px;
}

.dim-bar-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dim-label {
  font-size: 10px;
  color: #94a3b8;
  width: 68px;
  text-align: right;
  flex-shrink: 0;
}

.dim-track {
  flex: 1;
  height: 5px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.06);
  overflow: hidden;
}

.dim-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

/* 多源覆盖 */
.source-dots {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
}

.dots-label {
  font-size: 10px;
  color: #64748b;
  margin-right: 2px;
}

.source-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: all 0.2s;
}

.source-dot.covered {
  background: #38bdf8;
  border-color: #38bdf8;
  box-shadow: 0 0 4px rgba(56, 189, 248, 0.4);
}

.coverage-text {
  font-size: 10px;
  color: #38bdf8;
  margin-left: 4px;
}

.job-card-footer {
  display: flex;
  align-items: center;
  gap: 8px;
}

.job-skills {
  font-size: 11px;
  color: #64748b;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ===== 右栏：详细信息 ===== */
.detail-panel {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
}

.detail-hero {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(78, 200, 255, 0.1);
}

.detail-name {
  font-size: 18px;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 6px;
}

.detail-index-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.detail-index-label {
  font-size: 12px;
  color: #64748b;
}

.detail-index-val {
  font-size: 24px;
  font-weight: 700;
}

.detail-def {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.6;
  margin-bottom: 14px;
}

.detail-section {
  margin-bottom: 14px;
}

.detail-section h4 {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  margin: 0 0 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-section ul {
  margin: 0;
  padding-left: 16px;
}

.detail-section li {
  font-size: 12px;
  color: #cbd5e1;
  line-height: 1.7;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.text-muted {
  font-size: 12px;
  color: #64748b;
}

.evidence-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.evidence-item {
  padding: 8px 10px;
  border-radius: 6px;
  background: rgba(15, 23, 42, 0.4);
  border-left: 2px solid rgba(56, 189, 248, 0.4);
}

.evidence-quote {
  font-size: 11px;
  color: #cbd5e1;
  line-height: 1.5;
  font-style: italic;
}

.evidence-source {
  font-size: 10px;
  color: #38bdf8;
  margin-top: 4px;
}

.detail-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid rgba(78, 200, 255, 0.1);
}

/* ===== 底部：数据源动态轮播 ===== */
.source-ticker {
  display: flex;
  align-items: center;
  height: 40px;
  margin-top: 12px;
  border: 1px solid rgba(78, 200, 255, 0.15);
  border-radius: 10px;
  background: rgba(8, 42, 92, 0.28);
  backdrop-filter: blur(8px);
  overflow: hidden;
}

.ticker-label {
  flex-shrink: 0;
  padding: 0 16px;
  font-size: 12px;
  font-weight: 600;
  color: #60a5fa;
  white-space: nowrap;
  border-right: 1px solid rgba(78, 200, 255, 0.12);
  line-height: 40px;
  background: rgba(15, 23, 42, 0.3);
}

.ticker-track {
  flex: 1;
  overflow: hidden;
  position: relative;
  mask-image: linear-gradient(to right, transparent 0%, black 5%, black 95%, transparent 100%);
}

.ticker-inner {
  display: flex;
  gap: 0;
  width: max-content;
  animation: ticker-scroll 30s linear infinite;
}

.ticker-track:hover .ticker-inner {
  animation-play-state: paused;
}

.ticker-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 24px;
  white-space: nowrap;
  font-size: 12px;
  color: #94a3b8;
  flex-shrink: 0;
}

.ticker-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #64748b;
  flex-shrink: 0;
}

.ticker-dot.active {
  background: #46c8ff;
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.5);
}

.ticker-name {
  color: #e2e8f0;
  font-weight: 500;
}

.ticker-divider {
  color: rgba(78, 200, 255, 0.2);
}

.ticker-count {
  color: #38bdf8;
}

.ticker-time {
  color: #64748b;
  font-variant-numeric: tabular-nums;
}

@keyframes ticker-scroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
</style>
