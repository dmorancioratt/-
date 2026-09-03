<template>
  <div class="app-shell">
    <Teleport to="body">
      <div class="workspace-atmosphere" aria-hidden="true">
        <CosmosBackground />
      </div>
    </Teleport>

    <header class="app-header" v-if="!$route.meta.fullscreen">
      <div class="header-brand">
        <div class="brand-mark"><span>SR</span></div>
        <div class="brand-copy">
          <div class="brand-name">数融智联</div>
          <div class="brand-desc">智能驱动人才成长</div>
        </div>
      </div>

      <nav class="top-nav" ref="navRef">
        <button
          v-for="entry in visibleDirect"
          :key="'direct-' + entry.path"
          class="nav-trigger"
          :class="{ active: isDirectActive(entry) }"
          type="button"
          @click="navigateTo(entry.path)"
        >
          <el-icon v-if="entry.icon"><component :is="entry.icon" /></el-icon>
          <span>{{ entry.label }}</span>
        </button>
        <template v-for="group in visibleGroups" :key="group.key">
          <div class="nav-group" :ref="(el) => setTriggerRef(group.key, el as HTMLElement | null)">
            <button
              class="nav-trigger"
              :class="{ active: isGroupActive(group) || activeGroupKey === group.key }"
              type="button"
              @click.stop="toggleGroup(group.key)"
            >
              <el-icon v-if="group.icon"><component :is="group.icon" /></el-icon>
              <span>{{ group.label }}</span>
            </button>
          </div>
        </template>
      </nav>

      <div class="header-actions">
        <span class="role-tag">{{ roleLabel }}</span>
        <el-dropdown trigger="click" @command="handleUserCommand">
          <button class="user-chip">
            <div class="user-avatar-wrap">
              <el-avatar class="user-avatar" :size="34" :src="userAvatar || undefined">{{ userAvatar ? '' : avatarText }}</el-avatar>
            </div>
            <span>{{ auth.user?.display_name || auth.user?.username }}</span>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="account">账号设置</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <Teleport to="body">
      <Transition name="dropdown">
        <section v-if="activeGroup" class="nav-dropdown nav-dropdown--top" :style="dropdownStyle" aria-label="功能选择栏">
          <button
            v-for="item in activeGroup.items"
            :key="item.path"
            class="dropdown-item"
            :class="{ active: route.path === item.path }"
            type="button"
            @click="navigateTo(item.path)"
          >
            <el-icon v-if="item.icon"><component :is="item.icon" /></el-icon>
            <span class="item-copy">
              <b>{{ item.label }}</b>
              <small>{{ item.hint }}</small>
            </span>
          </button>
        </section>
      </Transition>
    </Teleport>

    <main class="app-main" :class="{ 'app-main--fullscreen': $route.meta.fullscreen }">

      <button v-if="$route.meta.fullscreen && !fullscreenPagesWithOwnHeader.includes(String($route.name))" class="fullscreen-exit-btn" @click="router.push('/overview')" title="返回系统概览">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回</span>
      </button>

      <RouterView v-slot="{ Component, route }">
        <KeepAlive :max="24" :exclude="['DigitalInterviewer']">
          <component :is="Component" :key="route.name || route.path" />
        </KeepAlive>
      </RouterView>
    </main>
  </div>
</template>

<script setup lang="ts">
import {
  Aim,
  ArrowLeft,
  Connection,
  DataAnalysis,
  DataLine,
  Document,
  Files,
  Histogram,
  List,
  MagicStick,
  Management,
  Operation,
  Reading,
  Setting,
  TrendCharts,
  User,
  VideoCamera
} from '@element-plus/icons-vue'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api/http'
import CosmosBackground from '@/components/CosmosBackground.vue'

type MenuItem = { path: string; label: string; icon: any; hint: string }
type MenuGroup = { key: string; label: string; icon: any; items: MenuItem[] }

// 这些全屏页面自带页头（含返回/全屏控制），隐藏左上角固定的"返回"按钮避免遮挡
const fullscreenPagesWithOwnHeader = ['personal-center', 'dashboards-admin']

