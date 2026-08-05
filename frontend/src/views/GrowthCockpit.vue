<template>
  <div class="cockpit-root">
    <header class="cockpit-nav">
      <div class="nav-left">
        <button class="nav-back" @click="goBack">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回
        </button>
        <div class="nav-title-group">
          <h1 class="nav-title">个人成长驾驶舱</h1>
          <div class="nav-meta">
            <span class="nav-stage">{{ profile.growthStage }}</span>
            <span class="nav-sep">·</span>
            <span>最近更新 {{ profile.updatedAt }}</span>
          </div>
        </div>
      </div>
      <div class="nav-right">
        <div class="role-switcher" @click="showRoleSwitch = !showRoleSwitch">
          <span class="role-icon">{{ currentRole.icon }}</span>
          <span class="role-name">{{ currentRole.name }}</span>
          <span class="role-arrow">▼</span>
          <div v-if="showRoleSwitch" class="role-dropdown" @click.stop>
            <div v-for="r in targetRoles" :key="r.id"
              class="role-option" :class="{active: r.id === currentRole.id}"
              @click="switchRole(r)">
              <span class="ro-icon">{{ r.icon }}</span>
              <div class="ro-info">
                <div class="ro-name">{{ r.name }}</div>
                <div class="ro-meta">{{ r.level }} · {{ r.city }} · {{ r.matchScore }}%</div>
              </div>
              <span v-if="r.id === currentRole.id" class="ro-check">✓</span>
            </div>
          </div>
        </div>
        <button class="nav-btn">更新简历</button>
        <button class="nav-btn primary">重新分析</button>
        <div class="nav-avatar">{{ profile.name.charAt(0) }}</div>
      </div>
    </header>

    <main class="first-screen">
      <aside class="left-col">
        <div class="panel">
          <div class="panel-header">
            <h2 class="panel-title">岗位匹配概览</h2>
          </div>
          <div class="match-overview">
            <div class="match-target">
              <div class="match-role-name">{{ currentRole.name }}</div>
              <div class="match-role-meta">{{ currentRole.level }} · {{ currentRole.city }}</div>
            </div>
            <div class="match-score-block">
              <div class="match-score-num">{{ currentRole.matchScore }}<span class="pct">%</span></div>
              <div class="match-score-label">综合匹配度</div>
              <div class="match-change up">
                <span class="change-icon">↑</span>
                较上次提升 {{ currentRole.matchChange }}%
              </div>
            </div>
            <div class="match-estimate">
              <svg class="clock-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              预计准备时间：{{ currentRole.estimatedReadyDays }} 天
            </div>
          </div>
          <div class="match-dimensions">
            <div v-for="dim in matchDimensions" :key="dim.key" class="dim-row">
              <span class="dim-name">{{ dim.name }}</span>
              <div class="dim-bar-wrap">
                <div class="dim-bar" :style="{width: dim.val+'%', background: dim.color}"></div>
              </div>
              <span class="dim-val">{{ dim.val }}</span>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header">
            <h2 class="panel-title">核心技能差距</h2>
            <span class="panel-hint">Top 3 最需关注</span>
          </div>
          <div class="gap-list">
            <div v-for="gap in coreGaps" :key="gap.id" class="gap-item">
              <div class="gap-header">
                <span class="gap-name">{{ gap.name }}</span>
                <span class="gap-impact">{{ gap.impact }}</span>
              </div>
              <div class="gap-levels">
                <span class="gap-level current">Lv.{{ gap.current }}</span>
                <span class="gap-arrow">→</span>
                <span class="gap-level required">Lv.{{ gap.required }}</span>
                <span class="gap-badge">差 {{ gap.gap }} 级</span>
              </div>
              <div class="gap-desc">{{ gap.desc }}</div>
              <button class="gap-action">加入学习路径</button>
            </div>
          </div>
        </div>
      </aside>

      <section class="center-col">
        <SkillGalaxy
          :skills="skills"
          :profile="profile"
          :selected-skill="selectedSkill"
          :filter="skillFilter"
          :match-score="currentRole.matchScore"
          @select="onSelectSkill"
          @filter-change="skillFilter = $event"
        />
      </section>

      <aside class="right-col">
        <div class="panel next-task-panel">
          <div class="panel-header">
            <h2 class="panel-title">下一步最值得做</h2>
          </div>
          <div class="next-task-card">
            <div class="nt-title">{{ nextTask.title }}</div>
            <div class="nt-reason">{{ nextTask.reason }}</div>
            <div class="nt-meta">
              <div class="nt-meta-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
                预计耗时 {{ nextTask.duration }}
              </div>
            </div>
            <div class="nt-skills">
              <span class="nt-skills-label">关联技能：</span>
              <span v-for="(sk, i) in nextTask.skills" :key="i" class="nt-skill-tag">{{ sk }}</span>
            </div>
            <div class="nt-impact">
              <div class="nt-impact-label">完成后预计匹配度</div>
              <div class="nt-impact-values">
                <span class="nt-val from">{{ nextTask.currentMatch }}%</span>
                <span class="nt-arrow">→</span>
                <span class="nt-val to">{{ nextTask.expectedMatch }}%</span>
              </div>
            </div>
            <button class="nt-start-btn">开始任务</button>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header">
            <h2 class="panel-title">本周成长计划</h2>
          </div>
          <div class="week-plan">
            <div class="wp-stats">
              <div class="wp-stat">
                <div class="wp-num">{{ weekPlan.tasksLeft }}</div>
                <div class="wp-label">待完成任务</div>
              </div>
              <div class="wp-stat">
                <div class="wp-num">{{ weekPlan.hoursNeeded }}<span class="wp-unit">h</span></div>
                <div class="wp-label">预计投入</div>
              </div>
              <div class="wp-stat">
                <div class="wp-num">{{ weekPlan.skillsBoosted }}</div>
                <div class="wp-label">提升技能</div>
              </div>
              <div class="wp-stat highlight">
                <div class="wp-num">+{{ weekPlan.matchBoost }}<span class="wp-unit">%</span></div>
                <div class="wp-label">匹配度</div>
              </div>
            </div>
            <button class="wp-view-btn">查看学习路径 →</button>
          </div>
        </div>
      </aside>
    </main>

    <section class="second-screen">
      <div class="section-header">
        <h2 class="section-title">成长路线</h2>
        <p class="section-desc">从基础补齐到求职冲刺的完整路径</p>
      </div>
      <div class="learning-path-container">
        <div class="path-main">
          <div class="path-track">
            <div v-for="(stage, idx) in growthStages" :key="stage.id"
              class="path-node" :class="stage.status">
              <div class="node-dot">
                <span v-if="stage.status === 'completed'" class="dot-check">✓</span>
                <span v-else-if="stage.status === 'in-progress'" class="dot-spinner"></span>
                <span v-else class="dot-num">{{ idx + 1 }}</span>
              </div>
              <div class="node-content">
                <div class="node-icon">{{ stage.icon }}</div>
                <div class="node-name">{{ stage.name }}</div>
                <div class="node-desc">{{ stage.description }}</div>
                <div v-if="stage.status === 'in-progress'" class="node-progress">
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{width: stage.progress+'%'}"></div>
                  </div>
                  <span class="progress-text">{{ stage.progress }}%</span>
                </div>
                <div v-if="stage.status !== 'locked'" class="node-meta">
                  <span>预计 {{ stage.estimatedDays }} 天</span>
                  <span v-if="stage.expectedMatchIncrease">匹配度 +{{ stage.expectedMatchIncrease }}%</span>
                </div>
              </div>
              <div v-if="idx < growthStages.length - 1" class="node-connector" :class="{done: stage.status === 'completed'}"></div>
            </div>
          </div>
        </div>
        <div class="path-side">
          <div class="panel" style="height: 100%;">
            <div class="panel-header">
              <h3 class="panel-title-sm">简历能力证据库</h3>
            </div>
            <div class="resume-info">
              <div class="resume-file">{{ resume.fileName }}</div>
              <div class="resume-version">版本 {{ resume.version }} · {{ resume.updatedDays }} 天前更新</div>
            </div>
            <div class="resume-mini-stats">
              <div class="rms-item">
                <div class="rms-num">{{ resume.skillsExtracted }}</div>
                <div class="rms-label">提取技能</div>
              </div>
              <div class="rms-item">
                <div class="rms-num">{{ resume.projectsExtracted }}</div>
                <div class="rms-label">项目</div>
              </div>
              <div class="rms-item">
                <div class="rms-num">{{ resume.quantifiedAchievements }}</div>
                <div class="rms-label">量化成果</div>
              </div>
            </div>
            <div class="resume-recent">
              <div class="rr-title">最近更新</div>
              <div v-for="(u, i) in resume.recentUpdates" :key="i" class="rr-item">
                <span class="rr-date">{{ u.date }}</span>
                <span class="rr-text">{{ u.detail }}</span>
              </div>
            </div>
            <button class="resume-action">查看解析详情</button>
            <button class="resume-action secondary">补充缺失证据</button>
          </div>
        </div>
      </div>
    </section>

    <section class="third-screen">
      <div class="section-header">
        <h2 class="section-title">能力演化与机会</h2>
      </div>
      <div class="third-grid">
        <div class="panel">
          <div class="panel-header">
            <h3 class="panel-title-sm">模拟面试成长轨迹</h3>
          </div>
          <div class="interview-stats">
            <div class="is-row">
              <div class="is-item">
                <div class="is-num">{{ interviews.length }}</div>
                <div class="is-label">模拟面试</div>
              </div>
              <div class="is-item">
                <div class="is-num">{{ latestInterview?.totalScore || 0 }}</div>
                <div class="is-label">最近得分</div>
              </div>
              <div class="is-item">
                <div class="is-num">{{ avgInterviewScore }}</div>
                <div class="is-label">平均分</div>
              </div>
            </div>
          </div>
          <div v-if="latestInterview" class="latest-interview">
            <div class="li-header">
              <span class="li-date">{{ latestInterview.date }}</span>
              <span class="li-score">{{ latestInterview.totalScore }} 分</span>
            </div>
            <div class="li-section">
              <div class="li-sec-title strengths">主要优势</div>
              <div class="li-tags">
                <span v-for="(s, i) in latestInterview.strengths.slice(0,3)" :key="i" class="li-tag strength">{{ s }}</span>
              </div>
            </div>
            <div class="li-section">
              <div class="li-sec-title weaknesses">待改进</div>
              <div class="li-tags">
                <span v-for="(w, i) in latestInterview.weaknesses.slice(0,2)" :key="i" class="li-tag weakness">{{ w }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="panel">
          <div class="panel-header">
            <h3 class="panel-title-sm">推荐岗位</h3>
          </div>
          <div class="recommend-list">
            <div v-for="r in recommendedRoles.slice(0,3)" :key="r.id" class="rec-item">
              <div class="rec-top">
                <div>
                  <div class="rec-name">{{ r.name }}</div>
                  <div class="rec-company">{{ r.company }}</div>
                </div>
                <div class="rec-match">
                  <div class="rec-score" :class="r.currentMatch >= 80 ? 'high' : r.currentMatch >= 70 ? 'mid' : 'low'">{{ r.currentMatch }}%</div>
                  <div class="rec-change up" v-if="r.matchChange >= 0">↑{{ r.matchChange }}%</div>
                </div>
              </div>
              <div class="rec-reason">{{ r.recommendReason }}</div>
              <div class="rec-footer">
                <span class="rec-gap">差距：{{ r.skillGaps.join('、') }}</span>
                <span class="rec-days">{{ r.estimatedDays }} 天</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="fourth-screen">
      <div class="section-header">
        <h2 class="section-title">个人成长时间线</h2>
        <button v-if="!showAllTimeline" class="section-more" @click="showAllTimeline = true">查看全部</button>
      </div>
      <div class="timeline-full">
        <div v-for="(ev, i) in displayedEvents" :key="ev.id" class="tl-item" :class="{milestone: i === 0 || ev.matchScoreChange >= 5}">
          <div class="tl-line">
            <div class="tl-dot" :class="ev.matchScoreChange > 0 ? 'up' : ''"></div>
            <div v-if="i < displayedEvents.length - 1" class="tl-connector"></div>
          </div>
          <div class="tl-content">
            <div class="tl-date">{{ ev.date }}</div>
            <div class="tl-title">{{ ev.title }}</div>
            <div class="tl-desc">{{ ev.description }}</div>
            <div class="tl-footer">
              <span class="tl-source">{{ ev.source }}</span>
              <span v-if="ev.matchScoreChange > 0" class="tl-match-up">+{{ ev.matchScoreChange }}%</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <SkillDetailDrawer
      v-model="drawerVisible"
      :skill="selectedSkill"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SkillGalaxy from '@/components/cockpit/SkillGalaxy.vue'
import SkillDetailDrawer from '@/components/cockpit/SkillDetailDrawer.vue'
import {
  mockProfile, mockTargetRoles, mockSkills,
  mockGrowthStages, mockInterviews, mockGrowthEvents, mockRecommendedRoles,
  mockResumeStats, mockNextTask, mockWeekPlan, mockCoreGaps, getMatchDimensions
} from '@/components/cockpit/mockData'
import type { Skill, TargetRole } from '@/components/cockpit/types'
import '@/components/cockpit/cockpit.css'

const router = useRouter()

const profile = ref(mockProfile)
const targetRoles = ref(mockTargetRoles)
const skills = ref(mockSkills)
const growthStages = ref(mockGrowthStages)
const interviews = ref(mockInterviews)
const growthEvents = ref(mockGrowthEvents)
const recommendedRoles = ref(mockRecommendedRoles)
const resume = ref(mockResumeStats)
const nextTask = ref(mockNextTask)
const weekPlan = ref(mockWeekPlan)
const coreGaps = ref(mockCoreGaps)

const currentRole = ref<TargetRole>(mockTargetRoles[0])
const selectedSkill = ref<Skill | null>(null)
const drawerVisible = ref(false)
const showRoleSwitch = ref(false)
const showAllTimeline = ref(false)
const skillFilter = ref({ status: 'all' as string, category: 'all', showCoreOnly: false })

const matchDimensions = computed(() => getMatchDimensions(currentRole.value))

const latestInterview = computed(() => interviews.value[interviews.value.length - 1])
const avgInterviewScore = computed(() => Math.round(interviews.value.reduce((s, i) => s + i.totalScore, 0) / interviews.value.length))

const displayedEvents = computed(() => showAllTimeline.value ? growthEvents.value : growthEvents.value.slice(-6))

function goBack() {
  router.push('/overview')
}

function onSelectSkill(skill: Skill) {
  selectedSkill.value = skill
  drawerVisible.value = true
}

function switchRole(role: TargetRole) {
  currentRole.value = role
  showRoleSwitch.value = false
  profile.value.targetRoleId = role.id
}

onMounted(() => {
})
</script>

<style scoped>
.cockpit-root {
  min-height: 100vh;
  background: transparent;
  color: #f4f7fc;
  font-size: 14px;
  line-height: 1.6;
  padding-bottom: 60px;
}

.cockpit-nav {
  height: 76px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: rgba(10, 20, 35, 0.92);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(78, 216, 255, 0.12);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 30px rgba(0,0,0,0.3), 0 1px 0 rgba(78,216,255,0.08) inset;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-back {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(135, 169, 220, 0.08);
  border: 1px solid rgba(135, 169, 220, 0.16);
  border-radius: 10px;
  color: #a8b4c8;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.nav-back:hover {
  background: rgba(78, 216, 255, 0.12);
  border-color: rgba(78, 216, 255, 0.35);
  color: #f4f7fc;
  box-shadow: 0 0 12px rgba(78,216,255,0.15);
}

.nav-title-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.nav-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  color: #f4f7fc;
}
.nav-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #68768d;
}
.nav-stage {
  padding: 2px 8px;
  background: rgba(78, 216, 255, 0.12);
  border-radius: 6px;
  color: #4ed8ff;
  font-size: 11px;
}
.nav-sep {
  color: rgba(135, 169, 220, 0.3);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-switcher {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(135, 169, 220, 0.08);
  border: 1px solid rgba(135, 169, 220, 0.16);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.role-switcher:hover {
  border-color: rgba(78, 216, 255, 0.3);
}
.role-icon { font-size: 16px; }
.role-name { font-size: 13px; color: #f4f7fc; }
.role-arrow { font-size: 9px; color: #68768d; }

.role-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 260px;
  background: rgba(14, 26, 43, 0.98);
  border: 1px solid rgba(135, 169, 220, 0.2);
  border-radius: 12px;
  overflow: hidden;
  z-index: 200;
  backdrop-filter: blur(20px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.4);
}
.role-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  cursor: pointer;
  transition: background 0.2s;
}
.role-option:hover { background: rgba(78, 216, 255, 0.08); }
.role-option.active { background: rgba(78, 216, 255, 0.12); }
.ro-icon { font-size: 18px; }
.ro-info { flex: 1; }
.ro-name { font-size: 13px; color: #f4f7fc; }
.ro-meta { font-size: 11px; color: #68768d; margin-top: 2px; }
.ro-check { color: #4ed8ff; font-size: 14px; }

.nav-btn {
  padding: 8px 16px;
  background: rgba(135, 169, 220, 0.08);
  border: 1px solid rgba(135, 169, 220, 0.16);
  border-radius: 10px;
  color: #a8b4c8;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.nav-btn:hover {
  border-color: rgba(78, 216, 255, 0.3);
  color: #f4f7fc;
}
.nav-btn.primary {
  background: linear-gradient(135deg, rgba(78,216,255,0.2), rgba(143,124,255,0.15));
  border-color: rgba(78, 216, 255, 0.45);
  color: #4ed8ff;
  box-shadow: 0 0 16px rgba(78,216,255,0.15), inset 0 1px 0 rgba(78,216,255,0.15);
}
.nav-btn.primary:hover {
  background: linear-gradient(135deg, rgba(78,216,255,0.3), rgba(143,124,255,0.22));
  box-shadow: 0 0 24px rgba(78,216,255,0.25), inset 0 1px 0 rgba(78,216,255,0.25);
  color: #fff;
}

.nav-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(78,216,255,0.25), rgba(143,124,255,0.25));
  border: 1.5px solid rgba(78, 216, 255, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 700;
  color: #4ed8ff;
  box-shadow: 0 0 16px rgba(78,216,255,0.25), inset 0 1px 0 rgba(255,255,255,0.15);
}

.first-screen {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr) 320px;
  gap: 20px;
  padding: 24px;
  min-height: 780px;
}

.left-col, .right-col {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.center-col {
  background: 
    radial-gradient(ellipse 80% 70% at center, rgba(78,216,255,0.08) 0%, rgba(143,124,255,0.04) 30%, transparent 70%);
  border-radius: 16px;
  position: relative;
  min-height: 760px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.panel {
  background: rgba(12, 24, 42, 0.85);
  border: 1px solid rgba(135, 169, 220, 0.14);
  border-radius: 16px;
  padding: 20px;
  backdrop-filter: blur(20px);
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 16px;
  right: 16px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(78,216,255,0.2), transparent);
  border-radius: 16px 16px 0 0;
  pointer-events: none;
}
.panel:hover {
  border-color: rgba(78, 216, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0,0,0,0.3), 0 0 20px rgba(78,216,255,0.06);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.panel-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #f4f7fc;
}
.panel-title-sm {
  font-size: 14px;
  font-weight: 600;
  margin: 0;
  color: #f4f7fc;
}
.panel-hint {
  font-size: 12px;
  color: #68768d;
}

.match-overview {
  margin-bottom: 20px;
}
.match-target {
  margin-bottom: 16px;
}
.match-role-name {
  font-size: 18px;
  font-weight: 700;
  color: #f4f7fc;
}
.match-role-meta {
  font-size: 12px;
  color: #68768d;
  margin-top: 2px;
}
.match-score-block {
  text-align: center;
  padding: 16px 0;
  border-top: 1px solid rgba(135, 169, 220, 0.1);
  border-bottom: 1px solid rgba(135, 169, 220, 0.1);
  margin-bottom: 12px;
}
.match-score-num {
  font-size: 52px;
  font-weight: 700;
  color: #4ed8ff;
  line-height: 1;
  text-shadow: 0 0 30px rgba(78,216,255,0.4), 0 0 60px rgba(78,216,255,0.15);
  filter: drop-shadow(0 0 8px rgba(78,216,255,0.3));
}
.pct {
  font-size: 20px;
  font-weight: 500;
  color: #a8b4c8;
}
.match-score-label {
  font-size: 13px;
  color: #68768d;
  margin-top: 4px;
}
.match-change {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  margin-top: 8px;
  padding: 3px 10px;
  border-radius: 8px;
}
.match-change.up {
  color: #37d6a5;
  background: rgba(55, 214, 165, 0.1);
}
.change-icon { font-size: 10px; }
.match-estimate {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #ffb65c;
}
.clock-icon { opacity: 0.8; }

.match-dimensions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.dim-row {
  display: grid;
  grid-template-columns: 70px 1fr 32px;
  gap: 10px;
  align-items: center;
  font-size: 12px;
}
.dim-name { color: #a8b4c8; }
.dim-bar-wrap {
  height: 6px;
  background: rgba(135, 169, 220, 0.1);
  border-radius: 3px;
  overflow: hidden;
}
.dim-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}
.dim-val {
  text-align: right;
  color: #f4f7fc;
  font-weight: 500;
}

.gap-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.gap-item {
  padding: 14px;
  background: rgba(255, 112, 136, 0.04);
  border: 1px solid rgba(255, 112, 136, 0.15);
  border-radius: 12px;
}
.gap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.gap-name {
  font-size: 14px;
  font-weight: 600;
  color: #f4f7fc;
}
.gap-impact {
  font-size: 12px;
  color: #37d6a5;
  font-weight: 500;
}
.gap-levels {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 12px;
}
.gap-level {
  padding: 2px 8px;
  border-radius: 6px;
}
.gap-level.current {
  background: rgba(168, 180, 200, 0.1);
  color: #a8b4c8;
}
.gap-level.required {
  background: rgba(78, 216, 255, 0.12);
  color: #4ed8ff;
}
.gap-arrow { color: #68768d; }
.gap-badge {
  margin-left: auto;
  padding: 2px 8px;
  background: rgba(255, 112, 136, 0.12);
  border-radius: 6px;
  color: #ff7088;
  font-size: 11px;
}
.gap-desc {
  font-size: 12px;
  color: #68768d;
  line-height: 1.5;
  margin-bottom: 10px;
}
.gap-action {
  width: 100%;
  padding: 8px;
  background: transparent;
  border: 1px solid rgba(78, 216, 255, 0.3);
  border-radius: 8px;
  color: #4ed8ff;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.gap-action:hover {
  background: rgba(78, 216, 255, 0.1);
}

.next-task-panel {
  border-color: rgba(78, 216, 255, 0.28);
  background: linear-gradient(180deg, rgba(78,216,255,0.08) 0%, rgba(12,24,42,0.9) 100%);
  box-shadow: 0 8px 32px rgba(0,0,0,0.3), 0 0 30px rgba(78,216,255,0.08), inset 0 1px 0 rgba(78,216,255,0.15);
}
.next-task-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.nt-title {
  font-size: 18px;
  font-weight: 700;
  color: #f4f7fc;
  line-height: 1.4;
}
.nt-reason {
  font-size: 13px;
  color: #a8b4c8;
  line-height: 1.5;
}
.nt-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #a8b4c8;
}
.nt-meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
.nt-skills {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}
.nt-skills-label { color: #68768d; }
.nt-skill-tag {
  padding: 2px 8px;
  background: rgba(143, 124, 255, 0.12);
  border-radius: 6px;
  color: #8f7cff;
  font-size: 11px;
}
.nt-impact {
  padding: 12px;
  background: rgba(14, 26, 43, 0.6);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.nt-impact-label {
  font-size: 12px;
  color: #68768d;
}
.nt-impact-values {
  display: flex;
  align-items: center;
  gap: 8px;
}
.nt-val {
  font-size: 20px;
  font-weight: 700;
}
.nt-val.from { color: #a8b4c8; }
.nt-val.to { color: #37d6a5; }
.nt-arrow { color: #68768d; font-size: 14px; }
.nt-start-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #4ed8ff 0%, #8f7cff 100%);
  border: none;
  border-radius: 12px;
  color: #07111f;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin-top: 4px;
  box-shadow: 0 4px 20px rgba(78,216,255,0.3), 0 0 40px rgba(143,124,255,0.15), inset 0 1px 0 rgba(255,255,255,0.25);
  position: relative;
  overflow: hidden;
}
.nt-start-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
  transition: left 0.6s;
}
.nt-start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(78,216,255,0.45), 0 0 60px rgba(143,124,255,0.25), inset 0 1px 0 rgba(255,255,255,0.35);
}
.nt-start-btn:hover::before {
  left: 100%;
}

.week-plan {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.wp-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.wp-stat {
  padding: 12px;
  background: rgba(135, 169, 220, 0.05);
  border-radius: 10px;
  text-align: center;
}
.wp-stat.highlight {
  background: rgba(55, 214, 165, 0.08);
}
.wp-num {
  font-size: 24px;
  font-weight: 700;
  color: #f4f7fc;
}
.wp-stat.highlight .wp-num { color: #37d6a5; }
.wp-unit {
  font-size: 12px;
  font-weight: 500;
  color: #a8b4c8;
}
.wp-label {
  font-size: 11px;
  color: #68768d;
  margin-top: 2px;
}
.wp-view-btn {
  width: 100%;
  padding: 10px;
  background: transparent;
  border: 1px solid rgba(135, 169, 220, 0.2);
  border-radius: 10px;
  color: #a8b4c8;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.wp-view-btn:hover {
  border-color: rgba(78, 216, 255, 0.3);
  color: #4ed8ff;
}

.second-screen, .third-screen, .fourth-screen {
  padding: 40px 24px 24px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.section-title {
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  color: #f4f7fc;
}
.section-desc {
  font-size: 13px;
  color: #68768d;
  margin: 6px 0 0;
}
.section-more {
  padding: 6px 14px;
  background: rgba(135, 169, 220, 0.08);
  border: 1px solid rgba(135, 169, 220, 0.16);
  border-radius: 8px;
  color: #a8b4c8;
  font-size: 12px;
  cursor: pointer;
}

.learning-path-container {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 20px;
}
.path-main {
  background: rgba(14, 26, 43, 0.82);
  border: 1px solid rgba(135, 169, 220, 0.16);
  border-radius: 16px;
  padding: 28px;
  backdrop-filter: blur(16px);
}
.path-track {
  display: flex;
  align-items: flex-start;
  gap: 0;
  overflow-x: auto;
  padding-bottom: 10px;
}
.path-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  min-width: 140px;
  flex: 1;
}
.node-dot {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  flex-shrink: 0;
  z-index: 2;
}
.path-node.completed .node-dot {
  background: rgba(55, 214, 165, 0.15);
  border: 2px solid #37d6a5;
  color: #37d6a5;
}
.path-node.in-progress .node-dot {
  background: rgba(78, 216, 255, 0.15);
  border: 2px solid #4ed8ff;
  color: #4ed8ff;
}
.path-node.available .node-dot {
  background: rgba(143, 124, 255, 0.1);
  border: 2px solid rgba(143, 124, 255, 0.5);
  color: #8f7cff;
}
.path-node.locked .node-dot {
  background: rgba(104, 118, 141, 0.1);
  border: 2px solid rgba(104, 118, 141, 0.3);
  color: #68768d;
}
.dot-spinner {
  width: 12px;
  height: 12px;
  border: 2px solid transparent;
  border-top-color: #4ed8ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.node-content {
  text-align: center;
  padding: 0 8px;
}
.node-icon {
  font-size: 24px;
  margin-bottom: 6px;
}
.node-name {
  font-size: 14px;
  font-weight: 600;
  color: #f4f7fc;
  margin-bottom: 4px;
}
.node-desc {
  font-size: 11px;
  color: #68768d;
  line-height: 1.4;
  margin-bottom: 8px;
}
.node-progress {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}
.progress-bar {
  flex: 1;
  height: 4px;
  background: rgba(135, 169, 220, 0.1);
  border-radius: 2px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4ed8ff, #8f7cff);
  border-radius: 2px;
}
.progress-text {
  font-size: 10px;
  color: #4ed8ff;
  min-width: 28px;
}
.node-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 10px;
  color: #68768d;
}

.node-connector {
  position: absolute;
  top: 20px;
  left: calc(50% + 20px);
  right: calc(-50% + 20px);
  height: 2px;
  background: rgba(135, 169, 220, 0.15);
  z-index: 1;
}
.node-connector.done {
  background: linear-gradient(90deg, #37d6a5, rgba(55, 214, 165, 0.3));
}

.resume-info {
  margin-bottom: 16px;
}
.resume-file {
  font-size: 13px;
  color: #f4f7fc;
  font-weight: 500;
  word-break: break-all;
}
.resume-version {
  font-size: 11px;
  color: #68768d;
  margin-top: 4px;
}
.resume-mini-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px;
  background: rgba(135, 169, 220, 0.04);
  border-radius: 10px;
}
.rms-item { text-align: center; }
.rms-num {
  font-size: 20px;
  font-weight: 700;
  color: #4ed8ff;
}
.rms-label {
  font-size: 10px;
  color: #68768d;
}
.resume-recent {
  margin-bottom: 16px;
}
.rr-title {
  font-size: 12px;
  color: #a8b4c8;
  margin-bottom: 10px;
}
.rr-item {
  display: flex;
  gap: 8px;
  font-size: 11px;
  margin-bottom: 8px;
  line-height: 1.4;
}
.rr-date {
  color: #ffb65c;
  flex-shrink: 0;
}
.rr-text { color: #a8b4c8; }

.resume-action {
  width: 100%;
  padding: 8px;
  background: rgba(78, 216, 255, 0.1);
  border: 1px solid rgba(78, 216, 255, 0.25);
  border-radius: 8px;
  color: #4ed8ff;
  font-size: 12px;
  cursor: pointer;
  margin-bottom: 8px;
  transition: all 0.2s;
}
.resume-action:hover { background: rgba(78, 216, 255, 0.18); }
.resume-action.secondary {
  background: transparent;
  border-color: rgba(135, 169, 220, 0.2);
  color: #a8b4c8;
}
.resume-action.secondary:hover {
  border-color: rgba(78, 216, 255, 0.3);
  color: #4ed8ff;
}

.third-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.interview-stats {
  margin-bottom: 16px;
}
.is-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.is-item {
  padding: 14px;
  background: rgba(135, 169, 220, 0.04);
  border-radius: 10px;
  text-align: center;
}
.is-num {
  font-size: 28px;
  font-weight: 700;
  color: #f4f7fc;
}
.is-label {
  font-size: 11px;
  color: #68768d;
  margin-top: 4px;
}

.latest-interview {
  padding: 14px;
  background: rgba(135, 169, 220, 0.04);
  border-radius: 10px;
}
.li-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(135, 169, 220, 0.1);
}
.li-date { font-size: 12px; color: #68768d; }
.li-score { font-size: 18px; font-weight: 700; color: #4ed8ff; }
.li-section { margin-bottom: 10px; }
.li-sec-title {
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 6px;
}
.li-sec-title.strengths { color: #37d6a5; }
.li-sec-title.weaknesses { color: #ff7088; }
.li-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.li-tag {
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
}
.li-tag.strength {
  background: rgba(55, 214, 165, 0.1);
  color: #37d6a5;
}
.li-tag.weakness {
  background: rgba(255, 112, 136, 0.1);
  color: #ff7088;
}

.recommend-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.rec-item {
  padding: 14px;
  background: rgba(135, 169, 220, 0.04);
  border: 1px solid rgba(135, 169, 220, 0.1);
  border-radius: 10px;
  transition: all 0.2s;
  cursor: pointer;
}
.rec-item:hover {
  border-color: rgba(78, 216, 255, 0.3);
  background: rgba(78, 216, 255, 0.04);
}
.rec-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}
.rec-name {
  font-size: 14px;
  font-weight: 600;
  color: #f4f7fc;
}
.rec-company {
  font-size: 11px;
  color: #68768d;
  margin-top: 2px;
}
.rec-match { text-align: right; }
.rec-score {
  font-size: 22px;
  font-weight: 700;
}
.rec-score.high { color: #37d6a5; }
.rec-score.mid { color: #4ed8ff; }
.rec-score.low { color: #ffb65c; }
.rec-change {
  font-size: 11px;
  margin-top: 2px;
}
.rec-change.up { color: #37d6a5; }
.rec-reason {
  font-size: 12px;
  color: #a8b4c8;
  line-height: 1.5;
  margin-bottom: 8px;
}
.rec-footer {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #68768d;
}
.rec-gap { color: #ff7088; }
.rec-days { color: #ffb65c; }

.timeline-full {
  position: relative;
  padding-left: 20px;
}
.tl-item {
  display: flex;
  gap: 20px;
  padding-bottom: 24px;
  position: relative;
}
.tl-line {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}
.tl-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(135, 169, 220, 0.3);
  border: 2px solid rgba(135, 169, 220, 0.2);
  flex-shrink: 0;
  z-index: 2;
}
.tl-dot.up {
  background: #4ed8ff;
  border-color: #4ed8ff;
  box-shadow: 0 0 10px rgba(78, 216, 255, 0.4);
}
.tl-item.milestone .tl-dot {
  background: #37d6a5;
  border-color: #37d6a5;
  width: 16px;
  height: 16px;
  box-shadow: 0 0 12px rgba(55, 214, 165, 0.4);
}
.tl-connector {
  width: 2px;
  flex: 1;
  background: rgba(135, 169, 220, 0.12);
  margin-top: 4px;
}
.tl-content {
  flex: 1;
  padding-bottom: 4px;
}
.tl-date {
  font-size: 12px;
  color: #68768d;
  margin-bottom: 4px;
}
.tl-title {
  font-size: 15px;
  font-weight: 600;
  color: #f4f7fc;
  margin-bottom: 4px;
}
.tl-desc {
  font-size: 13px;
  color: #a8b4c8;
  line-height: 1.5;
  margin-bottom: 6px;
}
.tl-footer {
  display: flex;
  gap: 12px;
  font-size: 11px;
}
.tl-source { color: #68768d; }
.tl-match-up {
  color: #37d6a5;
  font-weight: 500;
}

@media (max-width: 1440px) {
  .first-screen {
    grid-template-columns: 260px minmax(0, 1fr) 300px;
    gap: 16px;
    padding: 20px;
  }
}

@media (max-width: 1200px) {
  .first-screen {
    grid-template-columns: 1fr;
  }
  .center-col { min-height: 500px; }
  .learning-path-container {
    grid-template-columns: 1fr;
  }
  .third-grid {
    grid-template-columns: 1fr;
  }
}
</style>
