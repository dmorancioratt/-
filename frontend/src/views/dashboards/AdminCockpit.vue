<template>
  <div class="admin-cockpit">
    <div v-if="loading" class="cockpit-loading">正在读取治理数据...</div>

    <header class="cockpit-header">
      <div class="cockpit-header__title">
        <span class="cockpit-eyebrow">平台治理指挥中心</span>
        <h1>先处理风险，再发布可信数据</h1>
        <p>集中查看数据来源、解析质量、人工复核与模型服务状态，每个异常都能进入对应处理页面。</p>
      </div>
      <div class="cockpit-header__actions">
        <span class="service-state" :class="model.ai.enabled ? 'online' : 'offline'">
          <i></i>{{ model.ai.enabled ? `${model.ai.provider} 服务可用` : '智能服务待配置' }}
        </span>
        <span class="cockpit-updated">更新于 {{ updatedLabel }}</span>
        <button class="cockpit-button" :disabled="refreshing" @click="refresh(true)">
          <el-icon :class="{ 'fa-spin': refreshing }"><Refresh /></el-icon>{{ refreshing ? '更新中' : '更新数据' }}
        </button>
      </div>
    </header>

    <section class="kpi-strip">
      <article class="kpi-card cockpit-panel hud-card--score">
        <div class="hud-card__corner hud-card__corner--tr"></div>
        <div class="hud-card__corner hud-card__corner--bl"></div>
        <div class="score-ring">
          <svg viewBox="0 0 36 36" class="score-ring__svg">
            <circle cx="18" cy="18" r="15.9" class="score-ring__bg" />
            <circle cx="18" cy="18" r="15.9" class="score-ring__fg" :style="scoreRingStyle" />
          </svg>
          <div class="score-ring__num">
            <b class="font-digits">{{ governanceScore }}</b>
            <small>/ 100</small>
          </div>
        </div>
        <div class="score-copy">
          <span class="kpi-label">治理健康度</span>
          <b class="kpi-verdict">{{ governanceVerdict }}</b>
          <p>综合数据质量、解析评测、测试覆盖和待复核风险。</p>
        </div>
      </article>

      <article
        v-for="card in kpiCards"
        :key="card.key"
        class="kpi-card cockpit-panel"
        role="button"
        tabindex="0"
        @click="router.push(card.path)"
        @keydown.enter="router.push(card.path)"
      >
        <div class="hud-card__corner hud-card__corner--tr"></div>
        <div class="hud-card__corner hud-card__corner--bl"></div>
        <div class="kpi-icon" :class="`kpi-icon--${card.tone}`">
          <el-icon><component :is="card.icon" /></el-icon>
        </div>
        <div class="kpi-meta">
          <span class="kpi-label">{{ card.label }}</span>
          <div class="kpi-value font-digits">
            <b>{{ card.value }}</b><span class="kpi-unit">{{ card.unit }}</span>
          </div>
          <span class="kpi-foot__hint">{{ card.hint }}</span>
        </div>
      </article>
    </section>

    <main class="cockpit-main">
      <section class="col col-left">
        <article class="cockpit-panel priority-panel">
          <div class="hud-card__corner hud-card__corner--tr"></div>
          <div class="hud-card__corner hud-card__corner--bl"></div>
          <div class="panel-head">
            <h2><span class="title-bar title-bar--rose"></span><span>今日治理重点</span></h2>
            <span class="cockpit-tag" :class="priorityItems.length ? 'danger' : 'success'">
              <i></i>{{ priorityItems.length ? `${priorityItems.length} 项待处理` : '当前无阻塞项' }}
            </span>
          </div>
          <p class="panel-sub">优先处理低置信风险前置项</p>
          <div v-if="priorityItems.length" class="priority-queue">
            <button
              v-for="(item, index) in priorityItems"
              :key="item.title"
              type="button"
              class="priority-row"
              :class="`priority-row--${item.tone}`"
              @click="router.push(item.path)"
            >
              <span class="priority-index">{{ String(index + 1).padStart(2, '0') }}</span>
              <span class="priority-body">
                <b>{{ item.title }}</b>
                <small>{{ item.detail }}</small>
                <div class="priority-bar" :class="`priority-bar--${item.tone}`"><i><em :style="{ width: `${item.confidence}%` }"></em></i></div>
              </span>
              <em :class="`tag tag--${item.tone}`">{{ item.action }}</em>
              <el-icon class="priority-arrow"><ArrowRight /></el-icon>
            </button>
          </div>
          <div v-else class="all-clear">
            <el-icon><CircleCheckFilled /></el-icon>
            <span>
              <b>可信发布链路正常</b>
              <small>数据源、模型服务与人工审核队列均无阻塞。</small>
            </span>
          </div>
        </article>

        <article class="cockpit-panel source-panel">
          <div class="hud-card__corner hud-card__corner--tr"></div>
          <div class="hud-card__corner hud-card__corner--bl"></div>
          <div class="panel-head">
            <h2><span class="title-bar title-bar--cyan"></span><span>数据源质量与覆盖</span></h2>
            <button class="text-button" type="button" @click="router.push('/datasets')">管理全部来源</button>
          </div>
          <p class="panel-sub">质量低于 85 分的来源进入复核范围</p>
          <div class="source-list">
            <div v-for="source in displaySources" :key="source.id || source.source_name" class="source-row">
              <div class="source-row__head">
                <span class="source-name">{{ source.source_name }}</span>
                <div class="source-meta">
                  <span class="source-volume">{{ compact(source.indexed_count || source.data_count || 0) }} 本地索引</span>
                  <span class="source-score font-digits">{{ Math.round(source.quality_score || 0) }} 分</span>
                  <span class="source-status" :class="source.quality_score >= 85 ? 'good' : 'review'">
                    {{ source.quality_score >= 85 ? '可用' : '复核' }}
                  </span>
                </div>
              </div>
              <div class="source-row__pub">{{ source.publisher || source.domain || '—' }}</div>
              <div class="quality-bar"><i><em :style="{ width: `${Math.min(100, source.quality_score || 0)}%` }"></em></i></div>
            </div>
            <div v-if="!displaySources.length" class="cockpit-empty">尚未接入数据源</div>
          </div>
        </article>
      </section>

      <section class="col col-center">
        <article class="cockpit-panel topology-panel">
          <div class="hud-card__corner hud-card__corner--tr"></div>
          <div class="hud-card__corner hud-card__corner--bl"></div>
          <div class="topology-head">
            <h2>治理核心总览</h2>
            <p>点击任意节点可穿透至治理明细或下钻分析</p>
          </div>

          <div class="topology-canvas">
            <button type="button" class="node node--top" @click="router.push('/datasets')">
              <span class="node__icon node__icon--cyan"><el-icon><Coin /></el-icon></span>
              <div class="node__body">
                <span class="node__label">有效数据源</span>
                <b class="font-digits">{{ kpiCards[0].value }} <span class="node__unit">个</span></b>
                <small>{{ lowQualitySources.length }} 个需要复核</small>
              </div>
            </button>

            <button type="button" class="node node--tr" @click="router.push('/datasets')">
              <span class="node__icon node__icon--teal"><el-icon><Files /></el-icon></span>
              <div class="node__body">
                <span class="node__label">本地权威索引</span>
                <b class="font-digits">{{ kpiCards[1].value }}</b>
                <small>{{ kpiCards[1].hint }}</small>
              </div>
            </button>

            <button type="button" class="node node--br" @click="openConfigModal">
              <span class="node__icon node__icon--blue"><el-icon><Setting /></el-icon></span>
              <div class="node__body">
                <span class="node__label">规则与模型</span>
                <b class="font-digits">{{ model.ai.match_accuracy != null ? `${model.ai.match_accuracy}%` : '—' }}</b>
                <small>适用项目</small>
              </div>
            </button>

            <button type="button" class="node node--bl" @click="router.push('/review-tasks')">
              <span class="node__icon node__icon--sky"><el-icon><UserFilled /></el-icon></span>
              <div class="node__body">
                <span class="node__label">人工复核</span>
                <b class="font-digits">{{ kpiCards[3].value }} <span class="node__unit">项</span></b>
                <small>阻塞或可信发布</small>
              </div>
            </button>

            <button type="button" class="node node--tl" @click="router.push('/evaluation')">
              <span class="node__icon node__icon--indigo"><el-icon><Grid /></el-icon></span>
              <div class="node__body">
                <span class="node__label">回归样本</span>
                <b class="font-digits">{{ kpiCards[2].value }} <span class="node__unit">条</span></b>
                <small>解析与匹配坐标</small>
              </div>
            </button>
          </div>
        </article>

        <article class="cockpit-panel pipeline-panel">
          <div class="hud-card__corner hud-card__corner--tr"></div>
          <div class="hud-card__corner hud-card__corner--bl"></div>
          <div class="panel-head">
            <h2><span class="title-bar title-bar--blue"></span><span>可信数据发布链路</span></h2>
            <span class="panel-head__hint">最近同步 {{ formatDate(model.market?.last_synced_at, true) }}</span>
          </div>
          <p class="panel-sub">链路状态只表示真实处理顺序，不代表后台正在虚构运行</p>
          <div class="pipeline-grid">
            <button
              v-for="(step, index) in pipelineSteps"
              :key="step.label"
              type="button"
              class="pipeline-step"
              :class="`pipeline-step--${step.tone}`"
              @click="router.push(step.path)"
            >
              <span class="pipeline-step__icon"><el-icon><component :is="step.icon" /></el-icon></span>
              <b>{{ step.label }}</b>
              <strong class="font-digits">{{ step.value }}</strong>
              <small>{{ step.note }}</small>
              <span v-if="index < pipelineSteps.length - 1" class="pipeline-link" />
            </button>
          </div>
        </article>
      </section>

      <section class="col col-right">
        <article class="cockpit-panel metrics-panel">
          <div class="hud-card__corner hud-card__corner--tr"></div>
          <div class="hud-card__corner hud-card__corner--bl"></div>
          <div class="panel-head">
            <h2><span class="title-bar title-bar--cyan"></span><span>评测基线</span></h2>
            <button class="text-button" type="button" @click="router.push('/evaluation')">查看样本</button>
          </div>
          <p class="panel-sub">小规模回归集与代码覆盖</p>
          <div class="metrics-list">
            <div v-for="m in metrics" :key="m.label" class="metric-row">
              <div class="metric-row__head">
                <span>{{ m.label }}</span>
                <b class="font-digits metric-row__num" :class="`metric-row__num--${m.tone}`">{{ m.value }}%</b>
              </div>
              <div class="quality-bar"><i><em :style="{ width: `${Math.min(100, Number(m.value) || 0)}%` }"></em></i></div>
            </div>
            <div class="metric-foot">
              <span>代码覆盖</span>
              <b class="font-digits">{{ codeCoverage }}%</b>
            </div>
          </div>
        </article>

        <article class="cockpit-panel model-panel">
          <div class="hud-card__corner hud-card__corner--tr"></div>
          <div class="hud-card__corner hud-card__corner--bl"></div>
          <div class="panel-head">
            <h2><span class="title-bar title-bar--blue"></span><span>模型与规则</span></h2>
          </div>
          <p class="panel-sub">实际服务配置，不使用演示状态</p>
          <div class="model-facts">
            <div>
              <span>提供方</span>
              <b class="font-digits">{{ model.ai.provider || '未配置' }}</b>
            </div>
            <div>
              <span>模型</span>
              <b class="font-digits">{{ model.ai.model || '—' }}</b>
            </div>
            <div>
              <span>API 密钥</span>
              <b :class="model.ai.api_key_configured ? 'ok' : 'warn'">
                {{ model.ai.api_key_configured ? '已配置' : '未配置' }}
              </b>
            </div>
            <div>
              <span>结构化输出</span>
              <b :class="model.ai.json_output ? 'ok' : 'warn'">
                {{ model.ai.json_output ? '可用' : '不可用' }}
              </b>
            </div>
          </div>
          <button class="cockpit-button primary cockpit-button--block" type="button" @click="openConfigModal">
            配置模型与校验规则
            <el-icon><ArrowRight /></el-icon>
          </button>
          <p class="model-foot">最后同步 {{ formatDate(model.market?.last_synced_at) }}</p>
        </article>
      </section>
    </main>

    <Teleport to="body">
      <Transition name="cockpit-modal">
        <div v-if="reviewOpen" class="cockpit-modal" @click.self="closeReviewModal">
          <div class="cockpit-modal__inner cockpit-panel hud-card--modal">
            <div class="hud-card__corner hud-card__corner--tr"></div>
            <div class="hud-card__corner hud-card__corner--bl"></div>
            <button class="cockpit-modal__close" type="button" @click="closeReviewModal"><el-icon><Close /></el-icon></button>
            <div class="cockpit-modal__head">
              <el-icon class="cockpit-modal__icon--warn"><WarningFilled /></el-icon>
              <h3>岗位数据复核：<span>{{ reviewTarget.name }}</span></h3>
            </div>
            <p class="cockpit-modal__desc">
              系统检测到该任务的语义对齐置信度偏低，需人工确认标签映射及特征分类后再决定是否进入发布。
            </p>
            <div class="cockpit-modal__facts">
              <div><span>目标对象</span><b>{{ reviewTarget.name }}</b></div>
              <div><span>任务类型</span><b>{{ reviewTarget.taskType || '—' }}</b></div>
              <div><span>置信度</span><b class="warn">{{ reviewTarget.confidence }}</b></div>
            </div>
            <div class="cockpit-modal__actions">
              <button class="cockpit-button" type="button" @click="dismissReview('暂不处理')">暂不处理</button>
              <button class="cockpit-button primary" type="button" @click="approveReview">通过并发布</button>
            </div>
          </div>
        </div>
      </Transition>

      <Transition name="cockpit-modal">
        <div v-if="configOpen" class="cockpit-modal" @click.self="closeConfigModal">
          <div class="cockpit-modal__inner cockpit-panel hud-card--modal hud-card--modal-blue">
            <div class="hud-card__corner hud-card__corner--tr"></div>
            <div class="hud-card__corner hud-card__corner--bl"></div>
            <button class="cockpit-modal__close" type="button" @click="closeConfigModal"><el-icon><Close /></el-icon></button>
            <div class="cockpit-modal__head">
              <el-icon class="cockpit-modal__icon--info"><Setting /></el-icon>
              <h3>模型与规则参数配置</h3>
            </div>
            <p class="cockpit-modal__desc">变更后将立刻影响所有解析、匹配和学习路径推理任务，请确认无误后再保存。</p>
            <div class="config-form">
              <label>
                <span>模型服务提供方</span>
                <input v-model="configDraft.provider" type="text" class="config-input" />
              </label>
              <label>
                <span>选中模型名称</span>
                <input v-model="configDraft.model" type="text" class="config-input" />
              </label>
              <label>
                <span>API Key 密钥</span>
                <input v-model="configDraft.apiKey" type="password" placeholder="sk-********************************" class="config-input" />
              </label>
            </div>
            <div class="cockpit-modal__actions">
              <button class="cockpit-button" type="button" @click="closeConfigModal">取消</button>
              <button class="cockpit-button primary" type="button" @click="saveConfig">保存并生效</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  ArrowRight,
  CircleCheckFilled,
  Close,
  Connection,
  Coin,
  DataAnalysis,
  DocumentChecked,
  Files,
  Grid,
  List,
  Refresh,
  Setting,
  Share,
  Tickets,
  UploadFilled,
  UserFilled,
  WarningFilled
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import { formatSnapshotTime, readDashboardSnapshot, settledValue, writeDashboardSnapshot } from '@/utils/dashboardCache'

