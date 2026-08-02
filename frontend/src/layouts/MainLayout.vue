<template>
  <div class="app-shell">
    <div class="workspace-atmosphere" aria-hidden="true">
      <TechParticleBackground />
      <svg class="workspace-atmosphere__svg" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice">
        <defs>
          <linearGradient id="workspaceFlow" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stop-color="#0b73ff" stop-opacity="0.04" />
            <stop offset="0.42" stop-color="#17c8ff" stop-opacity="0.88" />
            <stop offset="0.74" stop-color="#78f5ff" stop-opacity="0.68" />
            <stop offset="1" stop-color="#0b73ff" stop-opacity="0.04" />
          </linearGradient>
          <linearGradient id="workspaceFlowSoft" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stop-color="#0b73ff" stop-opacity="0" />
            <stop offset="0.5" stop-color="#2fcfff" stop-opacity="0.38" />
            <stop offset="1" stop-color="#78f5ff" stop-opacity="0" />
          </linearGradient>
          <filter id="workspaceGlow" x="-30%" y="-80%" width="160%" height="260%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <g class="workspace-flow" filter="url(#workspaceGlow)">
          <path class="workspace-flow__line workspace-flow__line--wide" d="M-120 820 C340 676 760 900 1118 708 C1350 584 1464 486 1720 548" />
          <path class="workspace-flow__line workspace-flow__line--wide workspace-flow__line--second" d="M-100 868 C380 748 800 948 1170 748 C1380 636 1490 548 1720 610" />
          <path class="workspace-flow__line workspace-flow__line--thin" d="M-40 790 C350 660 760 860 1135 716 C1370 626 1490 536 1700 584" />
          <path class="workspace-flow__line workspace-flow__line--thin workspace-flow__line--third" d="M40 892 C430 788 820 936 1200 772 C1415 680 1510 610 1690 654" />
          <path class="workspace-flow__line workspace-flow__line--fine" d="M-20 748 C380 632 744 810 1098 676 C1330 588 1460 492 1680 530" />
        </g>

        <g class="workspace-network">
          <path d="M1118 308 L1266 174 L1410 244 L1518 126 L1610 208" />
          <path d="M1266 174 L1322 392 L1410 244 L1500 382 L1612 418" />
          <path d="M1322 392 L1456 458 L1500 382" />
          <path d="M1410 244 L1456 458 M1518 126 L1500 382" />
          <circle cx="1266" cy="174" r="6" />
          <circle cx="1322" cy="392" r="4" />
          <circle cx="1410" cy="244" r="8" />
          <circle cx="1456" cy="458" r="5" />
          <circle cx="1500" cy="382" r="6" />
          <circle cx="1518" cy="126" r="5" />
          <circle cx="1610" cy="208" r="4" />
        </g>

        <g class="workspace-stars">
          <circle cx="80" cy="116" r="2" /><circle cx="240" cy="176" r="3" /><circle cx="356" cy="92" r="2" />
          <circle cx="580" cy="216" r="3" /><circle cx="760" cy="138" r="2" /><circle cx="988" cy="252" r="3" />
          <circle cx="1160" cy="106" r="2" /><circle cx="1360" cy="84" r="3" /><circle cx="1510" cy="314" r="2" />
          <circle cx="210" cy="620" r="3" /><circle cx="444" cy="720" r="2" /><circle cx="680" cy="650" r="3" />
        </g>
      </svg>
      <span class="workspace-haze workspace-haze--right"></span>
      <span class="workspace-haze workspace-haze--bottom"></span>
    </div>

    <header class="app-header">
      <div class="header-brand">
        <div class="brand-mark"><span>SR</span></div>
        <div class="brand-copy">
          <div class="brand-name">数融智联</div>
          <div class="brand-desc">岗位能力图谱分析系统</div>
        </div>
      </div>

      <nav class="top-nav" ref="navRef">
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
              <span class="caret" :class="{ open: activeGroupKey === group.key }"></span>
            </button>
          </div>
        </template>
      </nav>

      <div class="header-actions">
        <el-tag effect="light" type="success">SQLite 已连接</el-tag>
        <el-tag effect="light" type="primary">{{ roleLabel }}</el-tag>
        <el-dropdown trigger="click" @command="handleUserCommand">
          <button class="user-chip">
            <el-avatar class="user-avatar" :size="32" :src="userAvatar || undefined">{{ userAvatar ? '' : userInitial }}</el-avatar>
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
            <span class="item-arrow"><el-icon><ArrowRight /></el-icon></span>
          </button>
        </section>
      </Transition>
    </Teleport>

    <main class="app-main">
      <div class="app-titlebar">
        <div class="header-title-row">
          <span class="section-mark"></span>
          <div class="header-title">{{ $route.meta.title }}</div>
        </div>
        <div class="header-desc">{{ headerSubtitle }}</div>
      </div>
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
  ArrowRight,
  Connection,
  DataAnalysis,
  DataLine,
  Document,
  Files,
  Histogram,
  List,
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
import TechParticleBackground from '@/components/TechParticleBackground.vue'

type MenuItem = { path: string; label: string; icon: any; hint: string }
type MenuGroup = { key: string; label: string; icon: any; items: MenuItem[] }

const rawMenus: MenuItem[] = [
  { path: '/overview', label: '系统概览', icon: Histogram, hint: '指标概览' },
  { path: '/personal-center', label: '个人中心', icon: User, hint: '画像 能力 证书' },
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
    '/review-tasks', '/evaluation', '/settings', '/account-settings'
  ],
  admin: [
    '/overview', '/hr-candidates', '/datasets', '/jd-parser', '/jobs',
    '/emerging-jobs', '/job-evolution', '/skill-graph', '/capability-evolution',
    '/resume-parser', '/match-analysis', '/digital-interviewer',
    '/review-tasks', '/evaluation', '/settings', '/account-settings'
  ]
}

