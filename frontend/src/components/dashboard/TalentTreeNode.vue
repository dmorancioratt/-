<template>
  <div
    class="talent-node"
    :class="[`talent-node--${data.kind}`, `talent-node--${data.status}`, { 'is-selected': data.selected }]"
    :style="{ '--talent-progress': `${progress}%` }"
  >
    <Handle class="talent-node__handle" type="target" :position="Position.Top" />

    <span class="talent-node__orbit" aria-hidden="true"></span>
    <span class="talent-node__frame" aria-hidden="true"></span>

    <div class="talent-node__content">
      <span class="talent-node__icon" aria-hidden="true">
        <el-icon><component :is="nodeIcon" /></el-icon>
      </span>
      <span class="talent-node__copy">
        <b>{{ data.label }}</b>
        <small>{{ data.subtitle }}</small>
      </span>
      <span v-if="data.kind === 'skill'" class="talent-node__level">LV.{{ level }}</span>
    </div>

    <div v-if="data.kind === 'skill'" class="talent-node__meter" aria-hidden="true"><i></i></div>
    <Handle class="talent-node__handle" type="source" :position="Position.Bottom" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position, type NodeProps } from '@vue-flow/core'
import { Aim, Connection, Cpu, Lock, Tools } from '@element-plus/icons-vue'
import type { TalentNodeData } from './talentTreeTypes'

const props = defineProps<NodeProps<TalentNodeData>>()

const progress = computed(() => Math.max(0, Math.min(100, Math.round(props.data.progress || 0))))
const level = computed(() => Math.max(1, Math.min(5, Math.ceil(progress.value / 20))))
const nodeIcon = computed(() => {
  if (props.data.status === 'missing' && props.data.kind === 'skill') return Lock
  if (props.data.kind === 'core') return Aim
  if (props.data.branch === 'engineering') return Tools
  if (props.data.branch === 'general') return Connection
  return Cpu
})
</script>