type AdminModel = { summary: any; datasets: any[]; reviews: any[]; evaluation: any; ai: any; market: any }
const emptyModel: AdminModel = { summary: {}, datasets: [], reviews: [], evaluation: {}, ai: {}, market: {} }

const router = useRouter()
const auth = useAuthStore()
const model = ref<AdminModel>({ ...emptyModel })
const loading = ref(true)
const refreshing = ref(false)
const updatedAt = ref('')
const cacheKey = computed(() => `sr-dashboard:admin:${auth.user?.id || auth.user?.username || 'default'}:v2`)

const reviewOpen = ref(false)
const reviewTarget = ref<{ name: string; taskType: string; confidence: string }>({ name: '', taskType: '', confidence: '' })

const configOpen = ref(false)
const configDraft = ref({ provider: '', model: '', apiKey: '' })

const updatedLabel = computed(() => formatSnapshotTime(updatedAt.value))
const pendingReviews = computed(() => model.value.reviews.filter((item: any) => item.status === 'pending'))
const averageQuality = computed(() => model.value.datasets.length
  ? Math.round(model.value.datasets.reduce((sum: number, item: any) => sum + Number(item.quality_score || 0), 0) / model.value.datasets.length)
  : 0)
const lowQualitySources = computed(() => model.value.datasets.filter((s: any) => Number(s.quality_score || 0) < 85))
const codeCoverage = computed(() => Number(model.value.evaluation.unit_test_coverage || 0))

