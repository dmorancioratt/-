<template>
  <section class="pie" aria-label="个人信息录入">
    <div class="pie-head">
      <div class="pie-title">
        <span class="pie-kicker">个人档案 / PERSONAL PROFILE</span>
        <h3>完善个人档案</h3>
        <p>填入真实信息后，岗位匹配、学习路径与面试练习会更贴近你的实际经历。</p>
      </div>

      <div class="pie-head-actions">
        <div class="pie-completion" role="progressbar" :aria-valuenow="completionPercent" aria-valuemin="0" aria-valuemax="100">
          <div class="pie-ring" :style="ringStyle">
            <strong>{{ completionPercent }}<i>%</i></strong>
            <span>完整度</span>
          </div>
        </div>
        <div class="pie-btns">
          <el-button class="pie-save" type="primary" :loading="saving" :disabled="resetting" @click="saveProfile">保存修改</el-button>
          <el-button class="pie-reset" :loading="resetting" :disabled="saving" @click="resetProfile">重置画像</el-button>
        </div>
      </div>
    </div>

    <div class="pie-quality">
      <span v-for="item in qualityItems" :key="item.label" :class="{ done: item.done }" :title="item.label">
        <i>{{ item.done ? '✓' : '·' }}</i>{{ item.label }}
      </span>
    </div>

    <!-- 01 基础信息与求职目标 -->
    <div class="pie-section">
      <div class="pie-section-head">
        <b>01</b><div><h4>基础信息与求职目标</h4><p>用于筛选岗位和计算匹配结果。</p></div>
      </div>
      <el-form label-position="top" class="pie-grid">
        <el-form-item label="真实姓名"><el-input v-model="profile.real_name" placeholder="填写真实姓名" /></el-form-item>
        <el-form-item label="最高学历">
          <el-select v-model="profile.education" filterable placeholder="选择学历">
            <el-option v-for="item in educationOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="专业"><el-input v-model="profile.major" placeholder="填写专业名称" /></el-form-item>
        <el-form-item label="学校">
          <div class="pie-school-field">
            <el-autocomplete v-model="profile.school" :fetch-suggestions="querySchools" clearable placeholder="输入学校名称" />
            <span v-for="badge in schoolBadges" :key="badge" class="pie-elite" :class="eliteBadgeClass(badge)">{{ badge }}</span>
          </div>
        </el-form-item>
        <el-form-item label="目标岗位">
          <el-select v-model="profile.target_role" filterable allow-create default-first-option placeholder="从岗位库选择或输入">
            <el-option v-for="item in jobOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="意向城市">
          <div class="pie-city">
            <el-select v-model="province" filterable placeholder="省份">
              <el-option v-for="prov in cityOptions" :key="prov.value" :label="prov.value" :value="prov.value" />
            </el-select>
            <el-select v-model="city" filterable clearable :disabled="!province" placeholder="城市">
              <el-option v-for="cityOption in currentCities" :key="cityOption.value" :label="cityOption.value" :value="cityOption.value" />
            </el-select>
          </div>
        </el-form-item>
        <el-form-item label="期望薪资" class="pie-salary-item">
          <div class="pie-salary">
            <el-select v-model="salaryStart" filterable placeholder="最低">
              <el-option v-for="item in salaryOptions" :key="`pstart-${item}`" :label="`${item}k`" :value="item" />
            </el-select>
            <span>至</span>
            <el-select v-model="salaryEnd" filterable placeholder="最高">
              <el-option v-for="item in salaryEndOptions" :key="`pend-${item}`" :label="`${item}k`" :value="item" />
            </el-select>
            <em>k / 月</em>
          </div>
        </el-form-item>
        <el-form-item label="头像">
          <div class="pie-avatar" @click="chooseAvatar" :title="profile.avatar_url ? '点击更换头像' : '点击上传头像'">
            <img v-if="profile.avatar_url" :src="profile.avatar_url" alt="头像" />
            <svg v-else class="pie-avatar__mark" viewBox="0 0 64 64" aria-hidden="true">
              <defs>
                <linearGradient id="pieAvatarOrb" x1="0" y1="0" x2="64" y2="64">
                  <stop offset="0" stop-color="#7ce8ff"/><stop offset="1" stop-color="#7c6dff"/>
                </linearGradient>
                <radialGradient id="pieAvatarCore" cx="50%" cy="40%" r="70%">
                  <stop offset="0" stop-color="#eafaff"/><stop offset="0.55" stop-color="#6be0ff"/><stop offset="1" stop-color="#2aa8ff"/>
                </radialGradient>
              </defs>
              <circle cx="32" cy="32" r="22" fill="none" stroke="url(#pieAvatarOrb)" stroke-width="1.3" opacity="0.5"/>
              <circle cx="32" cy="32" r="15.5" fill="none" stroke="url(#pieAvatarOrb)" stroke-width="1" opacity="0.32" stroke-dasharray="3 3.4"/>
              <circle cx="32" cy="31" r="9.6" fill="url(#pieAvatarCore)"/>
              <path d="M32 40.4V33.6" stroke="#08314f" stroke-width="1.8" stroke-linecap="round"/>
              <path d="M32 33.4c-2.5-2.7-2.3-5.5-2-7.3 1.6 1.4 2.5 2.2 3.7 2.9h1.6c1.2-.7 2.1-1.5 3.7-2.9.3 1.8.5 4.6-2 7.3z" fill="rgba(8,49,79,.85)"/>
            </svg>
          </div>
          <input ref="avatarInput" class="pie-avatar-input" type="file" accept="image/png,image/jpeg,image/webp" @change="handleAvatarFile" />
        </el-form-item>
      </el-form>
    </div>

    <!-- 02 能力与成果证据 -->
    <div class="pie-section">
      <div class="pie-section-head"><b>02</b><div><h4>能力与成果证据</h4><p>优先保留能被项目、证书或经历证明的能力。</p></div></div>
      <el-form label-position="top" class="pie-stack">
        <el-form-item label="技能与工具">
          <el-select v-model="profile.skills" multiple filterable allow-create collapse-tags collapse-tags-tooltip :max-collapse-tags="6" default-first-option placeholder="搜索或添加技能">
            <el-option-group v-for="group in skillGroups" :key="group.label" :label="group.label">
              <el-option v-for="item in group.options" :key="item" :label="item" :value="item" />
            </el-option-group>
          </el-select>
          <div v-if="profile.skills.length" class="pie-chips">
            <span v-for="item in profile.skills.slice(0, 10)" :key="item" class="pie-chip">{{ item }}</span>
            <span v-if="profile.skills.length > 10" class="pie-chip">+{{ profile.skills.length - 10 }}</span>
          </div>
          <div v-if="missingTargetSkills.length" class="pie-hint">
            <b>目标岗位待补能力</b>
            <button v-for="item in missingTargetSkills.slice(0, 5)" :key="item" type="button" @click="addProfileValue('skills', item)">+ {{ item }}</button>
          </div>
        </el-form-item>

        <el-form-item label="证书与资质">
          <el-select v-model="profile.certificates" multiple filterable allow-create collapse-tags collapse-tags-tooltip :max-collapse-tags="4" default-first-option placeholder="搜索或添加证书">
            <el-option-group v-for="group in certificateGroups" :key="group.label" :label="group.label">
              <el-option v-for="item in group.options" :key="item" :label="item" :value="item" />
            </el-option-group>
          </el-select>
          <div v-if="profile.certificates.length" class="pie-chips">
            <span v-for="item in profile.certificates.slice(0, 8)" :key="item" class="pie-chip pie-chip--cert">{{ item }}</span>
            <span v-if="profile.certificates.length > 8" class="pie-chip">+{{ profile.certificates.length - 8 }}</span>
          </div>
          <div v-if="targetCertificates.length" class="pie-hint">
            <b>岗位建议证书</b>
            <button v-for="item in targetCertificates.slice(0, 4)" :key="item.name" type="button" @click="addProfileValue('certificates', item.name)">+ {{ item.name }}</button>
          </div>
        </el-form-item>

        <el-form-item label="个人总结">
          <el-input v-model="profile.self_summary" type="textarea" :rows="4" placeholder="用 3-5 句话概括你的方向、核心能力和代表成果" />
        </el-form-item>
      </el-form>
    </div>

    <!-- 03 经历与作品 -->
    <div class="pie-section">
      <div class="pie-section-head"><b>03</b><div><h4>经历与作品</h4><p>每类保留最有代表性的 1-3 项即可。</p></div></div>
      <el-tabs v-model="experienceTab" class="pie-tabs">
        <el-tab-pane :label="`项目经历 ${profile.projects.length}`" name="projects">
          <tag-editor v-model="profile.projects" placeholder="例如：岗位能力图谱平台，负责关系建模与可视化" empty-text="还没有项目经历，先补充一个最能证明目标岗位能力的项目。" />
        </el-tab-pane>
        <el-tab-pane :label="`实习经历 ${profile.internships.length}`" name="internships">
          <tag-editor v-model="profile.internships" placeholder="例如：某科技公司数据平台实习，参与指标口径治理" empty-text="没有实习也可以填写课程实践、实验室或校企项目。" />
        </el-tab-pane>
        <el-tab-pane :label="`竞赛与奖项 ${profile.awards.length}`" name="awards">
          <tag-editor v-model="profile.awards" placeholder="例如：大学生软件设计竞赛省级二等奖" empty-text="可以填写竞赛、奖学金、论文、证书或作品成果。" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, h, onMounted, reactive, ref, watch } from 'vue'