const rawMenus: MenuItem[] = [
  { path: '/overview', label: '系统概览', icon: Histogram, hint: '指标概览' },
  { path: '/dashboards/hr', label: 'HR 大屏', icon: Histogram, hint: '岗位供需 候选人匹配' },
  { path: '/dashboards/admin', label: '管理员大屏', icon: Setting, hint: '平台治理 风险与发布' },
  { path: '/personal-center', label: '个人驾驶舱', icon: User, hint: '技能星系 成长全景' },
  { path: '/hr-candidates', label: '候选人管理', icon: User, hint: '候选人 简历 画像' },
  { path: '/datasets', label: '数据源管理', icon: Files, hint: '数据源 上传 质量' },
  { path: '/jd-parser', label: 'JD解析', icon: Document, hint: 'JD 解析 岗位抽取' },
  { path: '/jobs', label: '岗位管理', icon: Management, hint: '岗位 管理 描述' },
  { path: '/emerging-jobs', label: '新岗位发现', icon: TrendCharts, hint: '新岗位 发现' },
  { path: '/job-evolution', label: '岗位能力更新', icon: Operation, hint: '能力更新 版本' },
  { path: '/skill-graph', label: '能力图谱', icon: Connection, hint: '能力图谱 关系' },
  { path: '/capability-evolution', label: '能力演化', icon: DataLine, hint: '能力演化 趋势 淘汰' },
  { path: '/resume-parser', label: '简历解析', icon: User, hint: '简历解析' },
  { path: '/match-analysis', label: '匹配分析', icon: Aim, hint: '人岗匹配 分析' },
  { path: '/learning-path', label: '学习路径', icon: Reading, hint: '学习路径 推荐' },
  { path: '/digital-interviewer', label: '数字人面试官', icon: VideoCamera, hint: '数字人 面试' },
  { path: '/review-tasks', label: '人工审核', icon: List, hint: '人工审核' },
  { path: '/evaluation', label: '测试评估', icon: DataAnalysis, hint: '测试评估' },
  { path: '/rag-admin', label: 'RAG 检索增强', icon: MagicStick, hint: '向量检索 知识问答' },
  { path: '/settings', label: '系统设置', icon: Setting, hint: '系统设置' },
  { path: '/account-settings', label: '账号设置', icon: Setting, hint: '账号 密码 邮箱' }
]

const roleRouteMap: Record<string, string[]> = {
  candidate: [
    '/overview', '/personal-center', '/skill-graph', '/capability-evolution',
    '/resume-parser', '/match-analysis', '/learning-path', '/digital-interviewer', '/account-settings'
  ],
  hr: [
    '/overview', '/hr-candidates', '/datasets', '/jd-parser', '/jobs',
    '/emerging-jobs', '/job-evolution', '/skill-graph', '/capability-evolution',
    '/resume-parser', '/match-analysis', '/digital-interviewer',
    '/review-tasks', '/evaluation', '/settings', '/account-settings',
    '/rag-admin'
  ],
  admin: [
    '/overview', '/dashboards/admin', '/datasets', '/review-tasks',
    '/evaluation', '/rag-admin', '/settings', '/account-settings'
  ]
}

const groupDefs: Array<{ key: string; label: string; icon: any; items: string[] }> = [
  { key: 'overview', label: '概览', icon: Histogram, items: ['/dashboards/hr', '/dashboards/admin', '/hr-candidates'] },
  { key: 'jobs', label: '岗位管理', icon: Management, items: ['/datasets', '/jd-parser', '/jobs', '/emerging-jobs', '/job-evolution'] },
  { key: 'graph', label: '能力分析', icon: Connection, items: ['/skill-graph', '/capability-evolution'] },
  { key: 'match', label: '人岗匹配', icon: Aim, items: ['/resume-parser', '/match-analysis', '/learning-path'] },
  { key: 'ai', label: 'AI 互动', icon: VideoCamera, items: ['/digital-interviewer'] },
  { key: 'ops', label: '运营管理', icon: Setting, items: ['/review-tasks', '/evaluation', '/rag-admin', '/settings', '/account-settings'] }
]