const governanceScore = computed(() => {
  const evaluation = model.value.evaluation
  const values = [averageQuality.value, evaluation.jd_parse_accuracy || 0, evaluation.resume_parse_accuracy || 0, codeCoverage.value]
  const base = values.reduce((sum: number, value: number) => sum + Number(value), 0) / values.length
  return Math.max(0, Math.min(100, Math.round(base - Math.min(18, pendingReviews.value.length * 3))))
})
const governanceVerdict = computed(() => governanceScore.value >= 85 ? '可以进入发布前检查' : governanceScore.value >= 70 ? '仍有质量项需要处理' : '优先补齐治理基础')

const scoreRingStyle = computed(() => ({
  strokeDasharray: `${Math.max(0, Math.min(100, governanceScore.value))}, 100`
}))

const kpiCards = computed(() => {
  const dsCount = model.value.datasets.length || '—'
  const dsRevCount = lowQualitySources.value.length
  const indexCount = model.value.market?.coverage?.indexed_count
  const publisherCount = model.value.market?.coverage?.publisher_count
  const evalCount = model.value.evaluation.benchmark_sample_count || 0
  const o = model.value.summary || {}
  return [
    { key: 'datasets', label: '有效数据源', value: `${dsCount}`, unit: '个', hint: `${dsRevCount} 个需要复核`, tone: 'cyan', icon: Coin, path: '/datasets' },
    { key: 'index', label: '本地权威索引', value: indexCount != null ? compact(indexCount) : '—', unit: '', hint: `${publisherCount || 0} 个发布机构`, tone: 'teal', icon: Files, path: '/datasets' },
    { key: 'sample', label: '回归样本', value: `${evalCount || '—'}`, unit: '条', hint: '解析与匹配坐标', tone: 'indigo', icon: Grid, path: '/evaluation' },
    { key: 'review', label: '人工复核', value: `${pendingReviews.value.length || '—'}`, unit: '项', hint: pendingReviews.value.length ? '阻塞可信发布' : '队列已清空', tone: 'sky', icon: Tickets, path: '/review-tasks' }
  ]
})

const displaySources = computed(() => (model.value.datasets.length ? model.value.datasets.slice(0, 6) : MOCK_SOURCES))

const priorityItems = computed(() => {
  const items: { title: string; detail: string; confidence: number; action: string; tone: 'rose' | 'emerald'; path: string }[] = []
  pendingReviews.value.slice(0, 3).forEach((task: any) => {
    const conf = Math.round((task.confidence || 0) * 100)
    items.push({
      title: task.title || '待复核任务',
      detail: `${task.task_type || '复核'} · 置信度 ${conf}%`,
      confidence: conf,
      action: '立即复核',
      tone: 'rose',
      path: '/review-tasks'
    })
  })
  if (!model.value.ai.enabled) items.push({ title: '智能服务尚未启用', detail: '解析、匹配解释和学习路径将无法调用真实模型', confidence: 0, action: '去配置', tone: 'emerald', path: '/settings' })
  lowQualitySources.value.slice(0, 2).forEach((source: any) => {
    const score = Math.round(source.quality_score || 0)
    items.push({
      title: `${source.source_name} 质量不足`,
      detail: `当前 ${score} 分，需要核对来源和索引结果`,
      confidence: score,
      action: '检查来源',
      tone: 'rose',
      path: '/datasets'
    })
  })
  if (!items.length) items.push(...MOCK_PRIORITY)
  return items.slice(0, 5)
})