import { ElButton, ElInput, ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api/http'
import { certificateGroups } from '@/data/certificates'
import { cityOptions, doubleFirstClassUniversities, educationOptions, eliteUniversityOptions, salaryOptions, universities211, universities985 } from '@/data/profileOptions'
import { skillGroups } from '@/data/skills'

const auth = useAuthStore()
const saving = ref(false)
const resetting = ref(false)
const experienceTab = ref('projects')
const avatarInput = ref<HTMLInputElement>()
const province = ref<string>('')
const city = ref<string>('')
const salaryStart = ref<number>()
const salaryEnd = ref<number>()
const jobs = ref<any[]>([])
const profile = reactive<any>({
  real_name: '', education: '', major: '', school: '', target_role: '', city: '',
  expected_salary: '', avatar_url: '', skills: [], certificates: [],
  projects: [], internships: [], awards: [], self_summary: '', completeness: 0
})

const completionPercent = computed(() => Number(profile.completeness || 0).toFixed(1).replace(/\.0$/, ''))
const ringStyle = computed(() => ({ '--pie-degree': `${Math.max(0, Math.min(100, Number(profile.completeness || 0))) * 3.6}deg` }))
const salaryEndOptions = computed(() => salaryOptions.filter((item) => !salaryStart.value || item >= salaryStart.value))
const currentCities = computed(() => (cityOptions.find((item) => item.value === province.value)?.children || []).map((item) => item))
const jobOptions = computed(() => Array.from(new Set(jobs.value.map((item) => item.name).filter(Boolean))))
const targetJob = computed(() => jobs.value.find((item) => item.name === profile.target_role))
const missingTargetSkills = computed<string[]>(() => {
  const required = targetJob.value?.requirements?.required_skills || []
  const current = new Set(profile.skills.map((item: string) => item.toLowerCase()))
  return required.filter((item: string) => !current.has(item.toLowerCase()))
})
const targetCertificates = computed<any[]>(() => targetJob.value?.requirements?.recommended_certificates || [])
const schoolBadges = computed(() => {
  const normalized = normalizeSchoolName(profile.school)
  const badges: string[] = []
  if (universities985.some((name) => normalizeSchoolName(name) === normalized)) badges.push('985')
  if (badges.includes('985') || universities211.some((name) => normalizeSchoolName(name) === normalized)) badges.push('211')
  if (doubleFirstClassUniversities.some((name) => normalizeSchoolName(name) === normalized)) badges.push('双一流')
  return badges
})
const qualityItems = computed<{ label: string; done: boolean }[]>(() => [
  { label: '基础信息', done: Boolean(profile.real_name && profile.education && profile.school && profile.major) },
  { label: '求职意向', done: Boolean(profile.target_role && profile.city && profile.expected_salary) },
  { label: '能力标签', done: profile.skills.length >= 5 },
  { label: '证书成果', done: Boolean(profile.certificates.length || profile.awards.length) },
  { label: '项目证据', done: Boolean(profile.projects.length || profile.internships.length) },
  { label: '个人总结', done: Boolean(profile.self_summary) }
])

function addProfileValue(field: 'skills' | 'certificates', value: string) {
  if (!profile[field].includes(value)) profile[field].push(value)
}

const TagEditor = {
  props: ['modelValue', 'placeholder', 'emptyText'],
  emits: ['update:modelValue'],
  setup(props: any, { emit }: any) {
    const value = ref('')
    const add = () => {
      if (!value.value.trim()) return
      emit('update:modelValue', [...props.modelValue, value.value.trim()])
      value.value = ''
    }
    const remove = (item: string) => emit('update:modelValue', props.modelValue.filter((v: string) => v !== item))
    return () =>
      h('div', { class: 'pie-tag-editor' }, [
        props.modelValue.length
          ? h('div', { class: 'pie-exp-list' }, props.modelValue.map((item: string, index: number) =>
              h('div', { class: 'pie-exp-item' }, [
                h('span', { class: 'pie-exp-index' }, String(index + 1).padStart(2, '0')),
                h('p', item),
                h(ElButton, { class: 'pie-exp-remove', text: true, type: 'danger', onClick: () => remove(item) }, () => '移除')
              ])
            ))
          : h('div', { class: 'pie-exp-empty' }, [h('span'), h('p', props.emptyText || '暂无记录，补充后会用于画像完整度和匹配分析。')]),
        h('div', { class: 'pie-tag-input-row' }, [
          h(ElInput, { modelValue: value.value, 'onUpdate:modelValue': (v: string) => (value.value = v), placeholder: props.placeholder, onKeyup: (e: KeyboardEvent) => e.key === 'Enter' && add() }),
          h(ElButton, { type: 'primary', onClick: add }, () => '添加')
        ])
      ])
  }
}

async function loadProfile() {
  try {
    const [profileData, jobRows] = await Promise.all([api.myProfile(), api.jobs()])
    Object.assign(profile, profileData)
    jobs.value = jobRows
    const [prov, c] = parseLocation(profile.city)
    province.value = prov || ''
    city.value = c || ''
    const salary = parseSalary(profile.expected_salary)
    salaryStart.value = salary[0]
    salaryEnd.value = salary[1]
  } catch {
    // 后端不可用时保持空表单
  }
}

async function saveProfile() {
  saving.value = true
  try {
    profile.city = formatLocation()
    profile.expected_salary = formatSalary()
    Object.assign(profile, await api.updateMyProfile(profile))
    window.dispatchEvent(new CustomEvent('profile-avatar-updated', { detail: { avatar_url: profile.avatar_url } }))
    ElMessage.success('个人画像已保存')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || error?.message || '保存失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

async function resetProfile() {
  try {
    await ElMessageBox.confirm('将清空头像、教育经历、求职意向、能力、证书、项目、实习、奖项和个人总结。', '确认重置个人画像？', {
      confirmButtonText: '确认重置', cancelButtonText: '取消', type: 'warning', distinguishCancelAndClose: true
    })
  } catch {
    return
  }
  resetting.value = true
  try {
    const payload = {
      real_name: auth.user?.display_name || auth.user?.username || '', education: '', major: '', school: '',
      target_role: '', city: '', expected_salary: '', avatar_url: '', skills: [], certificates: [],
      projects: [], internships: [], awards: [], self_summary: ''
    }
    Object.assign(profile, await api.updateMyProfile(payload))
    province.value = ''
    city.value = ''
    salaryStart.value = undefined
    salaryEnd.value = undefined
    if (avatarInput.value) avatarInput.value.value = ''
    window.dispatchEvent(new CustomEvent('profile-avatar-updated', { detail: { avatar_url: '' } }))
    ElMessage.success('个人画像已重置')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || error?.message || '重置失败，请稍后重试')
  } finally {
    resetting.value = false
  }
}

watch(salaryStart, (value) => {
  if (value && salaryEnd.value && salaryEnd.value < value) salaryEnd.value = value
})
watch(province, () => { city.value = '' })

function querySchools(query: string, callback: (items: { value: string }[]) => void) {
  const keyword = normalizeSchoolName(query)
  callback(eliteUniversityOptions.filter((item) => !keyword || normalizeSchoolName(item.value).includes(keyword)).slice(0, 20))
}
function normalizeSchoolName(value = '') {
  return value.replace(/[（(].*?[）)]/g, '').replace(/\s+/g, '').trim()
}
function eliteBadgeClass(badge: string) {
  return { 'pie-elite--985': badge === '985', 'pie-elite--211': badge === '211', 'pie-elite--double': badge === '双一流' }
}
function parseLocation(value = '') {
  const parts = value.split('/').map((item) => item.trim()).filter(Boolean)
  if (parts.length >= 2) return [parts[0], parts[1]]
  const matchedProvince = cityOptions.find((item) => item.children.some((c) => c.value === value))
  return matchedProvince ? [matchedProvince.value, value] : []
}
function formatLocation() {
  if (province.value && city.value) return `${province.value} / ${city.value}`
  if (province.value) return province.value
  return ''
}
function parseSalary(value = ''): [number | undefined, number | undefined] {
  const numbers = value.match(/\d+/g)?.map(Number) || []
  return [numbers[0], numbers[1]]
}
function formatSalary() {
  if (!salaryStart.value && !salaryEnd.value) return ''
  if (salaryStart.value && salaryEnd.value) return `${salaryStart.value}k-${salaryEnd.value}k`
  return salaryStart.value ? `${salaryStart.value}k起` : `${salaryEnd.value}k以内`
}
function chooseAvatar() { avatarInput.value?.click() }
function handleAvatarFile(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) { ElMessage.warning('请选择图片文件'); return }
  if (file.size > 1.5 * 1024 * 1024) { ElMessage.warning('头像图片建议小于 1.5MB'); input.value = ''; return }
  const reader = new FileReader()
  reader.onload = () => { profile.avatar_url = String(reader.result || '') }
  reader.readAsDataURL(file)
  input.value = ''
}

onMounted(loadProfile)
</script>

<style scoped>
.pie { display: grid; gap: 16px; margin-top: 20px; }

.pie-head {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 22px; flex-wrap: wrap;
  padding: 22px 24px;
}
.pie-kicker { color: #52dcff; font-size: 10px; font-weight: 900; letter-spacing: .16em; }
.pie-title h3 { margin: 8px 0 6px; color: #f2fbff; font-size: 20px; }
.pie-title p { margin: 0; color: #7fa2c2; font-size: 12px; line-height: 1.7; }

.pie-head-actions { display: flex; align-items: center; gap: 20px; }
.pie-ring {
  --pie-degree: 0deg;
  position: relative; display: grid; place-items: center; width: 86px; height: 86px;
  border-radius: 50%;
  background: conic-gradient(#4fd8ff var(--pie-degree), rgba(78, 190, 255, .14) 0);
}
.pie-ring::before { content: ""; grid-area: 1 / 1; width: 68px; height: 68px; border-radius: 50%; background: rgba(8, 26, 58, .9); border: 1px solid rgba(96, 190, 255, .28); }
.pie-ring strong, .pie-ring span { grid-area: 1 / 1; color: #fff; font-size: 19px; }
.pie-ring strong i { color: #4fd8ff; font-size: 11px; font-style: normal; }
.pie-ring span { margin-top: 28px; color: #7fa2c2; font-size: 9px; }

.pie-btns { display: flex; flex-direction: column; gap: 8px; }
.pie-save, .pie-reset { width: 100%; border-radius: 9px; }
.pie-save { border: 0; background: linear-gradient(90deg, #1dbae7, #2857ee); font-weight: 700; }
.pie-reset { border: 1px solid rgba(120, 200, 255, .35); color: #8ae4ff; background: rgba(23, 110, 192, .14); }

.pie-quality { display: flex; flex-wrap: wrap; gap: 8px; padding: 0 24px; }
.pie-quality span {
  display: inline-flex; align-items: center; gap: 5px; border: 1px solid rgba(96, 186, 255, .2);
  border-radius: 999px; padding: 5px 10px; color: #86a8c8; background: rgba(4, 30, 70, .35); font-size: 11px;
}
.pie-quality i { color: #5fb8e6; font-style: normal; }
.pie-quality span.done { border-color: rgba(72, 224, 193, .5); color: #8af0d2; }
.pie-quality span.done i { color: #48e0c1; }

.pie-section {
  border: 1px solid rgba(96, 186, 255, .24); border-radius: 14px; padding: 20px 22px;
  background: linear-gradient(150deg, rgba(13, 34, 70, .66), rgba(6, 16, 38, .78));
  box-shadow: inset 0 1px 0 rgba(190, 235, 255, .06);
}
.pie-section-head { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 16px; }
.pie-section-head > b {
  display: grid; place-items: center; width: 30px; height: 30px; flex-shrink: 0;
  border: 1px solid rgba(88, 230, 255, .5); border-radius: 8px; color: #8ce6ff; background: rgba(31, 113, 206, .18); font-size: 12px;
}
.pie-section-head h4 { margin: 0; color: #ecf7ff; font-size: 15px; }
.pie-section-head p { margin: 4px 0 0; color: #7497ba; font-size: 11px; }

.pie-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0 18px; }
.pie-grid :deep(.el-form-item) { margin-bottom: 14px; }
.pie-grid :deep(.el-form-item__label) { color: #9bbcd8; font-size: 12px; padding-bottom: 6px; }
.pie-salary { display: flex; align-items: center; gap: 8px; }
.pie-salary > span { color: #7c9dbb; font-size: 12px; }
.pie-salary em { margin-left: 6px; color: #6d8ea6; font-size: 11px; font-style: normal; }
.pie-school-field { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.pie-elite { border-radius: 5px; padding: 2px 6px; font-size: 10px; }
.pie-elite--985 { color: #ffe08a; background: rgba(124, 74, 20, .28); }
.pie-elite--211 { color: #8ef0da; background: rgba(22, 110, 96, .28); }
.pie-elite--double { color: #d8bcff; background: rgba(84, 54, 150, .32); }

.pie-avatar {
  display: grid; place-items: center; width: 64px; height: 64px; overflow: hidden;
  border: 1px solid rgba(110, 214, 255, .5); border-radius: 16px; cursor: pointer;
  background:
    radial-gradient(120% 120% at 30% 18%, rgba(23, 209, 255, .18), transparent 58%),
    linear-gradient(145deg, rgba(12, 42, 84, .9), rgba(7, 19, 44, .92));
  box-shadow: inset 0 1px 0 rgba(178, 236, 255, .12);
}
.pie-avatar img { width: 100%; height: 100%; object-fit: cover; }
.pie-avatar__mark { width: 58px; height: 58px; display: block; }
.pie-avatar-input { display: none; }

.pie-city { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }

/* ===== 统一控件暗色主题 ===== */
.pie :deep(.el-input__wrapper),
.pie :deep(.el-select__wrapper),
.pie :deep(.el-textarea__inner) {
  background: rgba(6, 20, 46, .55);
  box-shadow: 0 0 0 1px rgba(104, 178, 255, .2) inset;
  border-radius: 9px;
  transition: box-shadow .18s ease, background .18s ease;
}
.pie :deep(.el-input__wrapper:hover),
.pie :deep(.el-select__wrapper:hover),
.pie :deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px rgba(119, 203, 255, .5) inset;
}
.pie :deep(.el-input__wrapper.is-focus),
.pie :deep(.el-select__wrapper.is-focused),
.pie :deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px #4fd8ff inset, 0 0 0 3px rgba(79, 216, 255, .12);
}
.pie :deep(.el-input__inner),
.pie :deep(.el-select__placeholder),
.pie :deep(.el-textarea__inner) {
  color: #eaf7ff;
}
.pie :deep(.el-input__inner::placeholder),
.pie :deep(.el-textarea__inner::placeholder) {
  color: #5c7d9c;
}
.pie :deep(.el-select__placeholder.is-transparent) { color: #5c7d9c; }
.pie :deep(.el-input__icon),
.pie :deep(.el-select__caret) { color: #6aa8d8; }
.pie :deep(.el-tag) {
  background: rgba(31, 113, 206, .22);
  border-color: rgba(110, 214, 255, .28);
  color: #cfeaff;
}
.pie :deep(.el-tag .el-tag__close) { color: #9fd4f5; }
.pie :deep(.el-tag .el-tag__close:hover) { color: #fff; background: rgba(255, 92, 128, .6); }

/* ===== 下拉选项面板暗色主题（teleport 到 body，走全局） ===== */
:global(.el-select__popper),
:global(.el-autocomplete-suggestion) {
  --el-bg-color-overlay: rgba(10, 26, 58, .96);
  background: rgba(10, 26, 58, .96);
  border-color: rgba(96, 186, 255, .24);
  backdrop-filter: blur(12px);
}
:global(.el-select__popper .el-select-dropdown__item),
:global(.el-autocomplete-suggestion__list li) {
  color: #c9e2f5;
  border-radius: 8px;
}
:global(.el-select__popper .el-select-dropdown__item.hover),
:global(.el-select__popper .el-select-dropdown__item.is-hovering),
:global(.el-select__popper .el-select-dropdown__item:hover),
:global(.el-autocomplete-suggestion__list li:hover) {
  background: rgba(79, 216, 255, .12);
  color: #eaf7ff;
}
:global(.el-select-dropdown__item.is-selected) { color: #6ee2ff; font-weight: 600; }
:global(.el-select-group__title) { color: #5f8fb5; }
:global(.el-popper.is-light .el-popper__arrow::before) { border-color: rgba(96, 186, 255, .3); background: rgba(10, 26, 58, .96); }

.pie-stack :deep(.el-form-item) { margin-bottom: 16px; }
.pie-stack :deep(.el-form-item__label) { color: #9bbcd8; font-size: 12px; padding-bottom: 6px; }
.pie-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.pie-chip { border: 1px solid rgba(96, 186, 255, .24); border-radius: 5px; padding: 4px 8px; color: #a9d9ff; background: rgba(21, 86, 152, .14); font-size: 11px; }
.pie-chip--cert { border-color: rgba(190, 104, 255, .4); color: #d8bcff; background: rgba(84, 54, 150, .16); }
.pie-hint { display: flex; flex-wrap: wrap; align-items: center; gap: 7px; margin-top: 10px; }
.pie-hint b { width: 100%; color: #789fc0; font-size: 11px; }
.pie-hint button { border: 1px dashed rgba(70, 221, 255, .5); border-radius: 6px; padding: 5px 9px; color: #8ce6ff; background: rgba(19, 116, 213, .14); font: inherit; font-size: 11px; cursor: pointer; }
.pie-hint button:hover { border-color: #6ee2ff; color: #fff; }

.pie-tabs :deep(.el-tabs__item) { color: #9bbcd8; font-size: 13px; }
.pie-tabs :deep(.el-tabs__item.is-active) { color: #6ee2ff; }
.pie-tabs :deep(.el-tabs__active-bar) { background-color: #4fd8ff; }
.pie-tabs :deep(.el-tabs__nav-wrap::after) { background-color: rgba(96, 186, 255, .16); }

.pie-tag-editor { display: grid; gap: 10px; }
.pie-exp-list { display: grid; gap: 8px; }
.pie-exp-item {
  display: grid; grid-template-columns: 30px 1fr auto; align-items: center; gap: 10px;
  border: 1px solid rgba(96, 186, 255, .2); border-radius: 9px; padding: 10px 12px; background: rgba(4, 30, 70, .35);
}
.pie-exp-index { color: #4fd8ff; font-size: 12px; font-weight: 800; }
.pie-exp-item p { margin: 0; color: #d5ecf8; font-size: 12.5px; line-height: 1.6; }
.pie-exp-remove { color: #ff9db0; }
.pie-exp-empty { display: grid; place-items: center; gap: 8px; border: 1px dashed rgba(96, 186, 255, .24); border-radius: 9px; padding: 26px; color: #6d8ea6; font-size: 12px; text-align: center; }
.pie-tag-input-row { display: flex; gap: 10px; }
.pie-tag-input-row :deep(.el-input) { flex: 1; }

@media (max-width: 1180px) {
  .pie-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>