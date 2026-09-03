<template>
  <div class="page source-page">
    <PageHeader title="权威数据源中心" desc="统一管理政府统计、职业标准与开放技能分类；每条数据保留发布机构、版本、日期和原始链接。">
      <div class="toolbar">
        <span class="sync-note">沿用上次成功快照；仅在管理员点击同步时联网更新</span>
        <div v-if="auth.role === 'admin'" class="toolbar-actions">
          <el-button :icon="Upload" @click="importDialog = true">导入真实 JD</el-button>
          <el-button type="primary" :icon="Refresh" :loading="syncing" @click="syncAll">同步全部权威源</el-button>
        </div>
        <el-tag v-else type="info" effect="plain">仅管理员可执行联网同步</el-tag>
      </div>
    </PageHeader>

    <section class="source-summary">
      <article><span>有效来源</span><strong>{{ snapshot.coverage?.source_count || rows.length }}</strong><small>政府 / 国际组织 / 开放标准</small></article>
      <article><span>发布机构</span><strong>{{ snapshot.coverage?.publisher_count || 0 }}</strong><small>跨来源交叉验证</small></article>
      <article><span>原始记录</span><strong>{{ compact(snapshot.coverage?.record_count || 0) }}</strong><small>完整源数据口径</small></article>
      <article><span>本地索引</span><strong>{{ compact(snapshot.coverage?.indexed_count || 0) }}</strong><small>可检索职业与技能关系</small></article>
    </section>

    <el-alert class="provenance-alert" type="info" :closable="false" show-icon>
      <template #title>{{ snapshot.provenance_note || '公开市场数据与用户隐私数据分层保存，不使用虚构招聘样本替代真实来源。' }}</template>
    </el-alert>

    <div v-if="auth.role === 'admin' || auth.role === 'hr'" class="panel import-history-panel">
      <div class="table-head">
        <div>
          <h3>真实 JD 导入批次</h3>
          <p>每个批次保留发布机构、原始链接、去重结果和 AI 解析进度</p>
        </div>
        <el-button v-if="auth.role === 'admin'" type="primary" plain :icon="Upload" @click="importDialog = true">新建导入</el-button>
      </div>
      <el-empty v-if="!imports.length" description="尚未导入真实 JD 数据" :image-size="72" />
      <el-table v-else :data="imports" row-key="id">
        <el-table-column label="批次与来源" min-width="240">
          <template #default="{ row }">
            <b>{{ row.source_name }}</b>
            <small>{{ row.publisher }} · {{ row.filename || '数据文件' }}</small>
          </template>
        </el-table-column>
        <el-table-column label="导入质量" min-width="175">
          <template #default="{ row }">
            <b>{{ row.imported_count }} / {{ row.total_count }} 条入库</b>
            <small>重复 {{ row.duplicate_count }} · 无效 {{ row.invalid_count }}</small>
          </template>
        </el-table-column>
        <el-table-column label="业务生效" min-width="180">
          <template #default="{ row }">
            <b v-if="row.integration?.published_at">已发布 {{ row.integration.eligible_jd_count || 0 }} 条可信 JD</b>
            <b v-else>尚未发布到岗位图谱</b>
            <small v-if="row.integration?.published_at">
              岗位 +{{ row.integration.created_jobs || 0 }} / 更新 {{ row.integration.updated_jobs || 0 }} · 能力关系 +{{ row.integration.added_relations || 0 }}
            </small>
            <small v-else>解析结果暂不影响岗位、人岗匹配和能力演化</small>
          </template>
        </el-table-column>
        <el-table-column label="解析进度" min-width="190">
          <template #default="{ row }">
            <b>{{ parsedCount(row) }} / {{ row.imported_count }} 条完成</b>
            <small>待解析 {{ row.status_counts?.pending || 0 }} · 失败 {{ row.status_counts?.failed || 0 }}</small>
          </template>
        </el-table-column>
        <el-table-column label="导入时间" min-width="155">
          <template #default="{ row }"><b>{{ formatDate(row.uploaded_at, true) }}</b><small>批次 #{{ row.id }}</small></template>
        </el-table-column>
        <el-table-column label="操作" width="190" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="auth.role === 'admin' && parsedCount(row) < row.imported_count"
              type="primary"
              text
              :loading="parsingBatchId === row.id"
              @click="parseBatch(row)"
            >继续解析</el-button>
            <el-button
              v-else-if="auth.role === 'admin'"
              type="success"
              text
              :loading="publishingBatchId === row.id"
              @click="publishBatch(row)"
            >{{ row.integration?.published_at ? '重新同步业务' : '发布到岗位图谱' }}</el-button>
            <el-tag v-else-if="row.integration?.published_at" type="success" effect="plain">已发布</el-tag>
            <el-tag v-else type="warning" effect="plain">待发布</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="panel source-table-panel" v-loading="loading">
      <div class="table-head">
        <div>
          <h3>已接入数据源</h3>
          <p>最后同步：{{ formatDate(snapshot.last_synced_at, true) }}</p>
        </div>
        <el-input v-model="keyword" clearable placeholder="搜索来源、机构或领域" :prefix-icon="Search" />
      </div>
      <el-table :data="filteredRows" stripe row-key="source_key">
        <el-table-column label="数据来源" min-width="250">
          <template #default="{ row }">
            <button class="source-link" type="button" @click="openSource(row.source_url)">
              <b>{{ row.source_name }}</b>
              <span>{{ row.publisher }}</span>
            </button>
          </template>
        </el-table-column>
        <el-table-column label="版本 / 发布日期" min-width="150">
          <template #default="{ row }"><b>{{ row.version || '-' }}</b><small>{{ formatDate(row.published_at) }}</small></template>
        </el-table-column>
        <el-table-column label="类型 / 领域" min-width="190">
          <template #default="{ row }"><b>{{ row.data_type }}</b><small>{{ row.domain }}</small></template>
        </el-table-column>
        <el-table-column label="数据规模" min-width="130" align="right">
          <template #default="{ row }"><b>{{ compact(row.data_count || 0) }}</b><small>{{ row.data_type === '真实岗位 JD' ? `入库 ${compact(row.indexed_count || 0)}` : `索引 ${compact(row.indexed_count || 0)}` }}</small></template>
        </el-table-column>
        <el-table-column label="质量" width="120">
          <template #default="{ row }"><el-progress :percentage="Math.round(row.quality_score || 0)" :stroke-width="7" /></template>
        </el-table-column>
        <el-table-column label="许可" min-width="150">
          <template #default="{ row }"><span class="license">{{ row.license_name || '公开信息' }}</span></template>
        </el-table-column>
        <el-table-column label="同步状态" width="130">
          <template #default="{ row }"><el-tag :type="statusType(row.status)" effect="dark">{{ statusLabel(row.status) }}</el-tag></template>
        </el-table-column>
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="source-detail">
              <p><b>同步说明：</b>{{ row.sync_message || '暂无说明' }}</p>
              <p><b>最近同步：</b>{{ formatDate(row.last_synced_at, true) }}</p>
              <p><b>原始地址：</b><a :href="row.source_url" target="_blank" rel="noreferrer">{{ row.source_url }}</a></p>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="importDialog" title="导入真实 JD 数据" width="min(560px, calc(100vw - 28px))" destroy-on-close>
      <el-form label-position="top" :model="importForm">
        <div class="form-grid">
          <el-form-item label="数据来源名称" required>
            <el-input v-model="importForm.source_name" placeholder="例如：某企业 2026 校招官网" />
          </el-form-item>
          <el-form-item label="发布机构" required>
            <el-input v-model="importForm.publisher" placeholder="企业或公开数据集发布方" />
          </el-form-item>
        </div>
        <el-form-item label="来源主页或数据集地址" required>
          <el-input v-model="importForm.source_url" placeholder="https://..." />
        </el-form-item>
        <el-form-item label="许可或使用说明">
          <el-input v-model="importForm.license_name" />
        </el-form-item>
        <el-form-item label="CSV / JSON 文件" required>
          <el-upload
            class="jd-upload"
            drag
            action="#"
            accept=".csv,.json"
            :auto-upload="false"
            :limit="1"
            :on-change="selectImportFile"
            :on-remove="removeImportFile"
          >
            <el-icon><UploadFilled /></el-icon>
            <div class="el-upload__text">拖入文件，或点击选择</div>
            <template #tip>
              <div class="el-upload__tip">最大 5 MB、1000 条；必须包含 content，建议包含 title、source_url、published_at、external_id。</div>
            </template>
          </el-upload>
        </el-form-item>
        <div class="parse-option">
          <div><b>导入后立即解析</b><small>当前未配置 DeepSeek 时会使用测试提供者；也可稍后按批次解析。</small></div>
          <el-switch v-model="importForm.auto_parse" />
        </div>
      </el-form>
      <template #footer>
        <el-button @click="importDialog = false">取消</el-button>
        <el-button type="primary" :loading="importing" @click="submitImport">校验并导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Refresh, Search, Upload, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const rows = ref<any[]>([])
