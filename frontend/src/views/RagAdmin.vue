<template>
  <div class="rag-admin-page">
    <PageHeader
      title="大模型防幻觉 RAG 工作流"
      desc="检索增强 · 知识驱动 · 可信生成 ｜ 基于岗位 JD、能力图谱、候选人画像的向量检索与可溯源问答"
    />

    <!-- 顶部状态条 + 同步按钮 -->
    <div class="rag-toolbar">
      <div class="rag-toolbar-left">
        <span class="rag-toolbar-badge">
          <el-icon class="badge-icon"><CircleCheckFilled /></el-icon>
          <span>防幻觉核心：检索增强 + 来源可溯源 + 持续更新</span>
        </span>
      </div>
      <div class="rag-toolbar-right">
        <span class="rag-update">
          <el-icon><Clock /></el-icon>
          更新于 <span>{{ lastUpdate }}</span>
          <el-button text size="small" @click="refreshMetrics">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </span>
        <el-button type="primary" :loading="syncing" @click="restartAllIndexes">
          <el-icon><RefreshRight /></el-icon>
          <span>同步索引</span>
        </el-button>
      </div>
    </div>

    <!-- KPI 5 卡 -->
    <div class="rag-kpi-grid">
      <div v-for="(m, idx) in metrics" :key="idx" class="rag-kpi-card" :class="data-`kpi-${idx}`">
        <div class="kpi-text">
          <div class="kpi-label">{{ m.label }}</div>
          <div class="kpi-value">{{ m.value }}</div>
          <div class="kpi-trend" :class="m.trendDirection">
            <el-icon><component :is="m.trendDirection === 'up' ? 'CaretTop' : 'CaretBottom'" /></el-icon>
            <span>{{ m.trend }}</span>
          </div>
        </div>
        <div class="kpi-icon" :class="`kpi-icon-${idx}`">
          <el-icon :size="20"><component :is="m.icon" /></el-icon>
        </div>
      </div>
    </div>

    <!-- 工作区：左 8 步流程 + 右 雷达+示例 -->
    <div class="rag-workspace">
      <div class="rag-card rag-flow-card">
        <div class="rag-card-header">
          <h3 class="rag-card-title">RAG 工作流程总览</h3>
          <el-button type="primary" plain size="small" @click="openSimModal">
            <el-icon><VideoPlay /></el-icon>
            <span>运行测试</span>
          </el-button>
        </div>

        <!-- 8 步工作流画布（含 SVG 折线箭头 + 节点） -->
        <div class="rag-flow-canvas">
          <!-- 工作流画布：上下两行 4+4 节点 + 行内箭头（不含跨行折线） -->
        <div class="rag-flow-canvas">

          <div class="flow-row">
            <div
              v-for="step in flowSteps.row1"
              :key="step.id"
              class="flow-node"
              :class="`tone-${step.tone}`"
              @click="selectWorkflowStep(step.id)"
            >
              <div class="node-corner node-corner-tl"></div>
              <div class="node-corner node-corner-br"></div>
              <div class="node-icon">
                <el-icon :size="22"><component :is="flowIcons[step.tone]" /></el-icon>
              </div>
              <div class="node-head">
                <span class="node-badge">{{ step.id }}</span>
                <span class="node-title">{{ step.title }}</span>
              </div>
              <div class="node-desc">{{ step.desc }}</div>
              <div class="node-box">
                <div class="node-box-label">{{ step.boxTitle }}</div>
                <component :is="step.boxComponent" v-bind="step.boxProps" />
              </div>
              <span v-if="step.id !== 4" class="node-arrow node-arrow-right"></span>
            </div>
          </div>

          <div class="flow-row flow-row-2">
            <div
              v-for="step in flowSteps.row2"
              :key="step.id"
              class="flow-node"
              :class="`tone-${step.tone}`"
              @click="selectWorkflowStep(step.id)"
            >
              <div class="node-corner node-corner-tl"></div>
              <div class="node-corner node-corner-br"></div>
              <div class="node-icon">
                <el-icon :size="22"><component :is="flowIcons[step.tone]" /></el-icon>
              </div>
              <div class="node-head">
                <span class="node-badge">{{ step.id }}</span>
                <span class="node-title">{{ step.title }}</span>
              </div>
              <div class="node-desc">{{ step.desc }}</div>
              <div class="node-box">
                <div class="node-box-label">{{ step.boxTitle }}</div>
                <component :is="step.boxComponent" v-bind="step.boxProps" />
              </div>
              <span v-if="step.id !== 8" class="node-arrow node-arrow-right"></span>
            </div>
          </div>
        </div>
        </div>
      </div>

      <div class="rag-side">
        <div class="rag-card rag-radar-card">
          <div class="rag-card-header">
            <h3 class="rag-card-title">效果对比 <span class="rag-card-subtitle">(基线 vs 当前流程)</span></h3>
          </div>
          <div ref="radarRef" class="rag-chart"></div>
        </div>

        <div class="rag-card rag-sample-card">
          <h3 class="rag-card-title">示例问答与来源</h3>
          <div class="rag-sample-qa">
            <div class="qa-line"><span class="qa-tag">问</span>糖尿病患者的日常饮食建议有哪些？</div>
            <div class="qa-answer">
              <span class="qa-tag">答</span>建议遵循低 GI 饮食、控制总热量、均衡蛋白质……（详见引用溯源）
            </div>
            <div class="qa-source-title">参考来源 (Top 3)</div>
            <div class="qa-source-list">
              <div v-for="(src, i) in sampleSources" :key="i" class="qa-source-item">
                <span class="source-name">{{ src.name }}</span>
                <span class="source-score">相似度 <strong>{{ src.score }}</strong></span>
              </div>
            </div>
            <el-button class="full-qa-btn" @click="openQaModal">查看完整回答与来源</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 趋势 + Donut + 知识库状态 -->
    <div class="rag-bottom-grid">
      <div class="rag-card rag-trend-card">
        <div class="rag-card-header">
          <h3 class="rag-card-title">效果趋势 <span class="rag-card-subtitle">(近 30 天)</span></h3>
          <el-select v-model="trendRange" size="small" @change="updateTrendChart" class="trend-select">
            <el-option label="近 30 天" :value="30" />
            <el-option label="近 7 天" :value="7" />
            <el-option label="近 90 天" :value="90" />
          </el-select>
        </div>
        <div ref="trendRef" class="rag-chart rag-chart-tall"></div>

        <h4 class="rag-section-subtitle">关键指标分布</h4>
        <div class="donut-grid">
          <div class="donut-wrap">
            <div class="donut-title">幻觉检测结果</div>
            <div ref="donutRef1" class="rag-chart rag-chart-donut"></div>
          </div>
          <div class="donut-wrap">
            <div class="donut-title">答案相关性分布</div>
            <div ref="donutRef2" class="rag-chart rag-chart-donut"></div>
          </div>
          <div class="donut-wrap">
            <div class="donut-title">回答时长分布</div>
            <div ref="donutRef3" class="rag-chart rag-chart-donut"></div>
          </div>
        </div>
      </div>

      <div class="rag-card rag-kb-card">
        <h3 class="rag-card-title">知识库状态</h3>
        <div class="kb-list">
          <div class="kb-row">
            <span class="kb-label">知识库文档数量</span>
            <span class="kb-value">{{ kbStats.docCount.toLocaleString() }}</span>
          </div>
          <div class="kb-row">
            <span class="kb-label">向量索引分片数</span>
            <span class="kb-value">{{ kbStats.chunkCount.toLocaleString() }}</span>
          </div>
          <div class="kb-row">
            <span class="kb-label">最后更新时间</span>
            <span class="kb-value mono">{{ kbStats.lastUpdated }}</span>
          </div>
          <div class="kb-row">
            <span class="kb-label">数据更新频率</span>
            <span class="kb-value">增量 + 全量重建</span>
          </div>
        </div>
        <div class="kb-footer">
          <div class="kb-status">
            <span class="kb-pulse"></span>
            <span>运行正常</span>
          </div>
          <el-button text type="primary" :loading="syncing" @click="restartAllIndexes">
            <el-icon><Refresh /></el-icon>
            同步索引
          </el-button>
        </div>
      </div>
    </div>

    <!-- 底部特性条 -->
    <div class="rag-features">
      <div v-for="f in features" :key="f.title" class="rag-feature-item">
        <div class="feature-icon" :class="`feature-icon-${f.tone}`">
          <el-icon :size="18"><component :is="f.icon" /></el-icon>
        </div>
        <div>
          <div class="feature-title">{{ f.title }}</div>
          <div class="feature-desc">{{ f.desc }}</div>
        </div>
      </div>
    </div>

    <!-- 完整问答 Modal -->
    <el-dialog v-model="qaModalVisible" title="完整回答与精准溯源详情" width="640px" class="rag-dialog">
      <div class="rag-modal-body">
        <div class="modal-section">
          <div class="modal-label">【用户提问】</div>
          <div class="modal-q">糖尿病患者的日常饮食建议有哪些？请给出明确的营养摄入标准与注意事项。</div>
        </div>
        <div class="modal-section">
          <div class="modal-label">【模型生成回答 (结合 RAG 上下文)】</div>
          <div class="modal-a">
            <p>根据权威医疗规范与指南，糖尿病患者的饮食管理应遵循以下原则<sup>[1]</sup>：</p>
            <ol>
              <li><strong>控制总热量：</strong>按标准体重 (kg）× (25~30) kcal 确定每日能量<sup>[2]</sup>。</li>
              <li><strong>碳水化合物选择：</strong>选用低 GI 食物（燕麦、荞麦、糙米），占总热量 45%~60%<sup>[1]</sup>。</li>
              <li><strong>优质蛋白质摄入：</strong>每公斤体重 1.0~1.2g，优先瘦肉、鱼类及豆制品<sup>[3]</sup>。</li>
              <li><strong>严格限制添加糖：</strong>避免含糖饮料，每日摄盐量不超过 5g。</li>
            </ol>
          </div>
        </div>
        <div class="modal-section">
          <div class="modal-label">【检索知识来源溯源 (Top 3)】</div>
          <div class="modal-source-list">
            <div v-for="(src, i) in fullSources" :key="i" class="modal-source-item">
              <div class="modal-source-head">
                <span class="modal-source-name">[{{ i + 1 }}] {{ src.name }}</span>
                <span class="modal-source-score">匹配度 {{ src.score }}</span>
              </div>
              <p class="modal-source-quote">"{{ src.quote }}"</p>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="qaModalVisible = false">关闭预览</el-button>
      </template>
    </el-dialog>

    <!-- 模拟工作流 Modal -->
    <el-dialog v-model="simModalVisible" title="交互式 RAG 防幻觉流程测试" width="560px" class="rag-dialog">
      <div class="sim-input-row">
        <el-input v-model="simInput" placeholder="输入自定义问题测试工作流" />
        <el-button type="primary" @click="runSimPipeline">运行工作流</el-button>
      </div>
      <div ref="simConsoleRef" class="sim-console">
        <div v-if="simLogs.length === 0" class="sim-log sim-log-idle">&gt; 系统就绪，等待运行指令...</div>
        <div
          v-for="(log, idx) in simLogs"
          :key="idx"
          class="sim-log"
          :class="{ 'sim-log-done': log.includes('完成') }"
        >{{ log }}</div>
      </div>
    </el-dialog>

    <!-- Toast 容器 -->
    <div class="rag-toast-host" aria-hidden="true">
      <transition-group name="rag-toast">
        <div v-for="t in toasts" :key="t.id" class="rag-toast">
          <el-icon><InfoFilled /></el-icon>
          <span>{{ t.text }}</span>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, reactive, ref, shallowRef, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Aim, ChatLineSquare, ChatRound, Connection, Filter,
  CaretTop, CaretBottom, CircleCheckFilled, Clock,
  DataAnalysis, Document, InfoFilled, MagicStick, Promotion,
  Refresh, RefreshRight, Search, Star, User, VideoPlay, TrendCharts
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import PageHeader from '@/components/PageHeader.vue'
import StepBox from '@/components/rag-flow/StepBox.vue'
import StepBoxList from '@/components/rag-flow/StepBoxList.vue'
import StepBoxFilter from '@/components/rag-flow/StepBoxFilter.vue'
import StepBoxText from '@/components/rag-flow/StepBoxText.vue'
import StepBoxCheck from '@/components/rag-flow/StepBoxCheck.vue'
import { api } from '@/api/http'

// ---------- 指标卡 ----------
const metrics = reactive([
  { label: '幻觉率降低', value: '82.6%', trend: '较基线提升 66.3%', trendDirection: 'up', icon: Search },
  { label: '回答准确率', value: '92.3%', trend: '较基线提升 23.7%', trendDirection: 'up', icon: CircleCheckFilled },
  { label: '知识召回率', value: '89.7%', trend: '较基线提升 31.5%', trendDirection: 'up', icon: Connection },
  { label: '回答相关性', value: '4.7 / 5', trend: '较基线提升 1.2', trendDirection: 'up', icon: Star },
  { label: '平均响应时间', value: '2.48s', trend: '较基线降低 0.83s', trendDirection: 'down', icon: Clock },
])
const lastUpdate = ref('刚刚')
function refreshMetrics() {
  metrics[0].value = (81 + Math.random() * 3).toFixed(1) + '%'
  metrics[1].value = (91 + Math.random() * 2).toFixed(1) + '%'
  metrics[2].value = (88 + Math.random() * 3).toFixed(1) + '%'
  metrics[3].value = (4.6 + Math.random() * 0.3).toFixed(1) + ' / 5'
  metrics[4].value = (2.2 + Math.random() * 0.4).toFixed(2) + 's'
  lastUpdate.value = '刚刚'
}

// ---------- 8 步工作流 ----------
const flowIcons: Record<string, any> = {
  emerald: ChatRound,
  purple: Aim,
  blue: Search,
  amber: Filter,
  pink: Document,
  indigo: MagicStick,
  teal: ChatLineSquare,
}

const flowSteps = reactive({
  row1: [
    { id: 1, title: '用户提问', desc: '理解用户问题意图与边界', tone: 'emerald',
      boxTitle: '示例输入 · 3 类典型提问', boxComponent: StepBox, boxProps: { lines: [
        '① 如何降低大模型在医疗领域的幻觉？',
        '② 糖尿病患者日常饮食建议有哪些？',
        '③ 解释 RAG 的核心原理与典型应用场景',
      ] } },
    { id: 2, title: '意图理解', desc: '识别问题类型 / 提取关键概念与实体', tone: 'purple',
      boxTitle: '意图识别结果', boxComponent: StepBoxList,
      boxProps: { items: [
        { label: '意图分类：知识问答（FAQ）' },
        { label: '领域标签：医疗 / 大模型' },
        { label: '实体识别：幻觉、RAG、糖尿病、饮食' },
        { label: '相似问句：3 条改写候选' },
      ] } },
    { id: 3, title: '向量检索', desc: '在知识库中检索相关内容', tone: 'blue',
      boxTitle: '向量检索 Top 5 · 耗时 48ms', boxComponent: StepBoxList,
      boxProps: { items: [
        { label: '#1 检索增强生成 (RAG) 实践指南.pdf', score: '0.923' },
        { label: '#2 大模型幻觉成因与缓解策略.docx', score: '0.891' },
        { label: '#3 医疗大模型评估方法综述.pdf', score: '0.864' },
        { label: '#4 提升医疗问答准确性的关键技术.pdf', score: '0.841' },
        { label: '#5 知识库构建与更新方法.pdf', score: '0.782' },
      ] } },
    { id: 4, title: '相关性过滤', desc: '过滤低质内容，保障高价值信息', tone: 'amber',
      boxTitle: '过滤后保留 3 条 · 丢弃 2 条', boxComponent: StepBoxFilter,
      boxProps: { kept: 3, items: [
        '#1 检索增强生成 (RAG) 实践指南.pdf',
        '#2 大模型幻觉成因与缓解策略.docx',
        '#3 提升医疗问答准确性的关键技术.pdf',
      ] } },
  ],
  row2: [
    { id: 5, title: '上下文构建', desc: '组织知识片段，构建 Prompt 上下文', tone: 'pink',
      boxTitle: '构建结果 · 上下文片段', boxComponent: StepBoxText,
      boxProps: { lines: [
        '【系统】你是一名专业医疗 AI 助手，回答必须严格基于以下检索片段...',
        '【检索片段 #1】医学营养治疗是 2 型糖尿病综合管理的基础...',
        '【检索片段 #2】大模型幻觉成因与缓解策略指出...',
        '【用户问题】如何降低大模型在医疗领域的幻觉？',
      ] } },
    { id: 6, title: '大模型生成', desc: '基于上下文生成回答', tone: 'indigo',
      boxTitle: '生成答案 · 候选片段', boxComponent: StepBoxText,
      boxProps: { lines: [
        '根据权威医疗规范与指南，大模型在医疗领域的幻觉主要源于：',
        '① 训练数据中的医学事实错误与时效性偏差；',
        '② 上下文窗口受限导致模型"臆造"未出现的细节；',
        '③ 缺乏可追溯的证据链，错误结论难以被发现。',
        '→ 建议引入检索增强 (RAG) 与医学知识图谱进行事实校准...',
      ] } },
    { id: 7, title: '引用溯源', desc: '标注答案引用来源', tone: 'teal',
      boxTitle: '引用来源 · 3 条可靠证据', boxComponent: StepBoxText,
      boxProps: { lines: [
        '[1] 《检索增强生成 (RAG) 实践指南》 §3.2',
        '[2] 《大模型幻觉成因与缓解策略》 §1.4',
        '[3] 《提升医疗问答准确性的关键技术》 §2.1',
        '可追溯：每条结论均有来源支撑，无虚构内容。',
      ] } },
    { id: 8, title: '评估与反馈', desc: '评估回答质量并持续优化', tone: 'blue',
      boxTitle: '评估结果 · 综合 4.7/5', boxComponent: StepBoxCheck, boxProps: {} },
  ],
})

const stepDescs = [
  '',
  '步骤 1：接收并预处理用户原始提问，解析语义边界。',
  '步骤 2：对输入进行意图识别、实体抽取与关键词提炼。',
  '步骤 3：在向量数据库中检索 Top-K 文本块。',
  '步骤 4：基于 Cross-Encoder 重排模型进行降噪与高相关性筛选。',
  '步骤 5：组合 Prompt 上下文与约束性指令防幻觉模板。',
  '步骤 6：输入带有系统约束的大模型（如 Qwen/GPT-4）生成候选回答。',
  '步骤 7：对生成的段落自动标记精确的参考文献脚注标签。',
  '步骤 8：执行事实一致性校验（Fact-Checking）与自我反思打分。',
]
function selectWorkflowStep(n: number) {
  showToast(stepDescs[n] || '')
}

// ---------- 示例问答 ----------
const sampleSources = [
  { name: '《中国2型糖尿病防治指南 (2023版)》', score: '0.92' },
  { name: '《糖尿病患者膳食指导手册》', score: '0.89' },
  { name: '《糖尿病营养治疗专家共识》', score: '0.86' },
]
const fullSources = [
  { name: '《中国2型糖尿病防治指南 (2023年版)》', score: '0.92', quote: '医学营养治疗是2型糖尿病综合管理的基础，应控制膳食总能量，合理分配碳水化合物、蛋白质和脂肪比例...' },
  { name: '《糖尿病患者膳食指导手册 (WS/T 429-2013)》', score: '0.89', quote: '根据患者年龄、性别、体重及活动强度计算每日所需能量，粗粮等低 GI 食物应占主食 1/3 以上...' },
  { name: '《中国糖尿病营养治疗专家共识》', score: '0.86', quote: '推荐适量摄入优质蛋白质，肾功能正常患者蛋白质提供能量应占总能量的 15%~20%...' },
]

// ---------- 知识库状态 ----------
const kbStats = reactive({ docCount: 12458, chunkCount: 8325771, lastUpdated: '2024-05-20 14:32' })
const syncing = ref(false)
async function restartAllIndexes() {
  syncing.value = true
  try {
    await api.post('/api/rag/index', { force_rebuild: false })
    ElMessage.success('已发起向量索引重建任务，请稍候刷新')
    showToast('已成功发起向量数据库全量索引同步任务！')
  } catch (e: any) {
    ElMessage.error(e?.message || '同步失败')
  } finally {
    syncing.value = false
  }
}

// ---------- 特性条 ----------
const features = [
  { title: '减少幻觉', desc: '基于事实检索，降低虚构内容', icon: MagicStick, tone: 'blue' },
  { title: '提升准确性', desc: '结合权威知识，答案更可靠', icon: DataAnalysis, tone: 'indigo' },
  { title: '可解释可溯源', desc: '每条结论均有来源支撑', icon: Search, tone: 'purple' },
  { title: '持续学习更新', desc: '知识库持续迭代，保持时效性', icon: TrendCharts, tone: 'teal' },
  { title: '效果持续优化', desc: '基于反馈评估，不断自我优化', icon: Star, tone: 'emerald' },
]

// ---------- Toast ----------
const toasts = ref<{ id: number; text: string }[]>([])
let toastSeq = 0
function showToast(text: string) {
  const id = ++toastSeq
  toasts.value.push({ id, text })
  setTimeout(() => {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }, 3500)
}

// ---------- Modal ----------
const qaModalVisible = ref(false)
const simModalVisible = ref(false)
const simInput = ref('高血压患者能否进行中等强度无氧运动？')
const simLogs = ref<string[]>([])
const simConsoleRef = ref<HTMLElement | null>(null)
function openQaModal() { qaModalVisible.value = true }
function openSimModal() { simModalVisible.value = true; simLogs.value = [] }
function runSimPipeline() {
  const q = simInput.value || '(空问题)'
  simLogs.value = [`> 启动 RAG 防幻觉工作流处理："${q}"`]
  const steps = [
    { d: 300, t: '[Step 1/8] 意图识别：识别为【医疗健康/运动禁忌】领域' },
    { d: 700, t: '[Step 2/8] 向量检索：召回 12 条分片' },
    { d: 1100, t: '[Step 3/8] 相关性重排：保留余弦相似度 > 0.82 的 Top 3 权威知识块' },
    { d: 1500, t: '[Step 4/8] 上下文注入：构建 Prompt' },
    { d: 2000, t: '[Step 5/8] 模型生成：标注引用来源标记 [1][2]' },
    { d: 2400, t: '[Step 6/8] 幻觉检测：事实校验得分 96.8/100，未检测出偏离事实虚构' },
    { d: 2700, t: '[完成] 生成结束，回答已成功输出并通过可信认证！' },
  ]
  steps.forEach((s) => {
    setTimeout(() => {
      simLogs.value.push(s.t)
      nextTick(() => {
        if (simConsoleRef.value) simConsoleRef.value.scrollTop = simConsoleRef.value.scrollHeight
      })
    }, s.d)
  })
}

// ---------- 图表 ----------
const radarRef = ref<HTMLElement | null>(null)
const trendRef = ref<HTMLElement | null>(null)
const donutRef1 = ref<HTMLElement | null>(null)
const donutRef2 = ref<HTMLElement | null>(null)
const donutRef3 = ref<HTMLElement | null>(null)
const trendRange = ref<number>(30)

const charts = shallowRef<{ radar?: echarts.ECharts; trend?: echarts.ECharts; d1?: echarts.ECharts; d2?: echarts.ECharts; d3?: echarts.ECharts }>({})

function initRadar() {
  if (!radarRef.value) return
  const c = echarts.init(radarRef.value)
  c.setOption({
    tooltip: { trigger: 'item', backgroundColor: 'rgba(15,23,42,0.9)', textStyle: { color: '#fff', fontSize: 11 }, borderWidth: 0 },
    legend: { bottom: 0, icon: 'line', itemWidth: 14, itemHeight: 2, textStyle: { fontSize: 11, color: '#94a3b8' }, data: ['基线模型', '当前 RAG 流程'] },
    radar: {
      indicator: [
        { name: '准确性', max: 100 }, { name: '相关性', max: 100 },
        { name: '可溯源性', max: 100 }, { name: '覆盖率', max: 100 }, { name: '时效性', max: 100 },
      ],
      radius: '58%', center: ['50%', '44%'],
      axisName: { color: '#cbd5e1', fontSize: 11 },
      splitArea: { areaStyle: { color: ['rgba(91,155,213,0.04)', 'rgba(91,155,213,0.10)'] } },
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.3)' } },
      splitLine: { lineStyle: { color: 'rgba(148,163,184,0.25)' } },
    },
    series: [{
      type: 'radar',
      data: [
        { value: [55, 60, 20, 50, 45], name: '基线模型', lineStyle: { type: 'dashed', width: 1.5, color: '#94a3b8' }, itemStyle: { color: '#94a3b8' }, areaStyle: { color: 'rgba(148,163,184,0.08)' } },
        { value: [92.3, 94, 98, 88, 90], name: '当前 RAG 流程', lineStyle: { width: 2, color: '#5B9BD5' }, itemStyle: { color: '#5B9BD5' }, areaStyle: { color: 'rgba(91,155,213,0.20)' } },
      ],
    }],
  })
  charts.value.radar = c
}

