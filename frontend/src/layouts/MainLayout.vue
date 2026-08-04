<template>
  <div class="app-shell" :class="{ 'app-shell--dashboard': isDashboard }">
    <div class="workspace-backdrop" aria-hidden="true"></div>

    <header class="app-header">
      <button class="header-brand" type="button" aria-label="返回系统概览" @click="navigateTo('/overview')">
        <span class="brand-mark"><el-icon><DataAnalysis /></el-icon></span>
        <span class="brand-copy">
          <b>数融智联</b>
          <small>岗位能力图谱分析系统</small>
        </span>
      </button>

      <nav ref="navRef" class="top-nav" aria-label="主导航">
        <div v-for="group in visibleGroups" :key="group.key" class="nav-group" :ref="(el) => setTriggerRef(group.key, el as HTMLElement | null)">
          <button
            class="nav-trigger"
            :class="{ active: isGroupActive(group) || activeGroupKey === group.key }"
            type="button"
            @click.stop="toggleGroup(group.key)"
          >
            <el-icon><component :is="group.icon" /></el-icon>
            <span>{{ group.label }}</span>
            <el-icon class="nav-caret" :class="{ open: activeGroupKey === group.key }"><ArrowDown /></el-icon>
          </button>
        </div>
      </nav>

      <div class="header-actions">
        <el-autocomplete
          v-model="searchKeyword"
          class="global-search"
          value-key="label"
          clearable
          :fetch-suggestions="querySearch"
          placeholder="搜索功能、岗位或能力"
          @select="handleSearchSelect"
          @keydown.enter="handleSearchEnter"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
          <template #default="{ item }">
            <div class="search-suggestion">
              <span>{{ item.label }}</span>
              <small>{{ item.hint }}</small>
            </div>
          </template>
        </el-autocomplete>

        <span class="role-chip"><i></i>{{ roleLabel }}</span>

        <el-dropdown trigger="click" @command="handleUserCommand">
          <button class="user-chip" type="button">
            <el-avatar class="user-avatar" :size="34" :src="userAvatar || undefined">{{ userAvatar ? '' : userInitial }}</el-avatar>
            <span>{{ auth.user?.display_name || auth.user?.username }}</span>
            <el-icon><ArrowDown /></el-icon>
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
      <section v-if="activeGroup" class="nav-dropdown" :style="dropdownStyle" aria-label="功能选择">
        <button
          v-for="item in activeGroup.items"
          :key="item.path"
          class="dropdown-item"
          :class="{ active: route.path === item.path }"
          type="button"
          @click="navigateTo(item.path)"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>
            <b>{{ item.label }}</b>
            <small>{{ item.hint }}</small>
          </span>
          <el-icon class="dropdown-arrow"><ArrowRight /></el-icon>
        </button>
      </section>
    </Teleport>

    <main class="app-main" :class="{ 'app-main--dashboard': isDashboard }">
      <div v-if="!isDashboard" class="app-titlebar">
        <div>
          <span class="section-mark"></span>
          <h1>{{ route.meta.title }}</h1>
        </div>
        <p>{{ headerSubtitle }}</p>
      </div>

      <RouterView v-slot="{ Component, route: currentRoute }">
        <KeepAlive :max="24" :exclude="['DigitalInterviewer']">
          <component :is="Component" :key="currentRoute.name || currentRoute.path" />
        </KeepAlive>
      </RouterView>
    </main>
  </div>
</template>