<style scoped>
.talent-node {
  --node-color: #34d7ff;
  --node-color-rgb: 52, 215, 255;
  position: relative;
  width: 148px;
  height: 82px;
  color: #eefdff;
  cursor: pointer;
  filter: drop-shadow(0 8px 16px rgba(0, 4, 18, .55));
  transition: filter .25s ease, transform .25s ease;
}
.talent-node--core { width: 190px; height: 108px; --node-color: #5eeaff; --node-color-rgb: 94, 234, 255; }
.talent-node--branch { width: 124px; height: 92px; --node-color: #2f9fff; --node-color-rgb: 47, 159, 255; }
.talent-node--mastered { --node-color: #47f0dc; --node-color-rgb: 71, 240, 220; }
.talent-node--missing { --node-color: #e0a14b; --node-color-rgb: 224, 161, 75; color: #9eb0bd; }
.talent-node:hover,
.talent-node.is-selected { z-index: 4; filter: drop-shadow(0 0 16px rgba(var(--node-color-rgb), .62)) drop-shadow(0 10px 18px rgba(0, 4, 18, .6)); }
.talent-node.is-selected { transform: translateY(-3px) scale(1.06); }
.talent-node__frame,
.talent-node__content {
  position: absolute;
  inset: 0;
  clip-path: polygon(14px 0, calc(100% - 14px) 0, 100% 50%, calc(100% - 14px) 100%, 14px 100%, 0 50%);
}
.talent-node__frame {
  border: 1px solid rgba(var(--node-color-rgb), .72);
  background: rgba(3, 19, 42, .96);
  box-shadow: inset 0 0 22px rgba(var(--node-color-rgb), .11);
}
.talent-node__frame::before {
  position: absolute;
  inset: 4px;
  border: 1px solid rgba(var(--node-color-rgb), .18);
  clip-path: inherit;
  content: '';
}
.talent-node__frame::after {
  position: absolute;
  right: 16px;
  bottom: 7px;
  left: 16px;
  height: 1px;
  background: rgba(var(--node-color-rgb), .48);
  box-shadow: 0 0 8px rgba(var(--node-color-rgb), .56);
  content: '';
}
.talent-node--missing .talent-node__frame { border-color: rgba(224, 161, 75, .38); background: rgba(7, 17, 31, .96); box-shadow: inset 0 0 18px rgba(224, 161, 75, .05); }
.talent-node__orbit { display: none; }
.talent-node--core .talent-node__orbit,
.talent-node--branch .talent-node__orbit {
  position: absolute;
  inset: -12px;
  display: block;
  border: 1px solid rgba(var(--node-color-rgb), .25);
  border-radius: 50%;
  box-shadow: 0 0 18px rgba(var(--node-color-rgb), .12);
  animation: talent-orbit 8s linear infinite;
}
.talent-node--branch .talent-node__orbit { inset: -8px; }
.talent-node--core .talent-node__frame { clip-path: polygon(24px 0, calc(100% - 24px) 0, 100% 50%, calc(100% - 24px) 100%, 24px 100%, 0 50%); background: rgba(3, 27, 58, .98); box-shadow: inset 0 0 34px rgba(94, 234, 255, .2); }
.talent-node--branch .talent-node__frame,
.talent-node--branch .talent-node__content { clip-path: polygon(50% 0, 100% 28%, 88% 82%, 50% 100%, 12% 82%, 0 28%); }
.talent-node__content { display: grid; grid-template-columns: 30px minmax(0, 1fr) auto; align-items: center; gap: 8px; padding: 11px 16px; }
.talent-node--core .talent-node__content { grid-template-columns: 38px minmax(0, 1fr); padding: 18px 25px; }
.talent-node--branch .talent-node__content { display: flex; flex-direction: column; justify-content: center; gap: 5px; padding: 15px 12px; text-align: center; }
.talent-node__icon { display: grid; place-items: center; width: 29px; height: 29px; border: 1px solid rgba(var(--node-color-rgb), .48); color: var(--node-color); background: rgba(var(--node-color-rgb), .08); box-shadow: inset 0 0 12px rgba(var(--node-color-rgb), .11); }
.talent-node--core .talent-node__icon { width: 36px; height: 36px; font-size: 20px; }
.talent-node--branch .talent-node__icon { width: 30px; height: 30px; font-size: 17px; transform: rotate(45deg); }
.talent-node--branch .talent-node__icon :deep(.el-icon) { transform: rotate(-45deg); }
.talent-node__copy { min-width: 0; }
.talent-node__copy b,
.talent-node__copy small { display: block; letter-spacing: 0; }
.talent-node__copy b { overflow: hidden; color: inherit; font-size: 13px; line-height: 1.25; text-overflow: ellipsis; white-space: nowrap; }
.talent-node__copy small { overflow: hidden; margin-top: 5px; color: #6f9db8; font-size: 9px; text-overflow: ellipsis; white-space: nowrap; }
.talent-node--core .talent-node__copy b { color: #f1fdff; font-size: 17px; }
.talent-node--core .talent-node__copy small { color: #6ed9f4; font-size: 10px; }
.talent-node--branch .talent-node__copy b { color: #eafbff; font-size: 12px; }
.talent-node--branch .talent-node__copy small { margin-top: 3px; color: #6da8ca; font-size: 9px; }
.talent-node__level { color: var(--node-color); font-size: 8px; font-weight: 800; }
.talent-node__meter { position: absolute; right: 20px; bottom: 8px; left: 20px; height: 2px; overflow: hidden; background: rgba(83, 130, 158, .14); }
.talent-node__meter i { display: block; width: var(--talent-progress); height: 100%; background: var(--node-color); box-shadow: 0 0 7px rgba(var(--node-color-rgb), .75); }
.talent-node__handle { width: 1px; height: 1px; min-width: 1px; min-height: 1px; border: 0; opacity: 0; pointer-events: none; }
.talent-node--growing .talent-node__frame { animation: talent-pulse 2.7s ease-in-out infinite; }
@keyframes talent-pulse { 50% { border-color: rgba(52, 215, 255, 1); box-shadow: inset 0 0 28px rgba(52, 215, 255, .18), 0 0 13px rgba(52, 215, 255, .17); } }
@keyframes talent-orbit { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) { .talent-node__orbit, .talent-node--growing .talent-node__frame { animation: none; } }
</style>