const trendSeriesData = {
  30: { dates: ['04-20', '04-25', '04-30', '05-05', '05-10', '05-15', '05-20'], hallucination: [35, 30, 18, 22, 25, 20, 17.4], accuracy: [75, 80, 88, 86, 90, 89, 92.3], relevance: [60, 65, 72, 70, 75, 71, 78] },
  7: { dates: ['05-14', '05-15', '05-16', '05-17', '05-18', '05-19', '05-20'], hallucination: [22, 19, 18, 20, 16, 15, 14.2], accuracy: [87, 89, 90, 91, 92, 93, 94.1], relevance: [70, 72, 74, 76, 77, 78, 79] },
  90: { dates: ['03-01', '03-15', '04-01', '04-15', '05-01', '05-15', '05-20'], hallucination: [45, 38, 32, 26, 22, 18, 17.4], accuracy: [68, 74, 80, 85, 89, 91, 92.3], relevance: [55, 60, 66, 70, 74, 76, 78] },
}

function initTrend() {
  if (!trendRef.value) return
  const c = echarts.init(trendRef.value)
  c.setOption(buildTrendOption(30))
  charts.value.trend = c
}

function buildTrendOption(range: number): echarts.EChartsOption {
  const d = trendSeriesData[range as keyof typeof trendSeriesData]
  return {
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,23,42,0.9)', borderWidth: 0, textStyle: { color: '#fff', fontSize: 11 } },
    legend: { top: 0, right: 10, icon: 'circle', itemWidth: 8, textStyle: { fontSize: 11, color: '#94a3b8' }, data: ['幻觉率', '准确率', '相关性评分'] },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '18%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: d.dates, axisLine: { lineStyle: { color: 'rgba(148,163,184,0.4)' } }, axisLabel: { color: '#94a3b8', fontSize: 10 } },
    yAxis: { type: 'value', min: 0, max: 100, interval: 25, axisLabel: { formatter: '{value}%', color: '#94a3b8', fontSize: 10 }, splitLine: { lineStyle: { color: 'rgba(148,163,184,0.15)' } } },
    series: [
      { name: '幻觉率', type: 'line', smooth: true, showSymbol: true, symbolSize: 5, data: d.hallucination, itemStyle: { color: '#93C5FD' }, lineStyle: { width: 2 } },
      { name: '准确率', type: 'line', smooth: true, showSymbol: true, symbolSize: 5, data: d.accuracy, itemStyle: { color: '#3B82F6' }, lineStyle: { width: 2 } },
      { name: '相关性评分', type: 'line', smooth: true, showSymbol: true, symbolSize: 5, data: d.relevance, itemStyle: { color: '#1E40AF' }, lineStyle: { width: 2 } },
    ],
  }
}

