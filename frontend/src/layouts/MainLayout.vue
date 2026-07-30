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

      <nav class="top-nav">
        <template v-for="group in visibleGroups" :key="group.key">
          <div class="nav-group">
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

            <section v-if="activeGroupKey === group.key" class="nav-dropdown" aria-label="功能选择栏">
              <button
                v-for="item in group.items"
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
          </div>
        </template>
      </nav>

      <div class="header-actions">
        <div class="search-bar-shell">
          <span class="search-glow"></span>
          <span class="search-white"></span>
          <span class="search-border"></span>
          <span class="search-dark-border"></span>
          <el-autocomplete
            v-model="searchKeyword"
            class="global-search"
            value-key="label"
            clearable
            :fetch-suggestions="querySearch"
            placeholder="搜索页面、岗位、简历或能力"
            @select="handleSearchSelect"
            @keydown.enter="handleSearchEnter"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
            <template #default="{ item }">
              <div class="search-suggestion">
                <span>{{ item.label }}</span>
                <small>{{ item.hint }}</small>
              </div>
            </template>
          </el-autocomplete>
        </div>
        <button class="theme-switch" type="button" :class="{ dark: isDarkTheme }" :aria-label="isDarkTheme ? '切换白天模式' : '切换黑夜模式'" @click="toggleTheme">
          <span class="theme-slider">
            <span class="theme-sun-moon">
              <i class="moon-dot dot-1"></i>
              <i class="moon-dot dot-2"></i>
              <i class="moon-dot dot-3"></i>
              <i class="light-ray ray-1"></i>
              <i class="light-ray ray-2"></i>
              <i class="light-ray ray-3"></i>
            </span>
            <i class="theme-cloud cloud-1"></i>
            <i class="theme-cloud cloud-2"></i>
            <i class="theme-cloud cloud-3"></i>
            <i class="theme-star star-1"></i>
            <i class="theme-star star-2"></i>
            <i class="theme-star star-3"></i>
          </span>
        </button>
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
  Search,
  Setting,
  TrendCharts,
  User,
  VideoCamera
} from '@element-plus/icons-vue'
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
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
const searchKeyword = ref('')
const candidateAvatar = ref('')
const isDarkTheme = ref(localStorage.getItem('sr-theme') !== 'light')
const activeGroupKey = ref<string | null>(null)

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
  if (route.path !== path) await router.push(path)
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

const searchTargets = computed(() =>
  visibleGroups.value.flatMap((g) =>
    g.items.map((item) => ({
      label: item.label,
      path: item.path,
      hint: item.hint,
      keywords: `${item.label} ${item.hint} ${g.label}`
    }))
  )
)

onMounted(() => {
  applyThemeClass()
  loadCandidateAvatar()
  window.addEventListener('profile-avatar-updated', handleAvatarUpdated as EventListener)
})

onBeforeUnmount(() => {
  window.removeEventListener('profile-avatar-updated', handleAvatarUpdated as EventListener)
})

function querySearch(query: string, callback: (items: any[]) => void) {
  const keyword = query.trim().toLowerCase()
  const rows = searchTargets.value.filter((item) => !keyword || item.keywords.toLowerCase().includes(keyword))
  callback(rows.slice(0, 8))
}

function handleSearchSelect(item: { path: string }) {
  searchKeyword.value = ''
  router.push(item.path).catch(() => undefined)
}

function handleSearchEnter() {
  const keyword = searchKeyword.value.trim().toLowerCase()
  if (!keyword) return
  const match = searchTargets.value.find((item) => item.keywords.toLowerCase().includes(keyword))
  if (!match) {
    ElMessage.info('没有找到匹配的功能入口')
    return
  }
  handleSearchSelect(match)
}

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

function toggleTheme() {
  isDarkTheme.value = !isDarkTheme.value
  localStorage.setItem('sr-theme', isDarkTheme.value ? 'dark' : 'light')
  applyThemeClass()
}

