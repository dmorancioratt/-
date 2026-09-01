<template>
  <div class="page jobs-page">
    <PageHeader title="岗位管理" desc="按领域、类型和等级筛选岗位，查看岗位画像、状态、版本和证据来源">
      <div class="job-summary">
        <div>
          <b>{{ rows.length }}</b>
          <span>岗位总数</span>
        </div>
        <div>
          <b>{{ emergingCount }}</b>
          <span>新兴岗位</span>
        </div>
        <div>
          <b>{{ domains.length }}</b>
          <span>覆盖领域</span>
        </div>
      </div>
    </PageHeader>

    <div class="panel job-analysis">
      <div class="analysis-head">
        <span class="analysis-mark"></span>
        <div class="analysis-title">
          <b>岗位数据分析</b>
          <small>领域分布 · 等级结构 · 热门技能需求 · 随筛选实时联动</small>
        </div>
        <span class="analysis-badge">VISUAL ANALYTICS</span>
      </div>
      <div class="analysis-grid">
        <div class="analysis-card">
          <div class="analysis-card-title"><i class="dot dot-blue"></i>领域分布 · 玫瑰光谱</div>
          <EChart :option="roseOption" class="analysis-chart" />
        </div>
        <div class="analysis-card">
          <div class="analysis-card-title"><i class="dot dot-violet"></i>等级结构 · 极坐标雷达柱</div>
          <EChart :option="levelOption" class="analysis-chart" />
        </div>
        <div class="analysis-card">
          <div class="analysis-card-title"><i class="dot dot-cyan"></i>热门技能需求 TOP8 · 能量条</div>
          <EChart :option="skillOption" class="analysis-chart" />
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="toolbar job-toolbar">
        <el-select v-model="domain" clearable placeholder="所属领域" style="width: 180px">
          <el-option v-for="item in domains" :key="item" :label="item" :value="item" />
        </el-select>
        <el-select v-model="type" clearable placeholder="岗位类型" style="width: 180px">
          <el-option v-for="item in jobTypes" :key="item" :label="item" :value="item" />
        </el-select>
        <el-select v-model="level" clearable placeholder="岗位等级" style="width: 180px">
          <el-option v-for="item in levels" :key="item" :label="item" :value="item" />
        </el-select>
        <el-button @click="resetFilters">重置筛选</el-button>
        <span class="result-count">当前显示 {{ filtered.length }} 条</span>
      </div>

      <el-table :data="paged" stripe class="job-table" @row-dblclick="openDetail">
        <el-table-column prop="name" label="岗位名称" min-width="190">
          <template #default="{ row }">
            <div class="job-name-cell">
              <span>{{ row.name }}</span>
              <el-tag v-if="row.is_emerging" size="small" type="primary">新岗位</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="domain" label="所属领域" width="120" />
        <el-table-column prop="job_type" label="岗位类型" width="120" />
        <el-table-column prop="level" label="岗位等级" width="110" />
        <el-table-column label="岗位描述" min-width="320">
          <template #default="{ row }">
            <span class="description-ellipsis">{{ row.description }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本号" width="100" />
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="table-pagination">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="filtered.length"
          :pager-count="7"
          background
          layout="total, prev, pager, next, jumper"
        />
      </div>
    </div>

    <el-dialog v-model="detailVisible" class="tech-dialog" width="680px" destroy-on-close align-center>
      <template #header>
        <div class="detail-header">
          <div>
            <div class="detail-kicker">JOB ENTITY PROFILE</div>
            <h3>{{ currentJob?.name }}</h3>
          </div>
          <el-tag :type="currentJob?.is_emerging ? 'primary' : 'info'">
            {{ currentJob?.is_emerging ? '新兴岗位' : '既有岗位' }}
          </el-tag>
        </div>
      </template>

      <div v-if="currentJob" class="detail-body">
        <div class="detail-meta">
          <div><span>所属领域</span><b>{{ currentJob.domain }}</b></div>
          <div><span>岗位类型</span><b>{{ currentJob.job_type }}</b></div>
          <div><span>岗位等级</span><b>{{ currentJob.level }}</b></div>
          <div><span>版本号</span><b>{{ currentJob.version }}</b></div>
        </div>

        <section>
          <h4>岗位描述</h4>
          <p>{{ currentJob.description }}</p>
        </section>

        <section>
          <h4>状态与写入规则</h4>
          <div class="tag-list">
            <el-tag :type="statusType(currentJob.status)">状态：{{ statusLabel(currentJob.status) }}</el-tag>
            <el-tag type="primary">证据可追溯</el-tag>
            <el-tag type="info">低置信度需审核</el-tag>
          </div>
        </section>

        <section>
          <h4>统一能力要求</h4>
          <div class="requirement-block">
            <b>必备能力</b>
            <div class="tag-list"><el-tag v-for="item in currentJob.requirements?.required_skills || []" :key="item">{{ item }}</el-tag></div>
          </div>
          <div class="requirement-block">
            <b>加分能力</b>
            <div class="tag-list"><el-tag v-for="item in currentJob.requirements?.preferred_skills || []" :key="item" type="info">{{ item }}</el-tag></div>
          </div>
        </section>

        <section>
          <h4>建议证书</h4>
          <p class="requirement-note">以下证书来自人社部考试计划，并按岗位领域关联，不代表强制任职门槛。</p>
          <div class="certificate-list">
            <div v-for="item in currentJob.requirements?.recommended_certificates || []" :key="item.id">
              <b>{{ item.name }}</b><span>{{ item.levels?.join(' / ') || '等级以考试计划为准' }}</span>
            </div>
          </div>
        </section>

        <section>
          <h4>证据来源</h4>
          <div class="evidence-box">{{ currentJob.evidence }}</div>
        </section>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button @click="openGraph">在图谱中查看</el-button>
        <el-button v-if="canEdit" @click="openEdit">人工优化</el-button>
        <el-button type="primary" @click="startMatch">用于匹配分析</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editVisible" class="edit-dialog" title="人工优化岗位画像" width="720px" align-center>
      <el-form label-position="top" class="edit-form">
        <div class="edit-grid">
          <el-form-item label="所属领域"><el-input v-model="editForm.domain" /></el-form-item>
          <el-form-item label="岗位类型"><el-input v-model="editForm.job_type" /></el-form-item>
          <el-form-item label="岗位等级"><el-input v-model="editForm.level" /></el-form-item>
          <el-form-item label="状态">
            <el-select v-model="editForm.status"><el-option label="已启用" value="active" /><el-option label="公示中" value="proposed" /><el-option label="趋势岗位" value="trend" /><el-option label="已归档" value="archived" /></el-select>
          </el-form-item>
        </div>
        <el-form-item label="岗位描述"><el-input v-model="editForm.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="必备技能（用逗号或换行分隔）"><el-input v-model="editForm.required_skills" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="加分技能（用逗号或换行分隔）"><el-input v-model="editForm.preferred_skills" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="本次更新说明"><el-input v-model="editForm.update_note" placeholder="说明为什么调整岗位画像" /></el-form-item>
        <el-form-item label="证据来源（每行一条 URL、报告或 JD 批次）"><el-input v-model="editForm.evidence_sources" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="editVisible = false">取消</el-button><el-button type="primary" :loading="saving" @click="saveJob">保存并生成新版本</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import EChart from '@/components/EChart.vue'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const rows = ref<any[]>([])
const router = useRouter()
const auth = useAuthStore()
const domain = ref('')
const type = ref('')
const level = ref('')
const detailVisible = ref(false)
const currentJob = ref<any>()
const editVisible = ref(false)
const saving = ref(false)
const editForm = ref<any>({})
const canEdit = computed(() => ['admin', 'hr'].includes(auth.user?.role || ''))

const domains = computed(() => Array.from(new Set(rows.value.map((row) => row.domain))))
const jobTypes = computed(() => Array.from(new Set(rows.value.map((row) => row.job_type))))
const levels = computed(() => Array.from(new Set(rows.value.map((row) => row.level))))
const emergingCount = computed(() => rows.value.filter((row) => row.is_emerging).length)
const filtered = computed(() =>
  rows.value.filter(
    (row) =>
      (!domain.value || row.domain === domain.value) &&
      (!type.value || row.job_type === type.value) &&
      (!level.value || row.level === level.value)
  )
)

const page = ref(1)
const pageSize = 12
const paged = computed(() =>
  filtered.value.slice((page.value - 1) * pageSize, page.value * pageSize)
)
watch([domain, type, level], () => {
  page.value = 1
})
watch(
  () => filtered.value.length,
  (len) => {
    const maxPage = Math.max(1, Math.ceil(len / pageSize))
    if (page.value > maxPage) page.value = maxPage
  }
)

const CHART_COLORS = ['#22f7ff', '#8ff7f4', '#00c9d2', '#8f7cff', '#22f7ff', '#65fff6', '#22d3ee', '#ffb65c']

function countBy(key: 'domain' | 'level') {
  const map = new Map<string, number>()
  filtered.value.forEach((row) => map.set(row[key], (map.get(row[key]) || 0) + 1))
  return [...map.entries()].sort((a, b) => b[1] - a[1])
}

const domainStats = computed(() => countBy('domain'))
const levelStats = computed(() => countBy('level'))
const skillStats = computed(() => {
  const map = new Map<string, number>()
  filtered.value.forEach((row) =>
    (row.requirements?.required_skills || []).forEach((skill: string) => {
      if (skill) map.set(skill, (map.get(skill) || 0) + 1)
    })
  )
  return [...map.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8)
})

const tooltipStyle = {
  backgroundColor: 'rgba(7, 26, 53, 0.92)',
  borderColor: 'rgba(78, 200, 255, 0.35)',
  borderWidth: 1,
  textStyle: { color: '#d6f1ff', fontSize: 12 }
}

const roseOption = computed(() => ({
  backgroundColor: 'transparent',
  color: CHART_COLORS,
  tooltip: { trigger: 'item', ...tooltipStyle },
  series: [
    {
      type: 'pie',
      roseType: 'area',
      radius: ['16%', '76%'],
      center: ['50%', '52%'],
      itemStyle: {
        borderRadius: 6,
        borderColor: 'rgba(7, 26, 53, 0.9)',
        borderWidth: 2,
        shadowBlur: 14,
        shadowColor: 'rgba(56, 189, 248, 0.35)'
      },
      label: { color: '#bfe3ff', fontSize: 11 },
      labelLine: { lineStyle: { color: 'rgba(125, 211, 252, 0.4)' } },
      data: domainStats.value.map(([name, value]) => ({ name, value }))
    }
  ]
}))

const levelOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'axis', ...tooltipStyle, axisPointer: { type: 'shadow' } },
  polar: { radius: ['16%', '70%'], center: ['50%', '52%'] },
  angleAxis: {
    data: levelStats.value.map(([name]) => name),
    startAngle: 90,
    axisLine: { lineStyle: { color: 'rgba(125, 211, 252, 0.25)' } },
    axisTick: { show: false },
    axisLabel: { color: '#bfe3ff', fontSize: 11 }
  },
  radiusAxis: {
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: 'rgba(168, 207, 232, 0.55)', fontSize: 10 },
    splitLine: { lineStyle: { color: 'rgba(125, 211, 252, 0.12)' } }
  },
  series: [
    {
      type: 'bar',
      coordinateSystem: 'polar',
      roundCap: true,
      barWidth: '55%',
      itemStyle: {
        borderRadius: 4,
        color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 1, colorStops: [
          { offset: 0, color: '#00c9d2' },
          { offset: 1, color: '#8ff7f4' }
        ] },
        shadowBlur: 10,
        shadowColor: 'rgba(56, 189, 248, 0.4)'
      },
      data: levelStats.value.map(([, value]) => value)
    }
  ]
}))

