<template>
  <Teleport to="body">
    <div class="skill-drawer-mask" :class="{active: visible}" @click="handleClose"></div>
    <div class="skill-drawer" :class="{active: visible}">
      <div class="drawer-aurora"></div>
      <button class="drawer-close" @click="handleClose" aria-label="关闭">✕</button>
      <template v-if="skill">
        <div class="drawer-header">
          <div class="drawer-skill-cat">{{ skill.category }}</div>
          <div class="drawer-title-row">
            <h3 class="drawer-skill-name">{{ skill.name }}</h3>
            <span class="drawer-skill-status" :class="skill.status">{{ getStatusLabel(skill.status) }}</span>
          </div>
          <div class="drawer-meta-row">
            <span class="drawer-meta-item"><i class="dot"></i>熟练度 {{ Math.round(skill.proficiency * 100) }}%</span>
            <span v-if="skill.lastUsedAt" class="drawer-meta-item"><i class="dot"></i>最近使用 {{ skill.lastUsedAt }}</span>
            <span v-if="skill.transferableFrom" class="drawer-meta-item"><i class="dot"></i>由 {{ skill.transferableFrom }} 迁移</span>
          </div>
        </div>

        <div class="drawer-level-section">
          <h4 class="drawer-level-title">
            <span class="title-glyph"></span>能力等级
            <span v-if="gap > 0" class="level-delta-badge">差距 {{ gap }} 级</span>
            <span v-else class="level-delta-badge met">已达标</span>
          </h4>
          <div class="drawer-level-compare">
            <div class="drawer-level-item">
              <div class="drawer-level-label">当前</div>
              <div class="drawer-level-bar">
                <div class="drawer-scale"><span v-for="n in 5" :key="n"></span></div>
                <div class="drawer-level-fill current" :style="{ width: (skill.currentLevel / 5 * 100) + '%' }"></div>
              </div>
              <div class="drawer-level-num current">Lv.{{ skill.currentLevel }}</div>
            </div>
            <div class="drawer-level-arrow">
              <svg width="22" height="10" viewBox="0 0 22 10" fill="none">
                <path d="M0 5h18m0 0-4-4m4 4-4 4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="drawer-level-item">
              <div class="drawer-level-label">岗位要求</div>
              <div class="drawer-level-bar">
                <div class="drawer-scale"><span v-for="n in 5" :key="n"></span></div>
                <div class="drawer-level-fill required" :style="{ width: (skill.requiredLevel / 5 * 100) + '%' }"></div>
              </div>
              <div class="drawer-level-num required">Lv.{{ skill.requiredLevel }}</div>
            </div>
          </div>
          <div class="drawer-stats">
            <div class="drawer-stat">
              <span class="drawer-stat-label">熟练度</span>
              <div class="drawer-stat-meter">
                <div class="drawer-stat-fill p" :style="{ width: (skill.proficiency * 100) + '%' }"></div>
              </div>
              <span class="drawer-stat-val">{{ Math.round(skill.proficiency * 100) }}%</span>
            </div>
            <div class="drawer-stat">
              <span class="drawer-stat-label">岗位重要度</span>
              <div class="drawer-stat-meter">
                <div class="drawer-stat-fill i" :style="{ width: (skill.importance * 100) + '%' }"></div>
              </div>
              <span class="drawer-stat-val">{{ importanceLabel }}</span>
            </div>
          </div>
        </div>

        <div class="drawer-section">
          <h4 class="drawer-section-title"><span class="title-glyph"></span>能力证据 <em class="title-count">{{ evidences.length }}</em></h4>
          <div v-if="evidences.length === 0" class="drawer-evidence-empty">
            暂无证据，通过上传简历、完成项目或认证来补充
          </div>
          <div v-else class="drawer-evidence-list">
            <div v-for="ev in evidences" :key="ev.id" class="drawer-evidence-item" :data-src="ev.sourceType">
              <span class="drawer-evidence-rail"></span>
              <div class="drawer-evidence-header">
                <span class="drawer-evidence-source">
                  <i class="drawer-evidence-icon">{{ getSourceGlyph(ev.sourceType) }}</i>{{ getSourceLabel(ev.sourceType) }}
                </span>
                <span class="drawer-evidence-cred">
                  <span class="cred-meter"><span class="cred-fill" :style="{ width: (ev.credibility * 100) + '%' }"></span></span>
                  {{ Math.round(ev.credibility * 100) }}%
                </span>
              </div>
              <div class="drawer-evidence-title">{{ ev.sourceTitle }}</div>
              <div class="drawer-evidence-content">{{ ev.content }}</div>
            </div>
          </div>
        </div>

        <div v-if="skill.relatedProjects?.length" class="drawer-section">
          <h4 class="drawer-section-title"><span class="title-glyph"></span>关联项目</h4>
          <div class="drawer-project-tags">
            <span v-for="p in skill.relatedProjects" :key="p" class="drawer-project-tag">{{ p }}</span>
          </div>
        </div>

        <div class="drawer-section">
          <h4 class="drawer-section-title"><span class="title-glyph"></span>学习建议</h4>
          <div class="drawer-suggestion">
            <span class="suggestion-glyph"></span>
            <p>{{ skill.learningSuggestion }}</p>
          </div>
        </div>

        <div class="drawer-actions">
          <button class="drawer-btn secondary" @click="handleClose">关闭</button>
          <button class="drawer-btn primary" v-if="skill.status !== 'mastered'">
            <span>加入学习路径</span>
          </button>
        </div>
      </template>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Skill, SkillEvidence, SkillStatus } from './types'

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
  return props.skill.evidences || []
})

const gap = computed(() => (props.skill ? props.skill.requiredLevel - props.skill.currentLevel : 0))

const importanceLabel = computed(() => {
  const v = props.skill?.importance ?? 0
  if (v >= 0.85) return '核心'
  if (v >= 0.6) return '重要'
  if (v >= 0.35) return '常规'
  return '辅助'
})

function handleClose() { visible.value = false }

function getStatusLabel(status: SkillStatus): string {
  const m: Record<SkillStatus, string> = {
    mastered: '已掌握', improving: '待提升',
    transferable: '可迁移', missing: '缺失'
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

function getSourceGlyph(t: string): string {
  const map: Record<string, string> = {
    resume: '◈', project: '⬡', certificate: '✦',
    portfolio: '▣', interview: '◉', assessment: '◇', manual: '✎'
  }
  return map[t] || '◈'
}
</script>
