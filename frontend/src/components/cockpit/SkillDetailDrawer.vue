<template>
  <Teleport to="body">
    <div class="skill-drawer-mask" :class="{active: visible}" @click="handleClose"></div>
    <div class="skill-drawer" :class="{active: visible}">
      <button class="drawer-close" @click="handleClose">✕</button>
      <template v-if="skill">
        <div class="drawer-header">
          <h3 class="drawer-skill-name">{{ skill.name }}</h3>
          <span class="drawer-skill-status" :class="skill.status">{{ getStatusLabel(skill.status) }}</span>
        </div>

        <div class="drawer-level-section">
          <h4 class="drawer-level-title">能力等级</h4>
          <div class="drawer-level-compare">
            <div class="drawer-level-item">
              <div class="drawer-level-label">当前</div>
              <div class="drawer-level-bar">
                <div class="drawer-level-fill current" :style="{ width: (skill.currentLevel / 5 * 100) + '%' }"></div>
              </div>
              <div class="drawer-level-num" style="color: #4ed8ff;">Lv.{{ skill.currentLevel }}</div>
            </div>
            <div class="drawer-level-arrow">→</div>
            <div class="drawer-level-item">
              <div class="drawer-level-label">要求</div>
              <div class="drawer-level-bar">
                <div class="drawer-level-fill required" :style="{ width: (skill.requiredLevel / 5 * 100) + '%' }"></div>
              </div>
              <div class="drawer-level-num" style="color: #ffb65c;">Lv.{{ skill.requiredLevel }}</div>
            </div>
          </div>
          <div v-if="skill.currentLevel < skill.requiredLevel" style="margin-top: 12px; text-align: center;">
            <span style="font-size: 13px; color: #ff7088;">还差 {{ skill.requiredLevel - skill.currentLevel }} 级</span>
          </div>
          <div v-else style="margin-top: 12px; text-align: center;">
            <span style="font-size: 13px; color: #37d6a5;">✓ 已达到岗位要求</span>
          </div>
        </div>

        <div class="drawer-section">
          <h4 class="drawer-section-title">能力证据 ({{ evidences.length }})</h4>
          <div v-if="evidences.length === 0" style="font-size: 13px; color: #68768d; padding: 16px; text-align: center; background: rgba(135,169,220,0.04); border-radius: 10px;">
            暂无证据，通过上传简历、完成项目或认证来补充
          </div>
          <div v-else class="drawer-evidence-list">
            <div v-for="ev in evidences" :key="ev.id" class="drawer-evidence-item">
              <div class="drawer-evidence-header">
                <span class="drawer-evidence-source">{{ getSourceLabel(ev.sourceType) }}</span>
                <span class="drawer-evidence-cred">可信度 {{ Math.round(ev.credibility * 100) }}%</span>
              </div>
              <div class="drawer-evidence-title">{{ ev.sourceTitle }}</div>
              <div class="drawer-evidence-content">{{ ev.content }}</div>
            </div>
          </div>
        </div>

        <div v-if="skill.relatedProjects?.length" class="drawer-section">
          <h4 class="drawer-section-title">关联项目</h4>
          <div style="display: flex; flex-wrap: wrap; gap: 6px;">
            <span v-for="p in skill.relatedProjects" :key="p" style="padding: 4px 10px; background: rgba(143,124,255,0.1); border-radius: 6px; font-size: 12px; color: #8f7cff;">
              {{ p }}
            </span>
          </div>
        </div>

        <div class="drawer-section">
          <h4 class="drawer-section-title">学习建议</h4>
          <div class="drawer-suggestion">
            {{ skill.learningSuggestion }}
          </div>
        </div>

        <div class="drawer-actions">
          <button class="drawer-btn secondary" @click="handleClose">关闭</button>
          <button class="drawer-btn primary" v-if="skill.status !== 'mastered'">加入学习路径</button>
        </div>
      </template>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Skill, SkillEvidence, SkillStatus } from './types'
import { getEvidencesBySkill } from './mockData'

const props = defineProps<{
  skill: Skill | null
  modelValue: boolean
}>()
const emit = defineEmits<{
  'update:modelValue': [val: boolean]
  addToPath: [skill: Skill]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: v => emit('update:modelValue', v)
})

const evidences = computed<SkillEvidence[]>(() => {
  if (!props.skill) return []
  return getEvidencesBySkill(props.skill.id)
})

function handleClose() { visible.value = false }

function getStatusLabel(status: SkillStatus): string {
  const m: Record<SkillStatus, string> = {
    mastered: '✓ 已掌握', improving: '◈ 待提升',
    transferable: '↔ 可迁移', missing: '✗ 缺失'
  }
  return m[status]
}

function getSourceLabel(t: string): string {
  const map: Record<string, string> = {
    resume: '简历', project: '项目', certificate: '证书',
    portfolio: '作品集', interview: '面试', assessment: '测评', manual: '手动'
  }
  return map[t] || t
}
</script>
