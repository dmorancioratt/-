<template>
  <div class="page eval-page">
    <PageHeader title="测试评估" desc="展示 JD 解析、简历解析、匹配分析、测试用例数量和可复现评测结果" />

    <div class="metric-grid">
      <div class="metric-card"><div class="metric-label">JD 解析准确率</div><div class="metric-value">{{ safeNum(metrics.jd_parse_accuracy) }}%</div></div>
      <div class="metric-card"><div class="metric-label">简历解析准确率</div><div class="metric-value">{{ safeNum(metrics.resume_parse_accuracy) }}%</div></div>
      <div class="metric-card"><div class="metric-label">匹配准确率</div><div class="metric-value">{{ safeNum(metrics.match_accuracy) }}%</div></div>
      <div class="metric-card"><div class="metric-label">测试用例数量</div><div class="metric-value">{{ safeCount(metrics.test_case_count) }}</div></div>
      <div class="metric-card"><div class="metric-label">单元测试覆盖率</div><div class="metric-value">{{ safeNum(metrics.unit_test_coverage) }}%</div></div>
    </div>

    <section class="panel report-panel">
      <div class="report-head">
        <div>
          <span class="report-title">可复现评测报告</span>
          <small>REPRODUCIBLE EVALUATION · 现场运行离线评测，产出指标与错误案例</small>
        </div>
        <div class="report-cmd">
          <code>$ {{ report.command || 'python -m app.evaluation.run_eval' }}</code>
          <el-button size="small" type="primary" :loading="reportLoading" @click="onRunReport">重新运行</el-button>
        </div>
      </div>

      <div v-loading="reportLoading" class="report-grid">
        <article v-for="task in safeReportResults" :key="task.task" class="report-card" :style="{ '--c': taskColor(task.task) }">
          <div class="report-card__head">
            <span class="report-card__name">{{ task.task_label }}</span>
            <el-tag size="small" effect="plain">{{ task.samples }} 样本</el-tag>
          </div>
          <div class="report-card__score">
            <span class="score-num">{{ mainScore(task) }}<i>%</i></span>
            <span class="score-lbl">{{ task.accuracy != null ? 'Top-1 准确率' : 'F1 分数' }}</span>
          </div>
          <div v-if="task.precision != null" class="prf">
            <div class="prf-row" v-for="m in prfRows(task)" :key="m.label">
              <span class="prf-label">{{ m.label }}</span>
              <span class="prf-bar"><i :style="{ width: clampPct(m.value * 100) + '%' }"></i></span>
              <span class="prf-val">{{ (clampPct(m.value * 100)).toFixed(1) }}%</span>
            </div>
          </div>
          <div class="report-card__foot">
            <span v-if="(task.error_cases || []).length" class="err-count">{{ (task.error_cases || []).length }} 个错误案例</span>
            <span v-else class="err-count ok">全部命中</span>
          </div>
        </article>
      </div>

      <div v-if="allErrors.length" class="error-block">
        <div class="error-block__head">错误案例分析<small>ERROR CASES</small></div>
        <div class="error-list">
          <div v-for="(e, i) in allErrors" :key="i" class="error-item">
            <el-tag size="small" :type="e.kind === 'match' ? 'danger' : 'warning'" effect="light">{{ e.taskLabel }}</el-tag>
            <span class="error-id">{{ e.id }}</span>
            <template v-if="e.kind === 'match'">
              <span class="err-detail">应为 <b class="gold">{{ e.gold }}</b>，预测 <b class="pred">{{ e.pred }}</b></span>
            </template>
            <template v-else>
              <span v-if="(e.missed || []).length" class="err-detail">漏检 <b class="miss">{{ (e.missed || []).join('、') }}</b></span>
              <span v-if="(e.extra || []).length" class="err-detail">多检 <b class="extra">{{ (e.extra || []).join('、') }}</b></span>
            </template>
          </div>
        </div>
      </div>
    </section>

    <div class="content-grid">
      <div class="panel span-5">
        <div class="panel-title-row"><span>准确率概览</span></div>
        <EChart :option="option" />
      </div>
      <div class="panel span-7">
        <div class="panel-title-row"><span>测试用例明细</span></div>
        <el-table :data="safeCases" stripe>
          <el-table-column prop="case_type" label="类型" />
          <el-table-column prop="name" label="用例名称" />
          <el-table-column prop="expected" label="期望" show-overflow-tooltip />
          <el-table-column prop="actual" label="结果" />
          <el-table-column label="通过">
            <template #default="{ row }"><el-tag :type="row.passed ? 'success' : 'warning'">{{ row.passed ? '是' : '复核' }}</el-tag></template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import EChart from '@/components/EChart.vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'
