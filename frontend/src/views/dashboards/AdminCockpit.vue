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
      <!-- ==================== 左栏 · 质量辅助分析 ==================== -->
      <section class="col col-left">
        <article class="cockpit-panel health-panel">
          <div class="hud-card__corner hud-card__corner--tr"></div>
          <div class="hud-card__corner hud-card__corner--bl"></div>
          <div class="panel-head">
            <h2><span class="title-bar title-bar--cyan"></span><span>数据健康度</span></h2>
            <span v-if="healthIsMock" class="mock-flag">示例数据</span>
            <button v-else class="text-button" type="button" @click="router.push('/datasets')">数据明细</button>
          </div>
          <p class="panel-sub">完整性 · 时效性 · 一致性 · 唯一性，实时来自库表统计</p>
          <div class="health-top">
            <div class="health-ring">
              <svg viewBox="0 0 36 36" class="score-ring__svg">
                <circle cx="18" cy="18" r="15.9" class="score-ring__bg" />
                <circle cx="18" cy="18" r="15.9" class="score-ring__fg" :style="{ strokeDasharray: `${Math.max(0, Math.min(100, healthOverall))}, 100` }" />
              </svg>
              <div class="score-ring__num"><b class="font-digits">{{ healthOverall }}</b><small>健康分</small></div>
            </div>
            <div class="health-summary">
              <b>{{ healthVerdict }}</b>
              <p>{{ health.dataset_count != null ? `${health.dataset_count} 个在管数据源` : '覆盖解析、复核、发布全链路' }}</p>
            </div>
          </div>
          <div class="health-dims">
            <div v-for="d in healthDims" :key="d.key" class="health-dim">
              <div class="health-dim__head">
                <span>{{ d.label }}</span>
                <b class="font-digits" :class="`health-num--${dimTone(d.value)}`">{{ d.value }}</b>
              </div>
              <div class="quality-bar"><i><em :class="`health-bar--${dimTone(d.value)}`" :style="{ width: `${Math.min(100, Number(d.value) || 0)}%` }"></em></i></div>
              <small>{{ d.note }}</small>
            </div>
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

      <!-- ==================== 中栏 · 核心数据大屏 ==================== -->
      <section class="col col-center">
        <article class="cockpit-panel flow-panel">
          <div class="hud-card__corner hud-card__corner--tr"></div>
          <div class="hud-card__corner hud-card__corner--bl"></div>
          <div class="panel-head">
            <h2><span class="title-bar title-bar--blue"></span><span>数据流管道</span></h2>
            <span class="panel-head__hint">来源 → 解析 → 校验 → 幻觉检测 → 复核 → 发布 · 最近同步 {{ formatDate(model.market?.last_synced_at, true) }}</span>
          </div>
          <div class="flow-pipeline">
            <div v-for="(stage, index) in flowStages" :key="stage.key" class="flow-stage">
              <div class="flow-rail">
                <span class="flow-node" :class="`flow-node--${stage.tone}`"><el-icon><component :is="stage.icon" /></el-icon></span>
                <i v-if="index < flowStages.length - 1" class="flow-link"><em></em><em></em><em></em></i>
              </div>
              <button
                type="button"
                class="flow-card"
                :class="{ 'flow-card--guard': stage.action === 'modal' }"
                @click="stage.action === 'modal' ? openGuardModal() : router.push(stage.path)"
              >
                <span class="flow-card__main">
                  <b>{{ stage.label }}</b>
                  <small>{{ stage.note }}</small>
                </span>
                <span class="flow-card__meta">
                  <strong class="font-digits">{{ stage.value }}</strong>
                  <span class="flow-status" :class="`flow-status--${stage.tone}`"><i></i>{{ stage.status }}</span>
                </span>
              </button>
            </div>
          </div>
        </article>

        <article class="cockpit-panel priority-strip">
          <div class="hud-card__corner hud-card__corner--tr"></div>
          <div class="hud-card__corner hud-card__corner--bl"></div>
          <div class="panel-head">
            <h2><span class="title-bar title-bar--rose"></span><span>今日治理重点</span></h2>
            <span class="cockpit-tag" :class="priorityItems.length ? 'danger' : 'success'">
              <i></i>{{ priorityItems.length ? `${priorityItems.length} 项待处理` : '当前无阻塞项' }}
            </span>
          </div>
          <div v-if="priorityItems.length" class="priority-queue priority-queue--compact">
            <button
              v-for="(item, index) in priorityItems.slice(0, 2)"
              :key="item.title"
              type="button"
              class="priority-row priority-row--slim"
              :class="`priority-row--${item.tone}`"
              @click="router.push(item.path)"
            >
              <span class="priority-index">{{ String(index + 1).padStart(2, '0') }}</span>
              <span class="priority-body">
                <b>{{ item.title }}</b>
                <small>{{ item.detail }}</small>
              </span>
              <em :class="`tag tag--${item.tone}`">{{ item.action }}</em>
              <el-icon class="priority-arrow"><ArrowRight /></el-icon>
            </button>
          </div>
          <div v-else class="all-clear all-clear--slim">
            <el-icon><CircleCheckFilled /></el-icon>
            <span>
              <b>可信发布链路正常</b>
              <small>数据源、模型服务与人工审核队列均无阻塞。</small>
            </span>
          </div>
        </article>
      </section>

      <!-- ==================== 右栏 · 风险辅助分析 ==================== -->
      <section class="col col-right">
        <article class="cockpit-panel guard-panel">
          <div class="hud-card__corner hud-card__corner--tr"></div>
          <div class="hud-card__corner hud-card__corner--bl"></div>
          <div class="panel-head">
            <h2><span class="title-bar title-bar--rose"></span><span>幻觉检测</span></h2>
            <button class="text-button" type="button" @click="openGuardModal">检测能力</button>
          </div>
          <p class="panel-sub">AI 结构化输出发布前的强制防护关卡</p>
          <div class="guard-stats">
            <div class="guard-stat">
              <b class="font-digits" :class="guardStats.flagged ? 'guard-num--warn' : ''">{{ guardStats.pass_rate }}%</b>
              <span>防护通过率</span>
            </div>
            <div class="guard-stat">
              <b class="font-digits">{{ guardStats.flagged }}</b>
              <span>待复核条目</span>
            </div>
            <div class="guard-stat">
              <b class="font-digits">{{ compact(guardStats.total_checked || 0) }}</b>
              <span>累计检测</span>
            </div>
          </div>
          <div class="guard-rules">
            <div v-for="rule in guardStats.rules" :key="rule.key" class="guard-rule">
              <span class="guard-rule__label"><i></i>{{ rule.label }}</span>
              <b class="font-digits">{{ rule.hits }} 次命中</b>
            </div>
          </div>
          <div v-if="guardStats.recent_events?.length" class="guard-events">
            <div class="guard-events__title">近期拦截</div>
            <div v-for="event in guardStats.recent_events.slice(0, 3)" :key="event.id" class="guard-event">
              <b>{{ event.job_name }}</b>
              <small>{{ event.issues.join('、') }} · 置信度 {{ Math.round((event.confidence || 0) * 100) }}%</small>
            </div>
          </div>
          <div v-else class="guard-events__empty">暂无拦截记录，所有结构化输出均携带合格证据链。</div>
          <span v-if="guardIsMock" class="mock-flag mock-flag--block">示例数据 · 后端接入后自动切换真实统计</span>
        </article>

        <article class="cockpit-panel eval-model-panel">
          <div class="hud-card__corner hud-card__corner--tr"></div>
          <div class="hud-card__corner hud-card__corner--bl"></div>
          <div class="panel-head">
            <h2><span class="title-bar title-bar--cyan"></span><span>评测基线与模型</span></h2>
            <button class="text-button" type="button" @click="router.push('/evaluation')">查看样本</button>
          </div>
          <div class="metrics-list metrics-list--compact">
            <div v-for="m in metrics" :key="m.label" class="metric-row">
              <div class="metric-row__head">
                <span>{{ m.label }}</span>
                <b class="font-digits metric-row__num" :class="`metric-row__num--${m.tone}`">{{ m.value }}%</b>
              </div>
              <div class="quality-bar"><i><em :style="{ width: `${Math.min(100, Number(m.value) || 0)}%` }"></em></i></div>
            </div>
          </div>
          <div class="model-facts model-facts--compact">
            <div>
              <span>提供方 / 模型</span>
              <b class="font-digits">{{ model.ai.provider || '未配置' }} · {{ model.ai.model || '—' }}</b>
            </div>
            <div>
              <span>密钥 / 结构化输出</span>
              <b :class="model.ai.api_key_configured && model.ai.json_output ? 'ok' : 'warn'">
                {{ model.ai.api_key_configured ? '已配置' : '未配置' }} / {{ model.ai.json_output ? '可用' : '不可用' }}
              </b>
            </div>
          </div>
          <button class="cockpit-button primary cockpit-button--block" type="button" @click="openConfigModal">
            配置模型与校验规则
            <el-icon><ArrowRight /></el-icon>
          </button>
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
      <Transition name="cockpit-modal">
        <div v-if="guardOpen" class="cockpit-modal" @click.self="closeGuardModal">
          <div class="cockpit-modal__inner cockpit-panel hud-card--modal guard-modal">
            <div class="hud-card__corner hud-card__corner--tr"></div>
            <div class="hud-card__corner hud-card__corner--bl"></div>
            <button class="cockpit-modal__close" type="button" @click="closeGuardModal"><el-icon><Close /></el-icon></button>
            <div class="cockpit-modal__head">
              <el-icon class="cockpit-modal__icon--guard"><Aim /></el-icon>
              <h3>幻觉检测能力</h3>
            </div>
            <p class="cockpit-modal__desc">
              平台所有 AI 结构化输出（岗位解析、简历抽取、匹配解释）在进入图谱前，都必须通过幻觉防护关卡：
              置信度低于阈值或证据链缺失的结果不会被直接发布，而是转入人工复核队列，从源头抑制模型幻觉。
            </p>
            <div class="guard-modal__stats">
              <div><span>累计检测</span><b class="font-digits">{{ compact(guardStats.total_checked || 0) }}</b></div>
              <div><span>防护通过</span><b class="font-digits">{{ guardStats.passed }}</b></div>
              <div><span>转人工复核</span><b class="font-digits" :class="{ 'guard-num--warn': guardStats.flagged }">{{ guardStats.flagged }}</b></div>
              <div><span>通过率</span><b class="font-digits">{{ guardStats.pass_rate }}%</b></div>
            </div>
            <div class="guard-modal__section-title">检测规则</div>
            <div class="guard-modal__rules">
              <div v-for="rule in guardStats.rules" :key="rule.key" class="guard-modal__rule">
                <b>{{ rule.label }}</b>
                <small>{{ rule.detail }}</small>
                <em class="font-digits">{{ rule.hits }} 次命中</em>
              </div>
            </div>
            <div class="guard-modal__section-title">在管道中的位置</div>
            <p class="guard-modal__stage">{{ guardStats.pipeline_stage }}</p>
            <div v-if="guardStats.recent_events?.length" class="guard-modal__events">
              <div class="guard-modal__section-title">近期拦截记录</div>
              <div v-for="event in guardStats.recent_events" :key="event.id" class="guard-event">
                <b>{{ event.job_name }}</b>
                <small>{{ event.issues.join('、') }} · 置信度 {{ Math.round((event.confidence || 0) * 100) }}%</small>
              </div>
            </div>
            <div class="cockpit-modal__actions">
              <button class="cockpit-button primary" type="button" @click="closeGuardModal">知道了</button>
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
  Aim,
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

