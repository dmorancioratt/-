<template>
  <div class="workflow-toolbar">
    <el-button :icon="RefreshLeft" plain @click="onReset">重置布局</el-button>

    <el-dropdown @command="onLoadConfig" trigger="click">
      <el-button :icon="FolderOpened" plain>
        加载工作流
        <el-icon class="el-icon--right"><ArrowDown /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item v-if="configs.length === 0" disabled>
            暂无历史工作流
          </el-dropdown-item>
          <el-dropdown-item
            v-for="cfg in configs"
            :key="cfg.id"
            :command="cfg.id"
          >
            #{{ cfg.id }} · {{ cfg.name }}
            <span v-if="cfg.is_default" class="cfg-default">默认</span>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <el-button :icon="DocumentCopy" plain @click="onSave" :loading="store.saving">
      保存工作流
    </el-button>

    <el-button type="primary" :icon="VideoPlay" @click="store.openTestDialog('什么是 RAG 工作流？')">
      测试运行
    </el-button>

    <div class="toolbar-spacer" />

    <div class="status-pill">
      <el-icon><Document /></el-icon>
      文档 <strong>{{ store.totalDocs }}</strong>
      · chunks <strong>{{ store.totalChunks }}</strong>
    </div>
    <div class="status-pill">
      <el-icon><Folder /></el-icon>
      当前: <strong>{{ store.configName }}</strong>
      <span v-if="store.configId" class="cfg-id">#{{ store.configId }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowDown,
  Document,
  DocumentCopy,
  Folder,
  FolderOpened,
  RefreshLeft,
  VideoPlay,
} from '@element-plus/icons-vue'
import { useWorkflowStore } from '@/stores/workflow'
import { ElDropdown, ElDropdownItem, ElDropdownMenu } from 'element-plus'

const store = useWorkflowStore()
const configs = ref<Array<{ id: number; name: string; is_default?: boolean }>>([])

async function refreshConfigs() {
  try {
    const list = await store.listConfigs()
    configs.value = Array.isArray(list) ? list : []
  } catch {
    configs.value = []
  }
}

function onReset() {
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
}

async function onSave() {
  let name = store.configName || ''
  if (store.configId) {
    try {
      const cfg = await store.save(name)
      ElMessage.success(`已保存为 #${cfg.id} · ${cfg.name}`)
      refreshConfigs()
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
    refreshConfigs()
  } catch (e: any) {
    if (e === 'cancel') return
    ElMessage.error(e?.message || '保存失败')
  }
}

async function onLoadConfig(id: number) {
  try {
    await store.load(id)
    ElMessage.success(`已加载 #${id} · ${store.configName}`)
  } catch (e: any) {
    ElMessage.error(e?.message || '加载失败')
  }
}

onMounted(() => {
  refreshConfigs()
})
</script>

<style scoped>
.workflow-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  margin-bottom: 12px;
  background: rgba(15,23,42,0.55);
  border: 1px solid rgba(91,155,213,0.18);
  border-radius: 12px;
  backdrop-filter: blur(8px);
}
.toolbar-spacer { flex: 1; }
.status-pill {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 4px 10px;
  font-size: 12px;
  color: #cbd5e1;
  background: rgba(91,155,213,0.06);
  border: 1px solid rgba(91,155,213,0.18);
  border-radius: 999px;
}
.status-pill strong {
  color: #e2e8f0;
  font-family: ui-monospace, Menlo, monospace;
  margin: 0 2px;
}
.cfg-id {
  margin-left: 4px;
  color: #93c5fd;
  font-family: ui-monospace, Menlo, monospace;
  font-size: 11px;
}
.cfg-default {
  margin-left: 6px;
  font-size: 10px;
  padding: 0 4px;
  background: rgba(52,211,153,0.18);
  color: #6ee7b7;
  border-radius: 3px;
}
</style>