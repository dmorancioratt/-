<template>
  <div class="workflow-toolbar">
    <div class="toolbar-left">
      <div class="workflow-title">
        <el-icon :size="16" color="#60a5fa"><Document /></el-icon>
        <span class="title-text">可视化 RAG 防幻觉工作流</span>
        <el-icon :size="14" color="#fbbf24"><Warning /></el-icon>
      </div>
      <div class="save-indicator">
        <span class="save-dot"></span>
        自动保存于 {{ autoSaveTime }}
      </div>
    </div>

    <div class="toolbar-right">
      <el-button
        type="primary"
        :icon="VideoPlay"
        @click="store.openTestDialog('什么是 RAG 工作流？')"
      >
        运行测试
      </el-button>

      <el-button :icon="DocumentCopy" @click="onSave" :loading="store.saving">
        保存
      </el-button>

      <el-button :icon="Upload" plain @click="onSave">
        更新工作流
      </el-button>

      <el-dropdown @command="onCommand" trigger="click">
        <el-button circle :icon="MoreFilled" />
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item :command="'reset'">重置布局</el-dropdown-item>
            <el-dropdown-item :command="'export'">导出 JSON</el-dropdown-item>
            <el-dropdown-item :command="'import'">导入 JSON</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, DocumentCopy, MoreFilled, Upload, VideoPlay, Warning } from '@element-plus/icons-vue'
import { useWorkflowStore } from '@/stores/workflow'

const store = useWorkflowStore()
const autoSaveTime = ref('14:32:18')

async function onSave() {
  let name = store.configName || ''
  if (store.configId) {
    try {
      const cfg = await store.save(name)
      ElMessage.success(`已保存为 #${cfg.id} · ${cfg.name}`)
      autoSaveTime.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
    } catch (e: any) {
      ElMessage.error(e?.message || '保存失败')
    }
    return
  }
  try {
    const { value } = await ElMessageBox.prompt('请输入工作流名称', '保存工作流', {
      inputValue: name || '默认 RAG 流程',
      confirmButtonText: '保存',
      cancelButtonText: '取消',
    })
    if (!value || !value.trim()) return
    const cfg = await store.save(value.trim())
    ElMessage.success(`已保存为 #${cfg.id} · ${cfg.name}`)
    autoSaveTime.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
  } catch (e: any) {
    if (e === 'cancel') return
    ElMessage.error(e?.message || '保存失败')
  }
}

function onCommand(cmd: string) {
  if (cmd === 'reset') {
    ElMessageBox.confirm('重置会清空当前画布节点和连线，确定吗？', '重置布局', {
      confirmButtonText: '重置',
      cancelButtonText: '取消',
      type: 'warning',
    })
      .then(() => {
        store.resetLayout()
        ElMessage.success('已重置为默认布局')
      })
      .catch(() => {})
  } else if (cmd === 'export') {
    const data = store.exportJSON()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `rag-workflow-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }
}
</script>

<style scoped>
.workflow-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: rgba(15, 23, 42, 0.7);
  border-bottom: 1px solid rgba(91, 155, 213, 0.15);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.workflow-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #e2e8f0;
}

.title-text {
  background: linear-gradient(90deg, #60a5fa, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.save-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
}

.save-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 6px rgba(52, 211, 153, 0.6);
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