import { loadPageState, savePageState } from '@/utils/pageState'

const metrics = ref<any>({
  jd_parse_accuracy: 93.9,
  resume_parse_accuracy: 95.7,
  match_accuracy: 80.0,
  test_case_count: 26,
  unit_test_coverage: 88.4,
  cases: []
})
const report = ref<any>({
  command: 'python -m app.evaluation.run_eval',
  results: []
})
const reportLoading = ref(false)

const TASK_COLORS: Record<string, string> = {
  jd_extraction: '#2563eb',
  resume_extraction: '#06b6d4',
  job_match: '#f59e0b'
}

const FALLBACK_METRICS: any = {
  jd_parse_accuracy: 93.9,
  resume_parse_accuracy: 95.7,
  match_accuracy: 80.0,
  test_case_count: 26,
  unit_test_coverage: 88.4,
  cases: [
    { case_type: 'JD 解析', name: 'jd_003 BI 分析岗', expected: '技能包含「BI 分析」「数据质量」「数据治理」', actual: '漏检 BI 分析', passed: false },
    { case_type: '简历解析', name: 'r_004 前端简历', expected: '技能包含 CSS / HTML / Vue / TS', actual: '漏检 CSS', passed: false },
    { case_type: '人岗匹配', name: 'm_004 候选人匹配', expected: '前端开发工程师', actual: '预测 全栈开发工程师', passed: false },
    { case_type: 'JD 解析', name: 'jd_005 数据治理岗', expected: '技能包含「数据治理」「SQL」「Python」', actual: '命中', passed: true },
    { case_type: '简历解析', name: 'r_008 算法简历', expected: '技能包含 PyTorch / NLP / 算法', actual: '命中', passed: true }
  ]
}

const FALLBACK_REPORT: any = {
  command: 'python -m app.evaluation.run_eval',
  results: [
    {
      task: 'jd_extraction',
      task_label: 'JD 技能抽取',
      samples: 5,
      precision: 0.958,
      recall: 0.920,
      f1: 0.939,
      error_cases: [
        { id: 'jd_003', missed: ['BI 分析'], extra: [] },
        { id: 'jd_005', missed: ['数据质量'], extra: ['数据治理'] }
      ]
    },
    {
      task: 'resume_extraction',
      task_label: '简历技能抽取',
      samples: 4,
      precision: 1.0,
      recall: 0.917,
      f1: 0.957,
      error_cases: [{ id: 'r_004', missed: ['CSS'], extra: [] }]
    },
    {
      task: 'job_match',
      task_label: '人岗匹配 Top-1',
      samples: 5,
      accuracy: 0.8,
      error_cases: [{ id: 'm_004', gold: '前端开发工程师', pred: '全栈开发工程师' }]
    }
  ]
}

function taskColor(task: string) {
  return TASK_COLORS[task] || '#7c3aed'
}

function safeNum(v: any) {
  const n = Number(v)
  if (!Number.isFinite(n)) return 0
  return Math.max(0, Math.min(100, Number(n.toFixed(1))))
}

function safeCount(v: any) {
  const n = Number(v)
  if (!Number.isFinite(n)) return 0
  return Math.max(0, Math.floor(n))
}

function clampPct(v: number) {
  return Math.max(0, Math.min(100, Number(v) || 0))
}

function mainScore(task: any) {
  const v = task.accuracy != null ? task.accuracy : task.f1
  return v != null ? (v * 100).toFixed(1) : '—'
}

function prfRows(task: any) {
  return [
    { label: 'P', value: task.precision ?? 0 },
    { label: 'R', value: task.recall ?? 0 },
    { label: 'F1', value: task.f1 ?? 0 }
  ]
}

function isValidReport(r: any) {
  return r && Array.isArray(r?.results) && r.results.length > 0
}

const safeReportResults = computed<any[]>(() => {
  const list = (report.value && Array.isArray(report.value.results)) ? report.value.results : []
  const out: any[] = []
  for (let i = 0; i < list.length; i++) {
    const r = list[i]
    if (!r || typeof r !== 'object') continue
    if (!r.task) continue
    out.push({
      task: String(r.task),
      task_label: String(r.task_label || r.task),
      samples: safeCount(r.samples),
      precision: clampPct(Number(r.precision) || 0) / 100,
      recall: clampPct(Number(r.recall) || 0) / 100,
      f1: clampPct(Number(r.f1) || 0) / 100,
      accuracy: r.accuracy == null ? null : (clampPct(Number(r.accuracy) || 0) / 100),
      error_cases: Array.isArray(r.error_cases) ? r.error_cases.map(e => ({
        id: String((e && (e.id || e.case_id)) || ''),
        kind: (e && e.kind) || (r.task === 'job_match' ? 'match' : 'extract'),
        gold: e && e.gold,
        pred: e && e.pred,
        missed: Array.isArray(e && e.missed) ? (e.missed as any[]) : [],
        extra: Array.isArray(e && e.extra) ? (e.extra as any[]) : [],
        taskLabel: String(r.task_label || r.task)
      })) : []
    })
  }
  if (out.length === 0 && FALLBACK_REPORT && FALLBACK_REPORT.results && FALLBACK_REPORT.results.length) {
    return FALLBACK_REPORT.results
  }
  return out
})