const groupDefs: Array<{ key: string; label: string; icon: any; items: string[] }> = [
  { key: 'overview', label: '概览', icon: Histogram, items: ['/overview', '/hr-candidates', '/personal-center'] },
  { key: 'jobs', label: '岗位管理', icon: Management, items: ['/datasets', '/jd-parser', '/jobs', '/emerging-jobs', '/job-evolution'] },
  { key: 'graph', label: '能力分析', icon: Connection, items: ['/skill-graph', '/capability-evolution'] },
  { key: 'match', label: '人岗匹配', icon: Aim, items: ['/resume-parser', '/match-analysis', '/learning-path'] },
  { key: 'ai', label: 'AI 互动', icon: VideoCamera, items: ['/digital-interviewer'] },
  { key: 'ops', label: '运营管理', icon: Setting, items: ['/review-tasks', '/evaluation', '/settings', '/account-settings'] }
]

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
  return groupDefs
    .map((g) => ({
      key: g.key,
      label: g.label,
      icon: g.icon,
      items: g.items
        .map((p) => rawMenus.find((m) => m.path === p))
        .filter((m): m is MenuItem => Boolean(m && allowed.has(m.path)))
    }))
    .filter((g) => g.items.length > 0)
})


const roleLabel = computed(() => (auth.role === 'hr' ? '企业 HR' : auth.role === 'admin' ? '管理员' : '求职者/学生'))
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
    '/personal-center': '维护个人画像，查看匹配分析、学习路径和面试练习',
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
  min-height: 100vh;
  isolation: isolate;
  color: var(--text);
  background: #04112b;
  display: flex;
  flex-direction: column;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 18px;
  height: 72px;
  flex: 0 0 auto;
  overflow: visible;
  border-bottom: 1px solid rgba(95, 211, 255, 0.28);
  background:
    radial-gradient(circle at 18% 0%, rgba(0, 200, 245, 0.18), transparent 28%),
    radial-gradient(circle at 82% 18%, rgba(30, 123, 255, 0.18), transparent 28%),
    linear-gradient(180deg, rgba(3, 13, 36, 0.9), rgba(5, 27, 68, 0.7));
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.26);
  backdrop-filter: blur(18px);
}