const skillOption = computed(() => {
  const data = skillStats.value.slice().reverse()
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...tooltipStyle, axisPointer: { type: 'shadow' } },
    grid: { left: 10, right: 44, top: 8, bottom: 8, containLabel: true },
    xAxis: { type: 'value', show: false },
    yAxis: {
      type: 'category',
      data: data.map(([name]) => name),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#bfe3ff', fontSize: 11 }
    },
    series: [
      {
        type: 'bar',
        barWidth: 9,
        showBackground: true,
        backgroundStyle: { color: 'rgba(56, 189, 248, 0.08)', borderRadius: 5 },
        itemStyle: {
          borderRadius: 5,
          color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [
            { offset: 0, color: '#00c9d2' },
            { offset: 1, color: '#8ff7f4' }
          ] },
          shadowBlur: 8,
          shadowColor: 'rgba(56, 189, 248, 0.45)'
        },
        label: { show: true, position: 'right', color: '#8ff7f4', fontSize: 11, fontWeight: 700 },
        data: data.map(([, value]) => value)
      }
    ]
  }
})

function resetFilters() {
  domain.value = ''
  type.value = ''
  level.value = ''
}

function openDetail(row: any) {
  currentJob.value = row
  detailVisible.value = true
}

function statusLabel(status: string) {
  return ({ active: '已启用', proposed: '公示中', trend: '趋势岗位', archived: '已归档' } as Record<string, string>)[status] || status
}