const snapshot = ref<any>({ coverage: {} })
const loading = ref(false)
const syncing = ref(false)
const keyword = ref('')
const imports = ref<any[]>([])
const importDialog = ref(false)
const importing = ref(false)
const parsingBatchId = ref<number | null>(null)
const publishingBatchId = ref<number | null>(null)
const importFile = ref<File | null>(null)
const importForm = ref({
  source_name: '',
  publisher: '',
  source_url: '',
  license_name: '公开招聘信息，仅用于教育研究与岗位能力分析',
  auto_parse: false,
  parse_limit: 20
})

const filteredRows = computed(() => {
  const query = keyword.value.trim().toLowerCase()
  if (!query) return rows.value
  return rows.value.filter((row) => [row.source_name, row.publisher, row.domain, row.data_type, row.version].some((value) => String(value || '').toLowerCase().includes(query)))
})

function compact(value: number) {
  return new Intl.NumberFormat('zh-CN', { notation: value >= 10000 ? 'compact' : 'standard', maximumFractionDigits: 1 }).format(value)
}

function formatDate(value?: string, withTime = false) {
  if (!value) return '尚未同步'
  return new Intl.DateTimeFormat('zh-CN', withTime ? { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' } : { year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(value))
}

function statusType(status: string) {
  if (status === 'synced' || status === 'verified') return 'success'
  if (status === 'verified_metadata') return 'warning'
  return 'info'
}

function statusLabel(status: string) {
  return ({ synced: '已完整同步', verified: '已核验', verified_metadata: '元数据已核验', imported: '已导入', partially_parsed: '解析中', parsed: '已解析' } as Record<string, string>)[status] || status || '未知'
}

function parsedCount(row: any) {
  return Number(row.status_counts?.parsed || 0)
}

function selectImportFile(uploadFile: any) {
  importFile.value = uploadFile.raw || null
}

function removeImportFile() {
  importFile.value = null
}

function openSource(url: string) {
  if (url) window.open(url, '_blank', 'noopener,noreferrer')
}

async function load() {
  loading.value = true
  try {
    const requests: Promise<any>[] = [api.datasets(), api.marketSnapshot()]
    if (auth.role === 'admin' || auth.role === 'hr') requests.push(api.jdImports())
    const [sources, market, importRows = []] = await Promise.all(requests)
    rows.value = sources
    snapshot.value = market
    imports.value = importRows
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '数据源加载失败')
  } finally {
    loading.value = false
  }
}

async function submitImport() {
  if (!importFile.value) return ElMessage.warning('请选择 CSV 或 JSON 文件')
  if (!importForm.value.source_name.trim() || !importForm.value.publisher.trim() || !importForm.value.source_url.trim()) {
    return ElMessage.warning('请完整填写来源名称、发布机构和来源地址')
  }
  importing.value = true
  try {
    const result = await api.importJds(importFile.value, importForm.value)
    ElMessage.success(`已入库 ${result.imported_count} 条，过滤重复 ${result.duplicate_count} 条、无效 ${result.invalid_count} 条`)
    importDialog.value = false
    importFile.value = null
    await load()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || 'JD 批量导入失败')
  } finally {
    importing.value = false
  }
}