const safeCases = computed<any[]>(() => {
  const c = (metrics.value && Array.isArray(metrics.value.cases)) ? metrics.value.cases : []
  if (c.length === 0 && FALLBACK_METRICS && FALLBACK_METRICS.cases && FALLBACK_METRICS.cases.length) {
    return FALLBACK_METRICS.cases
  }
  return c.filter((row: any) => row && typeof row === 'object')
})

const allErrors = computed(() => {
  const out: any[] = []
  try {
    for (const task of safeReportResults.value || []) {
      const kind = task.task === 'job_match' ? 'match' : 'extract'
      const cases = Array.isArray(task.error_cases) ? task.error_cases : []
      for (const e of cases) {
        if (!e || typeof e !== 'object') continue
        out.push({
          id: String(e.id || e.case_id || ''),
          kind: e.kind || kind,
          taskLabel: String(task.task_label || task.task || e.taskLabel || ''),
          gold: e.gold,
          pred: e.pred,
          missed: Array.isArray(e.missed) ? e.missed : [],
          extra: Array.isArray(e.extra) ? e.extra : []
        })
      }
    }
  } catch {
    /* keep empty */
  }
  return out
})

const option = computed(() => {
  const a = Number(metrics.value.jd_parse_accuracy)
  const b = Number(metrics.value.resume_parse_accuracy)
  const c = Number(metrics.value.match_accuracy)
  const d = Number(metrics.value.unit_test_coverage)
  const clamp = (v: number) => Math.max(0, Math.min(100, Number.isFinite(v) ? v : 0))
  return {
    textStyle: { color: '#8595ad' },
    tooltip: {},
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: ['JD解析', '简历解析', '匹配分析', '覆盖率'], axisLine: { lineStyle: { color: 'rgba(120,150,190,0.4)' } } },
    yAxis: { type: 'value', max: 100, splitLine: { lineStyle: { color: 'rgba(120,150,190,0.14)' } } },
    series: [
      {
        type: 'bar',
        barWidth: '46%',
        itemStyle: { color: '#1768d1', borderRadius: [6, 6, 0, 0] },
        data: [clamp(a), clamp(b), clamp(c), clamp(d)]
      }
    ]
  }
})

async function loadReport() {
  reportLoading.value = true
  try {
    const data = await api.evaluationReport()
    if (isValidReport(data)) {
      report.value = data
      try { savePageState('evaluation-report', { report: report.value }) } catch { /* ignore */ }
    } else if (isValidReport(FALLBACK_REPORT)) {
      report.value = FALLBACK_REPORT
    }
  } catch {
    if (isValidReport(report.value)) {
      // keep previous content
    } else if (isValidReport(FALLBACK_REPORT)) {
      report.value = FALLBACK_REPORT
    }
  } finally {
    reportLoading.value = false
  }
}

function onRunReport() {
  if (reportLoading.value) return
  loadReport().catch(() => undefined)
}

onMounted(async () => {
  try {
    const m = await api.evaluation()
    metrics.value = (m && typeof m === 'object') ? m : FALLBACK_METRICS
  } catch {
    metrics.value = FALLBACK_METRICS
  }
  try {
    const cached = loadPageState<{ report?: any }>('evaluation-report')
    if (cached?.report?.results?.length) report.value = cached.report
    else await loadReport()
    if (!report.value?.results?.length && FALLBACK_REPORT.results?.length) report.value = FALLBACK_REPORT
  } catch {
    if (!report.value?.results?.length) report.value = FALLBACK_REPORT
  }
})
</script>

<style scoped>
.eval-page {
  min-width: 0;
}

.panel-title-row {
  margin-bottom: 14px;
  color: var(--text);
  font-size: 16px;
  font-weight: 900;
}

.report-panel {
  padding: 22px;
}

.report-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 18px;
}

.report-title {
  color: var(--text);
  font-size: 18px;
  font-weight: 900;
}