function applyThemeClass() {
  document.body.classList.toggle('theme-dark', isDarkTheme.value)
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
@property --search-border-angle {
  syntax: "<angle>";
  inherits: false;
  initial-value: 0deg;
}

.app-shell {
  min-height: 100vh;
  color: var(--text);
  background: #f3f9ff;
  display: flex;
  flex-direction: column;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 18px;
  height: 72px;
  flex: 0 0 auto;
  overflow: visible;
  border-bottom: 1px solid rgba(107, 174, 255, 0.28);
  background:
    radial-gradient(circle at 18% 0%, rgba(0, 200, 245, 0.14), transparent 28%),
    radial-gradient(circle at 82% 18%, rgba(30, 123, 255, 0.12), transparent 28%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(232, 245, 255, 0.84));
  box-shadow: 0 12px 34px rgba(37, 99, 235, 0.08);
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
  color: #071a3d;
  font-size: 17px;
  font-weight: 950;
  line-height: 1.1;
}

.brand-desc {
  margin-top: 3px;
  color: #526b8e;
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
  color: #14346c;
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
  border-color: rgba(190, 213, 242, 0.86);
  background: rgba(255, 255, 255, 0.7);
  color: #0a2a6c;
}

.nav-trigger:hover .el-icon,
.nav-trigger.active .el-icon {
  color: #06b6d4;
}

.nav-trigger.active {
  border-color: rgba(37, 99, 235, 0.32);
  background: rgba(37, 99, 235, 0.1);
  color: #0a2a6c;
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
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  z-index: 2147483647;
  min-width: 240px;
  border: 1px solid rgba(190, 213, 242, 0.86);
  border-radius: 18px;
  padding: 8px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(232, 245, 255, 0.92));
  box-shadow: 0 18px 54px rgba(37, 99, 235, 0.16);
  backdrop-filter: blur(20px);
}

.nav-dropdown::before {
  position: absolute;
  top: -6px;
  left: 22px;
  width: 12px;
  height: 12px;
  content: "";
  border-top: 1px solid rgba(190, 213, 242, 0.86);
  border-left: 1px solid rgba(190, 213, 242, 0.86);
  border-radius: 3px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(232, 245, 255, 0.92));
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
  color: #14346c;
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
  color: #071a3d;
  font-size: 14px;
  font-weight: 850;
  line-height: 1.2;
}

.dropdown-item small {
  display: block;
  margin-top: 3px;
  color: #6f87a8;
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
  border-color: rgba(190, 213, 242, 0.86);
  background: rgba(255, 255, 255, 0.82);
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
  border-color: rgba(37, 99, 235, 0.24);
  background: rgba(37, 99, 235, 0.1);
}

.dropdown-item.active b {
  color: #0a2a6c;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 0 0 auto;
  padding-right: 4px;
}

.search-bar-shell {
  --search-border-angle: 0deg;

  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  width: 286px;
  height: 44px;
  isolation: isolate;
  overflow: hidden;
  border-radius: 14px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(239, 248, 255, 0.78));
  box-shadow: 0 10px 26px rgba(37, 99, 235, 0.08);
}

.search-glow,
.search-white,
.search-border,
.search-dark-border {
  display: none;
}