function statusType(status: string) {
  return status === 'active' ? 'success' : status === 'proposed' ? 'warning' : 'primary'
}

function openGraph() {
  if (!currentJob.value) return
  detailVisible.value = false
  router.push({ path: '/skill-graph', query: { jobId: String(currentJob.value.id) } })
}

function startMatch() {
  if (!currentJob.value) return
  detailVisible.value = false
  router.push({ path: '/match-analysis', query: { jobId: String(currentJob.value.id) } })
}

function splitItems(value: string) {
  return [...new Set(value.split(/[，,\n]/).map((item) => item.trim()).filter(Boolean))]
}

function openEdit() {
  if (!currentJob.value) return
  const job = currentJob.value
  editForm.value = {
    domain: job.domain,
    job_type: job.job_type,
    level: job.level,
    status: job.status,
    description: job.description,
    required_skills: (job.requirements?.required_skills || []).join('，'),
    preferred_skills: (job.requirements?.preferred_skills || []).join('，'),
    update_note: '',
    evidence_sources: ''
  }
  detailVisible.value = false
  editVisible.value = true
}

async function saveJob() {
  if (!currentJob.value) return
  if (!editForm.value.update_note.trim()) {
    ElMessage.warning('请填写本次更新说明')
    return
  }
  saving.value = true
  try {
    const updated = await api.updateJob(currentJob.value.id, {
      ...editForm.value,
      required_skills: splitItems(editForm.value.required_skills),
      preferred_skills: splitItems(editForm.value.preferred_skills),
      evidence_sources: splitItems(editForm.value.evidence_sources)
    })
    const index = rows.value.findIndex((item) => item.id === updated.id)
    if (index >= 0) rows.value[index] = updated
    currentJob.value = updated
    editVisible.value = false
    ElMessage.success(`岗位画像已更新至 ${updated.version}`)
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '岗位画像更新失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  rows.value = await api.jobs()
})
</script>