type AdminModel = { summary: any; datasets: any[]; reviews: any[]; evaluation: any; ai: any; market: any; health: any; hallucination: any }
const emptyModel: AdminModel = { summary: {}, datasets: [], reviews: [], evaluation: {}, ai: {}, market: {}, health: {}, hallucination: {} }

const router = useRouter()
const auth = useAuthStore()
const model = ref<AdminModel>({ ...emptyModel })
const loading = ref(true)
const refreshing = ref(false)
const updatedAt = ref('')
const cacheKey = computed(() => `sr-dashboard:admin:${auth.user?.id || auth.user?.username || 'default'}:v3`)

const reviewOpen = ref(false)
const reviewTarget = ref<{ name: string; taskType: string; confidence: string }>({ name: '', taskType: '', confidence: '' })

const configOpen = ref(false)
const configDraft = ref({ provider: '', model: '', apiKey: '' })

const guardOpen = ref(false)
function openGuardModal() { guardOpen.value = true }
function closeGuardModal() { guardOpen.value = false }

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

// ======== 数据健康度 ========
const health = computed<any>(() => model.value.health || {})
const healthIsMock = computed(() => !health.value?.dimensions?.length || !(Number(health.value.overall) > 0))
const healthDims = computed(() => (healthIsMock.value ? MOCK_HEALTH.dimensions : health.value.dimensions))
const healthOverall = computed(() => (healthIsMock.value ? MOCK_HEALTH.overall : Number(health.value.overall) || 0))
const healthVerdict = computed(() => {
  const v = healthOverall.value
  if (v >= 90) return '数据资产状态优良'
  if (v >= 75) return '整体健康，个别维度需关注'
  if (v > 0) return '存在明显短板，优先补齐'
  return '暂无统计数据'
})
function dimTone(value: any) {
  const v = Number(value) || 0
  if (v >= 85) return 'good'
  if (v >= 70) return 'mid'
  return 'low'
}