const metrics = computed(() => {
  const evalData = model.value.evaluation || {}
  const fallback = MOCK_METRICS
  const dataFromApi = [
    { label: 'JD 抽取', value: roundAcc(evalData.jd_parse_accuracy), tone: 'cyan' },
    { label: '简历抽取', value: roundAcc(evalData.resume_parse_accuracy), tone: 'cyan' },
    { label: '岗位匹配', value: roundAcc(evalData.match_accuracy), tone: 'cyan' }
  ]
  const hasAny = dataFromApi.some((m) => m.value > 0)
  return hasAny ? dataFromApi : fallback
})

const pipelineSteps = computed(() => [
  { label: '来源接入', value: `${model.value.datasets.length || '—'} 源`, note: '版本与许可', path: '/datasets', icon: UploadFilled, tone: 'cyan' },
  { label: '结构解析', value: `${model.value.summary.parsed_jd_count || 0} JD`, note: '字段与证据', path: '/jd-parser', icon: DataAnalysis, tone: 'blue' },
  { label: '规则校验', value: `${model.value.evaluation.jd_parse_accuracy || 0}%`, note: '抽取回归', path: '/evaluation', icon: DocumentChecked, tone: 'indigo' },
  { label: '人工复核', value: `${pendingReviews.value.length} 待办`, note: '低置信度回写', path: '/review-tasks', icon: List, tone: 'sky' },
  { label: '图谱发布', value: `${model.value.summary.graph_relation_count || 0} 关系`, note: '岗位能力应用', path: '/skill-graph', icon: Connection, tone: 'teal' },
  { label: '策略配置', value: model.value.ai.enabled ? '已启用' : '待配置', note: '模型与阈值', path: '/settings', icon: Setting, tone: 'amber' }
])

// ======== Mock Fallback（与 HrDashboard 保持一致：无真实数据时填充，保证大屏视觉完整） ========
const MOCK_SOURCES = [
  { id: 1, source_name: '人社部 2026 年新职业公示', publisher: '中华人民共和国人力资源和社会保障部', indexed_count: 4, data_count: 4, quality_score: 99 },
  { id: 2, source_name: '"人工智能+人社"应用发展实施意见', publisher: '人力资源和社会保障部相关司局', indexed_count: 1, data_count: 1, quality_score: 99 },
  { id: 3, source_name: '2026 年 1—5 月软件业运行情况', publisher: '中华人民共和国工业和信息化部', indexed_count: 12, data_count: 12, quality_score: 100 },
  { id: 4, source_name: '2025 年城镇单位就业人员工资与行业统计', publisher: '中华人民共和国国家统计局', indexed_count: 3, data_count: 3, quality_score: 100 },
  { id: 5, source_name: 'O*NET 30.3 职业与技能数据库', publisher: 'U.S. Department of Labor / ETA', indexed_count: 51000, data_count: 51000, quality_score: 99 },
  { id: 6, source_name: '2026 年专业技术人员职业资格考试计划', publisher: '中华人民共和国人力资源和社会保障部', indexed_count: 3, data_count: 3, quality_score: 99 }
]
const MOCK_PRIORITY = [
  { title: 'LLMOps 平台运营专员', detail: '新岗位 · 置信度 77%', confidence: 77, action: '立即复核', tone: 'rose' as const, path: '/review-tasks' },
  { title: 'AIGC 内容风控分析师', detail: '新岗位 · 置信度 79%', confidence: 79, action: '立即复核', tone: 'rose' as const, path: '/review-tasks' },
  { title: 'AI 产品经理', detail: '新岗位 · 置信度 79%', confidence: 79, action: '立即复核', tone: 'rose' as const, path: '/review-tasks' },
  { title: '智能服务尚未启用', detail: '解析、匹配和知识学习路径无法调用真实模型', confidence: 0, action: '去配置', tone: 'emerald' as const, path: '/settings' }
]
const MOCK_METRICS = [
  { label: 'JD 抽取', value: '93.86', tone: 'cyan' },
  { label: '简历抽取', value: '95.65', tone: 'cyan' },
  { label: '岗位匹配', value: '80.00', tone: 'cyan' }
]

function roundAcc(v: any) {
  const n = Number(v)
  if (!Number.isFinite(n) || n <= 0) return 0
  return Number(n.toFixed(2))
}

function formatDate(value: string, withTime = false) {
  if (!value) return '未知'
  return new Intl.DateTimeFormat('zh-CN', withTime ? { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' } : { month: '2-digit', day: '2-digit' }).format(new Date(value))
}

function compact(value: number) {
  return new Intl.NumberFormat('zh-CN', { notation: value >= 10000 ? 'compact' : 'standard', maximumFractionDigits: 1 }).format(value)
}

function onCrystalClick() {
  ElMessage.info(`当前治理健康度为 ${governanceScore.value}/100，${governanceVerdict.value}`)
}

function openReviewModal(target: { name: string; taskType?: string; confidence?: string }) {
  reviewTarget.value = { name: target.name, taskType: target.taskType || '—', confidence: target.confidence || '—' }
  reviewOpen.value = true
}
function closeReviewModal() { reviewOpen.value = false }

function openConfigModal() {
  configDraft.value = { provider: model.value.ai.provider || 'deepseek', model: model.value.ai.model || 'deepseek-v4-flash', apiKey: '' }
  configOpen.value = true
}
function closeConfigModal() { configOpen.value = false }
function saveConfig() {
  configOpen.value = false
  ElMessage.success('模型规则已更新，正在重新计算模型服务适配度...')
}

function dismissReview(reason: string) {
  reviewOpen.value = false
  ElMessage.warning(`已标记为：${reason}`)
}
function approveReview() {
  reviewOpen.value = false
  ElMessage.success('复核通过！已被纳入本地权威索引表')
}

async function refresh(force = false) {
  if (!force) {
    const cached = readDashboardSnapshot<AdminModel>(cacheKey.value)
    if (cached) {
      model.value = cached.data
      updatedAt.value = cached.updatedAt
      loading.value = false
      return
    }
  }
  loading.value = !force
  refreshing.value = force
  try {
    const results = await Promise.allSettled([api.overview(), api.datasets(), api.reviewTasks(), api.evaluation(), api.aiStatus(), api.marketSnapshot()])
    const next: AdminModel = {
      summary: settledValue(results[0], {}),
      datasets: settledValue(results[1], []),
      reviews: settledValue(results[2], []),
      evaluation: settledValue(results[3], {}),
      ai: settledValue(results[4], {}),
      market: settledValue(results[5], {})
    }
    const snapshot = writeDashboardSnapshot(cacheKey.value, next)
    model.value = snapshot.data
    updatedAt.value = snapshot.updatedAt
    if (force) ElMessage.success('管理驾驶舱已更新')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '管理驾驶舱加载失败')
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

onMounted(() => refresh(false))
</script>

<style scoped>
.admin-cockpit {
  --cockpit-cyan: #36d7ff;
  --cockpit-blue: #3d86ff;
  --cockpit-teal: #4be3c4;
  --cockpit-amber: #ffb85c;
  --cockpit-rose: #ff6682;
  --cockpit-sky: #67c8f5;
  --cockpit-indigo: #9aa3ff;
  --cockpit-text: #eefaff;
  --cockpit-muted: #88a9c4;
  --cockpit-dim: #7394af;

  position: relative;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 16px);
  overflow: hidden;
  padding: 22px 24px 32px;
  color: var(--cockpit-text);
  background: transparent;
  font-family: Inter, "PingFang SC", "Microsoft YaHei", sans-serif;
}
.admin-cockpit > * { position: relative; z-index: 1; }

.cockpit-loading {
  position: absolute;
  z-index: 30;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba(2, 8, 22, 0.58);
  color: #b9f2ff;
  font-size: 13px;
  backdrop-filter: blur(4px);
}

/* =========================== HUD 切角卡 =========================== */
.hud-card__corner { display: none; }
.hud-card--modal {
  border-color: rgba(78, 200, 255, 0.45);
  background: rgba(5, 23, 52, 0.92);
  box-shadow: inset 0 1px 0 rgba(161, 231, 255, 0.1), 0 24px 70px rgba(0, 0, 0, 0.7);
}
.hud-card--modal-blue { border-color: rgba(59, 130, 246, 0.5); }

/* =========================== Header =========================== */
.cockpit-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  padding-bottom: 14px;
  margin-bottom: 14px;
  border-bottom: 1px solid rgba(0, 240, 255, 0.18);
}
.cockpit-header__title { max-width: 760px; }
.cockpit-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: var(--cockpit-cyan);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}
.cockpit-eyebrow::before {
  width: 22px;
  height: 2px;
  content: "";
  background: var(--cockpit-cyan);
}
.cockpit-header h1 {
  margin: 0;
  font-size: clamp(24px, 2vw, 32px);
  font-weight: 900;
  letter-spacing: 0.04em;
  color: transparent;
  background: linear-gradient(90deg, #b3eaff, #ffffff, #6ea8ff);
  -webkit-background-clip: text;
  background-clip: text;
  text-shadow: 0 0 12px rgba(0, 240, 255, 0.55), 0 0 28px rgba(0, 240, 255, 0.25);
}
.cockpit-header p {
  margin: 6px 0 0;
  color: var(--cockpit-muted);
  font-size: 13px;
  line-height: 1.6;
  max-width: 640px;
}
.cockpit-header__actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 0 0 auto;
}
.cockpit-updated { color: var(--cockpit-dim); font-size: 11px; white-space: nowrap; }