.app-header::after {
  position: absolute;
  left: 24px;
  bottom: 0;
  width: 176px;
  height: 3px;
  content: "";
  border-radius: 99px;
  background: linear-gradient(90deg, #1e7bff, #00c8f5);
  box-shadow: 0 0 18px rgba(0, 200, 245, 0.42);
  animation: headerLineBreath 4.8s ease-in-out infinite;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 0 0 auto;
  padding-left: 6px;
  padding-right: 4px;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 14px;
  background:
    radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.92), transparent 28%),
    linear-gradient(135deg, #2563eb, #06b6d4);
  box-shadow: 0 0 24px rgba(6, 182, 212, 0.28);
  color: #fff;
  font-size: 15px;
  font-weight: 950;
}

.brand-copy {
  min-width: 0;
}

.brand-name {
  color: #ecf8ff;
  font-size: 17px;
  font-weight: 950;
  line-height: 1.1;
}

.brand-desc {
  margin-top: 3px;
  color: #9cc4e8;
  font-size: 11px;
  font-weight: 800;
  white-space: nowrap;
}

.top-nav {
  display: flex;
  align-items: center;
  gap: 4px;
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
  gap: 6px;
  height: 40px;
  border: 1px solid transparent;
  border-radius: 14px;
  padding: 0 14px;
  background: transparent;
  color: #ecf8ff;
  font-size: 14px;
  font-weight: 850;
  white-space: nowrap;
  cursor: pointer;
  transition: all 200ms ease;
}

.nav-trigger .el-icon {
  font-size: 16px;
  color: #2563eb;
  transition: transform 200ms ease, color 200ms ease;
}

.nav-trigger:hover {
  border-color: rgba(87, 223, 255, 0.36);
  background: rgba(19, 127, 209, 0.24);
  color: #fff;
}

.nav-trigger:hover .el-icon,
.nav-trigger.active .el-icon {
  color: #06b6d4;
}

.nav-trigger.active {
  border-color: rgba(87, 223, 255, 0.36);
  background: rgba(19, 127, 209, 0.24);
  color: #fff;
  box-shadow: 0 8px 22px rgba(37, 99, 235, 0.12);
}

.caret {
  display: inline-block;
  width: 0;
  height: 0;
  margin-left: 2px;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 5px solid currentColor;
  transition: transform 200ms ease;
  opacity: 0.7;
}

.caret.open {
  transform: rotate(180deg);
  opacity: 1;
}

.nav-dropdown {
  position: fixed;
  z-index: 2147483647;
  top: calc(100% + 2px);
  left: 0;
  min-width: 280px;
  max-height: calc(100vh - 92px);
  overflow-y: auto;
  border: 1px solid rgba(82, 192, 255, 0.42);
  border-radius: 18px;
  padding: 8px;
  background: #071d4a;
  box-shadow: 0 20px 46px rgba(0, 4, 22, 0.58);
  animation: dropdownIn 220ms ease;
  pointer-events: auto !important;
  user-select: none;
  isolation: isolate;
}

.nav-dropdown::before {
  position: absolute;
  top: -6px;
  left: 22px;
  width: 12px;
  height: 12px;
  content: "";
  border-top: 1px solid rgba(82, 192, 255, 0.42);
  border-left: 1px solid rgba(82, 192, 255, 0.42);
  border-radius: 3px;
  background: #071d4a;
  transform: rotate(45deg);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  height: auto;
  min-height: 48px;
  border: 1px solid transparent;
  border-radius: 13px;
  padding: 8px 12px;
  background: transparent;
  color: #e6f5ff;
  text-align: left;
  text-decoration: none;
  cursor: pointer;
  transition: all 200ms ease;
}

