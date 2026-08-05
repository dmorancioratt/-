<template>
  <div class="page profile-page">
    <div class="profile-redesign">
      <header class="profile-overview">
        <div class="profile-person">
          <button class="profile-avatar" type="button" aria-label="更换头像" @click="chooseAvatar">
            <img v-if="profile.avatar_url" :src="profile.avatar_url" alt="个人头像" />
            <span v-else>{{ avatarInitial }}</span>
          </button>
          <input ref="avatarInput" class="avatar-input" type="file" accept="image/png,image/jpeg,image/webp" @change="handleAvatarFile" />
          <div class="profile-person__copy">
            <span>个人求职档案</span>
            <h2>{{ profile.real_name || auth.user?.display_name || auth.user?.username }}</h2>
            <p>{{ profileBrief }}</p>
            <div class="profile-target-line">
              <b>{{ profile.target_role || '尚未选择目标岗位' }}</b>
              <span>{{ cityText || '意向城市待补充' }}</span>
              <span>{{ profile.expected_salary || '期望薪资待补充' }}</span>
            </div>
          </div>
        </div>

        <div class="profile-overview__right">
          <div class="profile-completion">
            <div><span>画像完整度</span><strong>{{ completionPercent }}%</strong></div>
            <i><span :style="{ width: `${Math.min(100, Number(profile.completeness || 0))}%` }"></span></i>
            <small>{{ qualityItems.filter((item) => item.done).length }} / {{ qualityItems.length }} 类资料已完善</small>
          </div>
          <div class="profile-actions">
            <el-button class="profile-save-btn" type="primary" :loading="saving" :disabled="resetting" @click="saveProfile">保存修改</el-button>
            <el-button class="profile-reset-btn" :loading="resetting" :disabled="saving" @click="resetProfile">重置画像</el-button>
          </div>
        </div>
      </header>

      <section class="profile-next-step">
        <div>
          <span>当前建议</span>
          <h3>{{ nextAction.title }}</h3>
          <p>{{ nextAction.desc }}</p>
        </div>
        <div class="profile-next-step__actions">
          <button type="button" @click="router.push('/resume-parser')">解析简历</button>
          <button type="button" @click="router.push('/match-analysis')">岗位匹配</button>
        </div>
      </section>

      <div class="profile-quality" aria-label="画像资料完成情况">
        <span v-for="item in qualityItems" :key="item.label" :class="{ done: item.done }">
          <i>{{ item.done ? '✓' : '·' }}</i>{{ item.label }}
        </span>
      </div>

      <section class="profile-edit-section profile-basic-card">
        <div class="profile-section-heading">
          <div><span>01</span><h3>基础信息与求职目标</h3></div>
          <p>这些信息用于筛选岗位和计算匹配结果。</p>
        </div>
        <el-form label-position="top" class="profile-form-grid">
          <el-form-item label="真实姓名"><el-input v-model="profile.real_name" /></el-form-item>
          <el-form-item label="最高学历">
            <el-select v-model="profile.education" placeholder="选择学历" filterable>
              <el-option v-for="item in educationOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="专业"><el-input v-model="profile.major" placeholder="填写专业名称" /></el-form-item>
          <el-form-item label="学校">
            <div class="school-field">
              <el-autocomplete v-model="profile.school" :fetch-suggestions="querySchools" clearable placeholder="输入学校名称" />
              <div v-if="schoolBadges.length" class="school-badges">
                <span v-for="badge in schoolBadges" :key="badge" class="elite-badge" :class="eliteBadgeClass(badge)">{{ badge }}</span>
              </div>
            </div>
          </el-form-item>
          <el-form-item label="目标岗位">
            <el-select v-model="profile.target_role" filterable allow-create default-first-option placeholder="选择或输入岗位">
              <el-option v-for="item in jobOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="意向城市">
            <el-cascader v-model="locationValue" :options="cityOptions" filterable clearable placeholder="选择省份 / 城市" />
          </el-form-item>
          <el-form-item label="期望薪资" class="salary-form-item">
            <div class="salary-range">
              <el-select v-model="salaryStart" filterable placeholder="最低">
                <el-option v-for="item in salaryOptions" :key="`start-new-${item}`" :label="`${item}k`" :value="item" />
              </el-select>
              <span>至</span>
              <el-select v-model="salaryEnd" filterable placeholder="最高">
                <el-option v-for="item in salaryEndOptions" :key="`end-new-${item}`" :label="`${item}k`" :value="item" />
              </el-select>
              <em>k / 月</em>
            </div>
          </el-form-item>
        </el-form>
      </section>

      <section class="profile-edit-section profile-ability-card">
        <div class="profile-section-heading">
          <div><span>02</span><h3>能力与成果证据</h3></div>
          <p>优先保留能被项目、证书或经历证明的能力。</p>
        </div>
        <div class="profile-evidence-grid">
          <el-form label-position="top">
            <el-form-item label="技能与工具">
              <el-select v-model="profile.skills" multiple filterable allow-create collapse-tags collapse-tags-tooltip :max-collapse-tags="5" default-first-option placeholder="搜索或添加技能">
                <el-option-group v-for="group in skillGroups" :key="group.label" :label="group.label">
                  <el-option v-for="item in group.options" :key="item" :label="item" :value="item" />
                </el-option-group>
              </el-select>
              <div v-if="profile.skills.length" class="chip-preview">
                <span v-for="item in profile.skills.slice(0, 10)" :key="item" class="profile-chip">{{ item }}</span>
                <span v-if="profile.skills.length > 10" class="profile-chip">+{{ profile.skills.length - 10 }}</span>
              </div>
              <div v-if="missingTargetSkills.length" class="profile-recommendation">
                <b>目标岗位待补能力</b>
                <button v-for="item in missingTargetSkills.slice(0, 5)" :key="item" type="button" @click="addProfileValue('skills', item)">+ {{ item }}</button>
              </div>
            </el-form-item>
          </el-form>

          <el-form label-position="top">
            <el-form-item label="证书与资质">
              <el-select v-model="profile.certificates" multiple filterable allow-create collapse-tags collapse-tags-tooltip :max-collapse-tags="4" default-first-option placeholder="搜索或添加证书">
                <el-option-group v-for="group in certificateGroups" :key="group.label" :label="group.label">
                  <el-option v-for="item in group.options" :key="item" :label="item" :value="item" />
                </el-option-group>
              </el-select>
              <div v-if="profile.certificates.length" class="chip-preview">
                <span v-for="item in profile.certificates.slice(0, 8)" :key="item" class="profile-chip certificate-chip">{{ item }}</span>
                <span v-if="profile.certificates.length > 8" class="profile-chip">+{{ profile.certificates.length - 8 }}</span>
              </div>
              <div v-if="targetCertificates.length" class="profile-recommendation">
                <b>岗位建议证书</b>
                <button v-for="item in targetCertificates.slice(0, 4)" :key="item.name" type="button" @click="addProfileValue('certificates', item.name)">+ {{ item.name }}</button>
              </div>
            </el-form-item>
          </el-form>
        </div>
        <el-form label-position="top" class="profile-summary-form">
          <el-form-item label="个人总结">
            <el-input v-model="profile.self_summary" type="textarea" :rows="4" placeholder="用 3-5 句话概括你的方向、核心能力和代表成果" />
          </el-form-item>
        </el-form>
      </section>

      <section class="profile-edit-section profile-experience-section">
        <div class="profile-section-heading">
          <div><span>03</span><h3>经历与作品</h3></div>
          <p>每类保留最有代表性的 1-3 项即可。</p>
        </div>
        <el-tabs v-model="experienceTab" class="profile-experience-tabs">
          <el-tab-pane :label="`项目经历 ${profile.projects.length}`" name="projects">
            <TagEditor v-model="profile.projects" placeholder="例如：岗位能力图谱平台，负责关系建模与可视化" empty-text="还没有项目经历，先补充一个最能证明目标岗位能力的项目。" />
          </el-tab-pane>
          <el-tab-pane :label="`实习经历 ${profile.internships.length}`" name="internships">
            <TagEditor v-model="profile.internships" placeholder="例如：某科技公司数据平台实习，参与指标口径治理" empty-text="没有实习也可以填写课程实践、实验室或校企项目。" />
          </el-tab-pane>
          <el-tab-pane :label="`竞赛与奖项 ${profile.awards.length}`" name="awards">
            <TagEditor v-model="profile.awards" placeholder="例如：大学生软件设计竞赛省级二等奖" empty-text="可以填写竞赛、奖学金、论文、证书或作品成果。" />
          </el-tab-pane>
        </el-tabs>
      </section>
    </div>

    <section class="profile-card profile-glass-card">
      <div class="profile-identity">
        <button class="avatar-picker" type="button" @click="chooseAvatar">
          <img v-if="profile.avatar_url" :src="profile.avatar_url" alt="个人头像" />
          <span v-else class="avatar-icon-wrap">
            <IconSprite name="profile" :size="68" />
            <b>{{ avatarInitial }}</b>
          </span>
        </button>
        <div class="identity-copy">
          <div class="identity-topline">
            <h2>{{ profile.real_name || auth.user?.display_name || auth.user?.username }}</h2>
            <span>求职者/学生</span>
          </div>
          <p class="identity-summary">{{ profileBrief }}</p>
          <div class="identity-targets">
            <span>目标岗位：{{ profile.target_role || '待选择' }}</span>
            <span>意向城市：{{ cityText || '待选择' }}</span>
          </div>
          <div class="avatar-actions">
            <el-button size="small" @click="chooseAvatar">更换头像</el-button>
            <el-button v-if="profile.avatar_url" size="small" text @click="profile.avatar_url = ''">移除</el-button>
          </div>
          <input ref="avatarInput" class="avatar-input" type="file" accept="image/png,image/jpeg,image/webp" @change="handleAvatarFile" />
        </div>
      </div>

      <div class="profile-card-side">
        <div class="completion-panel">
          <div class="completion-ring" :style="completionStyle">
            <span class="completion-stream stream-1"></span>
            <span class="completion-stream stream-2"></span>
            <span class="completion-stream stream-3"></span>
            <span class="completion-stream stream-4"></span>
            <span class="completion-progress"></span>
            <div class="completion-core">
              <strong>{{ completionPercent }}%</strong>
            </div>
          </div>
          <span>画像完整度</span>
        </div>
        <div class="profile-primary-actions">
          <el-button class="profile-save-btn" type="primary" :loading="saving" :disabled="resetting" @click="saveProfile">保存个人画像</el-button>
          <el-button class="profile-reset-btn" :loading="resetting" :disabled="saving" @click="resetProfile">一键重置</el-button>
        </div>
      </div>
    </section>

    <section class="profile-flow">
      <article class="profile-flow-summary profile-glass-card">
        <svg class="flow-aurora-svg" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
          <defs>
            <linearGradient id="flowAuroraGradient" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="100" y2="100">
              <stop offset="0%" stop-color="#00c8f5" stop-opacity="0.22" />
              <stop offset="24%" stop-color="#4df5ff" stop-opacity="0.72" />
              <stop offset="50%" stop-color="#1e7bff" stop-opacity="0.82" />
              <stop offset="76%" stop-color="#7c3aed" stop-opacity="0.58" />
              <stop offset="100%" stop-color="#00e5ff" stop-opacity="0.22" />
            </linearGradient>
            <filter id="flowAuroraGlow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="2.6" />
            </filter>
          </defs>
          <rect class="flow-border-base" x="0.8" y="0.8" width="98.4" height="98.4" rx="9" ry="9" />
          <rect class="flow-aurora-glow" pathLength="100" x="0.8" y="0.8" width="98.4" height="98.4" rx="9" ry="9" />
          <rect class="flow-aurora-streak" pathLength="100" x="1" y="1" width="98" height="98" rx="8" ry="8" />
        </svg>
        <span>求职闭环</span>
        <h3>{{ nextAction.title }}</h3>
        <p>{{ nextAction.desc }}</p>
      </article>
      <button v-for="item in flowSteps" :key="item.path" type="button" class="profile-flow-card profile-glass-card" @click="router.push(item.path)">
        <svg class="flow-aurora-svg" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
          <defs>
            <linearGradient id="flowAuroraGradient" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="100" y2="100">
              <stop offset="0%" stop-color="#00c8f5" stop-opacity="0.22" />
              <stop offset="24%" stop-color="#4df5ff" stop-opacity="0.72" />
              <stop offset="50%" stop-color="#1e7bff" stop-opacity="0.82" />
              <stop offset="76%" stop-color="#7c3aed" stop-opacity="0.58" />
              <stop offset="100%" stop-color="#00e5ff" stop-opacity="0.22" />
            </linearGradient>
            <filter id="flowAuroraGlow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="2.6" />
            </filter>
          </defs>
          <rect class="flow-border-base" x="0.8" y="0.8" width="98.4" height="98.4" rx="9" ry="9" />
          <rect class="flow-aurora-glow" pathLength="100" x="0.8" y="0.8" width="98.4" height="98.4" rx="9" ry="9" />
          <rect class="flow-aurora-streak" pathLength="100" x="1" y="1" width="98" height="98" rx="8" ry="8" />
        </svg>
        <span class="flow-arrow">→</span>
        <span class="flow-icon">
          <IconSprite :name="item.icon" :size="118" />
        </span>
        <b>{{ item.index }}</b>
        <strong>{{ item.title }}</strong>
        <em>{{ item.desc }}</em>
      </button>
    </section>

    <section class="profile-status-grid">
      <article v-for="item in qualityItems" :key="item.label" class="profile-status-card profile-glass-card" :class="{ done: item.done }">
        <span class="status-icon">
          <IconSprite :name="item.icon" :size="78" />
        </span>
        <div>
          <b>{{ item.label }}</b>
          <strong>{{ item.done ? '已完善' : '待完善' }}</strong>
        </div>
        <span class="status-check">✓</span>
      </article>
    </section>

    <div class="profile-info-grid">
      <section class="profile-section-card profile-glass-card profile-basic-card">
        <div class="section-head">
          <div>
            <span>BASIC INFORMATION</span>
            <h3>基础信息</h3>
          </div>
          <el-button class="profile-secondary-btn" size="small" @click="focusBasicForm">编辑</el-button>
        </div>
        <el-form label-width="90px">
          <el-form-item label="真实姓名"><el-input v-model="profile.real_name" /></el-form-item>
          <el-form-item label="学历">
            <el-select v-model="profile.education" placeholder="请选择最高学历" filterable>
              <el-option v-for="item in educationOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="专业"><el-input v-model="profile.major" /></el-form-item>
          <el-form-item label="学校">
            <div class="school-field">
              <el-autocomplete
                v-model="profile.school"
                :fetch-suggestions="querySchools"
                clearable
                placeholder="输入学校名称"
              />
              <div class="school-badges">
                <span v-for="badge in schoolBadges" :key="badge" class="elite-badge" :class="eliteBadgeClass(badge)">{{ badge }}</span>
              </div>
            </div>
          </el-form-item>
          <el-form-item label="目标岗位">
            <el-select v-model="profile.target_role" filterable allow-create default-first-option placeholder="从岗位库选择，也可输入自定义岗位">
              <el-option v-for="item in jobOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="意向城市">
            <el-cascader
              v-model="locationValue"
              :options="cityOptions"
              filterable
              clearable
              placeholder="请选择省份 / 城市"
            />
          </el-form-item>
          <el-form-item label="期望薪资">
            <div class="salary-range">
              <el-select v-model="salaryStart" filterable placeholder="最低">
                <el-option v-for="item in salaryOptions" :key="`start-${item}`" :label="`${item}k`" :value="item" />
              </el-select>
              <span>至</span>
              <el-select v-model="salaryEnd" filterable placeholder="最高">
                <el-option v-for="item in salaryEndOptions" :key="`end-${item}`" :label="`${item}k`" :value="item" />
              </el-select>
              <em>单位：k / 月</em>
            </div>
          </el-form-item>
        </el-form>
      </section>

      <section class="profile-section-card profile-glass-card profile-ability-card">
        <div class="section-head">
          <div>
            <span>ABILITIES & CERTIFICATES</span>
            <h3>能力与证书</h3>
          </div>
          <el-button class="profile-secondary-btn" size="small" @click="focusAbilityForm">编辑</el-button>
        </div>
        <el-form label-position="top">
          <el-form-item label="我拥有的能力">
            <el-select
              v-model="profile.skills"
              multiple
              filterable
              allow-create
              collapse-tags
              collapse-tags-tooltip
              :max-collapse-tags="4"
              default-first-option
              placeholder="搜索技能、工具、方向或自定义输入"
            >
              <el-option-group v-for="group in skillGroups" :key="group.label" :label="group.label">
                <el-option v-for="item in group.options" :key="item" :label="item" :value="item" />
              </el-option-group>
            </el-select>
            <div v-if="profile.skills.length" class="chip-preview">
              <span v-for="item in profile.skills.slice(0, 8)" :key="item" class="profile-chip">{{ item }}</span>
              <span v-if="profile.skills.length > 8" class="profile-chip more-chip">+{{ profile.skills.length - 8 }}</span>
            </div>
            <div class="select-meta">已内置 {{ skillOptions.length }} 项能力标签，覆盖开发、数据、智能应用、安全、交付和通用能力。</div>
            <div v-if="missingTargetSkills.length" class="requirement-hint">
              <b>{{ profile.target_role }} 还缺少的目录能力</b>
              <button v-for="item in missingTargetSkills.slice(0, 6)" :key="item" type="button" @click="addProfileValue('skills', item)">+ {{ item }}</button>
            </div>
          </el-form-item>
          <el-form-item label="证书">
            <el-select
              v-model="profile.certificates"
              multiple
              filterable
              allow-create
              collapse-tags
              collapse-tags-tooltip
              :max-collapse-tags="3"
              default-first-option
              placeholder="搜索证书名称、厂商或方向，也可自定义输入"
            >
              <el-option-group v-for="group in certificateGroups" :key="group.label" :label="group.label">
                <el-option v-for="item in group.options" :key="item" :label="item" :value="item" />
              </el-option-group>
            </el-select>
            <div v-if="profile.certificates.length" class="chip-preview">
              <span v-for="item in profile.certificates.slice(0, 6)" :key="item" class="profile-chip certificate-chip">{{ item }}</span>
              <span v-if="profile.certificates.length > 6" class="profile-chip more-chip">+{{ profile.certificates.length - 6 }}</span>
            </div>
            <div class="select-meta">已内置 {{ certificateOptions.length }} 项 IT 相关证书，支持关键词搜索和自定义添加。</div>
            <div v-if="targetCertificates.length" class="requirement-hint certificate-recommendation">
              <b>{{ profile.target_role }} 的建议证书（非强制门槛）</b>
              <button v-for="item in targetCertificates" :key="item.name" type="button" @click="addProfileValue('certificates', item.name)">+ {{ item.name }}</button>
            </div>
          </el-form-item>
          <el-form-item label="自我总结">
            <el-input v-model="profile.self_summary" type="textarea" :rows="5" />
          </el-form-item>
        </el-form>
      </section>
    </div>

    <section class="profile-experience-grid">
      <article class="profile-section-card profile-glass-card experience-card">
        <div class="experience-head">
          <span class="experience-icon">
            <IconSprite name="folder" :size="56" />
          </span>
          <div>
            <span>PROJECT EXPERIENCE</span>
            <h3>项目经历</h3>
            <p>写清项目目标、你的职责、技术栈和结果。</p>
          </div>
          <b>{{ profile.projects.length }} 项</b>
        </div>
        <TagEditor v-model="profile.projects" placeholder="例如：岗位能力图谱平台，负责图谱关系建模与可视化" empty-text="还没有项目经历，建议补充 1-3 个能证明能力的项目。" />
      </article>

      <article class="profile-section-card profile-glass-card experience-card">
        <div class="experience-head">
          <span class="experience-icon">
            <IconSprite name="shield" :size="56" />
          </span>
          <div>
            <span>INTERNSHIP EXPERIENCE</span>
            <h3>实习经历</h3>
            <p>记录公司、岗位、工作内容和产出。</p>
          </div>
          <b>{{ profile.internships.length }} 项</b>
        </div>
        <TagEditor v-model="profile.internships" placeholder="例如：某科技公司数据平台实习，参与指标口径治理" empty-text="还没有实习经历，可以先写课程实践、实验室经历或校企项目。" />
      </article>

      <article class="profile-section-card profile-glass-card experience-card">
        <div class="experience-head">
          <span class="experience-icon">
            <IconSprite name="certificate" :size="56" />
          </span>
          <div>
            <span>COMPETITIONS & AWARDS</span>
            <h3>竞赛 / 奖项</h3>
            <p>补充证书、竞赛、奖学金或作品成果。</p>
          </div>
          <b>{{ profile.awards.length }} 项</b>
        </div>
        <TagEditor v-model="profile.awards" placeholder="例如：大学生软件设计竞赛省级二等奖" empty-text="还没有竞赛或奖项，后续可补充证书、比赛、论文或作品成果。" />
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onMounted, reactive, ref, watch } from 'vue'
import { ElButton, ElInput, ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import IconSprite from '@/components/IconSprite.vue'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import { certificateGroups, certificateOptions } from '@/data/certificates'
import { cityOptions, doubleFirstClassUniversities, educationOptions, eliteUniversityOptions, salaryOptions, universities211, universities985 } from '@/data/profileOptions'
import { skillGroups, skillOptions } from '@/data/skills'

type SpriteName = 'profile' | 'progress' | 'certificate' | 'folder' | 'target' | 'chart' | 'education' | 'shield' | 'setting'

const auth = useAuthStore()
const router = useRouter()
const saving = ref(false)
const resetting = ref(false)
const experienceTab = ref('projects')
const avatarInput = ref<HTMLInputElement>()
const locationValue = ref<string[]>([])
const salaryStart = ref<number>()
const salaryEnd = ref<number>()
const jobs = ref<any[]>([])
const profile = reactive<any>({
  real_name: '',
  education: '',
  major: '',
  school: '',
  target_role: '',
  city: '',
  expected_salary: '',
  avatar_url: '',
  skills: [],
  certificates: [],
  projects: [],
  internships: [],
  awards: [],
  self_summary: '',
  completeness: 0
})

const avatarInitial = computed(() => (profile.real_name || auth.user?.display_name || auth.user?.username || '我').slice(0, 1))
const completionPercent = computed(() => Number(profile.completeness || 0).toFixed(1).replace(/\.0$/, ''))
const completionStyle = computed(() => {
  const degree = Math.max(0, Math.min(100, Number(profile.completeness || 0))) * 3.6
  return { '--completion-degree': `${degree}deg` }
})
const profileBrief = computed(() => {
  const fields = [profile.major, profile.education, profile.school].filter(Boolean)
  return fields.length ? fields.join(' · ') : '补充专业、学历和学校后，画像摘要会在这里展示'
})
const cityText = computed(() => formatLocation() || profile.city)
const schoolBadges = computed(() => {
  const normalized = normalizeSchoolName(profile.school)
  const badges: string[] = []
  if (universities985.some((name) => normalizeSchoolName(name) === normalized)) badges.push('985')
  if (badges.includes('985') || universities211.some((name) => normalizeSchoolName(name) === normalized)) badges.push('211')
  if (doubleFirstClassUniversities.some((name) => normalizeSchoolName(name) === normalized)) badges.push('双一流')
  return badges
})
const salaryEndOptions = computed(() => salaryOptions.filter((item) => !salaryStart.value || item >= salaryStart.value))
const jobOptions = computed(() => Array.from(new Set(jobs.value.map((item) => item.name).filter(Boolean))))
const targetJob = computed(() => jobs.value.find((item) => item.name === profile.target_role))
const missingTargetSkills = computed<string[]>(() => {
  const required = targetJob.value?.requirements?.required_skills || []
  const current = new Set(profile.skills.map((item: string) => item.toLowerCase()))
  return required.filter((item: string) => !current.has(item.toLowerCase()))
})
const targetCertificates = computed<any[]>(() => targetJob.value?.requirements?.recommended_certificates || [])
const qualityItems = computed<{ label: string; icon: SpriteName; done: boolean }[]>(() => [
  { label: '基础信息', icon: 'profile', done: Boolean(profile.real_name && profile.education && profile.school && profile.major) },
  { label: '求职意向', icon: 'target', done: Boolean(profile.target_role && profile.city && profile.expected_salary) },
  { label: '能力标签', icon: 'shield', done: profile.skills.length >= 5 },
  { label: '证书成果', icon: 'certificate', done: Boolean(profile.certificates.length || profile.awards.length) },
  { label: '项目证据', icon: 'folder', done: Boolean(profile.projects.length || profile.internships.length) },
  { label: '个人总结', icon: 'chart', done: Boolean(profile.self_summary) }
])
const nextAction = computed(() => {
  const missing = qualityItems.value.find((item) => !item.done)
  if (missing) {
    return {
      title: `建议先完善：${missing.label}`,
      desc: '补齐这些信息后，岗位匹配、学习路径和面试练习会更贴近你的实际经历。'
    }
  }
  return {
    title: '画像已具备匹配分析条件',
    desc: '现在可以查看目标岗位差距，再安排学习计划和面试练习。'
  }
})
const flowSteps: Array<{ index: string; title: string; desc: string; path: string; icon: SpriteName }> = [
  { index: '01', title: '解析简历', desc: '提取教育、项目、技能和证书信息', path: '/resume-parser', icon: 'certificate' },
  { index: '02', title: '完善画像', desc: '选择城市、薪资和能力材料', path: '/personal-center', icon: 'profile' },
  { index: '03', title: '人岗匹配', desc: '查看总分、差距和风险点', path: '/match-analysis', icon: 'target' },
  { index: '04', title: '学习路径', desc: '按缺失技能生成提升路线', path: '/learning-path', icon: 'education' },
  { index: '05', title: '面试练习', desc: '围绕岗位进行追问训练', path: '/digital-interviewer', icon: 'setting' }
]

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
      h('div', { class: 'tag-editor' }, [
        props.modelValue.length
          ? h('div', { class: 'experience-list' }, props.modelValue.map((item: string, index: number) =>
              h('div', { class: 'experience-item' }, [
                h('span', { class: 'experience-index' }, String(index + 1).padStart(2, '0')),
                h('p', item),
                h(ElButton, { class: 'experience-remove-btn', text: true, type: 'danger', onClick: () => remove(item) }, () => '移除')
              ])
            ))
          : h('div', { class: 'experience-empty' }, [
              h('span'),
              h('p', props.emptyText || '暂无记录，补充后会用于画像完整度和匹配分析。')
            ]),
        h('div', { class: 'tag-input-row' }, [
          h(ElInput, { modelValue: value.value, 'onUpdate:modelValue': (v: string) => (value.value = v), placeholder: props.placeholder, onKeyup: (e: KeyboardEvent) => e.key === 'Enter' && add() }),
          h(ElButton, { type: 'primary', onClick: add }, () => '添加')
        ])
      ])
  }
}

