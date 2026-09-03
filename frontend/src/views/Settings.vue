<template>
  <div class="page">
    <PageHeader title="系统设置" desc="管理智能服务配置、图谱写入规则和审核阈值" />
    <div class="content-grid">
      <div class="panel span-6">
        <h3>智能服务配置</h3>
        <el-form label-width="130px">
          <el-form-item label="当前服务">
            <el-tag :type="ai.enabled ? 'success' : 'primary'">{{ providerLabel }}</el-tag>
          </el-form-item>
          <el-form-item label="模型名称">
            <el-input :model-value="modelLabel" disabled />
          </el-form-item>
          <el-form-item label="接口状态">
            <el-tag :type="ai.enabled ? 'success' : 'danger'">
              {{ ai.enabled ? '真实模型服务已连接' : '真实模型服务未配置' }}
            </el-tag>
          </el-form-item>
          <el-form-item label="支持任务">
            <div class="tag-list">
              <el-tag v-for="item in ai.supported_tasks || []" :key="item" type="info">{{ item }}</el-tag>
            </div>
          </el-form-item>
        </el-form>
        <el-alert
          style="margin-top: 14px"
          title="切换外部模型服务时，在环境变量中配置服务地址、密钥和模型名称即可。"
          type="info"
          :closable="false"
        />
      </div>
      <div class="panel span-6">
        <h3>图谱写入规则</h3>
        <el-checkbox v-model="rules.evidence_required">写入岗位定义、技能关系、更新记录时必须带 evidence</el-checkbox>
        <el-checkbox v-model="rules.low_confidence_review">低置信度内容进入人工审核</el-checkbox>
        <el-checkbox v-model="rules.version_history">岗位能力更新保留版本记录</el-checkbox>
        <el-form label-width="130px" style="margin-top: 18px">
          <el-form-item label="低置信度阈值">
            <el-slider v-model="threshold" :min="50" :max="95" />
          </el-form-item>
        </el-form>
        <div class="settings-actions">
          <span v-if="updatedAt" class="updated-at">上次保存：{{ updatedAt }}</span>
          <el-button type="primary" :loading="saving" @click="saveRules">保存治理规则</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

const threshold = ref(72)
const ai = ref<any>({})
const saving = ref(false)
const updatedAt = ref('')
const providerLabel = computed(() => ai.value.provider === 'mock' ? '模拟服务（仅自动化测试）' : ai.value.provider || '未配置')
const modelLabel = computed(() => ai.value.model || '未配置')
const rules = reactive({
  evidence_required: true,
  low_confidence_review: true,
  version_history: true,
})

onMounted(async () => {
  try {
    const [aiStatus, settings] = await Promise.all([api.aiStatus(), api.governanceSettings()])
    ai.value = aiStatus
    rules.evidence_required = settings.evidence_required
    rules.low_confidence_review = settings.low_confidence_review
    rules.version_history = settings.version_history
    threshold.value = Math.round(Number(settings.confidence_threshold) * 100)
    updatedAt.value = formatTime(settings.updated_at)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '系统设置加载失败')
  }
})

function formatTime(value: string | undefined) {
  return value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : ''
}

async function saveRules() {
  saving.value = true
  try {
    const saved = await api.updateGovernanceSettings({
      ...rules,
      confidence_threshold: threshold.value / 100,
    })
    updatedAt.value = formatTime(saved.updated_at)
    ElMessage.success('治理规则已保存并应用到后端处理流程')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '治理规则保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.settings-actions { margin-top: 20px; display: flex; align-items: center; justify-content: flex-end; gap: 14px; }
.updated-at { color: #94a3b8; font-size: 12px; }
</style>
