<template>
  <div class="page resume-page">
    <PageHeader title="简历解析" desc="整理教育经历、项目经历、技能、证书、竞赛经历和岗位意向，并可同步到个人画像">
      <div class="toolbar">
        <el-button :disabled="!result" @click="copyToClipboard">复制解析摘要</el-button>
        <el-button v-if="isCandidate" :disabled="!result" type="primary" :loading="syncing" @click="syncProfile">同步到个人画像</el-button>
        <el-button type="primary" :loading="loading" @click="submit">{{ result ? '重新解析简历' : '解析简历' }}</el-button>
      </div>
    </PageHeader>

    <section class="resume-workflow panel">
      <div v-for="item in workflow" :key="item.title" class="workflow-item" :class="{ active: item.active }">
        <b>{{ item.index }}</b>
        <span>{{ item.title }}</span>
        <em>{{ item.desc }}</em>
      </div>
    </section>

    <div class="content-grid">
      <section class="panel span-5 input-panel">
        <div class="section-head">
          <div>
            <span>输入简历</span>
            <h3>上传或粘贴文本</h3>
          </div>
          <el-tag effect="light" type="success">PDF / Word 解析已接通</el-tag>
        </div>
        <el-upload drag action="#" :auto-upload="false" :show-file-list="false" :disabled="loading" accept=".txt,.md,.doc,.docx,.pdf" @change="handleFileChange">
          <el-icon><UploadFilled /></el-icon>
          <div class="upload-title">拖拽简历文件到此处，或点击选择</div>
          <p>支持 PDF、Word DOCX、TXT 和 Markdown，单个文件不超过 10MB；扫描版 PDF 需要先进行 OCR。</p>
        </el-upload>
        <el-alert
          v-if="selectedFileName"
          class="selected-file-alert"
          :title="`已选择：${selectedFileName}`"
          description="点击右上角“解析简历”后，将提取文件文字并交由 DeepSeek 解析。"
          type="success"
          show-icon
          @close="clearSelectedFile"
        />
        <el-input
          v-model="text"
          class="resume-textarea"
          type="textarea"
          :rows="15"
          placeholder="也可以直接粘贴简历文本，例如：姓名、学历、学校、项目经历、技能、证书、竞赛经历、岗位意向等。"
        />
      </section>

      <section class="panel span-7 result-panel">
        <el-empty v-if="!result" description="解析结果将在这里展示，解析后可一键同步到个人画像" />
        <template v-else>
          <div class="resume-summary">
            <div class="name-card">
              <span>候选人</span>
              <h3>{{ result.name || '未识别姓名' }}</h3>
              <p>{{ result.education || '学历未识别' }} · {{ result.major || '专业未识别' }} · {{ result.school || '学校未识别' }}</p>
            </div>
            <div class="intent-card">
              <span>岗位意向</span>
              <strong>{{ result.intention || '未识别' }}</strong>
            </div>
          </div>

          <div class="resume-metrics">
            <div class="metric-lite">
              <span>技能数</span>
              <strong>{{ skillRows.length }}</strong>
            </div>
            <div class="metric-lite">
              <span>项目经历</span>
              <strong>{{ result.projects?.length || 0 }}</strong>
            </div>
            <div class="metric-lite">
              <span>证书成果</span>
              <strong>{{ result.certificates?.length || 0 }}</strong>
            </div>
            <div class="metric-lite">
              <span>竞赛经历</span>
              <strong>{{ result.competitions?.length || 0 }}</strong>
            </div>
          </div>

          <div class="result-grid">
            <div class="result-block">
              <h3>技能清单</h3>
              <el-table :data="skillRows" height="260">
                <el-table-column prop="name" label="技能" min-width="130" />
                <el-table-column prop="level" label="熟练程度" width="120">
                  <template #default="{ row }">
                    <el-tag :type="levelTag(row.level)" effect="light">{{ row.level }}</el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div class="result-block">
              <h3>经历与成果</h3>
              <div class="tag-section">
                <span>项目经历</span>
                <el-tag v-for="item in result.projects || []" :key="item" type="primary" effect="light">{{ item }}</el-tag>
              </div>
              <div class="tag-section">
                <span>证书</span>
                <el-tag v-for="item in result.certificates || []" :key="item" type="success" effect="light">{{ item }}</el-tag>
              </div>
              <div class="tag-section">
                <span>竞赛 / 奖项</span>
                <el-tag v-for="item in result.competitions || []" :key="item" type="warning" effect="light">{{ item }}</el-tag>
              </div>
            </div>
          </div>

          <div class="next-actions">
            <el-button v-if="isCandidate" type="primary" :loading="syncing" @click="syncProfile">同步到个人画像</el-button>
            <el-button @click="router.push('/match-analysis')">进入匹配分析</el-button>
            <el-button @click="router.push('/learning-path')">查看学习路径</el-button>
          </div>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { UploadFilled } from '@element-plus/icons-vue'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import { loadPageState, savePageState } from '@/utils/pageState'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const syncing = ref(false)