async function loadProfile() {
  const [profileData, jobRows] = await Promise.all([api.myProfile(), api.jobs()])
  Object.assign(profile, profileData)
  jobs.value = jobRows
  locationValue.value = parseLocation(profile.city)
  const salary = parseSalary(profile.expected_salary)
  salaryStart.value = salary[0]
  salaryEnd.value = salary[1]
}

async function saveProfile() {
  saving.value = true
  try {
    profile.city = formatLocation()
    profile.expected_salary = formatSalary()
    Object.assign(profile, await api.updateMyProfile(profile))
    window.dispatchEvent(new CustomEvent('profile-avatar-updated', { detail: { avatar_url: profile.avatar_url } }))
    ElMessage.success('个人画像已保存')
  } finally {
    saving.value = false
  }
}

async function resetProfile() {
  try {
    await ElMessageBox.confirm(
      '将清空头像、教育经历、求职意向、能力、证书、项目、实习、奖项和个人总结。账号、密码、已上传简历及面试历史不会受影响。',
      '确认重置个人画像？',
      {
        confirmButtonText: '确认重置',
        cancelButtonText: '取消',
        type: 'warning',
        distinguishCancelAndClose: true
      }
    )
  } catch {
    return
  }

  resetting.value = true
  try {
    const resetPayload = {
      real_name: auth.user?.display_name || auth.user?.username || '',
      education: '',
      major: '',
      school: '',
      target_role: '',
      city: '',
      expected_salary: '',
      avatar_url: '',
      skills: [],
      certificates: [],
      projects: [],
      internships: [],
      awards: [],
      self_summary: ''
    }
    Object.assign(profile, await api.updateMyProfile(resetPayload))
    locationValue.value = []
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

function querySchools(query: string, callback: (items: { value: string }[]) => void) {
  const keyword = normalizeSchoolName(query)
  callback(eliteUniversityOptions.filter((item) => !keyword || normalizeSchoolName(item.value).includes(keyword)).slice(0, 20))
}

function normalizeSchoolName(value = '') {
  return value.replace(/[（(].*?[）)]/g, '').replace(/\s+/g, '').trim()
}

function eliteBadgeClass(badge: string) {
  return {
    'elite-badge-985': badge === '985',
    'elite-badge-211': badge === '211',
    'elite-badge-double': badge === '双一流'
  }
}

function parseLocation(value = '') {
  const parts = value.split('/').map((item) => item.trim()).filter(Boolean)
  if (parts.length >= 2) return [parts[0], parts[1]]
  const matchedProvince = cityOptions.find((province) => province.children.some((city) => city.value === value))
  return matchedProvince ? [matchedProvince.value, value] : []
}

function formatLocation() {
  if (!locationValue.value.length) return ''
  const [province, city] = locationValue.value
  if (!city || province === city) return province
  return `${province} / ${city}`
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

function chooseAvatar() {
  avatarInput.value?.click()
}

function handleAvatarFile(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    ElMessage.warning('请选择图片文件')
    return
  }
  if (file.size > 1.5 * 1024 * 1024) {
    ElMessage.warning('头像图片建议小于 1.5MB')
    input.value = ''
    return
  }
  const reader = new FileReader()
  reader.onload = () => {
    profile.avatar_url = String(reader.result || '')
  }
  reader.readAsDataURL(file)
  input.value = ''
}

function focusBasicForm() {
  document.querySelector<HTMLInputElement>('.profile-basic-card input')?.focus()
}

function focusAbilityForm() {
  document.querySelector<HTMLInputElement>('.profile-ability-card input')?.focus()
}

onMounted(loadProfile)
</script>

<style scoped>
.profile-page {
  position: relative;
  isolation: isolate;
  display: grid;
  gap: 20px;
  padding-bottom: 24px;
}

.profile-page::before {
  position: absolute;
  z-index: -1;
  inset: -22px;
  content: "";
  border-radius: 28px;
  background:
    radial-gradient(circle at 82% 6%, rgba(55, 139, 255, 0.2), transparent 28%),
    radial-gradient(circle at 18% 24%, rgba(0, 207, 245, 0.14), transparent 26%),
    linear-gradient(180deg, #f6fbff 0%, #eaf4ff 100%);
}

.profile-page::after {
  position: absolute;
  z-index: -1;
  inset: -22px;
  content: "";
  border-radius: 28px;
  background-image:
    repeating-linear-gradient(0deg, rgba(68, 128, 200, 0.08) 0 1px, transparent 1px 36px),
    repeating-linear-gradient(90deg, rgba(68, 128, 200, 0.08) 0 1px, transparent 1px 36px);
  opacity: 0.85;
  pointer-events: none;
}

.profile-glass-card {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(113, 177, 255, 0.32);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 18px 50px rgba(24, 96, 188, 0.1);
  backdrop-filter: blur(18px);
  transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}

.profile-glass-card:hover {
  border-color: rgba(56, 146, 255, 0.55);
  box-shadow: 0 22px 60px rgba(24, 96, 188, 0.16);
}

.section-head span,
.profile-flow-summary span,
.experience-head span {
  color: #00aee8;
  font-size: 11px;
  font-weight: 950;
  letter-spacing: 0.14em;
}

.profile-save-btn,
.profile-page :deep(.el-button--primary) {
  border: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, #1e7bff, #00bdeb);
  box-shadow: 0 12px 26px rgba(30, 123, 255, 0.25);
  font-weight: 850;
}

.profile-card {
  display: flex;
  min-height: 178px;
  align-items: center;
  justify-content: space-between;
  gap: 22px;
  padding: 24px 28px;
  background:
    radial-gradient(circle at 88% 12%, rgba(0, 200, 245, 0.14), transparent 28%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.78), rgba(234, 245, 255, 0.68));
}

.profile-identity {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 22px;
}

.avatar-picker {
  position: relative;
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  width: 104px;
  height: 104px;
  overflow: hidden;
  border: 1px solid rgba(89, 172, 255, 0.56);
  border-radius: 28px;
  background:
    radial-gradient(circle at 30% 18%, rgba(255, 255, 255, 0.95), transparent 30%),
    linear-gradient(135deg, #0b2b6f, #1e7bff 58%, #00c8f5);
  box-shadow: 0 20px 48px rgba(30, 123, 255, 0.24);
  color: #fff;
  cursor: pointer;
}

.avatar-picker::after {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  padding: 6px 0;
  background: rgba(7, 26, 61, 0.7);
  color: #dff8ff;
  content: "更换头像";
  font-size: 11px;
  font-weight: 850;
  opacity: 0;
  transition: opacity 180ms ease;
}

.avatar-picker:hover::after {
  opacity: 1;
}

.avatar-picker img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-icon-wrap {
  position: relative;
  display: grid;
  place-items: center;
}

.avatar-icon-wrap b {
  position: absolute;
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: rgba(6, 20, 52, 0.72);
  color: #fff;
  font-size: 18px;
  font-weight: 950;
}

.identity-copy {
  min-width: 0;
}

.identity-topline {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.identity-topline h2 {
  margin: 0;
  color: #071a3d;
  font-size: 28px;
  line-height: 1.2;
}

.identity-topline span {
  border: 1px solid rgba(30, 123, 255, 0.22);
  border-radius: 999px;
  padding: 6px 12px;
  background: rgba(235, 243, 255, 0.88);
  color: #1e63c7;
  font-size: 12px;
  font-weight: 850;
}

.identity-summary {
  margin: 10px 0 12px;
  color: #496487;
  font-size: 15px;
  font-weight: 750;
  line-height: 1.7;
}

.identity-targets {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.identity-targets span {
  border: 1px solid rgba(95, 159, 255, 0.28);
  border-radius: 12px;
  padding: 8px 11px;
  background: rgba(255, 255, 255, 0.58);
  color: #173b73;
  font-size: 13px;
  font-weight: 800;
}

.avatar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 13px;
}

.avatar-input {
  display: none;
}

.completion-panel {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  gap: 10px;
  min-width: 172px;
}

.completion-panel > span {
  color: #34537d;
  font-size: 13px;
  font-weight: 850;
}

.completion-ring {
  position: relative;
  display: grid;
  place-items: center;
  width: 142px;
  height: 142px;
  overflow: hidden;
  border-radius: 50%;
  background:
    linear-gradient(#9b59b6, #84cdfa, #5ad1cd);
  box-shadow: 0 0 38px rgba(30, 123, 255, 0.22), inset 0 0 18px rgba(255, 255, 255, 0.82);
}

.completion-ring::before {
  position: absolute;
  z-index: 2;
  inset: 15px;
  content: "";
  border: 6px solid rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: inset 0 0 24px rgba(30, 123, 255, 0.08);
}

.completion-ring::after {
  position: absolute;
  z-index: 1;
  inset: 10px;
  content: "";
  border-radius: 50%;
  background:
    conic-gradient(from -90deg, rgba(30, 123, 255, 0.95) 0 var(--completion-degree), rgba(216, 234, 255, 0.72) var(--completion-degree) 360deg);
  box-shadow:
    inset 0 0 12px rgba(255, 255, 255, 0.72),
    0 0 18px rgba(30, 123, 255, 0.14);
  -webkit-mask: radial-gradient(circle, transparent 0 70%, #000 71% 100%);
  mask: radial-gradient(circle, transparent 0 70%, #000 71% 100%);
}

.completion-stream {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: linear-gradient(#9b59b6, #84cdfa, #5ad1cd);
  animation: completionRotate 1.8s linear infinite;
}

.completion-stream.stream-1 {
  filter: blur(5px);
}

.completion-stream.stream-2 {
  filter: blur(10px);
}

.completion-stream.stream-3 {
  filter: blur(24px);
}

.completion-stream.stream-4 {
  filter: blur(42px);
  opacity: 0.72;
}

.completion-progress {
  display: none;
}

.completion-core {
  position: relative;
  z-index: 4;
  display: grid;
  place-items: center;
  width: 92px;
  height: 92px;
  border: 0;
  border-radius: 50%;
  background:
    radial-gradient(circle at 36% 25%, rgba(255, 255, 255, 1), rgba(255, 255, 255, 0.94) 58%, rgba(232, 243, 255, 0.92));
  box-shadow:
    inset 0 0 18px rgba(30, 123, 255, 0.08),
    0 0 0 1px rgba(255, 255, 255, 0.78);
  color: #0b2b6f;
}

.completion-core strong {
  font-size: 30px;
  font-weight: 950;
  letter-spacing: 0;
}

@keyframes completionRotate {
  to {
    transform: rotate(360deg);
  }
}

.profile-flow {
  display: grid;
  grid-template-columns: 300px repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.profile-flow-summary,
.profile-flow-card,
.profile-status-card,
.profile-section-card {
  padding: 18px;
}

.profile-flow-summary,
.profile-flow-card {
  animation: none;
}

.profile-flow-summary {
  position: relative;
  overflow: hidden;
  min-height: 150px;
  background:
    radial-gradient(circle at 12% 0%, rgba(0, 200, 245, 0.15), transparent 32%),
    rgba(255, 255, 255, 0.66);
}

.profile-flow-summary::after {
  display: none;
}

.profile-flow-summary > *,
.profile-flow-card > * {
  position: relative;
  z-index: 1;
}

.flow-aurora-svg {
  display: none;
}

.flow-border-base {
  fill: none;
  vector-effect: non-scaling-stroke;
  stroke: rgba(30, 123, 255, 0.13);
  stroke-width: 0.7;
}

.flow-aurora-glow,
.flow-aurora-streak {
  fill: none;
  vector-effect: non-scaling-stroke;
  stroke: url("#flowAuroraGradient");
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dashoffset: 82;
  animation: flowAuroraTravel 4.6s linear infinite;
  mix-blend-mode: screen;
}

.flow-aurora-glow {
  opacity: 0.78;
  stroke-width: 11;
  stroke-dasharray: 22 78;
  filter: url("#flowAuroraGlow");
}

.flow-aurora-streak {
  display: none;
}

.profile-flow-summary h3 {
  margin: 12px 0 8px;
  color: #071a3d;
  font-size: 21px;
  line-height: 1.35;
}

.profile-flow-summary p {
  margin: 0;
  color: #55708f;
  font-size: 13px;
  font-weight: 750;
  line-height: 1.8;
}

.profile-flow-card {
  position: relative;
  min-height: 176px;
  overflow: hidden;
  padding: 14px 18px 17px;
  text-align: left;
  cursor: pointer;
}

.profile-flow-card:hover,
.profile-status-card:hover,
.profile-section-card:hover {
  transform: translateY(-3px);
}

.profile-flow-summary:hover .flow-aurora-glow,
.profile-flow-card:hover .flow-aurora-glow {
  opacity: 0.92;
  stroke-width: 12;
}

.profile-flow-card::after {
  display: none;
}

.flow-arrow {
  position: absolute;
  top: 13px;
  right: 16px;
  color: #1e7bff;
  font-size: 18px;
  font-weight: 950;
}

.flow-icon {
  display: grid;
  place-items: center;
  width: 126px;
  height: 112px;
  margin: -8px auto 4px;
  overflow: hidden;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.flow-icon :deep(.sprite-icon),
.status-icon :deep(.sprite-icon),
.experience-icon :deep(.sprite-icon) {
  display: block;
  margin: auto;
  filter: drop-shadow(0 14px 22px rgba(30, 123, 255, 0.2));
}

.profile-flow-card b,
.profile-flow-card strong,
.profile-flow-card em {
  display: block;
}

.profile-flow-card b {
  color: #00aee8;
  font-size: 12px;
  font-weight: 950;
}

.profile-flow-card strong {
  margin-top: 7px;
  color: #0b2b6f;
  font-size: 16px;
  line-height: 1.3;
}

.profile-flow-card em {
  margin-top: 7px;
  color: #5b7190;
  font-style: normal;
  font-size: 12px;
  font-weight: 750;
  line-height: 1.55;
}

.profile-status-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 14px;
}

.profile-status-card {
  position: relative;
  display: grid;
  grid-template-columns: 82px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
  min-height: 94px;
  padding: 12px 18px;
}

.status-icon {
  display: grid;
  place-items: center;
  width: 82px;
  height: 82px;
  overflow: hidden;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.profile-status-card b,
.profile-status-card strong {
  display: block;
}

.profile-status-card b {
  color: #0b2b6f;
  font-size: 15px;
}

.profile-status-card strong {
  margin-top: 4px;
  color: #5c7392;
  font-size: 12px;
}

.profile-status-card.done .status-check {
  background: linear-gradient(135deg, #10b981, #00c8f5);
}

.status-check {
  position: absolute;
  top: 12px;
  right: 12px;
  display: grid;
  place-items: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #b9c8db;
  color: #fff;
  font-size: 11px;
  font-weight: 950;
}

.profile-info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.profile-section-card {
  overflow: hidden;
  background:
    radial-gradient(circle at 10% 0%, rgba(0, 200, 245, 0.12), transparent 30%),
    rgba(255, 255, 255, 0.72);
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 16px;
}

.section-head h3,
.experience-head h3 {
  margin: 7px 0 0;
  color: #071a3d;
  font-size: 20px;
  line-height: 1.25;
}

.profile-secondary-btn {
  border: 1px solid rgba(69, 145, 255, 0.28);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.56);
  color: #1e63c7;
  font-weight: 850;
}

.profile-page :deep(.el-form-item__label) {
  color: #536b8e;
  font-weight: 850;
}

.profile-page :deep(.el-input__wrapper),
.profile-page :deep(.el-select__wrapper),
.profile-page :deep(.el-cascader .el-input__wrapper),
.profile-page :deep(.el-textarea__inner) {
  min-height: 38px;
  border: 1px solid rgba(69, 145, 255, 0.28);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: none;
  transition: border-color 180ms ease, box-shadow 180ms ease, background 180ms ease;
}

.profile-page :deep(.el-input__wrapper.is-focus),
.profile-page :deep(.el-select__wrapper.is-focused),
.profile-page :deep(.el-textarea__inner:focus) {
  border-color: rgba(30, 123, 255, 0.68);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 0 0 4px rgba(30, 123, 255, 0.1);
}

.profile-page :deep(.el-select),
.profile-page :deep(.el-cascader),
.profile-page :deep(.el-autocomplete) {
  width: 100%;
}

.school-field {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.school-badges {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 184px;
}

.elite-badge {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 52px;
  height: 25px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 999px;
  color: #fff;
  font-size: 12px;
  font-weight: 950;
  line-height: 1;
  text-align: center;
  text-shadow: 0 1px 8px rgba(4, 25, 68, 0.34);
  box-shadow: 0 8px 18px rgba(30, 123, 255, 0.2);
  transform-style: preserve-3d;
  animation: badgeFlip 3.4s ease-in-out infinite;
}

.elite-badge::before {
  position: absolute;
  inset: 1px 4px auto;
  height: 45%;
  content: "";
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.48), transparent);
  opacity: 0.78;
  pointer-events: none;
}

.elite-badge-985 {
  background: linear-gradient(135deg, #ff8a00 0%, #ffd166 48%, #2f86ff 100%);
  animation-delay: 0s;
}

.elite-badge-211 {
  background: linear-gradient(135deg, #1e7bff 0%, #00c8f5 100%);
  animation-delay: 0.18s;
}

.elite-badge-double {
  min-width: 70px;
  background: linear-gradient(135deg, #6d5dfc 0%, #1e7bff 54%, #00c8f5 100%);
  animation-delay: 0.36s;
}

.salary-range {
  display: grid;
  grid-template-columns: minmax(96px, 1fr) auto minmax(96px, 1fr) auto;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.salary-range span,
.salary-range em,
.select-meta {
  color: #647895;
  font-style: normal;
  font-size: 12px;
}

.select-meta {
  margin-top: 8px;
  line-height: 1.5;
}

.requirement-hint {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 7px;
  margin-top: 10px;
  border: 1px solid rgba(66, 173, 232, 0.24);
  border-radius: 12px;
  padding: 10px;
  background: rgba(221, 242, 255, 0.42);
}

.requirement-hint b {
  width: 100%;
  color: #264c78;
  font-size: 12px;
}

.requirement-hint button {
  border: 1px solid rgba(56, 145, 218, 0.28);
  border-radius: 999px;
  padding: 5px 9px;
  background: rgba(255, 255, 255, 0.72);
  color: #1769a7;
  font-size: 11px;
  cursor: pointer;
}

.requirement-hint button:hover {
  border-color: #17bfe6;
  color: #057fa7;
}

.chip-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.profile-chip {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  border: 1px solid rgba(95, 159, 255, 0.35);
  border-radius: 999px;
  padding: 4px 10px;
  background: rgba(235, 243, 255, 0.9);
  color: #42618a;
  font-size: 12px;
  font-weight: 850;
}

.certificate-chip {
  background: rgba(232, 248, 255, 0.88);
}

.more-chip {
  color: #1e63c7;
}

.profile-experience-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.experience-card {
  display: flex;
  min-height: 348px;
  flex-direction: column;
  padding: 22px;
}

.experience-head {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr) auto;
  align-items: start;
  gap: 14px;
  min-height: 98px;
  margin-bottom: 14px;
}

.experience-icon {
  display: grid;
  place-items: center;
  width: 72px;
  height: 72px;
  overflow: hidden;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.experience-head > div {
  min-width: 0;
  padding-top: 2px;
}

.experience-head h3 {
  margin-top: 5px;
}

.experience-head p {
  min-height: 38px;
  margin: 6px 0 0;
  color: #647895;
  font-size: 12px;
  font-weight: 750;
  line-height: 1.6;
}

.experience-head b {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 50px;
  height: 30px;
  border: 1px solid rgba(255, 255, 255, 0.88);
  border-radius: 999px;
  padding: 0 11px;
  background: linear-gradient(135deg, rgba(30, 123, 255, 0.92), rgba(0, 200, 245, 0.82));
  box-shadow: 0 12px 24px rgba(30, 123, 255, 0.18);
  color: #fff;
  font-size: 13px;
  white-space: nowrap;
}

.tag-editor {
  display: flex;
  flex: 1;
  min-height: 184px;
  flex-direction: column;
  gap: 12px;
}

.experience-card :deep(.experience-list) {
  display: grid;
  gap: 10px;
  max-height: 156px;
  overflow-y: auto;
  padding-right: 3px;
}

.experience-card :deep(.experience-list)::-webkit-scrollbar {
  width: 4px;
}

.experience-card :deep(.experience-list)::-webkit-scrollbar-thumb {
  border-radius: 99px;
  background: rgba(30, 123, 255, 0.24);
}

.experience-card :deep(.experience-item) {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  min-height: 58px;
  border: 1px solid rgba(147, 197, 253, 0.58);
  border-radius: 14px;
  padding: 10px 11px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 8px 22px rgba(30, 123, 255, 0.08);
  transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
}

.experience-card :deep(.experience-item:hover) {
  border-color: rgba(0, 200, 245, 0.42);
  box-shadow: 0 14px 34px rgba(30, 123, 255, 0.1);
  transform: translateY(-1px);
}

.experience-card :deep(.experience-index) {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 11px;
  background: linear-gradient(135deg, rgba(30, 123, 255, 0.14), rgba(0, 200, 245, 0.12));
  color: #1455b8 !important;
  font-size: 12px;
  font-weight: 950;
  letter-spacing: 0;
}

.experience-card :deep(.experience-item p) {
  display: -webkit-box;
  overflow: hidden;
  margin: 0;
  color: #0c2856;
  font-size: 13px;
  font-weight: 800;
  line-height: 1.5;
  overflow-wrap: anywhere;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.experience-card :deep(.experience-remove-btn) {
  min-height: 30px;
  border: 1px solid rgba(220, 38, 38, 0.2);
  border-radius: 10px;
  padding: 6px 10px;
  background: rgba(254, 242, 242, 0.94);
  box-shadow: none;
  color: #b42318 !important;
  font-size: 12px;
  font-weight: 850;
}

.experience-card :deep(.experience-remove-btn:hover),
.experience-card :deep(.experience-remove-btn:focus-visible) {
  border-color: rgba(220, 38, 38, 0.38);
  background: #fee2e2;
  color: #991b1b !important;
}

.experience-card :deep(.experience-empty) {
  display: flex;
  flex: 1;
  align-items: center;
  gap: 11px;
  min-height: 88px;
  border: 1px dashed rgba(30, 123, 255, 0.25);
  border-radius: 18px;
  padding: 14px;
  background:
    radial-gradient(circle at 50% 0%, rgba(0, 200, 245, 0.1), transparent 42%),
    rgba(255, 255, 255, 0.48);
  text-align: left;
}

.experience-card :deep(.experience-empty span) {
  flex: 0 0 auto;
  width: 36px;
  height: 36px;
  border-radius: 13px;
  background: linear-gradient(90deg, #1e7bff, #00c8f5);
  box-shadow: 0 0 16px rgba(0, 200, 245, 0.34);
}

.experience-card :deep(.experience-empty p) {
  min-width: 0;
  margin: 0;
  color: #647895;
  font-size: 13px;
  font-weight: 750;
  line-height: 1.65;
}

.experience-card :deep(.tag-input-row) {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 76px;
  align-items: center;
  gap: 10px;
  margin-top: auto;
  border-top: 1px solid rgba(147, 197, 253, 0.2);
  padding-top: 12px;
}

.experience-card :deep(.tag-input-row .el-button) {
  width: 76px;
  min-height: 40px;
  border-radius: 13px;
}

@keyframes badgeFlip {
  0%,
  72%,
  100% {
    transform: perspective(240px) rotateY(0deg) translateY(0);
  }

  80% {
    transform: perspective(240px) rotateY(18deg) translateY(-1px);
  }

  88% {
    transform: perspective(240px) rotateY(-16deg) translateY(0);
  }

  94% {
    transform: perspective(240px) rotateY(8deg) translateY(-1px);
  }
}

@keyframes flowDashedOrbit {
  to {
    transform: rotate(360deg);
  }
}

@keyframes flowAuroraTravel {
  to {
    stroke-dashoffset: -18;
  }
}

.profile-card-side {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  gap: 12px;
}

.profile-card-side .profile-save-btn {
  min-width: 132px;
}

.profile-primary-actions {
  display: grid;
  gap: 8px;
}

.profile-primary-actions .el-button {
  width: 132px;
  margin-left: 0;
}

.profile-reset-btn {
  border-color: rgba(220, 38, 38, 0.22);
  background: rgba(255, 255, 255, 0.62);
  color: #b42318;
}

.profile-reset-btn:hover {
  border-color: rgba(220, 38, 38, 0.45);
  background: rgba(254, 242, 242, 0.9);
  color: #991b1b;
}

@media (max-width: 1380px) {
  .profile-flow {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .profile-flow-summary {
    grid-column: span 3;
  }

  .profile-status-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 1024px) {
  .profile-card {
    align-items: flex-start;
    flex-direction: column;
  }

  .profile-card-side,
  .completion-panel {
    justify-self: center;
    width: 100%;
  }

  .profile-info-grid,
  .profile-experience-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .profile-page {
    gap: 16px;
  }

  .profile-identity,
  .identity-targets {
    align-items: flex-start;
    flex-direction: column;
  }

  .profile-flow,
  .profile-status-grid {
    grid-template-columns: 1fr;
  }

  .profile-flow-summary {
    grid-column: auto;
  }

  .school-field,
  .salary-range,
  .experience-card :deep(.tag-input-row) {
    grid-template-columns: 1fr;
  }

  .school-badges {
    min-width: 0;
  }

  .experience-card :deep(.tag-input-row .el-button) {
    width: 100%;
  }
}

/* Superseded profile draft; the original portrait-led workspace is retained below. */
.profile-redesign { display: none !important; }
.profile-page { display: block; padding-bottom: 30px; color: #e7f3f8; }
.profile-page::before, .profile-page::after { display: none; }
.profile-redesign { overflow: hidden; border: 1px solid rgba(75, 145, 174, .28); border-radius: 8px; background: #071421; box-shadow: 0 20px 52px rgba(0, 3, 12, .28); }
.profile-overview { display: flex; align-items: center; justify-content: space-between; gap: 28px; min-height: 176px; padding: 26px 30px; border-bottom: 1px solid rgba(75, 145, 174, .2); background: #091a2a; }
.profile-person { display: flex; align-items: center; min-width: 0; gap: 20px; }
.profile-avatar { flex: 0 0 auto; display: grid; place-items: center; width: 92px; height: 92px; overflow: hidden; border: 1px solid rgba(80, 190, 214, .48); border-radius: 50%; padding: 0; color: #d8f8ff; background: #102d3e; font: inherit; font-size: 30px; font-weight: 800; cursor: pointer; }
.profile-avatar img { width: 100%; height: 100%; object-fit: cover; }
.profile-person__copy { min-width: 0; }
.profile-person__copy > span { color: #6fc9d9; font-size: 12px; font-weight: 700; }
.profile-person__copy h2 { margin: 6px 0 5px; color: #f1f8fb; font-size: 28px; letter-spacing: 0; }
.profile-person__copy p { margin: 0; color: #8fa9b7; font-size: 13px; }
.profile-target-line { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 15px; }
.profile-target-line b, .profile-target-line span { min-height: 26px; border: 1px solid rgba(89, 151, 178, .25); border-radius: 5px; padding: 5px 9px; color: #aac2cd; background: #0c2233; font-size: 11px; font-weight: 600; }
.profile-target-line b { color: #83e2df; }
.profile-overview__right { display: flex; align-items: center; gap: 22px; min-width: 390px; }
.profile-completion { flex: 1; min-width: 190px; }
.profile-completion > div { display: flex; align-items: baseline; justify-content: space-between; gap: 14px; }
.profile-completion span { color: #8eaab8; font-size: 12px; }
.profile-completion strong { color: #f3fafc; font-size: 28px; }
.profile-completion > i { display: block; height: 7px; overflow: hidden; margin-top: 10px; border-radius: 4px; background: #132c3d; }
.profile-completion > i span { display: block; height: 100%; border-radius: inherit; background: #35c6b1; }
.profile-completion small { display: block; margin-top: 7px; color: #6f8998; font-size: 10px; }
.profile-actions { display: grid; gap: 8px; }
.profile-actions .el-button { width: 112px; min-height: 37px; margin: 0; border-radius: 6px; font-weight: 700; }
.profile-save-btn { border-color: #187f92 !important; background: #187f92 !important; color: #fff !important; }
.profile-reset-btn { border-color: rgba(255, 172, 89, .35) !important; background: transparent !important; color: #f0b56f !important; }
.profile-next-step { display: flex; align-items: center; justify-content: space-between; gap: 22px; padding: 18px 30px; border-bottom: 1px solid rgba(75, 145, 174, .18); background: #0a1d2d; }
.profile-next-step > div:first-child { min-width: 0; }
.profile-next-step span { color: #6fc9d9; font-size: 11px; font-weight: 700; }
.profile-next-step h3 { margin: 4px 0 3px; color: #edf7fa; font-size: 17px; }
.profile-next-step p { margin: 0; color: #839eac; font-size: 12px; line-height: 1.55; }
.profile-next-step__actions { display: flex; flex: 0 0 auto; gap: 8px; }
.profile-next-step__actions button { min-height: 34px; border: 1px solid rgba(74, 174, 197, .36); border-radius: 6px; padding: 0 13px; color: #aeeaf2; background: #0d293b; font: inherit; font-size: 11px; font-weight: 700; cursor: pointer; }
.profile-quality { display: flex; flex-wrap: wrap; gap: 0; padding: 0 30px; border-bottom: 1px solid rgba(75, 145, 174, .18); background: #071725; }
.profile-quality span { display: inline-flex; align-items: center; gap: 6px; min-height: 42px; margin-right: 22px; color: #6f8998; font-size: 11px; }
.profile-quality span.done { color: #8cb7b5; }
.profile-quality i { display: grid; place-items: center; width: 16px; height: 16px; border: 1px solid rgba(123, 158, 173, .34); border-radius: 50%; color: #78919e; font-size: 9px; font-style: normal; }
.profile-quality .done i { border-color: rgba(53, 198, 177, .44); color: #4bdbc4; }
.profile-edit-section { padding: 26px 30px 30px; border-bottom: 1px solid rgba(75, 145, 174, .18); }
.profile-edit-section:last-child { border-bottom: 0; }
.profile-section-heading { display: flex; align-items: end; justify-content: space-between; gap: 20px; margin-bottom: 22px; }
.profile-section-heading > div { display: flex; align-items: center; gap: 11px; }
.profile-section-heading > div > span { display: grid; place-items: center; width: 28px; height: 28px; border: 1px solid rgba(73, 190, 204, .4); border-radius: 50%; color: #65cbd2; font-size: 10px; font-weight: 800; }
.profile-section-heading h3 { margin: 0; color: #edf7fa; font-size: 18px; }
.profile-section-heading p { margin: 0; color: #738e9d; font-size: 11px; }
.profile-form-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0 16px; }
.profile-form-grid .school-field, .profile-form-grid :deep(.el-select), .profile-form-grid :deep(.el-cascader) { width: 100%; }
.salary-form-item { grid-column: span 2; }
.salary-range { display: grid; grid-template-columns: minmax(90px, 1fr) auto minmax(90px, 1fr) auto; align-items: center; gap: 9px; width: 100%; }
.salary-range span, .salary-range em { color: #75909d; font-size: 11px; font-style: normal; }
.school-badges { display: flex; gap: 5px; margin-top: 7px; }
.elite-badge { border: 1px solid rgba(255, 184, 92, .34); border-radius: 4px; padding: 2px 5px; color: #f2bd78; background: rgba(103, 65, 18, .22); font-size: 9px; }
.profile-evidence-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 26px; }
.profile-evidence-grid :deep(.el-select) { width: 100%; }
.chip-preview { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 11px; }
.profile-chip { border: 1px solid rgba(71, 164, 181, .28); border-radius: 4px; padding: 4px 7px; color: #a7d5db; background: #0b2533; font-size: 10px; }
.certificate-chip { border-color: rgba(255, 184, 92, .26); color: #ddbd88; background: #28261f; }
.profile-recommendation { margin-top: 14px; border-left: 2px solid #d49a4c; padding-left: 11px; }
.profile-recommendation b { display: block; margin-bottom: 7px; color: #d9e6e9; font-size: 11px; }
.profile-recommendation button { margin: 0 6px 6px 0; border: 0; border-radius: 4px; padding: 4px 7px; color: #e1b77d; background: #29271f; font: inherit; font-size: 10px; cursor: pointer; }
.profile-summary-form { margin-top: 4px; }
.profile-redesign :deep(.el-form-item) { margin-bottom: 18px; }
.profile-redesign :deep(.el-form-item__label) { padding-bottom: 7px; color: #9bb2bd !important; font-size: 11px; font-weight: 700; }
.profile-redesign :deep(.el-input__wrapper), .profile-redesign :deep(.el-select__wrapper), .profile-redesign :deep(.el-textarea__inner), .profile-redesign :deep(.el-cascader .el-input__wrapper) { min-height: 38px; border: 1px solid rgba(83, 137, 160, .3); border-radius: 6px; background: #0b2030 !important; box-shadow: none !important; }
.profile-redesign :deep(.el-input__inner), .profile-redesign :deep(.el-select__selected-item), .profile-redesign :deep(.el-textarea__inner) { color: #dce9ed !important; }
.profile-redesign :deep(.el-input__inner::placeholder), .profile-redesign :deep(.el-textarea__inner::placeholder) { color: #607d8b !important; }
.profile-redesign :deep(.el-input__wrapper.is-focus), .profile-redesign :deep(.el-select__wrapper.is-focused), .profile-redesign :deep(.el-textarea__inner:focus) { border-color: rgba(80, 202, 210, .65) !important; }
.profile-experience-tabs :deep(.el-tabs__header) { margin-bottom: 18px; }
.profile-experience-tabs :deep(.el-tabs__nav-wrap::after) { height: 1px; background: rgba(75, 145, 174, .2); }
.profile-experience-tabs :deep(.el-tabs__item) { color: #7893a1; font-size: 12px; }
.profile-experience-tabs :deep(.el-tabs__item.is-active) { color: #71d6dd; }
.profile-experience-tabs :deep(.el-tabs__active-bar) { height: 2px; background: #38b7c2; }
.profile-experience-tabs :deep(.experience-list) { display: grid; gap: 8px; }
.profile-experience-tabs :deep(.experience-item) { display: grid; grid-template-columns: 34px minmax(0, 1fr) auto; align-items: center; gap: 10px; min-height: 48px; border: 1px solid rgba(73, 132, 154, .22); border-radius: 6px; padding: 8px 10px; background: #0a1d2b; }
.profile-experience-tabs :deep(.experience-index) { color: #5fc6ce; font-size: 10px; }
.profile-experience-tabs :deep(.experience-item p) { margin: 0; color: #cbdce1; font-size: 12px; line-height: 1.55; }
.profile-experience-tabs :deep(.experience-remove-btn) { color: #dd8e94 !important; }
.profile-experience-tabs :deep(.experience-empty) { min-height: 92px; border: 1px dashed rgba(80, 137, 158, .28); border-radius: 6px; padding: 22px; background: #091a27; }
.profile-experience-tabs :deep(.experience-empty p) { margin: 0; color: #718b98; font-size: 12px; }
.profile-experience-tabs :deep(.tag-input-row) { display: grid; grid-template-columns: minmax(0, 1fr) 76px; gap: 8px; margin-top: 10px; }

@media (max-width: 1080px) {
  .profile-overview { align-items: flex-start; flex-direction: column; }
  .profile-overview__right { width: 100%; min-width: 0; }
  .profile-form-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 720px) {
  .profile-overview, .profile-next-step, .profile-edit-section { padding-right: 16px; padding-left: 16px; }
  .profile-person { align-items: flex-start; }.profile-avatar { width: 64px; height: 64px; font-size: 22px; }
  .profile-person__copy h2 { font-size: 22px; }.profile-target-line { gap: 5px; }
  .profile-overview__right, .profile-next-step { align-items: stretch; flex-direction: column; }
  .profile-actions { grid-template-columns: 1fr 1fr; }.profile-actions .el-button { width: 100%; }
  .profile-next-step__actions button { flex: 1; }
  .profile-quality { padding: 0 16px; }.profile-quality span { margin-right: 14px; }
  .profile-section-heading { align-items: flex-start; flex-direction: column; gap: 7px; }
  .profile-form-grid, .profile-evidence-grid { grid-template-columns: 1fr; gap: 0; }
  .salary-form-item { grid-column: auto; }.salary-range { grid-template-columns: 1fr auto 1fr; }.salary-range em { grid-column: 1 / -1; }
}

/* Portrait-led personal profile */
.profile-page {
  display: grid;
  gap: 18px;
  color: #e7f2f6;
}

.profile-page::before,
.profile-page::after,
.profile-flow,
.profile-status-grid {
  display: none !important;
}

.profile-page .profile-glass-card {
  border-color: rgba(73, 135, 158, .28) !important;
  border-radius: 6px;
  background: #091a28 !important;
  box-shadow: none !important;
  backdrop-filter: none;
  transform: none !important;
}

.profile-page .profile-card {
  min-height: 248px;
  padding: 30px 34px;
  border-left: 3px solid #36b8c4;
  background:
    linear-gradient(90deg, rgba(37, 113, 133, .13), transparent 42%),
    #081824 !important;
}

.profile-identity { gap: 28px; }

.avatar-picker {
  width: 156px;
  height: 172px;
  border: 1px solid rgba(83, 176, 196, .45);
  border-radius: 6px;
  background: #0d2b3b;
  box-shadow: none;
}

.avatar-picker::after {
  padding: 8px 0;
  background: rgba(4, 18, 27, .88);
}

.avatar-picker img { object-position: center top; }
.avatar-icon-wrap { transform: scale(1.28); }
.avatar-icon-wrap b { display: none; }

.identity-topline h2 {
  color: #f1f7f9 !important;
  font-size: 31px;
  font-weight: 720;
}

.identity-topline span {
  border: 0;
  border-left: 2px solid #4bc0c9;
  border-radius: 0;
  padding: 2px 0 2px 9px;
  background: transparent;
  color: #85cbd2;
  font-size: 12px;
}

.identity-summary {
  max-width: 660px;
  margin: 13px 0 18px;
  color: #9ab0ba !important;
  font-size: 14px;
  font-weight: 500;
}

.identity-targets { gap: 18px; }
.identity-targets span {
  border: 0;
  border-radius: 0;
  padding: 0;
  background: transparent;
  color: #c7d8de;
  font-size: 13px;
  font-weight: 600;
}

.avatar-actions { margin-top: 20px; }
.avatar-actions .el-button {
  border-color: rgba(83, 159, 181, .34);
  border-radius: 4px;
  background: #0c2838;
  color: #a9dce2;
}

.profile-card-side {
  min-width: 270px;
  padding-left: 30px;
  border-left: 1px solid rgba(73, 135, 158, .24);
}

.completion-panel {
  grid-template-columns: 92px 1fr;
  place-items: center start;
  min-width: 0;
}

.completion-ring {
  width: 86px;
  height: 86px;
  background: #0b2736;
  box-shadow: none;
}

.completion-ring::before {
  inset: 8px;
  border: 0;
  background: #091a28;
  box-shadow: none;
}

.completion-ring::after {
  inset: 3px;
  background: conic-gradient(from -90deg, #42c5bd 0 var(--completion-degree), #163746 var(--completion-degree) 360deg);
  box-shadow: none;
  -webkit-mask: radial-gradient(circle, transparent 0 72%, #000 73% 100%);
  mask: radial-gradient(circle, transparent 0 72%, #000 73% 100%);
}

.completion-stream { display: none; }
.completion-core {
  width: 68px;
  height: 68px;
  background: transparent;
  box-shadow: none;
  color: #edf8f8;
}
.completion-core strong { font-size: 20px; }
.completion-panel > span { color: #91aab5; font-size: 12px; }

.profile-primary-actions {
  display: flex;
  gap: 8px;
  margin-top: 18px;
}

.profile-primary-actions .el-button {
  min-height: 36px;
  margin: 0;
  border-radius: 4px;
  box-shadow: none;
}

.profile-info-grid {
  display: grid;
  grid-template-columns: minmax(0, .95fr) minmax(0, 1.05fr);
  gap: 0;
  overflow: hidden;
  border: 1px solid rgba(73, 135, 158, .28);
  border-radius: 6px;
  background: #091a28;
}

.profile-info-grid .profile-section-card {
  border: 0 !important;
  border-radius: 0;
  background: transparent !important;
}

.profile-info-grid .profile-section-card + .profile-section-card {
  border-left: 1px solid rgba(73, 135, 158, .24) !important;
}

.profile-section-card { padding: 26px 28px; }
.section-head { margin-bottom: 22px; }
.section-head span,
.experience-head > div > span { display: none; }
.section-head h3,
.experience-head h3 {
  color: #edf5f7 !important;
  font-size: 18px;
  letter-spacing: 0;
}

.profile-page :deep(.el-form-item__label) {
  color: #91a8b3 !important;
  font-size: 12px;
  font-weight: 600;
}

.select-meta { display: none; }
.requirement-hint {
  border: 0;
  border-left: 2px solid #d29a54;
  border-radius: 0;
  padding: 2px 0 2px 12px;
  background: transparent;
}

.requirement-hint b { color: #cbd9de; }
.requirement-hint button {
  border-radius: 4px;
  background: #27251e;
  color: #dbb87d;
}

.profile-experience-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0;
  overflow: hidden;
  border: 1px solid rgba(73, 135, 158, .28);
  border-radius: 6px;
  background: #091a28;
}

.profile-experience-grid .experience-card {
  border: 0 !important;
  border-radius: 0;
  background: transparent !important;
}

.profile-experience-grid .experience-card + .experience-card {
  border-left: 1px solid rgba(73, 135, 158, .24) !important;
}

.experience-head { grid-template-columns: 60px minmax(0, 1fr) auto; }
.experience-icon {
  width: 58px;
  height: 58px;
  overflow: hidden;
  border: 1px solid rgba(77, 154, 178, .28);
  border-radius: 5px;
  background: #0c2838;
}
.experience-icon :deep(.sprite-icon) {
  --sprite-scale: .88 !important;
  filter: none;
}
.experience-head p { color: #859da8 !important; font-size: 12px; }
.experience-head > b { color: #71cbd2; }

.experience-card :deep(.experience-empty) {
  min-height: 112px;
  border: 1px solid rgba(72, 134, 157, .3);
  border-radius: 6px;
  padding: 18px;
  background: #0b2030 !important;
  box-shadow: none;
}

.experience-card :deep(.experience-empty span) {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #41c3c8;
  box-shadow: none;
}

.experience-card :deep(.experience-empty p) {
  color: #9db2bc !important;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.55;
}

.experience-card :deep(.experience-item) {
  min-height: 58px;
  border: 1px solid rgba(72, 134, 157, .3);
  border-radius: 6px;
  background: #0b2030 !important;
  box-shadow: none;
  transform: none;
}

.experience-card :deep(.experience-item:hover) {
  border-color: rgba(67, 186, 196, .5);
  background: #0d2636 !important;
  box-shadow: none;
  transform: none;
}

.experience-card :deep(.experience-index) {
  border-radius: 4px;
  background: #123247 !important;
  color: #76d8df !important;
}

.experience-card :deep(.experience-item p) {
  color: #d5e4e8 !important;
  font-weight: 600;
}

.experience-card :deep(.experience-remove-btn) {
  border-color: rgba(190, 102, 109, .3) !important;
  border-radius: 4px;
  background: #2a1d24 !important;
  color: #e6a4aa !important;
}

@media (max-width: 1020px) {
  .profile-page .profile-card { align-items: flex-start; }
  .profile-card-side { min-width: 230px; }
  .profile-experience-grid { grid-template-columns: 1fr; }
  .profile-experience-grid .experience-card + .experience-card { border-top: 1px solid rgba(73, 135, 158, .24) !important; border-left: 0 !important; }
}

@media (max-width: 760px) {
  .profile-page .profile-card { align-items: stretch; flex-direction: column; padding: 20px; }
  .profile-identity { align-items: flex-start; }
  .avatar-picker { width: 92px; height: 112px; }
  .avatar-icon-wrap { transform: scale(.86); }
  .identity-topline h2 { font-size: 24px; }
  .profile-card-side { width: 100%; min-width: 0; padding: 20px 0 0; border-top: 1px solid rgba(73, 135, 158, .24); border-left: 0; }
  .profile-info-grid { grid-template-columns: 1fr; }
  .profile-info-grid .profile-section-card + .profile-section-card { border-top: 1px solid rgba(73, 135, 158, .24) !important; border-left: 0 !important; }
  .profile-section-card { padding: 22px 18px; }
}
</style>