.dropdown-item .el-icon {
  flex: 0 0 auto;
  font-size: 18px;
  color: #2563eb;
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
  color: #e6f5ff;
  font-size: 14px;
  font-weight: 850;
  line-height: 1.2;
}

.dropdown-item small {
  display: block;
  margin-top: 3px;
  color: #98bde2;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-item .item-arrow {
  flex: 0 0 auto;
  margin-left: auto;
  font-size: 14px;
  color: #8a9bb1;
  opacity: 0;
  transition: opacity 200ms ease, transform 200ms ease;
}

.dropdown-item:hover {
  border-color: rgba(79, 220, 255, 0.36);
  background: rgba(18, 132, 209, 0.24);
  transform: translateX(3px);
}

.dropdown-item:hover .el-icon,
.dropdown-item.active .el-icon {
  color: #06b6d4;
  transform: scale(1.1);
}

.dropdown-item:hover .item-arrow,
.dropdown-item.active .item-arrow {
  opacity: 1;
  transform: translateX(2px);
  color: #2563eb;
}

.dropdown-item.active {
  border-color: rgba(79, 220, 255, 0.36);
  background: rgba(18, 132, 209, 0.24);
}

.dropdown-item.active b {
  color: #e6f5ff;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 0 0 auto;
  padding-right: 4px;
}

.user-avatar {
  background: linear-gradient(135deg, var(--primary), var(--cyan));
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.25);
  font-weight: 950;
}

.user-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  max-width: 176px;
  border: 1px solid rgba(99, 207, 255, 0.36);
  border-radius: 14px;
  padding: 4px 10px 4px 4px;
  background: rgba(4, 27, 68, 0.66);
  color: #eaf7ff;
  font-weight: 850;
}

.user-chip span {
  overflow: hidden;
  min-width: 0;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-main {
  position: relative;
  min-height: calc(100vh - 72px);
  padding: 18px 22px 28px;
  background: transparent;
}

.app-titlebar {
  position: relative;
  z-index: 1;
  margin-bottom: 14px;
  padding: 4px 4px 14px;
  border-bottom: 1px solid rgba(105, 213, 255, 0.26);
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
  background: linear-gradient(180deg, #2563eb, #06b6d4);
  box-shadow: 0 0 14px rgba(6, 182, 212, 0.3);
}

.app-titlebar .header-title {
  color: #ecf8ff;
  font-size: 22px;
  font-weight: 950;
  line-height: 1.2;
}

.app-titlebar .header-desc {
  margin-top: 6px;
  color: #9cc4e8;
  font-size: 13px;
  font-weight: 700;
}

.app-main > :deep(.RouterView),
.app-main > :deep(> *) {
  position: relative;
  z-index: 1;
}

.workspace-atmosphere {
  position: fixed;
  z-index: 0;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  background:
    radial-gradient(circle at 96% 2%, rgba(56, 207, 255, 0.52), transparent 25%),
    radial-gradient(circle at 18% 72%, rgba(0, 104, 255, 0.26), transparent 32%),
    linear-gradient(145deg, #02081c 0%, #041a48 48%, #03102c 100%);
}

.workspace-atmosphere::before,
.workspace-atmosphere::after {
  position: absolute;
  inset: 0;
  content: "";
}

.workspace-atmosphere::before {
  opacity: 0.26;
  background: url("@/assets/login-background.png") center / cover no-repeat;
  mix-blend-mode: screen;
  animation: workspaceBackgroundDrift 24s ease-in-out infinite;
}

.workspace-atmosphere::after {
  opacity: 0.16;
  background:
    linear-gradient(rgba(95, 217, 255, 0.16) 1px, transparent 1px),
    linear-gradient(90deg, rgba(95, 217, 255, 0.13) 1px, transparent 1px);
  background-size: 54px 54px;
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.54), transparent 72%);
}

.workspace-atmosphere__svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: visible;
}