.search-bar-shell::before {
  position: absolute;
  z-index: 0;
  inset: 0;
  content: "";
  padding: 2px;
  border-radius: inherit;
  background:
    conic-gradient(
      from var(--search-border-angle),
      transparent 0deg,
      transparent 26deg,
      rgba(0, 200, 245, 0.12) 35deg,
      rgba(77, 245, 255, 0.62) 44deg,
      rgba(255, 255, 255, 0.88) 50deg,
      rgba(30, 123, 255, 0.54) 58deg,
      transparent 72deg,
      transparent 190deg,
      rgba(77, 245, 255, 0.5) 208deg,
      rgba(255, 255, 255, 0.76) 216deg,
      rgba(30, 123, 255, 0.5) 226deg,
      transparent 244deg,
      transparent 360deg
    );
  opacity: 0.64;
  -webkit-mask:
    linear-gradient(#000 0 0) content-box,
    linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask:
    linear-gradient(#000 0 0) content-box,
    linear-gradient(#000 0 0);
  mask-composite: exclude;
  pointer-events: none;
  animation: searchBorderSpin 9s linear infinite;
}

.search-bar-shell:focus-within::before,
.search-bar-shell:hover::before {
  opacity: 0.82;
}

.global-search {
  width: 276px;
  position: relative;
  z-index: 1;
}

.global-search :deep(.el-input__wrapper) {
  height: 38px;
  border: 1px solid rgba(190, 213, 242, 0.24);
  border-radius: 11px;
  background: transparent;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.92),
    0 8px 24px rgba(37, 99, 235, 0.04);
  transition: border-color 180ms ease, box-shadow 180ms ease, background 180ms ease;
}

.global-search :deep(.el-input__wrapper.is-focus) {
  border-color: rgba(0, 200, 245, 0.58);
  box-shadow:
    0 0 0 3px rgba(0, 200, 245, 0.08),
    0 12px 30px rgba(37, 99, 235, 0.14);
}

.global-search :deep(.el-input__prefix) {
  color: var(--primary);
}

.theme-switch {
  position: relative;
  flex: 0 0 auto;
  width: 60px;
  height: 34px;
  border: 0;
  padding: 0;
  background: transparent;
  cursor: pointer;
}

.theme-slider {
  position: absolute;
  inset: 0;
  overflow: hidden;
  border: 1px solid rgba(93, 168, 255, 0.56);
  border-radius: 34px;
  background: linear-gradient(135deg, #51b6ff, #2196f3);
  box-shadow: 0 10px 22px rgba(33, 150, 243, 0.2);
  transition: background 0.4s ease, box-shadow 0.4s ease;
}

.theme-switch.dark .theme-slider {
  border-color: rgba(88, 112, 180, 0.62);
  background: linear-gradient(135deg, #071124, #101b3d);
  box-shadow: 0 10px 24px rgba(5, 10, 25, 0.24);
}

.theme-sun-moon {
  position: absolute;
  z-index: 3;
  left: 4px;
  bottom: 4px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #ffe45c;
  box-shadow: 0 0 16px rgba(255, 228, 92, 0.55);
  transition: transform 0.4s ease, background 0.4s ease, box-shadow 0.4s ease;
}

.theme-switch.dark .theme-sun-moon {
  transform: translateX(26px) rotate(180deg);
  background: #fff;
  box-shadow: 0 0 14px rgba(255, 255, 255, 0.48);
}

.moon-dot,
.light-ray,
.theme-cloud,
.theme-star {
  position: absolute;
  display: block;
  pointer-events: none;
}

.moon-dot {
  border-radius: 50%;
  background: #9ca3af;
  opacity: 0;
  transition: opacity 0.35s ease;
}

.theme-switch.dark .moon-dot {
  opacity: 1;
}

.dot-1 {
  top: 4px;
  left: 11px;
  width: 6px;
  height: 6px;
}

.dot-2 {
  top: 11px;
  left: 3px;
  width: 9px;
  height: 9px;
}

.dot-3 {
  top: 19px;
  left: 17px;
  width: 3px;
  height: 3px;
}

.light-ray {
  z-index: -1;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.ray-1 {
  inset: -8px;
}

.ray-2 {
  inset: -14px;
}

.ray-3 {
  inset: -20px;
}

.theme-cloud {
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.74);
  animation: themeCloudMove 6s ease-in-out infinite;
}

.cloud-1 {
  right: -3px;
  top: 15px;
  width: 34px;
  height: 9px;
}

.cloud-2 {
  right: 6px;
  top: 10px;
  width: 18px;
  height: 7px;
  animation-delay: 0.8s;
}

.cloud-3 {
  right: 18px;
  top: 24px;
  width: 26px;
  height: 8px;
  animation-delay: 1.3s;
}

.theme-switch.dark .theme-cloud {
  opacity: 0;
}

.theme-star {
  border-radius: 50%;
  background: #fff;
  opacity: 0;
  transform: translateY(-20px);
  transition: opacity 0.35s ease, transform 0.35s ease;
  animation: themeStarTwinkle 2s ease-in-out infinite;
}

.theme-switch.dark .theme-star {
  opacity: 1;
  transform: translateY(0);
}

.star-1 {
  left: 8px;
  top: 8px;
  width: 5px;
  height: 5px;
}

.star-2 {
  left: 18px;
  top: 20px;
  width: 3px;
  height: 3px;
  animation-delay: 0.5s;
}

.star-3 {
  left: 29px;
  top: 7px;
  width: 4px;
  height: 4px;
  animation-delay: 1.1s;
}

.search-suggestion {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
}

.search-suggestion span {
  color: #0f2b57;
  font-weight: 850;
}

.search-suggestion small {
  overflow: hidden;
  max-width: 150px;
  color: #8a9bb1;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  border: 1px solid rgba(190, 213, 242, 0.88);
  border-radius: 14px;
  padding: 4px 10px 4px 4px;
  background: rgba(255, 255, 255, 0.74);
  color: #14346c;
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
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.18), rgba(238, 247, 255, 0.2)),
    url("@/assets/images/layout-main-bg.png") center top / cover no-repeat fixed,
    #f3f9ff;
}

.app-titlebar {
  position: relative;
  z-index: 1;
  margin-bottom: 14px;
  padding: 4px 4px 14px;
  border-bottom: 1px solid rgba(190, 213, 242, 0.5);
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
  color: #071a3d;
  font-size: 22px;
  font-weight: 950;
  line-height: 1.2;
}

.app-titlebar .header-desc {
  margin-top: 6px;
  color: #526b8e;
  font-size: 13px;
  font-weight: 700;
}

.app-main > :deep(.RouterView),
.app-main > :deep(> *) {
  position: relative;
  z-index: 1;
}

:global(body.theme-dark) .app-shell {
  background: #071124;
}

:global(body.theme-dark) .app-header {
  border-color: rgba(91, 145, 220, 0.34);
  background:
    radial-gradient(circle at 18% 0%, rgba(0, 200, 245, 0.18), transparent 28%),
    radial-gradient(circle at 82% 18%, rgba(30, 123, 255, 0.18), transparent 28%),
    linear-gradient(135deg, rgba(7, 18, 40, 0.92), rgba(11, 28, 58, 0.92));
}

:global(body.theme-dark) .brand-name,
:global(body.theme-dark) .app-titlebar .header-title,
:global(body.theme-dark) .dropdown-item b,
:global(body.theme-dark) .nav-trigger {
  color: #e8f2ff;
}

:global(body.theme-dark) .brand-desc,
:global(body.theme-dark) .app-titlebar .header-desc,
:global(body.theme-dark) .dropdown-item small {
  color: #9db3cf;
}

:global(body.theme-dark) .nav-trigger:hover,
:global(body.theme-dark) .dropdown-item:hover {
  background: rgba(20, 40, 80, 0.72);
  border-color: rgba(91, 145, 220, 0.5);
}

:global(body.theme-dark) .nav-trigger.active,
:global(body.theme-dark) .dropdown-item.active {
  background: rgba(0, 200, 245, 0.16);
  border-color: rgba(0, 200, 245, 0.4);
}

:global(body.theme-dark) .nav-dropdown {
  border-color: rgba(91, 145, 220, 0.5);
  background:
    linear-gradient(135deg, rgba(7, 18, 40, 0.96), rgba(11, 28, 58, 0.96));
  box-shadow: 0 18px 54px rgba(0, 0, 0, 0.5);
}

:global(body.theme-dark) .nav-dropdown::before {
  border-color: rgba(91, 145, 220, 0.5);
  background: linear-gradient(135deg, rgba(7, 18, 40, 0.96), rgba(11, 28, 58, 0.96));
}

:global(body.theme-dark) .app-main {
  background:
    linear-gradient(180deg, rgba(5, 15, 34, 0.84), rgba(7, 19, 42, 0.88)),
    url("@/assets/images/layout-main-bg.png") center top / cover no-repeat fixed,
    #071124;
  background-blend-mode: multiply, normal, normal;
}

:global(body.theme-dark) .user-chip {
  border-color: rgba(91, 145, 220, 0.5);
  background: rgba(20, 40, 80, 0.6);
  color: #e8f2ff;
}

:global(body.theme-dark) .app-titlebar {
  border-color: rgba(91, 145, 220, 0.34);
}

/* Logged-in workspace: animated blue particle-and-flow background. */
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

.app-shell {
  position: relative;
  isolation: isolate;
  background: #04112b;
}

.app-shell > .app-header,
.app-shell > .app-main {
  position: relative;
  z-index: 1;
}

.app-shell > .app-header {
  z-index: 100;
}

.app-header {
  border-bottom-color: rgba(95, 211, 255, 0.28);
  background:
    linear-gradient(180deg, rgba(3, 13, 36, 0.9), rgba(5, 27, 68, 0.7)) !important;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.26);
}

.brand-name,
.nav-trigger,
.app-titlebar .header-title {
  color: #ecf8ff;
}

.brand-desc,
.app-titlebar .header-desc {
  color: #9cc4e8;
}

.nav-trigger:hover,
.nav-trigger.active {
  border-color: rgba(87, 223, 255, 0.36);
  background: rgba(19, 127, 209, 0.24);
  color: #fff;
}

.nav-dropdown {
  top: calc(100% + 8px);
  border-color: rgba(82, 192, 255, 0.55);
  background:
    linear-gradient(135deg, rgba(16, 42, 90, 0.98), rgba(8, 24, 54, 0.98));
  box-shadow:
    0 20px 46px rgba(0, 4, 22, 0.58),
    0 0 0 1px rgba(86, 207, 255, 0.22);
  backdrop-filter: blur(20px);
}

.nav-dropdown::before {
  border-color: rgba(82, 192, 255, 0.55);
  background:
    linear-gradient(135deg, rgba(16, 42, 90, 0.98), rgba(8, 24, 54, 0.98));
}

.dropdown-item,
.dropdown-item b {
  color: #e6f5ff;
}

.dropdown-item small {
  color: #98bde2;
}

.dropdown-item:hover,
.dropdown-item.active {
  border-color: rgba(79, 220, 255, 0.36);
  background: rgba(18, 132, 209, 0.24);
}

.search-bar-shell {
  background: rgba(4, 27, 68, 0.76);
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.24);
}