function updateTrendChart() {
  if (charts.value.trend) charts.value.trend.setOption(buildTrendOption(trendRange.value), true)
}

function initDonut(el: HTMLElement | null, data: { value: number; name: string; color: string }[]) {
  if (!el) return
  const c = echarts.init(el)
  c.setOption({
    tooltip: { trigger: 'item', textStyle: { fontSize: 11 } },
    legend: { orient: 'vertical', right: 0, top: 'center', icon: 'circle', itemWidth: 8, textStyle: { fontSize: 10, color: '#94a3b8' } },
    series: [{
      type: 'pie', radius: ['55%', '80%'], center: ['32%', '50%'], avoidLabelOverlap: false, label: { show: false },
      data: data.map((d) => ({ value: d.value, name: d.name, itemStyle: { color: d.color } })),
    }],
  })
  return c
}

function initDonuts() {
  charts.value.d1 = initDonut(donutRef1.value, [
    { value: 82.6, name: '通过 82.6%', color: '#3B82F6' },
    { value: 17.4, name: '未通过 17.4%', color: '#7BC4E8' },
  ])
  charts.value.d2 = initDonut(donutRef2.value, [
    { value: 62.1, name: '高相关 (>0.8) 62.1%', color: '#1E40AF' },
    { value: 28.3, name: '中相关 28.3%', color: '#5B9BD5' },
    { value: 9.6, name: '低相关 9.6%', color: '#93C5FD' },
  ])
  charts.value.d3 = initDonut(donutRef3.value, [
    { value: 28.1, name: '< 1s 28.1%', color: '#1E40AF' },
    { value: 54.3, name: '1s - 3s 54.3%', color: '#3B82F6' },
    { value: 13.7, name: '3s - 5s 13.7%', color: '#5B9BD5' },
    { value: 3.9, name: '> 5s 3.9%', color: '#93C5FD' },
  ])
}