<style>
/* Unscoped glass overrides — specificity must beat theme-fixes.css (loaded after page styles).
   theme-fixes: body.theme-dark .app-main:not(.app-main--dashboard) :is(.panel,.page-toolbar,.job-summary>div,...) { background:#0a1c2b!important; box-shadow:none!important }
   styles.css:  body:not(.login-active) .app-main :is(.panel,.page-toolbar,...) { background:linear-gradient(...)!important }
   Both ≈ 0-0-41. We add .page.jobs-page + per-element classes to reach 0-0-61+. */

/* === 1. .page-toolbar 工具栏（包裹 job-summary） === */
body.theme-dark .app-main:not(.app-main--dashboard) .page.jobs-page .page-toolbar,
body:not(.login-active) .app-main .page.jobs-page .page-toolbar {
  border: 1px solid rgba(78, 200, 255, 0.18) !important;
  border-radius: 13px !important;
  padding: 12px 16px !important;
  background: rgba(8, 42, 92, 0.35) !important;
  box-shadow:
    inset 0 1px 0 rgba(161, 231, 255, 0.08),
    0 8px 32px rgba(0, 10, 40, 0.25) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  animation: none !important;
}
body.theme-dark .app-main:not(.app-main--dashboard) .page.jobs-page .page-toolbar::before,
body:not(.login-active) .app-main .page.jobs-page .page-toolbar::before {
  display: none !important;
}

/* === 2. .job-summary > div 三张统计小卡（theme-fixes 将其强制 #0a1c2b） === */
body.theme-dark .app-main:not(.app-main--dashboard) .page.jobs-page .job-summary > div,
body:not(.login-active) .app-main .page.jobs-page .job-summary > div {
  border: 1px solid rgba(78, 200, 255, 0.18) !important;
  border-radius: 13px !important;
  padding: 10px 12px !important;
  background: rgba(8, 42, 92, 0.35) !important;
  box-shadow:
    inset 0 1px 0 rgba(161, 231, 255, 0.08),
    0 8px 32px rgba(0, 10, 40, 0.25) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}