<script setup lang="ts">
import {
  Aim,
  ArrowDown,
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
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api/http'

type MenuItem = { path: string; label: string; icon: any; hint: string }
type MenuGroup = { key: string; label: string; icon: any; items: MenuItem[] }

const rawMenus: MenuItem[] = [
  { path: '/overview', label: '决策驾驶舱', icon: Histogram, hint: '查看当前角色的核心决策信息' },
  { path: '/personal-center', label: '个人中心', icon: User, hint: '维护画像、技能、证书和经历' },
  { path: '/hr-candidates', label: '候选人管理', icon: User, hint: '查看人才画像与历史简历' },
  { path: '/datasets', label: '权威数据源', icon: Files, hint: '同步并核验政府、国际组织与开放标准数据' },
  { path: '/jd-parser', label: 'JD 解析', icon: Document, hint: '提取岗位职责与技能要求' },
  { path: '/jobs', label: '岗位管理', icon: Management, hint: '维护岗位画像与版本' },
  { path: '/emerging-jobs', label: '新岗位发现', icon: TrendCharts, hint: '发现市场新岗位与新能力' },
  { path: '/job-evolution', label: '岗位能力更新', icon: Operation, hint: '查看岗位能力变化记录' },
  { path: '/skill-graph', label: '能力图谱', icon: Connection, hint: '探索岗位、技能与证据关系' },
  { path: '/capability-evolution', label: '能力演化', icon: DataLine, hint: '追踪能力变化与趋势' },
  { path: '/resume-parser', label: '简历解析', icon: Document, hint: '上传并保存 PDF 或 Word 简历' },
  { path: '/match-analysis', label: '匹配分析', icon: Aim, hint: '生成人岗匹配与能力差距' },
  { path: '/learning-path', label: '学习路径', icon: Reading, hint: '根据差距规划成长路线' },
  { path: '/digital-interviewer', label: '数字人面试', icon: VideoCamera, hint: '进行实时模拟面试与评分' },
  { path: '/review-tasks', label: '人工审核', icon: List, hint: '复核低置信度数据与结论' },
  { path: '/evaluation', label: '模型评估', icon: DataAnalysis, hint: '查看解析、匹配与测试指标' },
  { path: '/settings', label: '系统设置', icon: Setting, hint: '管理智能服务和审核规则' },
  { path: '/account-settings', label: '账号设置', icon: Setting, hint: '维护账号与安全信息' }
]

const roleRouteMap: Record<string, string[]> = {
  candidate: ['/overview', '/personal-center', '/skill-graph', '/capability-evolution', '/resume-parser', '/match-analysis', '/learning-path', '/digital-interviewer', '/account-settings'],
  hr: ['/overview', '/hr-candidates', '/datasets', '/jd-parser', '/jobs', '/emerging-jobs', '/job-evolution', '/skill-graph', '/capability-evolution', '/resume-parser', '/match-analysis', '/digital-interviewer', '/review-tasks', '/evaluation', '/settings', '/account-settings'],
  admin: ['/overview', '/hr-candidates', '/datasets', '/jd-parser', '/jobs', '/emerging-jobs', '/job-evolution', '/skill-graph', '/capability-evolution', '/resume-parser', '/match-analysis', '/digital-interviewer', '/review-tasks', '/evaluation', '/settings', '/account-settings']
}

const groupDefs = [
  { key: 'overview', label: '总览', icon: Histogram, items: ['/overview', '/personal-center', '/hr-candidates'] },
  { key: 'jobs', label: '岗位', icon: Management, items: ['/datasets', '/jd-parser', '/jobs', '/emerging-jobs', '/job-evolution'] },
  { key: 'graph', label: '图谱', icon: Connection, items: ['/skill-graph', '/capability-evolution'] },
  { key: 'growth', label: '成长与匹配', icon: Aim, items: ['/resume-parser', '/match-analysis', '/learning-path'] },
  { key: 'interview', label: '智能面试', icon: VideoCamera, items: ['/digital-interviewer'] },
  { key: 'manage', label: '治理', icon: Setting, items: ['/review-tasks', '/evaluation', '/settings', '/account-settings'] }
]

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const searchKeyword = ref('')
const candidateAvatar = ref('')
const activeGroupKey = ref<string | null>(null)
const navRef = ref<HTMLElement | null>(null)
const triggerRefs = new Map<string, HTMLElement>()

const isDashboard = computed(() => route.path === '/overview')
const roleLabel = computed(() => auth.role === 'admin' ? '平台管理端' : auth.role === 'hr' ? '企业端' : '个人端')
const userInitial = computed(() => (auth.user?.display_name || auth.user?.username || '用').slice(0, 1))
const userAvatar = computed(() => auth.role === 'candidate' ? candidateAvatar.value : '')

const visibleGroups = computed<MenuGroup[]>(() => {
  const allowed = new Set(roleRouteMap[auth.role || 'candidate'] || roleRouteMap.candidate)
  return groupDefs.map((group) => ({
    ...group,
    items: group.items.map((path) => rawMenus.find((item) => item.path === path)).filter((item): item is MenuItem => Boolean(item && allowed.has(item.path)))
  })).filter((group) => group.items.length)
})

const activeGroup = computed(() => visibleGroups.value.find((group) => group.key === activeGroupKey.value) || null)
const dropdownStyle = computed(() => {
  const trigger = activeGroupKey.value ? triggerRefs.get(activeGroupKey.value) : undefined
  const nav = navRef.value
  if (!trigger || !nav) return {}
  const rect = trigger.getBoundingClientRect()
  const left = Math.max(12, Math.min(rect.left + rect.width / 2 - 145, window.innerWidth - 304))
  return { left: `${left}px`, top: `${nav.getBoundingClientRect().bottom + 6}px` }
})

const searchTargets = computed(() => visibleGroups.value.flatMap((group) => group.items.map((item) => ({ ...item, keywords: `${item.label} ${item.hint} ${group.label}` }))))
const headerSubtitleMap: Record<string, string> = {
  '/personal-center': '维护个人画像、技能证据、项目经历和求职目标',
  '/hr-candidates': '查看人才画像、历史简历与岗位匹配准备情况',
  '/datasets': '统一核验来源、版本、发布日期、许可与同步状态，三端共享同一市场事实基线',
  '/jd-parser': '从岗位描述中提取职责、技能、证书与证据来源',
  '/jobs': '维护岗位画像、状态、版本和能力要求',
  '/emerging-jobs': '从多源岗位样本中识别新岗位与新能力组合',
  '/job-evolution': '查看岗位能力的新增、调整、淘汰与版本记录',
  '/skill-graph': '探索岗位、技能、证书和证据之间的关系',
  '/capability-evolution': '追踪能力热点、迁移趋势和领域结构变化',
  '/resume-parser': '上传并保存 PDF 或 Word 简历解析记录',
  '/match-analysis': '对比简历与目标岗位，查看差距和行动建议',
  '/learning-path': '按顺序完成，不必同时开始',
  '/digital-interviewer': '通过语音与数字人进行模拟面试并生成总评分',
  '/review-tasks': '处理低置信度、证据不足和规则命中的内容',
  '/evaluation': '查看解析、匹配和测试评估结果',
  '/settings': '维护智能服务、知识库和审核规则',
  '/account-settings': '维护账号信息与登录安全'
}
const headerSubtitle = computed(() => headerSubtitleMap[route.path] || '查看并管理当前业务信息')

function setTriggerRef(key: string, el: HTMLElement | null) {
  if (el) triggerRefs.set(key, el)
  else triggerRefs.delete(key)
}

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

function querySearch(query: string, callback: (items: any[]) => void) {
  const keyword = query.trim().toLowerCase()
  callback(searchTargets.value.filter((item) => !keyword || item.keywords.toLowerCase().includes(keyword)).slice(0, 8))
}

function handleSearchSelect(item: { path: string }) {
  searchKeyword.value = ''
  navigateTo(item.path).catch(() => undefined)
}

function handleSearchEnter() {
  const keyword = searchKeyword.value.trim().toLowerCase()
  if (!keyword) return
  const match = searchTargets.value.find((item) => item.keywords.toLowerCase().includes(keyword))
  if (match) handleSearchSelect(match)
  else ElMessage.info('没有找到匹配的功能入口')
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

async function handleUserCommand(command: string) {
  if (command === 'account') await router.push('/account-settings')
  if (command === 'logout') {
    await auth.logout()
    await router.push('/login')
  }
}

function closeDropdown() {
  activeGroupKey.value = null
}

onMounted(() => {
  localStorage.setItem('sr-theme', 'dark')
  document.body.classList.add('theme-dark')
  loadCandidateAvatar()
  document.addEventListener('click', closeDropdown)
})

onBeforeUnmount(() => document.removeEventListener('click', closeDropdown))
</script>

<style scoped>
.app-shell {
  position: relative;
  isolation: isolate;
  min-height: 100vh;
  color: #e9f7ff;
  background: #030a1d;
}

.workspace-backdrop {
  position: fixed;
  z-index: -1;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 18% -12%, rgba(29, 126, 255, 0.22), transparent 34%),
    radial-gradient(circle at 86% 18%, rgba(0, 211, 255, 0.12), transparent 28%),
    radial-gradient(circle at 48% 112%, rgba(29, 126, 255, 0.12), transparent 34%),
    linear-gradient(160deg, #020718 0%, #06142f 52%, #030a1d 100%);
}

.app-header {
  position: sticky;
  z-index: 120;
  top: 0;
  display: flex;
  align-items: center;
  gap: 22px;
  height: 68px;
  padding: 0 24px;
  border-bottom: 1px solid rgba(73, 181, 255, 0.2);
  background: rgba(3, 11, 31, 0.92);
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.24);
  backdrop-filter: blur(18px);
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 11px;
  flex: 0 0 auto;
  border: 0;
  padding: 0;
  background: transparent;
  color: inherit;
  text-align: left;
  cursor: pointer;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 39px;
  height: 39px;
  border: 1px solid rgba(80, 217, 255, 0.52);
  border-radius: 11px;
  background: rgba(20, 112, 198, 0.24);
  color: #55dfff;
  box-shadow: inset 0 0 18px rgba(34, 194, 255, 0.12), 0 0 22px rgba(0, 153, 255, 0.12);
  font-size: 21px;
}

.brand-copy {
  display: flex;
  flex-direction: column;
}

.brand-copy b { color: #f2fbff; font-size: 17px; letter-spacing: 0.08em; }
.brand-copy small { margin-top: 3px; color: #7fa7c9; font-size: 10px; letter-spacing: 0.08em; }

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

.top-nav::-webkit-scrollbar { display: none; }
.nav-group { flex: 0 0 auto; }

.nav-trigger {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  height: 38px;
  border: 1px solid transparent;
  border-radius: 10px;
  padding: 0 12px;
  background: transparent;
  color: #9bbbd5;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: color 160ms ease, border-color 160ms ease, background 160ms ease;
}

.nav-trigger:hover,
.nav-trigger.active {
  border-color: rgba(60, 194, 255, 0.34);
  background: rgba(26, 117, 191, 0.17);
  color: #effbff;
}

.nav-trigger > .el-icon:first-child { color: #41cfff; font-size: 16px; }
.nav-caret { font-size: 11px; opacity: 0.58; transition: transform 160ms ease; }
.nav-caret.open { transform: rotate(180deg); }

.header-actions { display: flex; align-items: center; gap: 10px; flex: 0 0 auto; }
.global-search { width: 238px; }
.global-search :deep(.el-input__wrapper) {
  height: 38px;
  border: 1px solid rgba(80, 180, 235, 0.26);
  border-radius: 11px;
  background: rgba(6, 25, 55, 0.82);
  box-shadow: none;
}
.global-search :deep(.el-input__inner) { color: #eaf8ff; }
.global-search :deep(.el-input__inner::placeholder) { color: #6687a5; }

.role-chip {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  height: 34px;
  border: 1px solid rgba(55, 207, 255, 0.28);
  border-radius: 999px;
  padding: 0 12px;
  background: rgba(12, 71, 125, 0.3);
  color: #aeeeff;
  font-size: 12px;
  font-weight: 750;
  white-space: nowrap;
}

.role-chip i { width: 6px; height: 6px; border-radius: 50%; background: #35d8ff; box-shadow: 0 0 9px rgba(53, 216, 255, 0.8); }

.user-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  max-width: 176px;
  border: 1px solid rgba(80, 180, 235, 0.24);
  border-radius: 12px;
  padding: 3px 9px 3px 3px;
  background: rgba(6, 25, 55, 0.7);
  color: #e9f7ff;
  cursor: pointer;
}

.user-chip > span { overflow: hidden; font-size: 12px; font-weight: 750; text-overflow: ellipsis; white-space: nowrap; }
.user-chip > .el-icon { color: #7897b3; font-size: 11px; }
.user-avatar { background: #1267b8; color: #fff; font-weight: 800; }

.nav-dropdown {
  position: fixed;
  z-index: 2147483647;
  display: grid;
  width: 290px;
  max-height: calc(100vh - 86px);
  gap: 4px;
  overflow-y: auto;
  border: 1px solid rgba(72, 190, 255, 0.32);
  border-radius: 14px;
  padding: 8px;
  background: rgba(4, 17, 43, 0.98);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.52);
}

.dropdown-item {
  display: grid;
  grid-template-columns: 24px minmax(0, 1fr) 18px;
  align-items: center;
  gap: 10px;
  width: 100%;
  border: 1px solid transparent;
  border-radius: 10px;
  padding: 10px;
  background: transparent;
  color: #9abbd6;
  text-align: left;
  cursor: pointer;
}

.dropdown-item:hover,
.dropdown-item.active { border-color: rgba(67, 199, 255, 0.28); background: rgba(20, 105, 174, 0.2); }
.dropdown-item > .el-icon:first-child { color: #49d4ff; font-size: 18px; }
.dropdown-item span { min-width: 0; }
.dropdown-item b { display: block; color: #eaf8ff; font-size: 13px; }
.dropdown-item small { display: block; overflow: hidden; margin-top: 4px; color: #7595b0; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
.dropdown-arrow { color: #4e7393; }

.search-suggestion { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.search-suggestion span { color: #dff7ff; font-weight: 700; }
.search-suggestion small { color: #7393ad; font-size: 11px; }

.app-main { position: relative; min-height: calc(100vh - 68px); padding: 20px 24px 34px; }
.app-main--dashboard { padding: 0; }

.app-titlebar { margin-bottom: 16px; padding-bottom: 14px; border-bottom: 1px solid rgba(71, 160, 216, 0.18); }
.app-titlebar > div { display: flex; align-items: center; gap: 10px; }
.app-titlebar h1 { margin: 0; color: #f1fbff; font-size: 24px; font-weight: 850; letter-spacing: .01em; }
.app-titlebar p { max-width: 860px; margin: 7px 0 0 14px; color: #a2bfd6; font-size: 14px; line-height: 1.6; }
.section-mark { width: 3px; height: 22px; border-radius: 9px; background: #35d8ff; box-shadow: 0 0 12px rgba(53, 216, 255, 0.62); }

@media (max-width: 1500px) {
  .app-header { gap: 12px; padding: 0 16px; }
  .brand-copy small { display: none; }
  .global-search { width: 190px; }
  .nav-trigger { padding: 0 9px; }
}

@media (max-width: 1240px) {
  .brand-copy { display: none; }
  .role-chip { display: none; }
  .user-chip > span { display: none; }
}
</style>