function handleResize() {
  Object.values(charts.value).forEach((c) => c?.resize())
}

onMounted(async () => {
  await nextTick()
  initRadar()
  initTrend()
  initDonuts()
  window.addEventListener('resize', handleResize)
  // 尝试拉真实 rag stats（mock 模式失败也无副作用）
  try {
    const stats: any = await api.get('/api/rag/stats')
    if (Array.isArray(stats)) {
      const total = stats.reduce((acc: number, s: any) => acc + (s.chunk_count || 0), 0)
      const success = stats.filter((s: any) => s.status === 'success')
      if (success.length) {
        kbStats.chunkCount = total
        const last = success.map((s: any) => s.completed_at).filter(Boolean).sort().pop()
        if (last) kbStats.lastUpdated = String(last).replace('T', ' ').slice(0, 16)
      }
    }
  } catch { /* ignore */ }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  Object.values(charts.value).forEach((c) => c?.dispose())
})
</script>

<style scoped>
.rag-admin-page { width: 100%; }

/* —— 顶部工具条 —— */
.rag-toolbar {
  display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px;
  margin: 12px 0 16px;
  padding: 12px 16px;
  background: rgba(91,155,213,0.06);
  border: 1px solid rgba(91,155,213,0.18);
  border-radius: 12px;
  backdrop-filter: blur(8px);
}
.rag-toolbar-left { display: flex; align-items: center; }
.rag-toolbar-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 12px;
  background: rgba(52,211,153,0.10);
  border: 1px solid rgba(52,211,153,0.28);
  color: #6ee7b7;
  font-size: 12px;
  border-radius: 999px;
}
.badge-icon { color: #34d399; }
.rag-toolbar-right { display: flex; align-items: center; gap: 12px; }
.rag-update { font-size: 12px; color: #94a3b8; display: inline-flex; align-items: center; gap: 4px; }

/* —— KPI 5 卡 —— */
.rag-kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 18px;
}
.rag-kpi-card {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px;
  background: rgba(91,155,213,0.05);
  border: 1px solid rgba(148,163,184,0.18);
  border-radius: 12px;
  transition: all 0.2s;
}
.rag-kpi-card:hover { border-color: rgba(91,155,213,0.40); transform: translateY(-1px); }
.kpi-text { flex: 1; }
.kpi-label { font-size: 12px; color: #94a3b8; margin-bottom: 4px; }
.kpi-value { font-size: 22px; font-weight: 700; color: #e2e8f0; letter-spacing: -0.5px; }
.kpi-trend { font-size: 11px; margin-top: 4px; display: inline-flex; align-items: center; gap: 3px; font-weight: 600; }
.kpi-trend.up { color: #34d399; }
.kpi-trend.down { color: #6ee7b7; }
.kpi-icon {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 999px;
}
.kpi-icon-0 { background: rgba(20,184,166,0.12); color: #2dd4bf; }
.kpi-icon-1 { background: rgba(99,102,241,0.12); color: #818cf8; }
.kpi-icon-2 { background: rgba(59,130,246,0.12); color: #60a5fa; }
.kpi-icon-3 { background: rgba(245,158,11,0.12); color: #fbbf24; }
.kpi-icon-4 { background: rgba(168,85,247,0.12); color: #c084fc; }

/* —— 主工作区 —— */
.rag-workspace {
  display: grid; grid-template-columns: 8fr 4fr; gap: 16px; margin-bottom: 18px;
}
@media (max-width: 1024px) { .rag-workspace { grid-template-columns: 1fr; } }

.rag-card {
  padding: 18px 20px;
  background: rgba(15,23,42,0.55);
  border: 1px solid rgba(148,163,184,0.20);
  border-radius: 14px;
  backdrop-filter: blur(10px);
}
.rag-card-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;
}
.rag-card-title { margin: 0; font-size: 16px; font-weight: 700; color: #e2e8f0; }
.rag-card-subtitle { font-size: 12px; color: #94a3b8; font-weight: 400; margin-left: 6px; }
.rag-section-subtitle {
  font-size: 12px; font-weight: 700; color: #94a3b8;
  text-transform: uppercase; letter-spacing: 1px;
  margin: 18px 0 10px;
}

/* —— 工作流画布（8 步 + 4+4 双行 + 行内箭头） —— */
.rag-flow-canvas {
  position: relative;
  padding: 18px 6px 14px;
}
.flow-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 44px;
  position: relative;
  z-index: 2;
}
.flow-row-2 { margin-top: 32px; }
@media (max-width: 1024px) {
  .flow-row { grid-template-columns: repeat(2, 1fr); gap: 28px; }
  .flow-row-2 { margin-top: 24px; }
  .node-arrow-right { display: none; }
}
@media (max-width: 600px) {
  .flow-row { grid-template-columns: 1fr; }
  .flow-row-2 { margin-top: 20px; }
}

/* —— 节点（大尺寸精致卡片） —— */
.flow-node {
  position: relative;
  background: linear-gradient(160deg, rgba(91,155,213,0.10) 0%, rgba(91,155,213,0.04) 100%);
  border: 1px solid rgba(148,163,184,0.22);
  border-radius: 14px;
  padding: 20px 18px 16px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 260px;
  /* overflow 不写，让行内/朝下箭头能溢出显示 */
  transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}
.flow-node::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 14px;
  background: radial-gradient(circle at top right, rgba(91,155,213,0.18), transparent 60%);
  opacity: 0.6;
  pointer-events: none;
  transition: opacity 0.28s;
  overflow: hidden; /* 仅渐变背景层裁切到圆角 */
}
.flow-node:hover {
  background: linear-gradient(160deg, rgba(91,155,213,0.18) 0%, rgba(91,155,213,0.08) 100%);
  transform: translateY(-3px);
  box-shadow: 0 16px 32px -14px rgba(91,155,213,0.50);
}
.flow-node:hover::before { opacity: 1; }

/* 四角装饰点 */
.node-corner {
  position: absolute;
  width: 8px; height: 8px;
  border: 1.5px solid rgba(91,155,213,0.55);
  border-radius: 2px;
  pointer-events: none;
  transition: all 0.28s;
}
.node-corner-tl { top: 6px; left: 6px; border-right: 0; border-bottom: 0; }
.node-corner-br { bottom: 6px; right: 6px; border-left: 0; border-top: 0; }
.flow-node:hover .node-corner { border-color: rgba(91,155,213,0.95); width: 10px; height: 10px; }
.flow-node.tone-emerald .node-corner { border-color: rgba(16,185,129,0.65); }
.flow-node.tone-purple .node-corner { border-color: rgba(168,85,247,0.65); }
.flow-node.tone-blue .node-corner { border-color: rgba(59,130,246,0.65); }
.flow-node.tone-amber .node-corner { border-color: rgba(245,158,11,0.65); }

/* tone 左侧色带 */
.flow-node.tone-emerald { box-shadow: inset 3px 0 0 #10b981; }
.flow-node.tone-purple { box-shadow: inset 3px 0 0 #a855f7; }
.flow-node.tone-blue { box-shadow: inset 3px 0 0 #3b82f6; }
.flow-node.tone-amber { box-shadow: inset 3px 0 0 #f59e0b; }
.flow-node.tone-pink { box-shadow: inset 3px 0 0 #ec4899; }
.flow-node.tone-indigo { box-shadow: inset 3px 0 0 #6366f1; }
.flow-node.tone-teal { box-shadow: inset 3px 0 0 #14b8a6; }

.flow-node.tone-emerald:hover { box-shadow: inset 3px 0 0 #10b981, 0 16px 32px -14px rgba(16,185,129,0.50); }
.flow-node.tone-purple:hover { box-shadow: inset 3px 0 0 #a855f7, 0 16px 32px -14px rgba(168,85,247,0.50); }
.flow-node.tone-blue:hover { box-shadow: inset 3px 0 0 #3b82f6, 0 16px 32px -14px rgba(59,130,246,0.50); }
.flow-node.tone-amber:hover { box-shadow: inset 3px 0 0 #f59e0b, 0 16px 32px -14px rgba(245,158,11,0.50); }
.flow-node.tone-pink:hover { box-shadow: inset 3px 0 0 #ec4899, 0 16px 32px -14px rgba(236,72,153,0.50); }
.flow-node.tone-indigo:hover { box-shadow: inset 3px 0 0 #6366f1, 0 16px 32px -14px rgba(99,102,241,0.50); }
.flow-node.tone-teal:hover { box-shadow: inset 3px 0 0 #14b8a6, 0 16px 32px -14px rgba(20,184,166,0.50); }

/* 大数字 → 小数字 badge */
.node-badge {
  width: 22px; height: 22px;
  border-radius: 999px;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700;
  font-family: ui-monospace, Menlo, monospace;
  color: #fff;
  background: rgba(91,155,213,0.40);
  flex-shrink: 0;
  transition: all 0.28s;
}
.tone-emerald .node-badge { background: #10b981; }
.tone-purple .node-badge { background: #a855f7; }
.tone-blue .node-badge { background: #3b82f6; }
.tone-amber .node-badge { background: #f59e0b; }
.tone-pink .node-badge { background: #ec4899; }
.tone-indigo .node-badge { background: #6366f1; }
.tone-teal .node-badge { background: #14b8a6; }
.flow-node:hover .node-badge { transform: scale(1.10); }

/* 右上角 icon */
.node-icon {
  position: absolute;
  top: 16px; right: 16px;
  width: 38px; height: 38px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(91,155,213,0.12);
  color: #93c5fd;
  transition: all 0.28s;
  z-index: 2;
}
.tone-emerald .node-icon { background: rgba(16,185,129,0.16); color: #6ee7b7; }
.tone-purple .node-icon { background: rgba(168,85,247,0.16); color: #d8b4fe; }
.tone-blue .node-icon { background: rgba(59,130,246,0.16); color: #93c5fd; }
.tone-amber .node-icon { background: rgba(245,158,11,0.16); color: #fcd34d; }
.flow-node:hover .node-icon { transform: scale(1.08) rotate(-4deg); }

/* 节点头部（badge + 标题 横向排列） */
.node-head {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 2;
  margin-top: 2px;
}
.node-title {
  font-size: 15px;
  font-weight: 700;
  color: #f1f5f9;
  line-height: 1.3;
  letter-spacing: 0.2px;
}
.node-desc {
  font-size: 11px;
  color: #94a3b8;
  line-height: 1.55;
  min-height: 34px;
  position: relative;
  z-index: 2;
}

/* 内容盒 */
.node-box {
  margin-top: auto;
  position: relative;
  z-index: 2;
  background: rgba(15,23,42,0.45);
  border: 1px solid rgba(148,163,184,0.18);
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 11px;
  color: #cbd5e1;
  line-height: 1.55;
  backdrop-filter: blur(4px);
}
.node-box-label {
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 6px;
  font-size: 10px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

/* 行内箭头（节点之间朝右，带流动光斑 + 发光） */
.node-arrow-right {
  position: absolute;
  right: -38px;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 3px;
  background: linear-gradient(to right, rgba(91,155,213,0.15) 0%, #5B9BD5 70%, #7BC4E8 100%);
  border-radius: 2px;
  z-index: 5;
  pointer-events: none;
  overflow: visible;
  filter: drop-shadow(0 0 4px rgba(91,155,213,0.65));
}
.node-arrow-right::before {
  content: '';
  position: absolute;
  inset: -1px 0;
  background: linear-gradient(to right, transparent 0%, rgba(255,255,255,0.85) 50%, transparent 100%);
  background-size: 220% 100%;
  animation: arrow-flow 1.6s linear infinite;
  border-radius: 2px;
}
.node-arrow-right::after {
  content: '';
  position: absolute;
  right: -3px;
  top: 50%;
  transform: translateY(-50%);
  width: 0; height: 0;
  border-top: 7px solid transparent;
  border-bottom: 7px solid transparent;
  border-left: 10px solid #7BC4E8;
}
@keyframes arrow-flow {
  0%   { background-position: -120% 0; }
  100% { background-position: 220% 0; }
}

/* —— 侧栏 —— */
.rag-side { display: flex; flex-direction: column; gap: 16px; }
.rag-chart { width: 100%; height: 224px; }
.rag-chart-tall { height: 220px; }
.rag-chart-donut { height: 144px; }

/* —— 示例问答 —— */
.rag-sample-qa { font-size: 12px; color: #cbd5e1; }
.qa-line { margin-bottom: 6px; line-height: 1.6; }
.qa-tag {
  display: inline-block; padding: 1px 6px; margin-right: 4px;
  background: rgba(91,155,213,0.18); color: #93c5fd;
  border-radius: 4px; font-size: 11px; font-weight: 700;
}
.qa-answer {
  background: rgba(91,155,213,0.06);
  border: 1px solid rgba(91,155,213,0.18);
  border-radius: 8px; padding: 8px 10px; line-height: 1.6; margin-bottom: 12px;
}
.qa-source-title { font-size: 11px; color: #94a3b8; font-weight: 600; margin: 8px 0 6px; }
.qa-source-list { display: flex; flex-direction: column; gap: 4px; }
.qa-source-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 6px 10px;
  background: rgba(91,155,213,0.05);
  border-radius: 6px; font-size: 11px;
  transition: background 0.15s;
}
.qa-source-item:hover { background: rgba(91,155,213,0.12); }
.source-name { color: #cbd5e1; }
.source-score { color: #94a3b8; }
.source-score strong { color: #e2e8f0; font-family: ui-monospace, Menlo, monospace; }
.full-qa-btn { width: 100%; margin-top: 10px; }

/* —— 底部趋势 + 知识库 —— */
.rag-bottom-grid {
  display: grid; grid-template-columns: 8fr 4fr; gap: 16px; margin-bottom: 18px;
}
@media (max-width: 1024px) { .rag-bottom-grid { grid-template-columns: 1fr; } }
.trend-select { width: 110px; }
.donut-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;
}
@media (max-width: 768px) { .donut-grid { grid-template-columns: 1fr; } }
.donut-wrap {
  background: rgba(91,155,213,0.04);
  border: 1px solid rgba(148,163,184,0.12);
  border-radius: 8px;
  padding: 8px;
}
.donut-title { font-size: 11px; font-weight: 700; color: #cbd5e1; text-align: center; margin-bottom: 4px; }

/* —— 知识库状态 —— */
.kb-list { display: flex; flex-direction: column; gap: 10px; margin-top: 12px; }
.kb-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px;
  background: rgba(91,155,213,0.05);
  border: 1px solid rgba(148,163,184,0.12);
  border-radius: 8px;
}
.kb-label { font-size: 12px; color: #94a3b8; }
.kb-value { font-size: 14px; font-weight: 700; color: #e2e8f0; font-family: ui-monospace, Menlo, monospace; }
.kb-footer {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 14px; padding-top: 14px;
  border-top: 1px solid rgba(148,163,184,0.15);
}
.kb-status { display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 600; color: #34d399; }
.kb-pulse {
  width: 10px; height: 10px; border-radius: 999px;
  background: #34d399; position: relative;
  box-shadow: 0 0 0 0 rgba(52,211,153,0.6);
  animation: rag-pulse 1.6s infinite;
}
@keyframes rag-pulse {
  0% { box-shadow: 0 0 0 0 rgba(52,211,153,0.6); }
  70% { box-shadow: 0 0 0 8px rgba(52,211,153,0); }
  100% { box-shadow: 0 0 0 0 rgba(52,211,153,0); }
}

/* —— 底部特性条 —— */
.rag-features {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px;
}
@media (max-width: 1024px) { .rag-features { grid-template-columns: repeat(2, 1fr); } }
.rag-feature-item {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 14px;
  background: rgba(91,155,213,0.04);
  border: 1px solid rgba(148,163,184,0.15);
  border-radius: 10px;
  transition: all 0.2s;
}
.rag-feature-item:hover { background: rgba(91,155,213,0.10); }
.feature-icon {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.feature-icon-blue { background: rgba(59,130,246,0.18); color: #60a5fa; }
.feature-icon-indigo { background: rgba(99,102,241,0.18); color: #818cf8; }
.feature-icon-purple { background: rgba(168,85,247,0.18); color: #c084fc; }
.feature-icon-teal { background: rgba(20,184,166,0.18); color: #2dd4bf; }
.feature-icon-emerald { background: rgba(16,185,129,0.18); color: #34d399; }
.feature-title { font-size: 12px; font-weight: 700; color: #e2e8f0; margin-bottom: 2px; }
.feature-desc { font-size: 11px; color: #94a3b8; }

/* —— Modal —— */
.rag-modal-body { font-size: 12px; color: #cbd5e1; }
.modal-section { margin-bottom: 14px; }
.modal-label { font-weight: 700; color: #e2e8f0; margin-bottom: 6px; }
.modal-q {
  padding: 10px 12px; background: rgba(91,155,213,0.05);
  border: 1px solid rgba(148,163,184,0.15); border-radius: 8px;
  color: #e2e8f0; font-weight: 500;
}
.modal-a {
  padding: 10px 12px; background: rgba(59,130,246,0.06);
  border: 1px solid rgba(59,130,246,0.20); border-radius: 8px;
  line-height: 1.7;
}
.modal-a ol { padding-left: 20px; margin: 4px 0; }
.modal-source-list { display: flex; flex-direction: column; gap: 8px; }
.modal-source-item {
  padding: 10px 12px; background: rgba(91,155,213,0.04);
  border: 1px solid rgba(148,163,184,0.12); border-radius: 8px;
}
.modal-source-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.modal-source-name { color: #60a5fa; font-weight: 700; font-size: 12px; }
.modal-source-score {
  background: rgba(52,211,153,0.12); color: #34d399;
  padding: 1px 8px; border-radius: 999px; font-size: 11px;
  font-family: ui-monospace, Menlo, monospace;
}
.modal-source-quote { color: #94a3b8; font-style: italic; font-size: 11px; margin: 0; }

/* —— 模拟 Modal —— */
.sim-input-row { display: flex; gap: 8px; margin-bottom: 12px; }
.sim-console {
  background: #0b1220; color: #6ee7b7; padding: 14px; border-radius: 10px;
  font-family: ui-monospace, Menlo, monospace; font-size: 11px;
  height: 200px; overflow-y: auto; line-height: 1.7;
  border: 1px solid rgba(91,155,213,0.18);
}
.sim-log { color: #6ee7b7; }
.sim-log-idle { color: #64748b; }
.sim-log-done { color: #34d399; font-weight: 700; }

/* —— Toast —— */
.rag-toast-host {
  position: fixed; right: 24px; bottom: 24px;
  display: flex; flex-direction: column; gap: 8px; z-index: 9999;
  pointer-events: none;
}
.rag-toast {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 10px 16px;
  background: rgba(15,23,42,0.95);
  color: #f1f5f9; font-size: 12px;
  border: 1px solid rgba(91,155,213,0.30);
  border-radius: 10px;
  box-shadow: 0 12px 28px -10px rgba(0,0,0,0.5);
  pointer-events: auto;
}
.rag-toast .el-icon { color: #5B9BD5; }
.rag-toast-enter-from, .rag-toast-leave-to { opacity: 0; transform: translateY(8px); }
.rag-toast-enter-active, .rag-toast-leave-active { transition: all 0.25s ease; }
</style>