const hrGroupDefs: Array<{ key: string; label: string; icon: any; items: string[] }> = [
  { key: 'data-fusion', label: '多元数据融合中心', icon: Files, items: ['/datasets'] },
  { key: 'jobs', label: '岗位管理', icon: Management, items: ['/jd-parser', '/jobs', '/emerging-jobs', '/job-evolution'] },
  { key: 'graph', label: '能力分析', icon: Connection, items: ['/skill-graph', '/capability-evolution'] },
  { key: 'match', label: '人岗匹配', icon: Aim, items: ['/hr-candidates', '/resume-parser', '/match-analysis'] },
  { key: 'ai', label: 'AI 互动', icon: VideoCamera, items: ['/digital-interviewer'] },
  { key: 'ops', label: '运营管理', icon: Setting, items: ['/review-tasks', '/evaluation', '/rag-admin', '/settings', '/account-settings'] }
]

const adminGroupDefs: Array<{ key: string; label: string; icon: any; items: string[] }> = []

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const candidateAvatar = ref('')
const activeGroupKey = ref<string | null>(null)
const navRef = ref<HTMLElement | null>(null)
const triggerRefs = new Map<string, HTMLElement>()

function setTriggerRef(key: string, el: HTMLElement | null) {
  if (el) {
    triggerRefs.set(key, el)
  } else {
    triggerRefs.delete(key)
  }
}

const dropdownStyle = computed(() => {
  if (!activeGroupKey.value) return {}
  const trigger = triggerRefs.get(activeGroupKey.value)
  if (!trigger) return {}
  const nav = navRef.value
  if (!nav) return {}
  const triggerRect = trigger.getBoundingClientRect()
  const navRect = nav.getBoundingClientRect()
  const left = triggerRect.left + triggerRect.width / 2 - 140
  const clampedLeft = Math.max(8, Math.min(left, window.innerWidth - 296))
  return {
    left: `${clampedLeft}px`,
    top: `${navRect.bottom + 2}px`
  }
})

const visibleGroups = computed<MenuGroup[]>(() => {
  const allowed = new Set(roleRouteMap[auth.role || 'candidate'] || roleRouteMap.candidate)
  const isHr = auth.role === 'hr'
  const isAdmin = auth.role === 'admin'
  const groups = isHr ? hrGroupDefs : isAdmin ? adminGroupDefs : groupDefs
  return groups
    .map((g) => ({
      key: g.key,
      label: g.label,
      icon: g.icon,
      items: g.items
        .map((p) => {
          const menu = rawMenus.find((m) => m.path === p)
          if (!menu || !allowed.has(p)) return null
          if (isHr && p === '/datasets') return { ...menu, label: '多数据源' }
          return menu
        })
        .filter((m): m is MenuItem => Boolean(m))
    }))
    .filter((g) => g.items.length > 0)
})

const visibleDirect = computed(() => {
  if (auth.role === 'hr') return [{ path: '/overview', label: 'HR 工作台', icon: Histogram }]
  if (auth.role === 'admin') {
    return [
      { path: '/overview', label: '系统概览', icon: Histogram },
      { path: '/dashboards/admin', label: '治理大屏', icon: Operation },
      { path: '/rag-admin', label: 'AI 防幻觉', icon: MagicStick },
      { path: '/review-tasks', label: '人工审核', icon: List },
      { path: '/evaluation', label: '测试评估', icon: DataAnalysis },
      { path: '/datasets', label: '数据治理', icon: Files },
      { path: '/settings', label: '系统设置', icon: Setting }
    ]
  }
  if (auth.role === 'candidate') {
    return [
      { path: '/overview', label: '系统概览', icon: Histogram },
      { path: '/personal-center', label: '驾驶舱', icon: User }
    ]
  }
  return []
})

function isDirectActive(entry: { path: string }) {
  return route.path === entry.path
}


const roleLabel = computed(() => (auth.role === 'hr' ? '企业 HR' : auth.role === 'admin' ? '管理员' : '求职端/学生'))
const avatarText = computed(() => (auth.role === 'hr' ? 'HR' : auth.role === 'admin' ? '管' : '学'))
const userInitial = computed(() => (auth.user?.display_name || auth.user?.username || '用').slice(0, 1))
const userAvatar = computed(() => (auth.role === 'candidate' ? candidateAvatar.value : ''))