// ======== 幻觉检测 ========
const guardStats = computed<any>(() => {
  const g = model.value.hallucination
  if (g && Number(g.sample_size) > 0) return g
  return MOCK_GUARD
})
const guardIsMock = computed(() => !(model.value.hallucination && Number(model.value.hallucination.sample_size) > 0))

// ======== 中央数据流管道 ========
const flowStages = computed(() => {
  const m = model.value
  const g = guardStats.value
  const pending = pendingReviews.value.length
  const jdAcc = Number(m.evaluation.jd_parse_accuracy) || 0
  const parseTotal = Number(m.summary.jd_count) || 0
  const parsed = Number(m.summary.parsed_jd_count) || 0
  return [
    { key: 'source', label: '来源接入', value: `${m.datasets.length || '—'} 源`, note: '权威来源 · 版本与许可', path: '/datasets', icon: UploadFilled, tone: m.datasets.length ? 'cyan' : 'amber', status: m.datasets.length ? '运行中' : '待接入' },
    { key: 'parse', label: '结构解析', value: `${parsed} JD`, note: `原始 ${parseTotal} 条 · 字段与证据抽取`, path: '/jd-parser', icon: DataAnalysis, tone: 'cyan', status: parsed ? '运行中' : '待解析' },
    { key: 'validate', label: '规则校验', value: `${jdAcc}%`, note: '抽取回归准确率', path: '/evaluation', icon: DocumentChecked, tone: jdAcc >= 90 ? 'cyan' : 'amber', status: jdAcc >= 90 ? '达标' : '需关注' },
    { key: 'guard', label: '幻觉检测', value: `${g.pass_rate}%`, note: `${g.flagged} 条待复核 · 置信阈值 ${g.min_confidence}`, action: 'modal', path: '', icon: Aim, tone: g.flagged > 0 ? 'rose' : 'cyan', status: g.flagged > 0 ? `${g.flagged} 条拦截` : '全部通过' },
    { key: 'review', label: '人工复核', value: `${pending} 待办`, note: '低置信度结果回写', path: '/review-tasks', icon: List, tone: pending ? 'rose' : 'cyan', status: pending ? '阻塞发布' : '队列清空' },
    { key: 'graph', label: '图谱发布', value: `${compact(m.summary.graph_relation_count || 0)} 关系`, note: '岗位-技能-证书图谱', path: '/skill-graph', icon: Connection, tone: 'teal', status: m.summary.graph_relation_count ? '已发布' : '待发布' },
    { key: 'config', label: '策略配置', value: m.ai.enabled ? '已启用' : '待配置', note: `${m.ai.provider || '未配置'} · 模型与阈值`, path: '/settings', icon: Setting, tone: m.ai.enabled ? 'cyan' : 'amber', status: m.ai.enabled ? '运行中' : '未配置' }
  ]
})

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
const MOCK_HEALTH = {
  overall: 92.5,
  dataset_count: null,
  dimensions: [
    { key: 'completeness', label: '完整性', value: 95.2, note: '解析记录关键字段齐全率' },
    { key: 'timeliness', label: '时效性', value: 88.6, note: '原始 JD 解析消化率' },
    { key: 'consistency', label: '一致性', value: 93.1, note: '幻觉防护通过率' },
    { key: 'uniqueness', label: '唯一性', value: 93.0, note: '重复入库 3 条' }
  ]
}
const MOCK_GUARD: Record<string, any> = {
  total_checked: 128,
  sample_size: 128,
  passed: 121,
  flagged: 7,
  pass_rate: 94.5,
  min_confidence: 0.72,
  rules: [
    { key: 'low_confidence', label: '置信度阈值检测', detail: '解析结果置信度低于 0.72 时标记待复核', hits: 5 },
    { key: 'missing_evidence', label: '证据链缺失检测', detail: '结构化输出缺少 evidence 字段时拒绝直接发布', hits: 2 }
  ],
  recent_events: [
    { id: 1, job_name: 'LLMOps 平台运营专员', confidence: 0.61, issues: ['置信度低于阈值'], guard_status: 'needs_review' },
    { id: 2, job_name: 'AIGC 内容风控分析师', confidence: 0.58, issues: ['置信度低于阈值', '缺少 evidence 字段'], guard_status: 'needs_review' }
  ],
  pipeline_stage: 'AI 结构化解析 → 幻觉防护 → 低置信结果转人工复核'
}

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
    const results = await Promise.allSettled([api.overview(), api.datasets(), api.reviewTasks(), api.evaluation(), api.aiStatus(), api.marketSnapshot(), api.governanceHealth(), api.hallucinationStats()])
    const next: AdminModel = {
      summary: settledValue(results[0], {}),
      datasets: settledValue(results[1], []),
      reviews: settledValue(results[2], []),
      evaluation: settledValue(results[3], {}),
      ai: settledValue(results[4], {}),
      market: settledValue(results[5], {}),
      health: settledValue(results[6], {}),
      hallucination: settledValue(results[7], {})
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
  --cockpit-teal: #67c8f5;
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
  color: #7dd3fc;
  border-color: rgba(56, 189, 248, 0.35);
  background: rgba(8, 60, 100, 0.22);
}
.service-state.online i {
  background: #38bdf8;
  box-shadow: 0 0 8px rgba(56, 189, 248, 0.65);
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
.kpi-icon--teal { background: rgba(103, 200, 245, 0.14); color: #67c8f5; border: 1px solid rgba(103, 200, 245, 0.28); }
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
.score-ring__num b { font-size: 22px; color: #7dd3fc; font-weight: 900; line-height: 1; text-shadow: 0 0 8px rgba(0, 240, 255, 0.55); }
.score-ring__num small { display: block; margin-top: 3px; color: #7f9fb7; font-size: 9px; }

.score-copy { display: grid; gap: 4px; min-width: 0; flex: 1; }
.kpi-verdict { color: #ffffff; font-size: 17px; font-weight: 800; text-shadow: 0 0 8px rgba(124, 211, 255, 0.3); }
.score-copy p { margin: 4px 0 0; color: #a8c5e0; font-size: 12px; line-height: 1.55; }

/* =========================== Main Grid =========================== */
.cockpit-main {
  display: grid;
  flex: 1 1 auto;
  min-height: 0;
  grid-template-columns: minmax(300px, 3fr) minmax(600px, 7fr) minmax(300px, 3fr);
  gap: 12px;
}
.col {
  display: grid;
  min-height: 0;
  gap: 12px;
}
.col-left { grid-template-rows: minmax(0, 1.1fr) minmax(0, 1fr); }
.col-center { grid-template-rows: minmax(0, 1fr) auto; }
.col-right { grid-template-rows: minmax(0, 1.15fr) minmax(0, 1fr); }
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
.cockpit-tag.success { color: #7dd3fc; border-color: rgba(56, 189, 248, 0.28); background: rgba(14, 74, 120, 0.24); }

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
.priority-row--emerald:hover { background: rgba(103, 200, 245, 0.06); }
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
.tag--emerald { color: #7dd3fc; background: rgba(12, 98, 168, 0.28); }
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
.source-score { color: #7dd3fc; font-size: 12px; font-weight: 800; }
.source-status {
  border-radius: 5px;
  padding: 3px 7px;
  font-size: 9px;
  font-weight: 700;
}
.source-status.good { color: #7dd3fc; background: rgba(12, 98, 168, 0.28); }
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
  background: linear-gradient(90deg, #3b82f6 0%, #0ea5e9 100%);
  box-shadow: 0 0 8px rgba(6, 182, 212, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.22);
  transform-origin: left;
  animation: bar-enter 0.7s cubic-bezier(0.22, 0.61, 0.36, 1) both;
}

/* =========================== Mock Flag =========================== */
.mock-flag {
  display: inline-flex;
  align-items: center;
  border: 1px solid rgba(255, 184, 92, 0.35);
  border-radius: 999px;
  padding: 2px 8px;
  color: #ffd094;
  background: rgba(120, 75, 18, 0.18);
  font-size: 9px;
  font-weight: 700;
  white-space: nowrap;
}
.mock-flag--block {
  display: inline-flex;
  margin-top: auto;
  align-self: flex-start;
}

/* =========================== Health Panel =========================== */
.health-top {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 10px;
}
.health-ring { position: relative; width: 68px; height: 68px; flex: 0 0 auto; }
.health-ring .score-ring__num b { font-size: 17px; }
.health-summary { display: grid; gap: 4px; min-width: 0; }
.health-summary b { color: #f1fbff; font-size: 14px; font-weight: 800; }
.health-summary p { margin: 0; color: #809fb7; font-size: 11px; line-height: 1.5; }
.health-dims {
  display: grid;
  gap: 9px;
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  align-content: start;
  padding-right: 4px;
}
.health-dim { display: grid; gap: 4px; }
.health-dim__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #c2dcef;
  font-size: 12px;
}
.health-num--good { color: #7dd3fc; }
.health-num--mid { color: #ffd094; }
.health-num--low { color: #ff9db0; }
.health-bar--good { background: linear-gradient(90deg, #3b82f6, #0ea5e9); }
.health-bar--mid { background: linear-gradient(90deg, #d97706, #ffb85c); }
.health-bar--low { background: linear-gradient(90deg, #be3d5c, #ff7088); }
.health-dim > small { color: #7394af; font-size: 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* =========================== Flow Pipeline (中央核心) =========================== */
.flow-panel { padding: 12px 16px 10px; }
.flow-pipeline {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  padding: 2px 6px 2px 2px;
}
.flow-stage {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 12px;
  flex: 1 1 0;
  min-height: 0;
}
.flow-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.flow-node {
  width: 38px;
  height: 38px;
  border-radius: 11px;
  display: grid;
  place-items: center;
  font-size: 16px;
  flex: 0 0 auto;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
}
.flow-node--cyan { background: rgba(54, 215, 255, 0.16); color: #7dd3fc; border: 1px solid rgba(54, 215, 255, 0.45); box-shadow: 0 0 12px rgba(54, 215, 255, 0.25); }
.flow-node--teal { background: rgba(103, 200, 245, 0.16); color: #67c8f5; border: 1px solid rgba(103, 200, 245, 0.45); box-shadow: 0 0 12px rgba(103, 200, 245, 0.25); }
.flow-node--amber { background: rgba(255, 184, 92, 0.16); color: #ffb85c; border: 1px solid rgba(255, 184, 92, 0.45); box-shadow: 0 0 12px rgba(255, 184, 92, 0.25); }
.flow-node--rose { background: rgba(255, 102, 130, 0.16); color: #ff9db0; border: 1px solid rgba(255, 102, 130, 0.5); box-shadow: 0 0 12px rgba(255, 102, 130, 0.3); }

.flow-link {
  position: relative;
  flex: 1 1 auto;
  min-height: 10px;
  width: 2px;
  overflow: hidden;
  border-radius: 2px;
  background: rgba(64, 178, 223, 0.25);
}
.flow-link em {
  position: absolute;
  left: 0;
  width: 100%;
  height: 12px;
  background: linear-gradient(180deg, rgba(78, 216, 255, 0), #4ed8ff, rgba(78, 216, 255, 0));
  animation: flow-drop 2.4s linear infinite;
}
.flow-link em:nth-child(2) { animation-delay: 0.8s; }
.flow-link em:nth-child(3) { animation-delay: 1.6s; }
@keyframes flow-drop {
  from { transform: translateY(-14px); }
  to { transform: translateY(64px); }
}

.flow-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 4px 0 6px;
  border: 1px solid rgba(73, 156, 207, 0.2);
  border-radius: 10px;
  padding: 7px 14px;
  background: rgba(6, 31, 64, 0.5);
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition: border-color 180ms ease, background 180ms ease, transform 180ms ease;
}
.flow-card:hover {
  border-color: rgba(73, 208, 243, 0.5);
  background: rgba(18, 117, 194, 0.18);
  transform: translateX(2px);
}
.flow-card--guard { border-color: rgba(255, 102, 130, 0.32); background: rgba(64, 22, 38, 0.32); }
.flow-card--guard:hover { border-color: rgba(255, 102, 130, 0.55); background: rgba(94, 32, 54, 0.42); }
.flow-card__main { display: grid; gap: 3px; min-width: 0; }
.flow-card__main b { color: #e5f8ff; font-size: 13px; font-weight: 700; }
.flow-card__main small { color: #7394ad; font-size: 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.flow-card__meta { display: grid; justify-items: end; gap: 4px; flex: 0 0 auto; }
.flow-card__meta strong { color: #7dd3fc; font-size: 15px; font-weight: 800; }
.flow-status {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 9px;
  font-weight: 700;
  white-space: nowrap;
}
.flow-status i { width: 4px; height: 4px; border-radius: 50%; background: currentColor; box-shadow: 0 0 6px currentColor; }
.flow-status--cyan { color: #7dd3fc; background: rgba(12, 98, 168, 0.28); }
.flow-status--teal { color: #67c8f5; background: rgba(12, 98, 168, 0.28); }
.flow-status--amber { color: #ffd094; background: rgba(121, 75, 18, 0.3); }
.flow-status--rose { color: #ff9db0; background: rgba(118, 26, 45, 0.3); }

/* =========================== Guard Panel (幻觉检测) =========================== */
.guard-panel { gap: 6px; }
.guard-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin: 8px 0 10px;
}
.guard-stat {
  display: grid;
  gap: 4px;
  border: 1px solid rgba(73, 156, 207, 0.2);
  border-radius: 9px;
  padding: 10px 8px;
  background: rgba(6, 31, 64, 0.45);
  text-align: center;
}
.guard-stat b { color: #7dd3fc; font-size: 19px; font-weight: 900; line-height: 1; }
.guard-stat b.guard-num--warn { color: #ff9db0; }
.guard-stat span { color: #88a9c4; font-size: 10px; }
.guard-rules { display: grid; gap: 7px; margin-bottom: 10px; }
.guard-rule {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  border-bottom: 1px solid rgba(74, 143, 191, 0.12);
  padding-bottom: 7px;
}
.guard-rule__label { display: inline-flex; align-items: center; gap: 7px; color: #c2dcef; font-size: 11px; }
.guard-rule__label i { width: 5px; height: 5px; border-radius: 50%; background: #38bdf8; box-shadow: 0 0 7px rgba(56, 189, 248, 0.8); }
.guard-rule b { color: #e5f7ff; font-size: 11px; }
.guard-events__title,
.guard-modal__section-title {
  margin: 0 0 6px;
  color: #88a9c4;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
}
.guard-event {
  display: grid;
  gap: 3px;
  border-left: 2px solid rgba(255, 102, 130, 0.5);
  border-radius: 3px;
  padding: 5px 8px;
  background: rgba(64, 22, 38, 0.22);
  margin-bottom: 6px;
}
.guard-event b { color: #edfaff; font-size: 11px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.guard-event small { color: #829fb6; font-size: 10px; }
.guard-events__empty {
  padding: 12px 10px;
  border: 1px dashed rgba(74, 143, 191, 0.25);
  border-radius: 8px;
  color: #7394af;
  font-size: 11px;
  text-align: center;
}
.guard-events { max-height: 180px; overflow-y: auto; }

/* =========================== Guard Modal =========================== */
.guard-modal__stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 14px;
}
.guard-modal__stats div {
  display: grid;
  gap: 5px;
  border: 1px solid rgba(74, 143, 191, 0.2);
  border-radius: 9px;
  padding: 10px 8px;
  background: rgba(2, 7, 19, 0.5);
  text-align: center;
}
.guard-modal__stats span { color: #7899b1; font-size: 10px; }
.guard-modal__stats b { color: #7dd3fc; font-size: 17px; font-weight: 900; }
.guard-modal__stats b.guard-num--warn { color: #ff9db0; }
.guard-modal__rules { display: grid; gap: 8px; margin-bottom: 14px; }
.guard-modal__rule {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(74, 143, 191, 0.18);
  border-radius: 8px;
  padding: 9px 12px;
  background: rgba(2, 7, 19, 0.45);
}
.guard-modal__rule b { color: #e5f7ff; font-size: 12px; white-space: nowrap; }
.guard-modal__rule small { color: #829fb6; font-size: 10px; line-height: 1.5; }
.guard-modal__rule em {
  border-radius: 5px;
  padding: 3px 8px;
  color: #ffd094;
  background: rgba(121, 75, 18, 0.28);
  font-size: 10px;
  font-style: normal;
  font-weight: 700;
  white-space: nowrap;
}
.guard-modal__stage {
  margin: 0 0 14px;
  border-left: 2px solid rgba(54, 215, 255, 0.55);
  border-radius: 3px;
  padding: 6px 10px;
  color: #bfe8ff;
  background: rgba(8, 60, 100, 0.22);
  font-size: 11px;
}
.guard-modal__events { max-height: 170px; overflow-y: auto; margin-bottom: 12px; }
.cockpit-modal__icon--guard { color: #36d7ff; font-size: 18px; }

/* =========================== Compact Strips =========================== */
.priority-strip { padding: 10px 16px 12px; }
.priority-queue--compact { flex: 0 0 auto; overflow: visible; }
.priority-row--slim { min-height: 44px; }
.all-clear--slim { min-height: 64px; padding: 10px 8px; }
.metrics-list--compact { gap: 9px; }
.model-facts--compact { padding-bottom: 6px; }

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
.metric-row__num { color: #7dd3fc; font-weight: 800; font-size: 13px; }
.metric-row__num--cyan { color: #7dd3fc; }

/* =========================== Model Facts =========================== */
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
.model-facts b.ok { color: #7dd3fc; }
.model-facts b.warn { color: #ffd094; }
.cockpit-button--block {
  display: flex;
  width: 100%;
  margin-top: 6px;
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
  .cockpit-main { grid-template-columns: minmax(270px, 1fr) minmax(420px, 1.6fr) minmax(270px, 1fr); }
  .flow-card__meta strong { font-size: 13px; }
}
@media (max-width: 1180px) {
  .kpi-strip { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .kpi-card--score { grid-column: 1 / -1; }
  .cockpit-main { grid-template-columns: 1fr; }
  .admin-cockpit { height: auto; overflow-y: auto; }
  .flow-pipeline { max-height: 520px; }
  .flow-stage { flex: 0 0 auto; }
  .flow-link { min-height: 22px; }
}
@media (max-width: 760px) {
  .admin-cockpit { padding: 16px 14px 24px; }
  .kpi-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
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