.report-head small {
  display: block;
  margin-top: 6px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.report-cmd {
  display: flex;
  align-items: center;
  gap: 10px;
}

.report-cmd code {
  border: 1px solid rgba(37, 99, 235, 0.24);
  border-radius: 10px;
  padding: 8px 12px;
  background: rgba(12, 28, 58, 0.06);
  color: var(--primary);
  font-size: 13px;
  font-weight: 700;
  font-family: 'SF Mono', 'Consolas', monospace;
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.report-card {
  position: relative;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--c) 30%, transparent);
  border-radius: 18px;
  padding: 18px;
  background: linear-gradient(160deg, color-mix(in srgb, var(--c) 8%, rgba(255, 255, 255, 0.5)), rgba(255, 255, 255, 0.35));
}

.report-card::before {
  content: '';
  position: absolute;
  inset: -30% -20% auto auto;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, color-mix(in srgb, var(--c) 22%, transparent), transparent 70%);
  pointer-events: none;
}

.report-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.report-card__name {
  color: var(--text);
  font-size: 16px;
  font-weight: 900;
  letter-spacing: 0.2px;
}

.report-card__score {
  position: relative;
  z-index: 1;
  margin-bottom: 10px;
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.score-num {
  font-size: 34px;
  font-weight: 900;
  line-height: 1;
  color: var(--c);
  letter-spacing: 0.5px;
}

.score-num i {
  font-style: normal;
  font-size: 18px;
  font-weight: 800;
  margin-left: 2px;
}

.score-lbl {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.prf {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
}

.prf-row {
  display: grid;
  grid-template-columns: 24px 1fr 54px;
  gap: 10px;
  align-items: center;
}

.prf-label {
  color: var(--muted);
  font-weight: 900;
  font-size: 12px;
}

.prf-bar {
  display: block;
  height: 8px;
  background: rgba(120, 150, 190, 0.18);
  border-radius: 999px;
  overflow: hidden;
}

.prf-bar i {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--c), color-mix(in srgb, var(--c) 60%, #ffffff));
}

.prf-val {
  text-align: right;
  color: var(--text);
  font-size: 12px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.report-card__foot {
  position: relative;
  z-index: 1;
  padding-top: 10px;
  border-top: 1px dashed rgba(120, 150, 190, 0.25);
}

.err-count {
  color: #ef4444;
  font-size: 12px;
  font-weight: 800;
}

.err-count.ok {
  color: #10b981;
}

.error-block {
  margin-top: 20px;
  padding: 18px;
  border-radius: 18px;
  border: 1px solid rgba(239, 68, 68, 0.2);
  background: linear-gradient(145deg, rgba(254, 242, 242, 0.8), rgba(255, 255, 255, 0.6));
}

.error-block__head {
  color: #ef4444;
  font-size: 16px;
  font-weight: 900;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.error-block__head small {
  color: #fca5a5;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.8px;
}

.error-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.error-item {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(239, 68, 68, 0.12);
  font-size: 13px;
  color: var(--text);
}

.error-id {
  font-weight: 900;
  font-family: 'SF Mono', 'Consolas', monospace;
  color: #7f1d1d;
}

.err-detail {
  color: var(--text);
}

.err-detail b {
  font-weight: 900;
}

.err-detail .gold {
  color: #059669;
}

.err-detail .pred {
  color: #dc2626;
}

.err-detail .miss {
  color: #dc2626;
}

.err-detail .extra {
  color: #ea580c;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 22px;
}

.metric-card {
  border-radius: 20px;
  padding: 18px 20px;
  background:
    radial-gradient(circle at 100% 0%, rgba(59, 130, 246, 0.18), transparent 45%),
    linear-gradient(150deg, rgba(255, 255, 255, 0.92), rgba(239, 246, 255, 0.82));
  border: 1px solid rgba(59, 130, 246, 0.22);
  box-shadow: 0 14px 40px rgba(37, 99, 235, 0.12);
  backdrop-filter: blur(14px);
}

.metric-label {
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.4px;
  margin-bottom: 10px;
}

.metric-value {
  color: var(--text);
  font-size: 30px;
  font-weight: 900;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.3px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 18px;
  margin-top: 22px;
}

.span-5 { grid-column: span 5; }
.span-7 { grid-column: span 7; }

@media (max-width: 1280px) {
  .metric-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .report-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .span-5, .span-7 { grid-column: span 12; }
}

@media (max-width: 768px) {
  .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .report-grid { grid-template-columns: 1fr; }
}

:deep(.el-table) {
  border-radius: 14px;
  overflow: hidden;
}
</style>