const activeGroup = computed(() =>
  visibleGroups.value.find((group) => group.key === activeGroupKey.value) || null
)

function isGroupActive(group: MenuGroup) {
  return group.items.some((item) => item.path === route.path)
}

function toggleGroup(key: string) {
  activeGroupKey.value = activeGroupKey.value === key ? null : key
}

async function navigateTo(path: string) {
  activeGroupKey.value = null
  const isEvaluation = path === '/evaluation'
  if (route.path === path) {
    if (isEvaluation) {
      location.href = path + '#'
      requestAnimationFrame(() => { location.replace(path + '?v=' + Date.now()) })
    }
    return
  }
  try {
    if (isEvaluation) {
      location.replace(path + '?v=' + Date.now())
      return
    }
    const res = await router.push(path)
    if (res && (res as any)?.failed) {
      const failure = (res as any)?.type ? String((res as any).type) : ''
      const code = (res as any)?.code ? String((res as any).code) : ''
      if (failure.includes('aborted') || failure.includes('cancelled') || failure.includes('4') || code.includes('NAVIGATION_ABORTED') || /redirect|duplicated/i.test(failure + code)) {
        if (location.pathname !== path) location.href = path
      } else if (location.pathname !== path) {
        location.href = path
      }
    } else if (location.pathname !== path) {
      requestAnimationFrame(() => {
        if (location.pathname !== path) location.href = path
      })
    }
  } catch {
    if (location.pathname !== path) location.href = path
  }
}

const headerSubtitle = computed(() => {
  const map: Record<string, string> = {
    '/overview': '查看岗位数据、能力图谱、解析质量和系统运行概况',
    '/dashboards/hr': '岗位供需、人才优先联系、招聘动作与产业趋势全景',
    '/dashboards/admin': '数据源质量、治理重点、评测基线与可信发布链路',
    '/personal-center': '360°技能星系全景，掌握能力现状、成长路径与岗位匹配',
    '/hr-candidates': '查看求职者提交的个人画像、简历、技能证书和匹配准备情况',
    '/datasets': '管理多源 JD 数据，观察质量评分、重复率、噪声率和处理状态',
    '/jd-parser': '输入岗位 JD 文本，提取岗位名称、职责、技能、工具、证书、场景和证据来源',
    '/jobs': '按领域、类型和等级筛选岗位，查看岗位画像、状态、版本和证据来源',
    '/emerging-jobs': '基于多源一致性、技能增长和场景扩散识别新岗位候选',
    '/job-evolution': '选择岗位后查看新增、删除、修改技能和版本记录',
    '/skill-graph': '展示岗位、技能、工具、证书、课程和等级之间的关系',
    '/capability-evolution': '追踪岗位能力的新增、淘汰、迁移趋势与领域能力结构对比',
    '/resume-parser': '整理教育经历、项目经历、技能、证书、竞赛经历和岗位意向',
    '/match-analysis': '选择简历与目标岗位，查看匹配结论、能力差距、风险提醒和下一步行动',
    '/digital-interviewer': '围绕目标岗位进行结构化追问、表达反馈和能力评分',
    '/learning-path': '基于最近一次人岗匹配差距，生成阶段化成长路线',
    '/review-tasks': '处理低置信度的新岗位、新技能、删除技能和修改技能任务',
    '/evaluation': '查看 JD 解析、简历解析、匹配分析、测试用例数量和单元测试评估结果',
    '/settings': '管理智能服务配置、图谱写入规则和审核阈值',
    '/account-settings': '维护账号资料、联系方式和登录密码'
  }
  return map[route.path] || (auth.role === 'candidate' ? '维护个人画像，查看岗位匹配和学习路径' : '管理岗位数据、能力图谱和候选人资料')
})

onMounted(() => {
  document.body.classList.add('theme-dark')
  loadCandidateAvatar()
  window.addEventListener('profile-avatar-updated', handleAvatarUpdated as EventListener)
})

onBeforeUnmount(() => {
  window.removeEventListener('profile-avatar-updated', handleAvatarUpdated as EventListener)
})

async function loadCandidateAvatar() {
  if (auth.role !== 'candidate' || !auth.token) return
  try {
    const profile = await api.myProfile()
    candidateAvatar.value = profile.avatar_url || ''
  } catch {
    candidateAvatar.value = ''
  }
}