const result = ref<any>()
const text = ref('姓名：林一\n本科 计算机科学与技术 示例大学\n熟悉 Python、RAG、LangChain、FastAPI、Docker，参与企业知识库问答系统项目，获得软考中级。')
const pendingFile = ref<File>()
const selectedFileName = ref('')
const isCandidate = computed(() => auth.role === 'candidate')
const skillRows = computed(() => result.value?.skills || [])
const workflow = computed(() => [
  { index: '01', title: '输入简历', desc: '上传或粘贴文本', active: true },
  { index: '02', title: '结构化解析', desc: '抽取教育、技能、项目', active: Boolean(result.value) },
  { index: '03', title: '同步画像', desc: '把经历整理进个人中心', active: false },
  { index: '04', title: '匹配岗位', desc: '查看差距与建议', active: false }
])

async function submit() {
  if (!pendingFile.value && !text.value.trim()) {
    ElMessage.warning('请先上传或粘贴简历内容')
    return
  }
  loading.value = true
  try {
    if (pendingFile.value) {
      const response = await api.parseResumeFile(pendingFile.value)
      text.value = response.extracted_text || ''
      result.value = response.result
      pendingFile.value = undefined
      selectedFileName.value = ''
      ElMessage.success(`已解析并保存为历史简历 #${result.value?.resume_id || '-'}，现在可直接进入匹配分析`)
    } else {
      result.value = await api.parseResume(text.value)
      ElMessage.success(`简历解析完成并已保存为历史简历 #${result.value?.resume_id || '-'}`)
    }
    localStorage.setItem('last_parsed_resume', JSON.stringify(result.value))
    persistState()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '简历解析失败，请检查文件格式或后端服务')
  } finally {
    loading.value = false
  }
}

async function syncProfile() {
  if (!result.value) return
  syncing.value = true
  try {
    const current = await api.myProfile()
    const payload = {
      ...current,
      real_name: result.value.name || current.real_name,
      education: result.value.education || current.education,
      major: result.value.major || current.major,
      school: result.value.school || current.school,
      target_role: result.value.intention || current.target_role,
      skills: mergeList(current.skills, skillRows.value.map((item: any) => item.name || item)),
      certificates: mergeList(current.certificates, result.value.certificates || []),
      projects: mergeList(current.projects, result.value.projects || []),
      awards: mergeList(current.awards, result.value.competitions || []),
      self_summary: current.self_summary || buildSummary()
    }
    await api.updateMyProfile(payload)
    ElMessage.success('已同步到个人画像')
  } finally {
    syncing.value = false
  }
}

function handleFileChange(file: any) {
  const raw = file.raw as File | undefined
  if (!raw) return
  if (raw.size > 10 * 1024 * 1024) {
    ElMessage.warning('简历文件不能超过 10MB')
    return
  }
  if (/\.doc$/i.test(raw.name)) {
    ElMessage.warning('旧版 .doc 暂不支持，请在 Word 中另存为 .docx 后上传')
    return
  }
  if (!/\.(pdf|docx|txt|md)$/i.test(raw.name)) {
    ElMessage.warning('仅支持 PDF、DOCX、TXT 和 Markdown 文件')
    return
  }
  pendingFile.value = raw
  selectedFileName.value = raw.name
  result.value = undefined
  text.value = ''
  persistState()
  ElMessage.success('文件已选择，请点击“解析简历”')
}

function clearSelectedFile() {
  pendingFile.value = undefined
  selectedFileName.value = ''
}

function persistState() {
  savePageState('resume-parser', { text: text.value, result: result.value })
}

watch(text, persistState)