async function parseBatch(row: any) {
  parsingBatchId.value = row.id
  try {
    const result = await api.parseJdImport(row.id)
    ElMessage.success(`本次解析成功 ${result.parsed_now} 条，失败 ${result.failed_now} 条`)
    await load()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '批量解析失败')
  } finally {
    parsingBatchId.value = null
  }
}

async function publishBatch(row: any) {
  publishingBatchId.value = row.id
  try {
    const result = await api.publishJdImport(row.id)
    const indexNote = result.rag_index?.status === 'success'
      ? `，RAG 索引 ${result.rag_index.chunk_count} 条`
      : '，但 RAG 索引刷新失败'
    ElMessage.success(
      `已发布 ${result.eligible_jd_count} 条可信 JD：新增岗位 ${result.created_jobs}，更新岗位 ${result.updated_jobs}，能力关系 +${result.added_relations}${indexNote}`
    )
    await load()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || 'JD 发布到岗位图谱失败')
  } finally {
    publishingBatchId.value = null
  }
}

async function syncAll() {
  syncing.value = true
  try {
    const result = await api.syncDataSources()
    Object.keys(localStorage).filter((key) => key.startsWith('sr-dashboard:')).forEach((key) => localStorage.removeItem(key))
    ElMessage.success(`同步完成：${compact(result.record_count || 0)} 条原始记录，${compact(result.indexed_count || 0)} 条本地索引`)
    await load()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '同步失败，请检查网络后重试')
  } finally {
    syncing.value = false
  }
}