function handleAvatarUpdated(event: CustomEvent<{ avatar_url?: string }>) {
  candidateAvatar.value = event.detail?.avatar_url || ''
}

async function handleUserCommand(command: string) {
  if (command === 'account') {
    router.push('/account-settings').catch(() => undefined)
  }
  if (command === 'logout') {
    await auth.logout()
    router.push('/login').catch(() => undefined)
  }
}
</script>

<style scoped>
.app-shell {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  color: var(--text);
  background: transparent;
  display: flex;
  flex-direction: column;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 24px;
  height: 70px;
  flex: 0 0 auto;
  overflow: visible;
  border-top: 1px solid rgba(185, 229, 242, 0.05);
  border-bottom: 1px solid rgba(82, 221, 255, 0.28);
  background: rgba(10, 29, 48, 0.97);
  box-shadow: 0 10px 32px rgba(0, 3, 14, 0.38), inset 0 -1px 0 rgba(185, 229, 242, 0.03);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  padding: 0 24px;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 0 0 auto;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid rgba(82, 221, 255, 0.48);
  background: #113142;
  box-shadow: inset 0 0 20px rgba(82, 221, 255, 0.08);
  color: #52ddff;
  font-size: 16px;
  font-weight: 900;
}

.brand-copy {
  min-width: 0;
}

.brand-name {
  color: #ffffff;
  font-size: 18px;
  font-weight: 900;
  line-height: 1.2;
  letter-spacing: 0.5px;
}

.brand-desc {
  margin-top: 2px;
  color: #7893a5;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}

.top-nav {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1 1 auto;
  min-width: 0;
  height: 100%;
  overflow-x: auto;
  scrollbar-width: none;
}

.top-nav::-webkit-scrollbar {
  display: none;
}

.nav-group {
  position: relative;
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  height: 100%;
}

.nav-trigger {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  height: 42px;
  border: none;
  border-radius: 6px;
  padding: 0 18px;
  background: transparent;
  color: #b9d5e4;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  transition: all 200ms ease;
}

.nav-trigger .el-icon {
  font-size: 17px;
  color: #7893a5;
  transition: all 200ms ease;
}

.nav-trigger:hover {
  background: rgba(82, 221, 255, 0.10);
  color: #ffffff;
}

.nav-trigger:hover .el-icon {
  color: #52ddff;
}

.nav-trigger.active {
  border: 1px solid rgba(82, 221, 255, 0.32);
  background: #113142;
  color: #ffffff;
  box-shadow: inset 0 0 18px rgba(82, 221, 255, 0.08);
}

.nav-trigger.active::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -14px;
  transform: translateX(-50%);
  width: 60%;
  height: 3px;
  border-radius: 3px;
  background: #52ddff;
  box-shadow: 0 0 12px rgba(82, 221, 255, 0.52);
}

.nav-trigger.active .el-icon {
  color: #52ddff;
  filter: drop-shadow(0 0 6px rgba(82, 221, 255, 0.38));
}

.nav-dropdown {
  position: fixed;
  z-index: 2147483647;
  top: calc(100% + 4px);
  left: 0;
  min-width: 280px;
  max-height: calc(100vh - 92px);
  overflow-y: auto;
  border: 1px solid rgba(82, 221, 255, 0.24);
  border-radius: 8px;
  padding: 8px;
  background: rgba(6, 18, 37, 0.98);
  box-shadow: 0 20px 60px rgba(0, 3, 14, 0.52);
  animation: dropdownIn 220ms ease;
  pointer-events: auto !important;
  user-select: none;
  isolation: isolate;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
}

.nav-dropdown::before {
  position: absolute;
  top: -6px;
  left: 22px;
  width: 12px;
  height: 12px;
  content: "";
  border-top: 1px solid rgba(82, 221, 255, 0.24);
  border-left: 1px solid rgba(82, 221, 255, 0.24);
  border-radius: 3px;
  background: #061225;
  transform: rotate(45deg);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  height: auto;
  min-height: 46px;
  border: 1px solid transparent;
  border-radius: 6px;
  padding: 8px 12px;
  background: transparent;
  color: rgba(220, 245, 246, 0.9);
  text-align: left;
  text-decoration: none;
  cursor: pointer;
  transition: all 200ms ease;
}