onMounted(() => {
  const cached = loadPageState<{ text?: string; result?: any }>('resume-parser')
  const legacyResult = localStorage.getItem('last_parsed_resume')
  if (cached) {
    if (typeof cached.text === 'string') text.value = cached.text
    result.value = cached.result
    return
  }
  if (legacyResult) {
    try {
      result.value = JSON.parse(legacyResult)
      persistState()
    } catch {
      /* ignore damaged legacy cache */
    }
  }
})

function mergeList(a: string[] = [], b: string[] = []) {
  return Array.from(new Set([...a, ...b].filter(Boolean)))
}

function buildSummary() {
  const skills = skillRows.value.map((item: any) => item.name || item).slice(0, 6).join('、')
  return `具备${skills || '岗位相关'}能力，目标岗位为${result.value?.intention || '新一代信息技术相关岗位'}。`
}

function levelTag(level = '') {
  if (/高级|熟练|精通/.test(level)) return 'success'
  if (/了解|基础/.test(level)) return 'warning'
  return 'primary'
}

function copyToClipboard() {
  if (!result.value) return
  const summary = `${result.value.name || ''}｜${result.value.education || ''}｜${result.value.school || ''}｜技能：${skillRows.value.map((item: any) => item.name || item).join('、')}`
  navigator.clipboard?.writeText(summary)
  ElMessage.success('解析摘要已复制')
}
</script>

<style scoped>
.selected-file-alert {
  margin: 14px 0;
}

.resume-workflow {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.workflow-item {
  border: 1px solid rgba(190, 213, 242, 0.78);
  border-radius: 18px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.56);
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.workflow-item.active {
  border-color: rgba(6, 182, 212, 0.38);
  background:
    radial-gradient(circle at 8% 0%, rgba(6, 182, 212, 0.13), transparent 34%),
    rgba(255, 255, 255, 0.66);
}

.workflow-item:hover,
.name-card:hover,
.intent-card:hover,
.metric-lite:hover,
.result-block:hover {
  border-color: rgba(6, 182, 212, 0.42);
  box-shadow: 0 18px 42px rgba(37, 99, 235, 0.12);
  transform: translateY(-2px);
}

.workflow-item b {
  color: var(--cyan);
  font-size: 13px;
  font-weight: 950;
}

.workflow-item span {
  display: block;
  margin-top: 10px;
  color: #0f2148;
  font-size: 17px;
  font-weight: 950;
}

.workflow-item em {
  display: block;
  margin-top: 6px;
  color: #64748b;
  font-style: normal;
  font-size: 12px;
  font-weight: 700;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 16px;
}

.section-head span {
  color: var(--cyan);
  font-size: 11px;
  font-weight: 950;
  letter-spacing: 0.14em;
}

.section-head h3 {
  margin: 7px 0 0;
  color: #071a3d;
}

.upload-title {
  margin-top: 8px;
  color: #0f2148;
  font-weight: 900;
}

:deep(.el-upload-dragger p) {
  color: #64748b;
  font-size: 12px;
  line-height: 1.6;
}

.resume-textarea {
  margin-top: 14px;
}

.resume-summary {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 210px;
  gap: 14px;
  margin-bottom: 14px;
}

.name-card,
.intent-card,
.metric-lite,
.result-block {
  border: 1px solid rgba(190, 213, 242, 0.75);
  border-radius: 18px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.6);
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.name-card span,
.intent-card span,
.metric-lite span,
.tag-section span {
  color: #64748b;
  font-size: 12px;
  font-weight: 850;
}

.name-card h3 {
  margin: 8px 0 6px;
  color: #071a3d;
  font-size: 24px;
}

.name-card p {
  margin: 0;
  color: #53657e;
  font-weight: 700;
}

.intent-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.intent-card strong {
  margin-top: 10px;
  color: #0f2f78;
  font-size: 20px;
}

.resume-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}

.metric-lite strong {
  display: block;
  margin-top: 8px;
  color: #071a3d;
  font-size: 26px;
}

.result-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.result-block h3 {
  margin: 0 0 12px;
}

.tag-section {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-bottom: 14px;
}

.tag-section span {
  flex: 0 0 76px;
}

.next-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 16px;
}

@media (max-width: 1100px) {
  .resume-workflow,
  .resume-summary,
  .resume-metrics,
  .result-grid {
    grid-template-columns: 1fr;
  }
}
</style>