onMounted(load)
</script>

<style>
/* Unscoped glass overrides — specificity must beat theme-fixes.css loaded after page styles.
   theme-fixes uses: body.theme-dark .app-main:not(.app-main--dashboard) :is(.panel,.page-toolbar,.el-alert,...) { background:#0a1c2b!important; box-shadow:none!important }
   specificity ≈ 0-0-41. We add .page.source-page + per-element classes to reach 0-0-61+ and win. */

/* === 1. .page-toolbar 工具栏（theme-fixes 将 .page-toolbar 强制 #0a1c2b） === */
body.theme-dark .app-main:not(.app-main--dashboard) .page.source-page .page-toolbar,
body:not(.login-active) .app-main .page.source-page .page-toolbar {
  justify-content: stretch;
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
body.theme-dark .app-main:not(.app-main--dashboard) .page.source-page .page-toolbar::before,
body:not(.login-active) .app-main .page.source-page .page-toolbar::before {
  display: none !important;
}

/* === 2. 4 张统计卡片 article（不在 theme-fixes 列表里，但也统一一下） === */
body.theme-dark .page.source-page .source-summary article,
body:not(.login-active) .app-main .page.source-page .source-summary article {
  border: 1px solid rgba(78, 200, 255, 0.18) !important;
  border-radius: 13px !important;
  background: rgba(8, 42, 92, 0.35) !important;
  box-shadow:
    inset 0 1px 0 rgba(161, 231, 255, 0.08),
    0 8px 32px rgba(0, 10, 40, 0.25) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

/* === 3. .el-alert.provenance-alert 数据来源声明条（theme-fixes 将 .el-alert 强制 #0c2231） === */
body.theme-dark .page.source-page .el-alert.provenance-alert,
body:not(.login-active) .app-main .page.source-page .el-alert.provenance-alert {
  border: 1px solid rgba(78, 200, 255, 0.18) !important;
  border-radius: 13px !important;
  background: rgba(8, 42, 92, 0.35) !important;
  box-shadow:
    inset 0 1px 0 rgba(161, 231, 255, 0.08),
    0 8px 32px rgba(0, 10, 40, 0.25) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}
body.theme-dark .page.source-page .el-alert.provenance-alert .el-alert__title,
body:not(.login-active) .app-main .page.source-page .el-alert.provenance-alert .el-alert__title {
  color: #d6f1ff !important;
}

/* === 4. 两个 .panel 面板（theme-fixes 将 .panel 强制 #0a1c2b + 阴影清空 + 浮动动画） === */
body.theme-dark .app-main:not(.app-main--dashboard) .page.source-page .panel.import-history-panel,
body:not(.login-active) .app-main .page.source-page .panel.import-history-panel {
  overflow: hidden;
  padding: 0;
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
body.theme-dark .app-main:not(.app-main--dashboard) .page.source-page .panel.import-history-panel::before,
body:not(.login-active) .app-main .page.source-page .panel.import-history-panel::before {
  display: none !important;
}

body.theme-dark .app-main:not(.app-main--dashboard) .page.source-page .panel.source-table-panel,
body:not(.login-active) .app-main .page.source-page .panel.source-table-panel {
  overflow: hidden;
  padding: 0;
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
body.theme-dark .app-main:not(.app-main--dashboard) .page.source-page .panel.source-table-panel::before,
body:not(.login-active) .app-main .page.source-page .panel.source-table-panel::before {
  display: none !important;
}
</style>

<style scoped>
.source-page { display: grid; gap: 16px; }
.source-page :deep(.page-toolbar) { justify-content: stretch; }
.toolbar { display: flex; width: 100%; align-items: center; justify-content: space-between; gap: 16px; }
.toolbar-actions { display: flex; align-items: center; gap: 10px; }
.sync-note { color: #83a9c5; font-size: 12px; }
.source-summary { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.source-summary article { padding: 16px 18px; }
.source-summary span { display: block; color: #85a9c4; font-size: 13px; }
.source-summary strong { display: block; margin-top: 7px; color: #effbff; font-size: 28px; line-height: 1; }
.source-summary small { display: block; margin-top: 7px; color: #5f86a4; font-size: 11px; }
.table-head { display: flex; align-items: center; justify-content: space-between; gap: 18px; padding: 18px 20px; border-bottom: 1px solid rgba(75, 149, 201, .14); }
.table-head h3 { margin: 0; color: #e7f8ff; font-size: 18px; }.table-head p { margin: 5px 0 0; color: #6f95b1; font-size: 12px; }.table-head .el-input { width: 280px; }
.source-link { border: 0; padding: 0; background: transparent; color: inherit; text-align: left; cursor: pointer; }.source-link:hover b { color: #4edcff; }
.source-link b, :deep(.el-table__cell b) { display: block; color: #dff7ff; font-size: 13px; }.source-link span, :deep(.el-table__cell small) { display: block; margin-top: 5px; color: #7195af; font-size: 11px; }
.license { color: #9ec1d8; font-size: 12px; }
.source-detail { display: grid; gap: 8px; padding: 14px 28px; color: #90b1c8; font-size: 12px; }.source-detail p { margin: 0; }.source-detail b { display: inline; color: #cfefff; }.source-detail a { color: #45d8ff; word-break: break-all; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.jd-upload { width: 100%; }.jd-upload :deep(.el-upload), .jd-upload :deep(.el-upload-dragger) { width: 100%; }
.parse-option { display: flex; align-items: center; justify-content: space-between; gap: 20px; border: 1px solid rgba(72, 154, 210, .2); padding: 13px 14px; background: rgba(8, 37, 69, .56); }
.parse-option b, .parse-option small { display: block; }.parse-option b { color: #dff7ff; font-size: 13px; }.parse-option small { margin-top: 4px; color: #7195af; font-size: 11px; }
:deep(.el-table) { --el-table-bg-color: transparent; --el-table-tr-bg-color: rgba(5, 27, 58, .58); --el-table-row-hover-bg-color: rgba(15, 63, 105, .72); --el-table-header-bg-color: rgba(8, 40, 78, .92); --el-table-border-color: rgba(73, 146, 198, .14); --el-table-text-color: #a9c7da; --el-table-header-text-color: #84dfff; }
:deep(.el-progress__text) { color: #bcecff; font-size: 11px !important; }
@media (max-width: 1450px) { .source-summary { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 760px) {
  .source-summary { grid-template-columns: 1fr; }
  .toolbar { align-items: stretch; flex-direction: column; }
  .toolbar-actions { align-items: stretch; flex-direction: column; }
  .table-head { align-items: stretch; flex-direction: column; }
  .table-head .el-input { width: 100%; }
  .form-grid { grid-template-columns: 1fr; gap: 0; }
}
</style>