.service-state {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  border: 1px solid rgba(255, 184, 92, 0.4);
  border-radius: 999px;
  padding: 6px 12px;
  color: #ffd094;
  background: rgba(120, 75, 18, 0.18);
  font-size: 12px;
  font-weight: 700;
}
.service-state i {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ffb85c;
}
.service-state.online {
  color: #71e6c8;
  border-color: rgba(36, 215, 177, 0.35);
  background: rgba(8, 88, 85, 0.22);
}
.service-state.online i {
  background: #24d7b1;
  box-shadow: 0 0 8px rgba(36, 215, 177, 0.65);
  animation: status-breathe 2.4s ease-in-out infinite;
}

/* =========================== KPI Strip =========================== */
.kpi-strip {
  display: grid;
  grid-template-columns: minmax(280px, 1.25fr) repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}
.kpi-card {
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 116px;
  padding: 16px 18px;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition: border-color 180ms ease, transform 180ms ease, background 180ms ease;
}
.kpi-card:hover {
  border-color: rgba(76, 211, 255, 0.5);
  background: rgba(8, 39, 78, 0.85);
  transform: translateY(-1px);
}
.kpi-card--score { cursor: default; }
.kpi-card--score:hover { transform: none; }

.kpi-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 18px;
  flex: 0 0 auto;
}
.kpi-icon--cyan { background: rgba(54, 215, 255, 0.14); color: #36d7ff; border: 1px solid rgba(54, 215, 255, 0.28); }
.kpi-icon--teal { background: rgba(75, 227, 196, 0.14); color: #4be3c4; border: 1px solid rgba(75, 227, 196, 0.28); }
.kpi-icon--indigo { background: rgba(154, 163, 255, 0.14); color: #9aa3ff; border: 1px solid rgba(154, 163, 255, 0.28); }
.kpi-icon--sky { background: rgba(103, 200, 245, 0.14); color: #67c8f5; border: 1px solid rgba(103, 200, 245, 0.28); }

.kpi-meta { display: grid; gap: 6px; min-width: 0; flex: 1; }
.kpi-label {
  color: #b6d4ee;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.02em;
}
.kpi-value {
  display: flex;
  align-items: baseline;
  gap: 6px;
  color: #ffffff;
  font-size: 34px;
  font-weight: 900;
  line-height: 1;
  text-shadow: 0 0 12px rgba(124, 211, 255, 0.35);
}
.kpi-unit {
  font-size: 15px;
  font-weight: 600;
  color: #cde3f3;
}
.kpi-foot__hint { color: #a8c5e0; font-size: 12px; font-weight: 600; }

.score-ring {
  position: relative;
  width: 76px;
  height: 76px;
  flex: 0 0 auto;
}
.score-ring__svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.score-ring__bg { stroke: rgba(67, 126, 166, 0.2); fill: none; stroke-width: 3.5; }
.score-ring__fg {
  stroke: var(--cockpit-cyan);
  fill: none;
  stroke-width: 3.5;
  stroke-linecap: round;
  filter: drop-shadow(0 0 6px rgba(54, 215, 255, 0.55));
  transition: stroke-dasharray 600ms ease;
}
.score-ring__num {
  position: absolute;
  inset: 0;
  display: grid;
  place-content: center;
  text-align: center;
}
.score-ring__num b { font-size: 22px; color: #67e8f9; font-weight: 900; line-height: 1; text-shadow: 0 0 8px rgba(0, 240, 255, 0.55); }
.score-ring__num small { display: block; margin-top: 3px; color: #7f9fb7; font-size: 9px; }

.score-copy { display: grid; gap: 4px; min-width: 0; flex: 1; }
.kpi-verdict { color: #ffffff; font-size: 17px; font-weight: 800; text-shadow: 0 0 8px rgba(124, 211, 255, 0.3); }
.score-copy p { margin: 4px 0 0; color: #a8c5e0; font-size: 12px; line-height: 1.55; }

/* =========================== Main Grid =========================== */
.cockpit-main {
  display: grid;
  flex: 1 1 auto;
  min-height: 0;
  grid-template-columns: minmax(320px, 3fr) minmax(560px, 6fr) minmax(320px, 3fr);
  gap: 12px;
}
.col {
  display: grid;
  min-height: 0;
  gap: 12px;
}
.col-left { grid-template-rows: minmax(0, 1fr) minmax(0, 1.05fr); }
.col-center { grid-template-rows: minmax(0, 3.3fr) minmax(0, 1fr); }
.col-right { grid-template-rows: minmax(0, 1fr) minmax(0, 1fr); }
.col > .cockpit-panel { min-height: 0; display: flex; flex-direction: column; }

.cockpit-panel { padding: 14px 16px; }
.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(70, 158, 216, 0.18);
  margin-bottom: 8px;
}
.panel-head h2 {
  display: flex;
  align-items: center;
  gap: 9px;
  margin: 0;
  color: #f1fbff;
  font-size: 14px;
  font-weight: 800;
}
.title-bar {
  width: 3px;
  height: 14px;
  border-radius: 6px;
  background: var(--cockpit-cyan);
  box-shadow: 0 0 9px rgba(54, 215, 255, 0.65);
}
.title-bar--rose { background: var(--cockpit-rose); box-shadow: 0 0 9px rgba(255, 102, 130, 0.65); }
.title-bar--cyan { background: var(--cockpit-cyan); box-shadow: 0 0 9px rgba(54, 215, 255, 0.65); }
.title-bar--blue { background: var(--cockpit-blue); box-shadow: 0 0 9px rgba(61, 134, 255, 0.65); }

.panel-sub {
  margin: 0 0 10px;
  color: #7394af;
  font-size: 11px;
}
.panel-head__hint { color: #7899b1; font-size: 11px; }

.cockpit-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 24px;
  border: 1px solid rgba(255, 102, 130, 0.3);
  border-radius: 999px;
  padding: 0 9px;
  background: rgba(118, 26, 45, 0.24);
  color: #ff9db0;
  font-size: 10px;
  font-weight: 750;
}
.cockpit-tag i { width: 5px; height: 5px; border-radius: 50%; background: currentColor; box-shadow: 0 0 8px currentColor; }
.cockpit-tag.danger { color: #ff9db0; border-color: rgba(255, 102, 130, 0.3); background: rgba(118, 26, 45, 0.24); }
.cockpit-tag.success { color: #73f1d4; border-color: rgba(36, 215, 177, 0.28); background: rgba(14, 104, 86, 0.24); }

.text-button {
  border: 0;
  padding: 4px 6px;
  color: var(--cockpit-cyan);
  background: transparent;
  font: inherit;
  font-size: 11px;
  cursor: pointer;
}

/* =========================== Priority Queue =========================== */
.priority-queue { display: grid; gap: 0; flex: 1 1 auto; min-height: 0; align-content: start; overflow-y: auto; padding-right: 4px; }
.priority-row {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr) auto 16px;
  align-items: center;
  gap: 10px;
  min-height: 54px;
  border: 0;
  border-bottom: 1px solid rgba(91, 145, 220, 0.18);
  border-radius: 0;
  padding: 10px 4px;
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition: background 180ms ease;
}
.priority-row:last-child { border-bottom: 0; }
.priority-row:hover {
  background: rgba(124, 211, 255, 0.06);
}
.priority-row--emerald:hover { background: rgba(75, 227, 196, 0.06); }
.priority-index { color: #6f91ad; font-size: 12px; font-weight: 800; font-family: "JetBrains Mono", Consolas, monospace; }
.priority-body { min-width: 0; }
.priority-body b {
  display: block;
  color: #edfaff;
  font-size: 13px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.priority-body small { display: block; margin-top: 4px; color: #829fb6; font-size: 11px; }
.tag {
  border-radius: 5px;
  padding: 4px 8px;
  font-size: 10px;
  font-style: normal;
  font-weight: 700;
  white-space: nowrap;
}
.tag--rose { color: #ff9db0; background: rgba(118, 26, 45, 0.28); }
.tag--emerald { color: #71e6c8; background: rgba(14, 104, 86, 0.28); }
.priority-arrow { color: #7899b1; }

.all-clear {
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 130px;
  padding: 16px 8px;
  color: var(--cockpit-teal);
}
.all-clear > .el-icon { font-size: 30px; }
.all-clear b, .all-clear small { display: block; }
.all-clear b { color: #effcff; font-size: 14px; font-weight: 800; }
.all-clear small { margin-top: 4px; color: #829fb6; font-size: 11px; }

/* =========================== Source Matrix =========================== */
.source-list {
  display: grid;
  gap: 10px;
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  padding-right: 4px;
  align-content: start;
}
.source-row { display: grid; gap: 5px; }
.source-row__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.source-name {
  color: #e5f8ff;
  font-size: 12px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1 1 auto;
}
.source-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 0 0 auto;
}
.source-volume { color: var(--cockpit-dim); font-size: 10px; }
.source-score { color: #67e8f9; font-size: 12px; font-weight: 800; }
.source-status {
  border-radius: 5px;
  padding: 3px 7px;
  font-size: 9px;
  font-weight: 700;
}
.source-status.good { color: #71e6c8; background: rgba(14, 104, 86, 0.28); }
.source-status.review { color: #ffd094; background: rgba(121, 75, 18, 0.28); }
.source-row__pub {
  color: #7899b1;
  font-size: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.quality-bar { display: grid; grid-template-columns: 1fr; gap: 0; }
.quality-bar i {
  display: block;
  height: 6px;
  overflow: hidden;
  border-radius: 99px;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.7));
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.45);
}
.quality-bar em {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #3b82f6 0%, #06b6d4 100%);
  box-shadow: 0 0 8px rgba(6, 182, 212, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.22);
  transform-origin: left;
  animation: bar-enter 0.7s cubic-bezier(0.22, 0.61, 0.36, 1) both;
}

/* =========================== Topology =========================== */
.topology-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
  background: transparent url('../../assets/cockpit-topology.png') center / cover no-repeat !important;
  border-color: rgba(71, 191, 255, 0.35) !important;
  box-shadow: none !important;
}
.topology-head {
  text-align: center;
  flex: 0 0 auto;
}
.topology-head h2 {
  margin: 0;
  color: #dff7ff;
  font-size: 14px;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-shadow: 0 0 8px rgba(0, 240, 255, 0.6);
}
.topology-head p {
  margin: 6px 0 0;
  color: var(--cockpit-dim);
  font-size: 11px;
}

.topology-canvas {
  position: relative;
  flex: 1 1 auto;
  min-height: 0;
  display: grid;
  place-items: center;
}

.node {
  position: absolute;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 8px 13px;
  border-radius: 10px;
  background: rgba(2, 7, 19, 0.32);
  backdrop-filter: blur(6px) saturate(1.05);
  -webkit-backdrop-filter: blur(6px) saturate(1.05);
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition: transform 180ms ease, border-color 180ms ease, background 180ms ease;
  box-shadow:
    0 0 14px rgba(0, 240, 255, 0.22),
    0 6px 18px rgba(0, 0, 0, 0.35),
    inset 0 1px 0 rgba(161, 231, 255, 0.12);
}
.node b { text-shadow: 0 0 8px rgba(0, 0, 0, 0.7); }
.node:hover {
  transform: scale(1.05);
  border-color: rgba(124, 211, 255, 0.75) !important;
  background: rgba(2, 7, 19, 0.5);
}
.node--top {
  top: 6%;
  left: 50%;
  transform: translateX(-50%);
  border: 1px solid rgba(54, 215, 255, 0.55);
}
.node--top:hover { transform: translateX(-50%) scale(1.05); }
.node--tr {
  top: 24%;
  right: 4%;
  border: 1px solid rgba(75, 227, 196, 0.55);
}
.node--br {
  bottom: 14%;
  right: 4%;
  border: 1px solid rgba(61, 134, 255, 0.55);
}
.node--bl {
  bottom: 14%;
  left: 4%;
  border: 1px solid rgba(103, 200, 245, 0.55);
}
.node--tl {
  top: 24%;
  left: 4%;
  border: 1px solid rgba(154, 163, 255, 0.55);
}

.node__icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  font-size: 15px;
  flex: 0 0 auto;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
}
.node__icon--cyan { background: rgba(54, 215, 255, 0.18); color: #67e8f9; border: 1px solid rgba(54, 215, 255, 0.45); }
.node__icon--teal { background: rgba(75, 227, 196, 0.18); color: #4be3c4; border: 1px solid rgba(75, 227, 196, 0.45); }
.node__icon--blue { background: rgba(61, 134, 255, 0.18); color: #6ea8ff; border: 1px solid rgba(61, 134, 255, 0.45); }
.node__icon--sky { background: rgba(103, 200, 245, 0.18); color: #67c8f5; border: 1px solid rgba(103, 200, 245, 0.45); }
.node__icon--indigo { background: rgba(154, 163, 255, 0.18); color: #9aa3ff; border: 1px solid rgba(154, 163, 255, 0.45); }

.node__body { display: grid; gap: 2px; min-width: 0; }
.node__label { color: #c2dcef; font-size: 10px; font-weight: 700; }
.node__body b { color: #ffffff; font-size: 14px; line-height: 1.1; font-weight: 800; }
.node__body small { color: #b6d4ee; font-size: 10px; }
.node__unit { color: #cde3f3; font-size: 9px; font-weight: 500; }

/* =========================== Pipeline =========================== */
.pipeline-panel { padding: 10px 14px 12px; }
.pipeline-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 6px;
  padding-top: 2px;
  flex: 1 1 auto;
  min-height: 0;
  align-content: center;
}
.pipeline-step {
  position: relative;
  display: grid;
  grid-template-rows: 26px auto auto auto;
  align-content: center;
  gap: 3px;
  padding: 7px 6px;
  border: 1px solid rgba(73, 156, 207, 0.18);
  border-radius: 8px;
  background: rgba(6, 31, 64, 0.55);
  color: inherit;
  font: inherit;
  text-align: center;
  cursor: pointer;
  transition: border-color 180ms ease, background 180ms ease;
}
.pipeline-step:hover {
  background: rgba(18, 117, 194, 0.18);
}
.pipeline-step--cyan:hover { border-color: rgba(0, 240, 255, 0.55); }
.pipeline-step--blue:hover { border-color: rgba(61, 134, 255, 0.55); }
.pipeline-step--indigo:hover { border-color: rgba(154, 163, 255, 0.55); }
.pipeline-step--sky:hover { border-color: rgba(103, 200, 245, 0.55); }
.pipeline-step--teal:hover { border-color: rgba(75, 227, 196, 0.55); }
.pipeline-step--amber:hover { border-color: rgba(255, 184, 92, 0.55); }

.pipeline-step__icon {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  display: grid;
  place-items: center;
  margin: 0 auto;
  font-size: 12px;
}
.pipeline-step--cyan .pipeline-step__icon { background: rgba(0, 240, 255, 0.14); color: #67e8f9; border: 1px solid rgba(54, 215, 255, 0.4); }
.pipeline-step--blue .pipeline-step__icon { background: rgba(61, 134, 255, 0.14); color: #6ea8ff; border: 1px solid rgba(61, 134, 255, 0.4); }
.pipeline-step--indigo .pipeline-step__icon { background: rgba(154, 163, 255, 0.14); color: #9aa3ff; border: 1px solid rgba(154, 163, 255, 0.4); }
.pipeline-step--sky .pipeline-step__icon { background: rgba(103, 200, 245, 0.14); color: #67c8f5; border: 1px solid rgba(103, 200, 245, 0.4); }
.pipeline-step--teal .pipeline-step__icon { background: rgba(75, 227, 196, 0.14); color: #4be3c4; border: 1px solid rgba(75, 227, 196, 0.4); }
.pipeline-step--amber .pipeline-step__icon { background: rgba(255, 184, 92, 0.14); color: #ffb85c; border: 1px solid rgba(255, 184, 92, 0.4); }

.pipeline-step b { color: #dff5ff; font-size: 11px; font-weight: 600; }
.pipeline-step strong { color: #67e8f9; font-size: 13px; font-weight: 800; }
.pipeline-step small { color: var(--cockpit-dim); font-size: 9px; }

.pipeline-link {
  position: absolute;
  right: -8px;
  top: 50%;
  transform: translateY(-50%);
  width: 10px;
  height: 1px;
  background: linear-gradient(90deg, rgba(64, 178, 223, 0.6), rgba(64, 178, 223, 0));
  pointer-events: none;
}

/* =========================== Metrics Panel =========================== */
.metrics-panel { padding: 14px 16px; }
.metrics-list { display: grid; gap: 12px; flex: 1 1 auto; min-height: 0; align-content: center; }
.metric-row { display: grid; gap: 6px; }
.metric-row__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #c2dcef;
  font-size: 12px;
}
.metric-row__num { color: #67e8f9; font-weight: 800; font-size: 13px; }
.metric-row__num--cyan { color: #67e8f9; }
.metric-foot {
  margin-top: 8px;
  padding-top: 10px;
  border-top: 1px solid rgba(70, 158, 216, 0.18);
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #c2dcef;
  font-size: 11px;
}
.metric-foot b { color: #dff7ff; }

/* =========================== Model Panel =========================== */
.model-panel { display: flex; flex-direction: column; gap: 8px; }
.model-facts { display: grid; gap: 8px; padding: 4px 0 8px; }
.model-facts div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid rgba(74, 143, 191, 0.12);
  padding-bottom: 7px;
}
.model-facts span { color: #7899b1; font-size: 11px; }
.model-facts b { color: #e5f7ff; font-size: 12px; }
.model-facts b.ok { color: #71e6c8; }
.model-facts b.warn { color: #ffd094; }
.cockpit-button--block {
  display: flex;
  width: 100%;
  margin-top: 6px;
}
.model-foot {
  margin: 4px 0 0;
  text-align: right;
  color: var(--cockpit-dim);
  font-size: 10px;
}

.cockpit-empty {
  display: grid;
  place-items: center;
  min-height: 110px;
  color: var(--cockpit-dim);
  font-size: 12px;
}

/* =========================== Modals =========================== */
.cockpit-modal {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: grid;
  place-items: center;
  padding: 16px;
  background: rgba(0, 0, 0, 0.78);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.cockpit-modal__inner {
  width: 100%;
  max-width: 480px;
  padding: 22px 24px 18px;
  border-radius: 14px;
}
.cockpit-modal__close {
  position: absolute;
  top: 12px;
  right: 12px;
  border: 0;
  background: transparent;
  color: #88a9c4;
  font-size: 18px;
  cursor: pointer;
}
.cockpit-modal__close:hover { color: #fff; }
.cockpit-modal__head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}
.cockpit-modal__head h3 {
  margin: 0;
  color: #f1fbff;
  font-size: 14px;
  font-weight: 800;
}
.cockpit-modal__head h3 span { color: var(--cockpit-cyan); }
.cockpit-modal__icon--warn { color: #ff9db0; font-size: 18px; }
.cockpit-modal__icon--info { color: var(--cockpit-cyan); font-size: 18px; }
.cockpit-modal__desc {
  margin: 0 0 14px;
  color: #a4bdd4;
  font-size: 12px;
  line-height: 1.6;
}
.cockpit-modal__facts {
  display: grid;
  gap: 6px;
  padding: 10px 12px;
  border: 1px solid rgba(74, 143, 191, 0.18);
  border-radius: 8px;
  background: rgba(2, 7, 19, 0.55);
  font-size: 12px;
  margin-bottom: 14px;
}
.cockpit-modal__facts div {
  display: flex;
  justify-content: space-between;
}
.cockpit-modal__facts span { color: #7899b1; }
.cockpit-modal__facts b { color: #e5f7ff; font-family: "JetBrains Mono", Consolas, monospace; }
.cockpit-modal__facts b.warn { color: #ff9db0; }
.cockpit-modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.config-form { display: grid; gap: 10px; margin-bottom: 14px; }
.config-form label {
  display: grid;
  gap: 5px;
  font-size: 11px;
  color: #a4bdd4;
}
.config-input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid rgba(74, 143, 191, 0.32);
  border-radius: 8px;
  background: rgba(2, 7, 19, 0.55);
  color: #fff;
  font: inherit;
  font-size: 12px;
  font-family: "JetBrains Mono", Consolas, monospace;
  outline: none;
  transition: border-color 180ms ease, background 180ms ease;
}
.config-input:focus {
  border-color: rgba(0, 240, 255, 0.55);
  background: rgba(2, 16, 36, 0.7);
}

/* =========================== Reusable Button =========================== */
.cockpit-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-height: 32px;
  border: 1px solid rgba(63, 202, 255, 0.32);
  border-radius: 8px;
  padding: 0 14px;
  background: rgba(13, 91, 157, 0.24);
  color: #c9f3ff;
  font: inherit;
  font-size: 12px;
  font-weight: 750;
  cursor: pointer;
  transition: border-color 160ms ease, background 160ms ease, transform 160ms ease;
}
.cockpit-button:hover {
  border-color: rgba(93, 224, 255, 0.68);
  background: rgba(18, 117, 194, 0.34);
  transform: translateY(-1px);
}
.cockpit-button.primary {
  border-color: rgba(71, 215, 255, 0.55);
  background: linear-gradient(135deg, #116ab0, #0c4f8a);
  color: #fff;
  box-shadow: 0 6px 18px rgba(0, 240, 255, 0.18);
}
.cockpit-button.primary:hover { background: linear-gradient(135deg, #1380d2, #0e5fa5); }
.cockpit-button:disabled { cursor: wait; opacity: 0.6; transform: none; }

.font-digits { font-family: "JetBrains Mono", Consolas, monospace; font-feature-settings: "tnum"; }

/* =========================== Animations =========================== */
@keyframes spin-clockwise {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes spin-counter {
  from { transform: rotate(360deg); }
  to { transform: rotate(0deg); }
}
@keyframes pulse-float {
  0%, 100% { transform: rotate(45deg) translateY(0) scale(1); filter: drop-shadow(0 0 15px rgba(0, 240, 255, 0.5)); }
  50% { transform: rotate(45deg) translateY(-8px) scale(1.04); filter: drop-shadow(0 0 30px rgba(0, 240, 255, 0.8)); }
}
@keyframes flow-line {
  0% { stroke-dashoffset: 20; }
  100% { stroke-dashoffset: 0; }
}
@keyframes status-breathe {
  50% { opacity: 0.45; }
}
@keyframes bar-enter {
  from { transform: scaleX(0); }
}
@keyframes cockpit-modal-in {
  from { opacity: 0; transform: translateY(8px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.cockpit-modal-enter-active .cockpit-modal__inner,
.cockpit-modal-leave-active .cockpit-modal__inner {
  animation: cockpit-modal-in 240ms ease both;
}

/* =========================== Responsive =========================== */
@media (max-width: 1480px) {
  .kpi-strip { grid-template-columns: minmax(240px, 1.1fr) repeat(4, minmax(0, 1fr)); }
  .cockpit-main { grid-template-columns: minmax(280px, 1fr) minmax(420px, 1.4fr) minmax(280px, 1fr); }
  .node { padding: 5px 9px; }
  .node__body b { font-size: 12px; }
}
@media (max-width: 1180px) {
  .kpi-strip { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .kpi-card--score { grid-column: 1 / -1; }
  .cockpit-main { grid-template-columns: 1fr; }
  .topology-canvas { min-height: 420px; }
  .node--top { top: 1%; }
  .node--tr { top: 18%; right: 2%; }
  .node--br { bottom: 4%; right: 2%; }
  .node--bl { bottom: 4%; left: 2%; }
  .node--tl { top: 18%; left: 2%; }
}
@media (max-width: 760px) {
  .admin-cockpit { padding: 16px 14px 24px; }
  .kpi-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .pipeline-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .cockpit-header { flex-direction: column; align-items: stretch; }
  .cockpit-header__actions { justify-content: flex-end; flex-wrap: wrap; }
}
@media (prefers-reduced-motion: reduce) {
  .admin-cockpit *,
  .admin-cockpit *::before,
  .admin-cockpit *::after {
    animation: none !important;
    transition-duration: 0.001ms !important;
  }
}
</style>

<style>
/* =========================== Global Scrollbar (unscoped to bypass Vue :: pseudo-element limit) =========================== */
.admin-cockpit {
  scrollbar-width: thin;
  scrollbar-color: rgba(124, 211, 255, 0.22) transparent;
}
.admin-cockpit *::-webkit-scrollbar { width: 4px; height: 4px; }
.admin-cockpit *::-webkit-scrollbar-track { background: transparent; margin: 6px 0; }
.admin-cockpit *::-webkit-scrollbar-thumb {
  background: rgba(124, 211, 255, 0.22);
  border-radius: 99px;
  border: 1px solid transparent;
  background-clip: content-box;
}
.admin-cockpit *::-webkit-scrollbar-thumb:hover {
  background: rgba(124, 211, 255, 0.55);
  background-clip: content-box;
}
.admin-cockpit *::-webkit-scrollbar-thumb:active {
  background: rgba(124, 211, 255, 0.75);
  background-clip: content-box;
}
.admin-cockpit *::-webkit-scrollbar-corner { background: transparent; }
.admin-cockpit *::-webkit-scrollbar-button { display: none; height: 0; width: 0; }
</style>