body.theme-dark .app-main:not(.app-main--dashboard) .page.jobs-page .job-summary b,
body:not(.login-active) .app-main .page.jobs-page .job-summary b {
  color: #effbff !important;
}
body.theme-dark .app-main:not(.app-main--dashboard) .page.jobs-page .job-summary span,
body:not(.login-active) .app-main .page.jobs-page .job-summary span {
  color: #85a9c4 !important;
}

/* === 3. .panel 主面板（包裹 job-toolbar + job-table） === */
body.theme-dark .app-main:not(.app-main--dashboard) .page.jobs-page > .panel,
body:not(.login-active) .app-main .page.jobs-page > .panel {
  border: 1px solid rgba(78, 200, 255, 0.18) !important;
  border-radius: 13px !important;
  background: rgba(8, 42, 92, 0.35) !important;
  box-shadow:
    inset 0 1px 0 rgba(161, 231, 255, 0.08),
    0 8px 32px rgba(0, 10, 40, 0.25) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  animation: none !important;
}
body.theme-dark .app-main:not(.app-main--dashboard) .page.jobs-page > .panel::before,
body:not(.login-active) .app-main .page.jobs-page > .panel::before {
  display: none !important;
}

/* === 4. .el-select__wrapper 三个下拉筛选器（theme-fixes 将其强制 #0a1d2c 实色） === */
body.theme-dark .app-main:not(.app-main--dashboard) .page.jobs-page .el-select__wrapper,
body:not(.login-active) .app-main .page.jobs-page .el-select__wrapper {
  border: 1px solid rgba(78, 200, 255, 0.18) !important;
  border-radius: 10px !important;
  background: rgba(8, 42, 92, 0.35) !important;
  box-shadow: inset 0 1px 0 rgba(161, 231, 255, 0.08) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}
body.theme-dark .app-main:not(.app-main--dashboard) .page.jobs-page .el-select__wrapper:hover,
body:not(.login-active) .app-main .page.jobs-page .el-select__wrapper:hover {
  border-color: rgba(78, 200, 255, 0.35) !important;
}
body.theme-dark .app-main:not(.app-main--dashboard) .page.jobs-page .el-select__wrapper.is-focused,
body:not(.login-active) .app-main .page.jobs-page .el-select__wrapper.is-focused {
  border-color: rgba(78, 200, 255, 0.45) !important;
  box-shadow: inset 0 1px 0 rgba(161, 231, 255, 0.08), 0 0 0 3px rgba(54, 215, 255, 0.12) !important;
}
body.theme-dark .app-main:not(.app-main--dashboard) .page.jobs-page .el-select__placeholder,
body.theme-dark .app-main:not(.app-main--dashboard) .page.jobs-page .el-select__selected-item,
body:not(.login-active) .app-main .page.jobs-page .el-select__placeholder,
body:not(.login-active) .app-main .page.jobs-page .el-select__selected-item {
  color: #d6f1ff !important;
}
body.theme-dark .app-main:not(.app-main--dashboard) .page.jobs-page .el-select__caret,
body:not(.login-active) .app-main .page.jobs-page .el-select__caret {
  color: #85b8d6 !important;
}
</style>

<style scoped>
.job-summary {
  display: grid;
  grid-template-columns: repeat(3, 92px);
  gap: 10px;
}

.job-summary > div {
  border: 1px solid rgba(190, 213, 242, 0.86);
  border-radius: 16px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.65);
  text-align: center;
  box-shadow: 0 10px 26px rgba(37, 99, 235, 0.08);
}

.job-summary b {
  display: block;
  color: #071a3d;
  font-size: 22px;
  font-weight: 950;
}

.job-summary span {
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
}

.job-toolbar {
  margin-bottom: 16px;
}

.result-count {
  margin-left: auto;
  color: #64748b;
  font-size: 13px;
  font-weight: 800;
}

/* ===== 数据分析面板 ===== */
.job-analysis {
  margin-bottom: 16px;
}

.analysis-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.analysis-mark {
  width: 4px;
  height: 34px;
  border-radius: 4px;
  background: linear-gradient(180deg, #8ff7f4, #00c9d2);
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.55);
}

.analysis-title b {
  display: block;
  color: #eaf8ff;
  font-size: 16px;
  font-weight: 900;
  letter-spacing: 0.02em;
}

.analysis-title small {
  color: #85a9c4;
  font-size: 12px;
  font-weight: 600;
}