.global-search :deep(.el-input__wrapper) {
  border-color: rgba(111, 217, 255, 0.22);
  background: rgba(3, 16, 44, 0.3);
  box-shadow: inset 0 1px 0 rgba(164, 235, 255, 0.1);
}

.global-search :deep(.el-input__inner) {
  color: #e9f8ff;
}

.global-search :deep(.el-input__inner::placeholder) {
  color: rgba(192, 222, 246, 0.62);
}

.user-chip {
  border-color: rgba(99, 207, 255, 0.36);
  background: rgba(4, 27, 68, 0.66);
  color: #eaf7ff;
}

.app-main {
  background: transparent !important;
}

.app-titlebar {
  border-bottom-color: rgba(105, 213, 255, 0.26);
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

  .search-bar-shell {
    width: 180px;
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

@keyframes searchBorderSpin {
  to {
    --search-border-angle: 360deg;
  }
}

@keyframes themeCloudMove {
  0%,
  100% {
    transform: translateX(0);
  }

  45% {
    transform: translateX(4px);
  }

  80% {
    transform: translateX(-4px);
  }
}

@keyframes themeStarTwinkle {
  0%,
  100% {
    transform: scale(1);
  }

  45% {
    transform: scale(1.28);
  }

  80% {
    transform: scale(0.82);
  }
}
</style>
