<template>
  <div class="run-progress-bar">
    <div class="progress-head">
      <span class="progress-title">
        <el-icon :size="14" :class="{ 'spin': store.runtime.running }"><Loading /></el-icon>
        RAG 流程进度
      </span>
      <span class="progress-meta">
        <span v-if="store.runtime.running" class="state running">运行中</span>
        <span v-else-if="knowledgeRequired" class="state warn">等待知识库</span>
        <span v-else-if="store.runtime.lastResult" class="state done">已完成</span>
        <span v-else class="state idle">待运行</span>
        <span class="percent">{{ store.runtime.progress }}%</span>
      </span>
    </div>

    <div class="progress-track">
      <div class="progress-fill" :style="{ width: store.runtime.progress + '%' }"></div>
    </div>

    <div class="stepper">
      <div class="stepper-baseline"></div>
      <div v-for="(s, i) in STAGES" :key="s" class="step" :class="stepClass(s, i)">
        <div class="step-dot">
          <el-icon v-if="stageStatus(s) === 'done'" :size="12"><Check /></el-icon>
          <el-icon v-else-if="stageStatus(s) === 'error'" :size="12"><Close /></el-icon>
          <span v-else>{{ i + 1 }}</span>
        </div>
        <div class="step-label" :title="stageOutput(s)">{{ s }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Check, Close, Loading } from '@element-plus/icons-vue'
import { useWorkflowStore } from '@/stores/workflow'

const store = useWorkflowStore()

const STAGES = ['问题解析', '本地知识库', 'Top-K 检索', '向量检索', '相关性判断', '大模型生成', '幻觉检测', '引用校验']
const knowledgeRequired = computed(() => store.runtime.lastResult?.guard_issues.some((issue) => issue.includes('本地知识库为空')) ?? false)

function stageStatus(stage: string): string {
  const log = store.runtime.logs.find((l) => l.stage === stage)
  return log ? log.status : 'idle'
}

function stageOutput(stage: string): string {
  const log = store.runtime.logs.find((l) => l.stage === stage)
  return log?.output || ''
}

function stepClass(stage: string, index: number): Record<string, boolean> {
  return {
    [`s-${stageStatus(stage)}`]: true,
    's-current': store.runtime.running && store.runtime.stageIndex === index,
  }
}
</script>

<style scoped>
.run-progress-bar {
  padding: 8px 20px 10px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.72) 55%, rgba(15, 23, 42, 0.9));
  border: 1px solid rgba(91, 155, 213, 0.22);
  border-radius: 10px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 16px rgba(2, 10, 40, 0.4);
}

.progress-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.progress-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #cbd5e1;
}

.progress-title .spin {
  animation: spin 1s linear infinite;
}

.progress-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
}

.state {
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 4px;
}
.state.running { color: #93c5fd; background: rgba(96, 165, 250, 0.15); }
.state.warn { color: #fbbf24; background: rgba(251, 191, 36, 0.15); }
.state.done { color: #46c8ff; background: rgba(70, 200, 255, 0.15); }
.state.idle { color: #64748b; background: rgba(30, 41, 59, 0.6); }

.percent {
  font-family: ui-monospace, Menlo, monospace;
  font-size: 12px;
  color: #60a5fa;
  min-width: 34px;
  text-align: right;
}

.progress-track {
  position: relative;
  height: 6px;
  border-radius: 3px;
  background: rgba(30, 41, 59, 0.6);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #52ddff, #52ddff, #8f7cff);
  box-shadow: 0 0 10px rgba(82, 221, 255, 0.40);
  transition: width 0.35s ease;
}

.stepper {
  position: relative;
  display: flex;
  margin-top: 12px;
}

.stepper-baseline {
  position: absolute;
  top: 12px;
  left: 0;
  right: 0;
  height: 2px;
  background: rgba(91, 155, 213, 0.15);
  z-index: 0;
}

.step {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  z-index: 1;
}

.step-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  background: #1e293b;
  border: 2px solid rgba(91, 155, 213, 0.25);
  transition: all 0.25s ease;
}

.step-label {
  font-size: 10px;
  color: #64748b;
  white-space: nowrap;
}

/* 状态着色 */
.step.s-done .step-dot {
  color: #0b1220;
  background: #46c8ff;
  border-color: #46c8ff;
  box-shadow: 0 0 10px rgba(70, 200, 255, 0.5);
}
.step.s-done .step-label { color: #46c8ff; }

.step.s-warn .step-dot {
  color: #0b1220;
  background: #fbbf24;
  border-color: #fbbf24;
}
.step.s-warn .step-label { color: #fbbf24; }

.step.s-error .step-dot {
  color: #fff;
  background: #f43f5e;
  border-color: #f43f5e;
  box-shadow: 0 0 10px rgba(244, 63, 94, 0.5);
}
.step.s-error .step-label { color: #f43f5e; }

.step.s-running .step-dot {
  color: #fff;
  border-color: #60a5fa;
  background: rgba(96, 165, 250, 0.25);
  box-shadow: 0 0 12px rgba(96, 165, 250, 0.7);
  animation: pulse 1.2s ease-in-out infinite;
}
.step.s-running .step-label { color: #93c5fd; }

.step.s-current .step-dot {
  border-color: #93c5fd;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 6px rgba(96, 165, 250, 0.5); transform: scale(1); }
  50% { box-shadow: 0 0 16px rgba(96, 165, 250, 0.9); transform: scale(1.12); }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