.workspace-flow__line {
  fill: none;
  stroke: url(#workspaceFlow);
  stroke-linecap: round;
  stroke-dasharray: 740 360;
  animation: workspaceFlowTravel 14s linear infinite;
}

.workspace-flow__line--wide {
  stroke-width: 15;
  opacity: 0.18;
}

.workspace-flow__line--second {
  stroke-width: 11;
  opacity: 0.12;
  animation-delay: -5s;
  animation-duration: 18s;
}

.workspace-flow__line--thin {
  stroke-width: 3.5;
  opacity: 0.7;
  animation-delay: -2s;
  animation-duration: 10s;
}

.workspace-flow__line--third {
  opacity: 0.42;
  animation-delay: -9s;
  animation-duration: 16s;
}

.workspace-flow__line--fine {
  stroke: url(#workspaceFlowSoft);
  stroke-width: 1.8;
  opacity: 0.7;
  animation-delay: -4s;
  animation-duration: 9s;
}

.workspace-network {
  opacity: 0.7;
  transform-origin: 1440px 300px;
  animation: workspaceNetworkPulse 7.5s ease-in-out infinite;
}

.workspace-network path {
  fill: none;
  stroke: rgba(56, 211, 255, 0.44);
  stroke-width: 1.4;
  stroke-dasharray: 6 14;
  animation: workspaceNetworkTrace 12s linear infinite;
}

.workspace-network circle,
.workspace-stars circle {
  fill: #c2f8ff;
  filter: none;
  transform-box: fill-box;
  transform-origin: center;
  animation: workspaceNodePulse 4.4s ease-in-out infinite;
}

.workspace-network circle:nth-of-type(2n),
.workspace-stars circle:nth-of-type(3n) {
  animation-delay: -1.4s;
}

.workspace-network circle:nth-of-type(3n),
.workspace-stars circle:nth-of-type(4n) {
  animation-delay: -2.6s;
}

.workspace-stars {
  opacity: 0.8;
}

.workspace-haze {
  position: absolute;
  border-radius: 50%;
  filter: blur(24px);
  mix-blend-mode: screen;
}

.workspace-haze--right {
  right: -16vw;
  top: 8vh;
  width: 42vw;
  height: 40vw;
  background: radial-gradient(circle, rgba(0, 186, 255, 0.18), transparent 68%);
  animation: workspaceHazeMove 13s ease-in-out infinite;
}

.workspace-haze--bottom {
  left: 10vw;
  bottom: -22vw;
  width: 64vw;
  height: 36vw;
  background: radial-gradient(ellipse, rgba(0, 135, 255, 0.16), transparent 68%);
  animation: workspaceHazeMove 16s ease-in-out infinite reverse;
}

@media (max-width: 1380px) {
  .app-header {
    gap: 10px;
  }

  .header-brand {
    gap: 8px;
    padding-right: 0;
  }

  .brand-desc {
    display: none;
  }

  .header-actions {
    gap: 6px;
  }

  .user-chip {
    padding: 3px;
  }

  .user-chip > span {
    display: none;
  }
}

@keyframes workspaceFlowTravel {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: -1100; }
}

@keyframes workspaceNetworkTrace {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: -160; }
}

@keyframes workspaceNetworkPulse {
  0%, 100% { opacity: 0.42; transform: scale(0.985); }
  50% { opacity: 0.92; transform: scale(1.015); }
}

@keyframes workspaceNodePulse {
  0%, 100% { opacity: 0.44; transform: scale(0.78); }
  50% { opacity: 1; transform: scale(1.36); }
}

@keyframes workspaceHazeMove {
  0%, 100% { opacity: 0.58; transform: translate3d(0, 0, 0) scale(1); }
  50% { opacity: 1; transform: translate3d(-4vw, 3vh, 0) scale(1.12); }
}

@keyframes workspaceBackgroundDrift {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05) translate3d(-1%, 1%, 0); }
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

@keyframes headerLineBreath {
  0%,
  100% {
    opacity: 0.72;
    width: 176px;
  }

  50% {
    opacity: 1;
    width: 236px;
  }
}
</style>