.analysis-badge {
  margin-left: auto;
  padding: 5px 12px;
  border: 1px solid rgba(78, 200, 255, 0.3);
  border-radius: 999px;
  color: #8ff7f4;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.18em;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.analysis-card {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(78, 200, 255, 0.16);
  border-radius: 12px;
  padding: 12px 12px 6px;
  background: rgba(7, 28, 62, 0.35);
}

.analysis-card-title {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 4px;
  color: #a8d4ef;
  font-size: 13px;
  font-weight: 800;
}

.analysis-card-title .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.dot-blue { background: #22f7ff; box-shadow: 0 0 8px rgba(56, 189, 248, 0.8); }
.dot-violet { background: #8f7cff; box-shadow: 0 0 8px rgba(143, 124, 255, 0.8); }
.dot-cyan { background: #22f7ff; box-shadow: 0 0 8px rgba(54, 215, 255, 0.8); }

.analysis-chart {
  width: 100%;
  height: 248px;
}

@media (max-width: 1100px) {
  .analysis-grid {
    grid-template-columns: 1fr;
  }
}

/* ===== 表格分页 ===== */
.table-pagination {
  display: flex;
  justify-content: flex-end;
  padding-top: 14px;
}

.job-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 900;
  color: #14346c;
}

.description-ellipsis {
  display: -webkit-box;
  overflow: hidden;
  color: #53657e;
  line-height: 1.55;
  text-align: left;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.detail-kicker {
  color: var(--cyan);
  font-size: 11px;
  font-weight: 950;
  letter-spacing: 0.16em;
}

.detail-header h3 {
  margin: 8px 0 0;
  color: #071a3d;
  font-size: 23px;
  font-weight: 950;
}

.detail-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.detail-meta {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.detail-meta > div {
  border: 1px solid rgba(190, 213, 242, 0.82);
  border-radius: 16px;
  padding: 12px;
  background: rgba(232, 242, 255, 0.52);
}

.detail-meta span {
  display: block;
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
}

.detail-meta b {
  display: block;
  margin-top: 8px;
  color: #0f2f78;
  font-size: 15px;
}

.detail-body section h4 {
  margin: 0 0 9px;
  color: #14346c;
  font-size: 15px;
  font-weight: 950;
}

.detail-body section p {
  margin: 0;
  color: #334155;
  line-height: 1.9;
}

.evidence-box {
  border: 1px solid rgba(6, 182, 212, 0.26);
  border-radius: 16px;
  padding: 13px;
  background: rgba(231, 251, 255, 0.48);
  color: #31506f;
  line-height: 1.8;
}

.requirement-block { margin-bottom: 12px; }
.requirement-block > b { display: block; margin-bottom: 8px; color: #29456f; font-size: 12px; }
.requirement-note { margin: 0 0 10px; color: #718096; font-size: 12px; }
.certificate-list { display: grid; gap: 8px; }
.certificate-list > div { display: flex; align-items: center; justify-content: space-between; gap: 12px; border: 1px solid rgba(190,213,242,.72); border-radius: 12px; padding: 10px 12px; background: rgba(232,242,255,.48); }
.certificate-list b { color: #14346c; font-size: 13px; }
.certificate-list span { color: #718096; font-size: 11px; }
.edit-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 16px; }
:deep(.edit-dialog) { border: 1px solid rgba(77,198,255,.32); background: #071a36; color: #eaf8ff; }
:deep(.edit-dialog .el-dialog__title) { color: #f1fbff; font-weight: 850; }
:deep(.edit-dialog .el-dialog__headerbtn .el-dialog__close) { color: #9fc4de; }
:deep(.edit-dialog .el-form-item__label) { color: #acc8dd; font-weight: 750; }
:deep(.edit-dialog .el-input__wrapper),
:deep(.edit-dialog .el-select__wrapper),
:deep(.edit-dialog .el-textarea__inner) { border: 1px solid rgba(83,166,218,.3); background: #0b274d; box-shadow: none; }
:deep(.edit-dialog .el-input__inner),
:deep(.edit-dialog .el-select__selected-item),
:deep(.edit-dialog .el-textarea__inner) { color: #edfaff; }
:deep(.edit-dialog .el-input__inner::placeholder),
:deep(.edit-dialog .el-textarea__inner::placeholder) { color: #789ab5; }
@media (max-width: 720px) { .edit-grid { grid-template-columns: 1fr; } }
</style>