.dropdown-item .el-icon {
  flex: 0 0 auto;
  font-size: 18px;
  color: #52ddff;
  transition: transform 200ms ease, color 200ms ease;
}

.dropdown-item .item-copy {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  min-width: 0;
}

.dropdown-item b {
  display: block;
  color: #f4fbfc;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.2;
}

.dropdown-item small {
  display: block;
  margin-top: 3px;
  color: rgba(170, 220, 224, 0.8);
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-item:hover {
  border-color: rgba(82, 221, 255, 0.24);
  background: rgba(82, 221, 255, 0.12);
  transform: translateX(3px);
}

.dropdown-item:hover .el-icon,
.dropdown-item.active .el-icon {
  color: #70e4ff;
  transform: scale(1.08);
}

.dropdown-item.active {
  border-color: rgba(82, 221, 255, 0.30);
  background: #113142;
}

.dropdown-item.active b {
  color: #ffffff;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 0 0 auto;
}

.role-tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 16px;
  border: 1px solid rgba(82, 221, 255, 0.26);
  background: #0a1d30;
  color: #b9d5e4;
  font-size: 13px;
  font-weight: 700;
  border-radius: 999px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.user-chip {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  border: none;
  border-radius: 999px;
  padding: 3px 14px 3px 3px;
  background: #0a1d30;
  color: #ffffff;
  font-weight: 600;
  cursor: pointer;
  transition: background 200ms ease;
}

.user-chip:hover {
  background: #113142;
}

.user-avatar-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar {
  background: #113142 !important;
  box-shadow: inset 0 0 16px rgba(82, 221, 255, 0.10);
  font-weight: 800;
  font-size: 15px;
  border: 1px solid rgba(82, 221, 255, 0.38);
}

.user-chip span {
  overflow: hidden;
  min-width: 0;
  font-size: 14px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-main {
  position: relative;
  min-height: calc(100vh - 70px);
  padding: 18px 22px 28px;
  background: transparent !important;
}

.app-main--fullscreen {
  padding: 0;
  height: 100vh;
  background: transparent !important;
  overflow-y: auto;
  overflow-x: hidden;
}

.fullscreen-exit-btn {
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(6, 18, 37, 0.92);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(82, 221, 255, 0.26);
  border-radius: 10px;
  color: #b9d5e4;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.fullscreen-exit-btn:hover {
  background: rgba(82, 221, 255, 0.18);
  border-color: rgba(101, 255, 246, 0.55);
  color: #ffffff;
}

.fullscreen-exit-btn .el-icon {
  font-size: 16px;
}

.app-titlebar {
  position: relative;
  z-index: 1;
  margin-bottom: 14px;
  padding: 4px;
  border: 0;
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

.app-titlebar .header-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.app-titlebar .section-mark {
  width: 4px;
  height: 24px;
  border-radius: 99px;
  background: #52ddff;
  box-shadow: 0 0 14px rgba(82, 221, 255, 0.36);
}

.app-titlebar .header-title {
  color: #ffffff;
  font-size: 22px;
  font-weight: 800;
  line-height: 1.2;
}

.app-titlebar .header-desc {
  margin-top: 6px;
  color: #7893a5;
  font-size: 13px;
  font-weight: 500;
}

.app-main > :deep(*) {
  position: relative;
  z-index: 1;
}

.workspace-atmosphere {
  position: fixed;
  z-index: 0;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  background: transparent;
}

@media (max-width: 1380px) {
  .app-header {
    gap: 12px;
    padding: 0 16px;
  }

  .header-brand {
    gap: 8px;
  }

  .brand-desc {
    display: none;
  }

  .header-actions {
    gap: 8px;
  }

  .user-chip > span {
    display: none;
  }

  .nav-trigger {
    padding: 0 12px;
  }
}

@keyframes dropdownIn {
  from {
    opacity: 0;
    transform: translateY(-6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

<style>
html body.theme-dark .app-main {
  background: transparent !important;
}

html body.theme-dark #app .app-main .app-titlebar {
  border: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}
</style>
