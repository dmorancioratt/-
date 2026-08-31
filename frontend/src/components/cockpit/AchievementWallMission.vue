<template>
  <Transition name="wall-appear" appear>
    <section class="achv-wall" aria-label="成就墙" tabindex="-1">
      <!-- 纯 CSS 蓝金科幻展厅：参考构图，不直接使用参考图 -->
      <div class="hall-bg" aria-hidden="true">
        <div class="hall-bg__shell"></div>
        <div class="hall-bg__ceiling">
          <i v-for="n in 7" :key="`lamp-${n}`" :style="{ '--lamp-index': n }"></i>
        </div>
        <div class="hall-bg__arch"></div>
        <div class="hall-bg__horizon"></div>
        <div class="hall-bg__floor"></div>
        <div class="hall-bg__stars">
          <i
            v-for="star in ambientStars"
            :key="star.id"
            :style="{ left: `${star.x}%`, top: `${star.y}%`, animationDelay: `${star.delay}s`, opacity: star.opacity }"
          ></i>
        </div>
        <div class="hall-bg__vignette"></div>
        <div class="hall-bg__spot"></div>
        <div class="hall-bg__magenta"></div>
      </div>

      <button class="wall-back" type="button" @click="emit('close')">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m14.5 5-7 7 7 7" /></svg>
        <span>返回驾驶舱</span>
      </button>

      <header class="wall-title">
        <h1>成就墙</h1>
        <p>每一份努力，都值得被看见</p>
      </header>

      <!-- 左侧统计 -->
      <aside class="stat-panel" aria-label="成就统计">
        <div class="sp-item">
          <span class="sp-label">已获得成就</span>
          <strong class="sp-value">{{ stats.total }}</strong>
        </div>
        <div class="sp-item">
          <span class="sp-label">累计积分</span>
          <strong class="sp-value">{{ stats.points.toLocaleString() }}</strong>
        </div>
        <div class="sp-item">
          <span class="sp-label">排名</span>
          <strong class="sp-value">{{ stats.rankPercent }}<small>%</small></strong>
          <span class="sp-delta"><i>↑</i>较上月</span>
        </div>
      </aside>

      <!-- 中央领奖台 -->
      <div class="stage">
        <i class="arch-glow" aria-hidden="true"></i>

        <div class="podium-row">
          <template v-for="(slot, i) in podiumSlots" :key="`${i}-${slot.id}`">
            <div v-if="i === 2" class="podium podium--center">
              <Transition name="focus-swap" mode="out-in">
                <article
                  :key="slot.id"
                  class="showcase"
                  role="button"
                  tabindex="0"
                  :aria-label="`查看 ${slot.name} 详情`"
                  @click="openDetail(slot)"
                  @keydown.enter="openDetail(slot)"
                >
                  <i class="showcase__corner showcase__corner--tl"></i>
                  <i class="showcase__corner showcase__corner--tr"></i>
                  <i class="showcase__corner showcase__corner--bl"></i>
                  <i class="showcase__corner showcase__corner--br"></i>
                  <h3>{{ slot.name }}</h3>
                  <span class="showcase__date">{{ slot.date }}</span>
                  <button class="showcase__btn" type="button" @click.stop="openDetail(slot)">查看详情 ›</button>
                  <div class="showcase__stage-area">
                    <img
                      class="showcase__trophy showcase__trophy--real"
                      :src="heroTrophyImage"
                      alt="蓝金星盾奖杯"
                    />
                    <i class="showcase__pedestal"></i>
                  </div>
                </article>
              </Transition>
            </div>

            <div v-else class="podium" :class="`podium--s${i}`">
              <button class="podium-case" type="button" :aria-label="`聚焦成就 ${slot.name}`" @click="selectAchievement(slot)">
                <TrophyStatue :variant="slot.variant" class="podium-case__trophy" :style="{ animationDelay: `${i * 0.7}s` }" />
              </button>
              <div class="podium-plate">
                <b>{{ slot.name }}</b>
                <span>{{ slot.date }}</span>
              </div>
            </div>
          </template>
        </div>

        <div class="stage-discs" aria-hidden="true">
          <i class="stage-disc stage-disc--base"></i>
          <i class="stage-disc stage-disc--mid"></i>
          <i class="stage-disc stage-disc--top"></i>
          <i class="stage-sweep"></i>
        </div>
        <div class="stage-crest" aria-hidden="true">卓越成就</div>
      </div>

      <!-- 右侧成就列表 -->
      <aside class="record-panel" aria-label="成就列表">
        <div class="record-tabs" role="tablist" aria-label="成就分类筛选">
          <button
            v-for="cat in categories"
            :key="cat"
            type="button"
            class="record-tabs__btn"
            :class="{ active: activeCategory === cat }"
            role="tab"
            :aria-selected="activeCategory === cat"
            @click="activeCategory = cat"
          >{{ cat }}</button>
        </div>

        <div class="record-list">
          <button
            v-for="ach in filteredAchievements"
            :key="ach.id"
            type="button"
            class="record-row"
            :class="{ active: focusId === ach.id }"
            :aria-label="`聚焦成就 ${ach.name}`"
            @click="selectAchievement(ach)"
            @dblclick="openDetail(ach)"
          >
            <span class="record-row__medal" v-html="categoryIcons[ach.category]"></span>
            <span class="record-row__copy">
              <b>{{ ach.name }}</b>
              <small>{{ ach.date }}</small>
            </span>
            <svg class="record-row__arrow" viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7" /></svg>
          </button>

          <p v-if="!filteredAchievements.length" class="record-empty">该分类下暂无成就记录</p>
        </div>
      </aside>

      <footer class="wall-motto" aria-hidden="true">更好的你，正在路上</footer>

      <!-- 成就详情弹层 -->
      <Transition name="detail-pop">
        <div v-if="detailAchievement" class="detail-mask" @click.self="detailAchievement = null">
          <article class="detail-card" role="dialog" aria-modal="true" :aria-label="`成就详情 ${detailAchievement.name}`">
            <button class="detail-card__close" type="button" aria-label="关闭详情" @click="detailAchievement = null">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" /></svg>
            </button>

            <span class="detail-card__rarity" :style="{ color: rarityColors[detailAchievement.rarity], borderColor: rarityColors[detailAchievement.rarity] }">
              {{ detailAchievement.rarity }}成就
            </span>

            <div class="detail-card__trophy-wrap">
              <i class="detail-card__halo"></i>
              <TrophyStatue :variant="detailAchievement.variant" class="detail-card__trophy" />
            </div>

            <h3>{{ detailAchievement.name }}</h3>

            <div class="detail-card__chips">
              <span class="chip chip--cat">{{ detailAchievement.category }}</span>
              <span class="chip">{{ detailAchievement.date }}</span>
              <span class="chip chip--points">+{{ detailAchievement.points }} 积分</span>
            </div>

            <p class="detail-card__desc">{{ detailAchievement.desc }}</p>

            <ul class="detail-card__evidence">
              <li v-for="item in detailAchievement.evidence" :key="item">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 4.5 4.5L19 7" /></svg>
                {{ item }}
              </li>
            </ul>

            <div class="detail-card__actions">
              <button class="detail-btn detail-btn--primary" type="button" @click="shareAchievement">生成成就名片</button>
              <button class="detail-btn" type="button" @click="detailAchievement = null">关闭</button>
            </div>
          </article>
        </div>
      </Transition>

      <Transition name="toast">
        <div v-if="toastText" class="wall-toast" role="status">{{ toastText }}</div>
      </Transition>
    </section>
  </Transition>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import TrophyStatue from './TrophyStatue.vue'
import heroTrophyImage from '@/assets/cockpit/trophy-shield.png'

const emit = defineEmits<{ close: [] }>()

const ambientStars = Array.from({ length: 42 }, (_, index) => ({
  id: index,
  x: 8 + ((index * 37) % 84),
  y: 17 + ((index * 53) % 58),
  delay: -((index * 0.37) % 4),
  opacity: 0.28 + ((index * 17) % 60) / 100,
}))

type AchievementCategory = '学习类' | '竞赛类' | '实践类'
type TrophyVariant = 'cup' | 'shield' | 'star' | 'gem' | 'medal'
type Rarity = '普通' | '稀有' | '史诗' | '传说'

type Achievement = {
  id: string
  name: string
  date: string
  category: AchievementCategory
  variant: TrophyVariant
  points: number
  rarity: Rarity
  desc: string
  evidence: string[]
  showcase?: boolean
}

const achievements: Achievement[] = [
  {
    id: 'national-2nd',
    name: '国家级成就二等奖',
    date: '2025.05',
    category: '竞赛类',
    variant: 'cup',
    points: 800,
    rarity: '传说',
    showcase: true,
    desc: '在全国大学生职业能力大赛总决赛中斩获二等奖，作品「岗位技能知识图谱平台」从 1,200 余支队伍中脱颖而出，获得评审团一致认可。',
    evidence: ['国家级赛事获奖证书（编号已核验）', '决赛现场答辩视频存档', '作品被大赛官网收录为优秀案例'],
  },
  {
    id: 'learning-master',
    name: '学习达人',
    date: '2024.12',
    category: '学习类',
    variant: 'shield',
    points: 320,
    rarity: '稀有',
    showcase: true,
    desc: '连续 12 周保持每日 3 小时以上深度学习，季度课程完成率 98%，位列同专业学习者前 5%。',
    evidence: ['连续 84 天学习打卡记录', '季度学习报告已生成', '12 门课程全部通过测验'],
  },
  {
    id: 'project-breakthrough',
    name: '项目突破奖',
    date: '2025.03',
    category: '竞赛类',
    variant: 'cup',
    points: 460,
    rarity: '史诗',
    showcase: true,
    desc: '在校级创新项目中首次独立完成 RAG 知识库问答系统，检索准确率突破 92%，获评年度十大突破项目。',
    evidence: ['项目演示视频与代码仓库已归档', '导师推荐信（项目方向）', '检索评估报告达标'],
  },
  {
    id: 'excellent-cadre',
    name: '优秀学生干部',
    date: '2024.10',
    category: '实践类',
    variant: 'star',
    points: 260,
    rarity: '稀有',
    showcase: true,
    desc: '担任班级学习委员期间组织 8 场技术分享会，带动班级平均绩点提升 0.4，获校级优秀学生干部表彰。',
    evidence: ['校团委表彰文件', '8 场分享会签到与讲义存档', '班级绩点对比数据'],
  },
  {
    id: 'outstanding-student',
    name: '优秀学子称号',
    date: '2024.10',
    category: '学习类',
    variant: 'gem',
    points: 240,
    rarity: '稀有',
    showcase: true,
    desc: '综合测评位列专业前 3%，学业成绩与综合素质双优，荣获本年度优秀学子荣誉称号。',
    evidence: ['综合测评成绩单（教务处认证）', '荣誉证书已归档', '辅导员推荐意见'],
  },
  {
    id: 'python-cert',
    name: 'Python 编程技能证书',
    date: '2024.08',
    category: '学习类',
    variant: 'medal',
    points: 180,
    rarity: '普通',
    desc: '通过全国计算机等级考试 Python 二级（94 分），掌握数据分析与自动化脚本核心能力。',
    evidence: ['等级考试证书（94 分）', '配套实验代码已归档'],
  },
  {
    id: 'cet4',
    name: '英语四级证书',
    date: '2024.06',
    category: '学习类',
    variant: 'medal',
    points: 160,
    rarity: '普通',
    desc: '大学英语四级考试 586 分，可流畅阅读英文技术文档与论文，为进阶学习打下语言基础。',
    evidence: ['四级成绩单（586 分）'],
  },
  {
    id: 'school-excellent',
    name: '校级优秀学生',
    date: '2024.02',
    category: '学习类',
    variant: 'medal',
    points: 150,
    rarity: '普通',
    desc: '凭第一学期学业成绩与综合表现获校级优秀学生奖学金，位列专业前 10%。',
    evidence: ['奖学金评定公示文件'],
  },
  {
    id: 'social-practice',
    name: '社会实践先进个人',
    date: '2023.12',
    category: '实践类',
    variant: 'medal',
    points: 140,
    rarity: '普通',
    desc: '参与「数字支教」寒假社会实践，累计服务 120 课时，获评社会实践先进个人。',
    evidence: ['实践单位鉴定表', '服务时长认证记录'],
  },
]

const stats = { total: 24, points: 3680, rankPercent: 12 }

const categories = ['全部', '学习类', '竞赛类', '实践类'] as const
type FilterCategory = (typeof categories)[number]
const activeCategory = ref<FilterCategory>('全部')

const filteredAchievements = computed(() => {
  const sorted = [...achievements].sort((a, b) => (a.date < b.date ? 1 : -1))
  if (activeCategory.value === '全部') return sorted
  return sorted.filter(item => item.category === activeCategory.value)
})

const categoryIcons: Record<AchievementCategory, string> = {
  学习类: '<svg viewBox="0 0 24 24"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21.5v-16Z"/><path d="M4 19a2.5 2.5 0 0 1 2.5-2.5H20"/></svg>',
  竞赛类: '<svg viewBox="0 0 24 24"><path d="M8 21h8m-4-4v4M7 4h10v6a5 5 0 0 1-10 0V4Z"/><path d="M7 6H4a3 3 0 0 0 3 5m10-5h3a3 3 0 0 1-3 5"/></svg>',
  实践类: '<svg viewBox="0 0 24 24"><path d="M6 21V4m0 0h12l-2.5 4L18 12H6"/></svg>',
}

const rarityColors: Record<Rarity, string> = {
  普通: '#9fb4d8',
  稀有: '#58c6ff',
  史诗: '#b18cff',
  传说: '#ffc86b',
}

const focusId = ref(achievements[0].id)
const focusAchievement = computed(() => achievements.find(item => item.id === focusId.value) ?? achievements[0])

function selectAchievement(ach: Achievement) {
  focusId.value = ach.id
}

const showcaseAchievements = achievements.filter(item => item.showcase)
const centerAchievement = computed(() => {
  const focus = focusAchievement.value
  return focus.showcase ? focus : showcaseAchievements[0]
})
const sideAchievements = computed(() => showcaseAchievements.filter(item => item.id !== centerAchievement.value.id).slice(0, 4))
const podiumSlots = computed<Achievement[]>(() => [
  sideAchievements.value[0],
  sideAchievements.value[1],
  centerAchievement.value,
  sideAchievements.value[2],
  sideAchievements.value[3],
].filter(Boolean))

const detailAchievement = ref<Achievement | null>(null)

function openDetail(ach: Achievement) {
  detailAchievement.value = ach
}

const toastText = ref('')
let toastTimer = 0

function shareAchievement() {
  if (detailAchievement.value) selectAchievement(detailAchievement.value)
  showToast('成就名片已生成，可分享到成长档案')
}

function showToast(message: string) {
  toastText.value = message
  if (toastTimer) window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => { toastText.value = '' }, 2400)
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key !== 'Escape') return
  if (detailAchievement.value) {
    detailAchievement.value = null
    return
  }
  emit('close')
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
  if (toastTimer) window.clearTimeout(toastTimer)
})

// 大厅环境元素已由 stage-3d-bg 效果图承载，无需额外生成
</script>

<style scoped>
.achv-wall {
  position: fixed;
  inset: 0;
  z-index: 60;
  overflow: hidden;
  outline: none;
  color: #fff;
  /* 严格沿用参考图的深紫红+洋红+午夜蓝基调，不用青蓝科技风底色 */
  background:
    radial-gradient(88% 60% at 50% 14%, rgba(148, 36, 116, 0.55), transparent 62%),
    radial-gradient(110% 90% at 50% 110%, rgba(36, 46, 120, 0.82), rgba(10, 10, 34, 0.96) 58%),
    linear-gradient(180deg, #1a0c23 0%, #12091a 50%, #0a102a 100%);
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
}

/* ============ 大厅背景：严格使用 3D 效果图作地台 ============ */
.hall-bg { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
.hall-bg__stage {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  /* 让效果图铺满屏幕（保持纵横比，16:10 匹配舞台占比） */
  width: 106%;
  height: 114%;
  max-width: none;
  object-fit: cover;
  object-position: center 58%;
  filter: saturate(1.1) contrast(1.06) brightness(0.98);
  opacity: 0.985;
}
/* 暗色 vignette，保持边缘沉浸 */
.hall-bg__vignette {
  position: absolute; inset: 0;
  background:
    radial-gradient(120% 80% at 50% 42%, transparent 40%, rgba(4, 4, 24, 0.65) 82%, rgba(0, 0, 0, 0.92) 100%),
    linear-gradient(180deg, rgba(10, 6, 22, 0.45), transparent 30%, transparent 75%, rgba(2, 6, 22, 0.6));
}
/* 顶部一道洋红聚光，呼应参考图上半部分的紫红暖光 */
.hall-bg__spot {
  position: absolute;
  left: 50%;
  top: -6%;
  transform: translateX(-50%);
  width: 58%;
  height: 48%;
  background: radial-gradient(ellipse at 50% 0%, rgba(255, 76, 176, 0.22), rgba(180, 70, 180, 0.08) 40%, transparent 72%);
  mix-blend-mode: screen;
  filter: blur(24px);
}
/* 中央展台后方的洋红辉光（与图中银灰展台周围呼应） */
.hall-bg__magenta {
  position: absolute;
  left: 50%;
  bottom: 36%;
  transform: translateX(-50%);
  width: 30%;
  height: 28%;
  background: radial-gradient(ellipse at center, rgba(255, 125, 196, 0.18), transparent 70%);
  mix-blend-mode: screen;
  filter: blur(14px);
  animation: magenta-breathe 6s ease-in-out infinite;
}
@keyframes magenta-breathe { 0%, 100% { opacity: .8; } 50% { opacity: 1; } }

/* ============ 返回 & 标题 ============ */
.wall-back {
  position: absolute;
  top: 22px; left: 24px;
  z-index: 20;
  display: flex; align-items: center; gap: 8px;
  padding: 10px 18px;
  border: 1px solid rgba(255, 178, 220, 0.36);
  border-radius: 12px;
  background: rgba(46, 14, 48, 0.6);
  color: #ffdceb;
  font-size: 13px; font-weight: 600;
  cursor: pointer;
  backdrop-filter: blur(8px);
  transition: all 0.25s ease;
}
.wall-back svg { width: 16px; height: 16px; transition: transform 0.25s ease; }
.wall-back:hover {
  border-color: rgba(255, 140, 200, 0.7);
  background: rgba(88, 22, 88, 0.76);
  color: #fff;
  box-shadow: 0 0 18px rgba(255, 80, 170, 0.35);
}
.wall-back:hover svg { transform: translateX(-3px); }

.wall-title {
  position: absolute;
  top: clamp(64px, 9vh, 96px);
  left: clamp(28px, 3.6vw, 64px);
  z-index: 5;
}
.wall-title h1 {
  margin: 0;
  font-size: clamp(30px, 3.2vw, 44px);
  font-weight: 800;
  letter-spacing: clamp(4px, 0.5vw, 8px);
  background: linear-gradient(135deg, #ffffff 22%, #ffc7e0 55%, #c7c4ff 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 20px rgba(255, 120, 190, 0.35));
}
.wall-title p {
  margin: 10px 0 0 4px;
  font-size: clamp(13px, 1.1vw, 16px);
  letter-spacing: clamp(2px, 0.3vw, 4px);
  color: rgba(245, 210, 228, 0.82);
}

/* ============ 左侧统计（参考图紫红系同步） ============ */
.stat-panel {
  position: absolute;
  left: clamp(24px, 3.4vw, 60px);
  top: 50%;
  transform: translateY(-56%);
  z-index: 10;
  width: clamp(196px, 16.5vw, 272px);
  padding: clamp(20px, 2.4vh, 32px) clamp(20px, 1.8vw, 28px) clamp(14px, 2vh, 22px);
  border: 1px solid rgba(255, 164, 210, 0.3);
  border-radius: 16px;
  background: linear-gradient(168deg, rgba(142, 36, 108, 0.22), rgba(42, 14, 58, 0.58) 52%, rgba(104, 46, 142, 0.3));
  box-shadow: 0 18px 44px rgba(30, 4, 44, 0.45), inset 0 0 36px rgba(255, 80, 170, 0.08);
  backdrop-filter: blur(7px);
}
.stat-panel::before,
.stat-panel::after {
  content: '';
  position: absolute;
  width: 20px; height: 20px;
  border: 2px solid rgba(255, 190, 228, 0.75);
  filter: drop-shadow(0 0 6px rgba(255, 120, 190, 0.7));
}
.stat-panel::before { top: -2px; left: -2px; border-right: 0; border-bottom: 0; border-top-left-radius: 14px; }
.stat-panel::after { bottom: -2px; right: -2px; border-left: 0; border-top: 0; border-bottom-right-radius: 14px; }

.sp-item { display: flex; flex-direction: column; }
.sp-item + .sp-item { margin-top: clamp(14px, 2.4vh, 24px); padding-top: clamp(14px, 2.4vh, 24px); border-top: 1px solid rgba(255, 160, 208, 0.16); }
.sp-label { font-size: 13px; letter-spacing: 3px; color: rgba(248, 212, 228, 0.68); }
.sp-value {
  margin-top: 8px;
  font-size: clamp(34px, 2.9vw, 46px);
  font-weight: 800;
  line-height: 1;
  font-family: Bahnschrift, "DIN Alternate", "Microsoft YaHei", sans-serif;
  background: linear-gradient(135deg, #fff 30%, #ffd0e5 85%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 18px rgba(255, 120, 190, 0.5));
}
.sp-value small { margin-left: 2px; font-size: 0.42em; font-weight: 600; color: #ff9fc9; -webkit-text-fill-color: #ff9fc9; }
.sp-delta {
  margin-top: 8px;
  align-self: flex-start;
  padding: 2px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255, 200, 107, 0.4);
  background: rgba(255, 190, 80, 0.1);
  color: #ffc86b;
  font-size: 11.5px;
}
.sp-delta i { font-style: normal; font-weight: 700; }

/* ============ 中央领奖台：奖杯站在参考图的银灰展台上 ============ */
.stage {
  position: absolute;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  width: min(1080px, 70vw);
  height: min(82vh, 820px);
  z-index: 8;
  pointer-events: none;
  perspective: 1500px;
  perspective-origin: 50% 56%;
}
/* 舞台背景图中银灰展台位于 y≈58%-78%、x 居中。因此奖杯行和展示舱往下对齐 */
.arch-glow {
  position: absolute;
  left: 50%; bottom: 10%;
  transform: translateX(-50%);
  width: clamp(420px, 40vw, 620px);
  aspect-ratio: 1;
  border-radius: 50%;
  border: 2px solid rgba(255, 130, 200, 0.24);
  box-shadow: 0 0 72px rgba(255, 80, 170, 0.2), inset 0 0 96px rgba(220, 90, 190, 0.14);
  -webkit-mask-image: linear-gradient(180deg, #000 68%, transparent 92%);
  mask-image: linear-gradient(180deg, #000 68%, transparent 92%);
  animation: arch-pulse 5s ease-in-out infinite;
}
@keyframes arch-pulse {
  0%, 100% { opacity: 0.68; }
  50% { opacity: 1; }
}

.podium-row {
  position: absolute;
  left: 0; right: 0;
  /* 1080 屏 y≈626-670 为效果图银灰展台顶面；奖杯 bottom 落地应落在此区间 */
  bottom: 39.5%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: clamp(10px, 1.2vw, 24px);
  transform-style: preserve-3d;
}
.podium { display: flex; flex-direction: column; align-items: center; pointer-events: none; transform-style: preserve-3d; }
.podium--s0, .podium--s4 { display: none; }
.podium--s0, .podium--s4 { transform: translateY(-24px) scale(0.76) translateZ(-220px); opacity: 0.78; z-index: 1; }
/* 两侧奖杯：后退并内收 10°，形成弧形陈列 */
.podium--s1 { transform: translateY(-8px) scale(0.9) translateZ(-110px) rotateY(10deg); opacity: 0.93; z-index: 2; }
.podium--s3 { transform: translateY(-8px) scale(0.9) translateZ(-110px) rotateY(-10deg); opacity: 0.93; z-index: 2; }
/* 中央展示舱：前凸，站在最上层地台 */
.podium--center { transform: translateZ(90px); z-index: 6; }
@media (min-width: 1760px) {
  .podium--s0, .podium--s4 { display: flex; }
}

.podium-case {
  pointer-events: auto;
  position: relative;
  width: clamp(100px, 9.6vw, 156px);
  aspect-ratio: 0.76;
  padding: 8% 6% 5%;
  border: 1px solid rgba(255, 176, 220, 0.26);
  border-radius: 14px;
  background: linear-gradient(168deg, rgba(255, 140, 200, 0.11), rgba(70, 22, 80, 0.12) 48%, rgba(200, 90, 190, 0.16));
  box-shadow: inset 0 0 28px rgba(255, 100, 180, 0.1), 0 12px 30px rgba(28, 4, 40, 0.42);
  cursor: pointer;
  display: grid;
  place-items: end center;
  overflow: hidden;
  transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}
.podium-case::before {
  content: '';
  position: absolute;
  top: -40%; left: -30%;
  width: 46%; height: 170%;
  background: linear-gradient(180deg, rgba(255, 235, 248, 0.14), transparent);
  transform: rotate(22deg);
  pointer-events: none;
}
.podium-case:hover,
.podium-case:focus-visible {
  border-color: rgba(255, 190, 230, 0.6);
  box-shadow: inset 0 0 36px rgba(255, 130, 200, 0.2), 0 0 28px rgba(255, 90, 180, 0.32);
  transform: translateY(-4px) translateZ(46px);
}
.podium-case__trophy {
  width: 82%;
  filter: drop-shadow(0 10px 16px rgba(255, 140, 60, 0.35));
  animation: trophy-float 4.2s ease-in-out infinite;
}
@keyframes trophy-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-7px); }
}

.podium-plate {
  margin-top: 10px;
  min-width: 82%;
  padding: 9px 12px 10px;
  text-align: center;
  border: 1px solid rgba(255, 168, 220, 0.3);
  border-radius: 10px;
  background: linear-gradient(180deg, rgba(54, 14, 60, 0.92), rgba(32, 8, 44, 0.92));
  box-shadow: 0 8px 22px rgba(26, 4, 40, 0.5), 0 0 16px rgba(255, 100, 180, 0.14);
  clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
}
.podium-plate b { display: block; font-size: clamp(12px, 0.95vw, 15px); letter-spacing: 1px; white-space: nowrap; color: #fff0f7; }
.podium-plate span { display: block; margin-top: 3px; font-size: 11px; letter-spacing: 1px; color: rgba(255, 202, 230, 0.6); }

/* 中央展示舱 */
.showcase {
  pointer-events: auto;
  position: relative;
  width: clamp(260px, 22vw, 340px);
  padding: clamp(16px, 2.4vh, 24px) 16px 12px;
  border: 1px solid rgba(255, 200, 230, 0.42);
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255, 130, 200, 0.11), rgba(44, 12, 60, 0.32) 42%, rgba(190, 90, 180, 0.12));
  box-shadow: 0 0 48px rgba(255, 80, 170, 0.26), inset 0 0 44px rgba(255, 140, 210, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: box-shadow 0.3s ease, border-color 0.3s ease;
}
.showcase:hover { border-color: rgba(255, 220, 240, 0.65); box-shadow: 0 0 62px rgba(255, 100, 180, 0.38), inset 0 0 50px rgba(255, 160, 220, 0.12); }
.showcase__corner {
  position: absolute;
  width: 22px; height: 22px;
  border: 2px solid #ffc4e0;
  filter: drop-shadow(0 0 6px rgba(255, 140, 200, 0.85));
}
.showcase__corner--tl { top: -2px; left: -2px; border-right: 0; border-bottom: 0; border-top-left-radius: 16px; }
.showcase__corner--tr { top: -2px; right: -2px; border-left: 0; border-bottom: 0; border-top-right-radius: 16px; }
.showcase__corner--bl { bottom: -2px; left: -2px; border-right: 0; border-top: 0; border-bottom-left-radius: 16px; }
.showcase__corner--br { bottom: -2px; right: -2px; border-left: 0; border-top: 0; border-bottom-right-radius: 16px; }
.showcase h3 {
  margin: 0;
  font-size: clamp(17px, 1.5vw, 23px);
  font-weight: 750;
  letter-spacing: 2px;
  text-align: center;
  text-shadow: 0 0 18px rgba(255, 140, 200, 0.55);
}
.showcase__date { margin-top: 7px; font-size: 13px; letter-spacing: 3px; color: #ffcce5; }
.showcase__btn {
  margin-top: 11px;
  padding: 6px 20px;
  border: 1px solid rgba(255, 176, 222, 0.55);
  border-radius: 999px;
  background: rgba(130, 30, 120, 0.38);
  color: #ffe5f2;
  font-size: 12.5px;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.25s ease;
}
.showcase__btn:hover {
  background: linear-gradient(135deg, #ff5ab5, #c629a7);
  border-color: rgba(255, 210, 235, 0.85);
  color: #fff;
  box-shadow: 0 0 20px rgba(255, 120, 190, 0.58);
}
.showcase__stage-area { position: relative; width: 100%; display: grid; place-items: center; margin-top: 4px; }
.showcase__trophy {
  width: clamp(160px, 13.2vw, 220px);
  filter: drop-shadow(0 16px 28px rgba(255, 160, 80, 0.42));
  animation: trophy-float 4.6s ease-in-out infinite;
}
.showcase__pedestal {
  position: absolute;
  bottom: -4px;
  width: 66%; height: 18px;
  border-radius: 50%;
  background: radial-gradient(ellipse at center, rgba(255, 160, 210, 0.42), transparent 70%);
  filter: blur(2px);
}

/* 舞台地台圆盘：效果图已有三层地台 → 这里只做发光描边，不覆盖底图 */
.stage-discs {
  position: absolute;
  left: 50%; bottom: 16%;
  transform: translateX(-50%);
  width: min(62%, 760px);
  height: clamp(130px, 26vh, 260px);
  transform-style: preserve-3d;
  pointer-events: none;
  mix-blend-mode: screen;
  opacity: .85;
}
.stage-disc {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 50%;
  background: transparent;
}
/* 只留描边 + 光感，避免盖住效果图上真实的银色地台 */
.stage-disc--base {
  bottom: 0;
  transform: translateX(-50%) translateZ(-160px);
  width: 100%; height: 86%;
  border: 1px solid rgba(255, 150, 210, 0.26);
  box-shadow: 0 0 64px rgba(90, 60, 200, 0.35);
}
.stage-disc--mid {
  bottom: 22%;
  transform: translateX(-50%) translateZ(-80px);
  width: 72%; height: 56%;
  border: 1px solid rgba(180, 170, 255, 0.36);
  box-shadow: 0 0 48px rgba(120, 100, 220, 0.3);
}
.stage-disc--top {
  bottom: 40%;
  transform: translateX(-50%) translateZ(0px);
  width: 50%; height: 34%;
  border: 1px solid rgba(255, 210, 240, 0.48);
  box-shadow: 0 0 56px rgba(255, 130, 200, 0.42);
}
.stage-disc--top::after {
  content: '';
  position: absolute;
  inset: 14% 11%;
  border-radius: 50%;
  border: 1px solid rgba(255, 200, 235, 0.25);
}
.stage-sweep {
  position: absolute;
  bottom: 40%;
  left: 50%;
  width: 50%; aspect-ratio: 1.35;
  transform: translateX(-50%);
  border-radius: 50%;
  border: 1px dashed rgba(255, 180, 220, 0.3);
  animation: sweep-spin 16s linear infinite;
}
@keyframes sweep-spin {
  from { transform: translateX(-50%) rotate(0deg); }
  to { transform: translateX(-50%) rotate(360deg); }
}
.stage-crest {
  position: absolute;
  left: 50%; bottom: 9%;
  transform: translateX(-50%);
  padding: 6px 24px;
  border: 1px solid rgba(255, 210, 170, 0.52);
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(88, 24, 72, 0.85), rgba(40, 10, 40, 0.92));
  color: #ffdcae;
  font-size: clamp(11px, 0.85vw, 13px);
  letter-spacing: 6px;
  text-indent: 6px;
  text-shadow: 0 0 12px rgba(255, 180, 120, 0.5);
  box-shadow: 0 0 22px rgba(255, 140, 100, 0.2), inset 0 1px 0 rgba(255, 230, 200, 0.26);
}

/* ============ 右侧成就列表（紫红系同步） ============ */
.record-panel {
  position: absolute;
  right: clamp(20px, 2.8vw, 52px);
  top: clamp(88px, 13vh, 140px);
  bottom: clamp(64px, 10vh, 110px);
  width: clamp(300px, 25vw, 416px);
  z-index: 10;
  display: flex;
  flex-direction: column;
}
.record-tabs { display: flex; gap: 8px; justify-content: flex-end; margin-bottom: 12px; }
.record-tabs__btn {
  padding: 7px 18px;
  border: 1px solid rgba(255, 160, 210, 0.26);
  border-radius: 999px;
  background: rgba(60, 16, 62, 0.55);
  color: rgba(255, 210, 230, 0.75);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.25s ease;
}
.record-tabs__btn:hover { color: #ffc4e0; border-color: rgba(255, 176, 222, 0.52); }
.record-tabs__btn.active {
  background: linear-gradient(135deg, #ff5ab5, #b828a0);
  border-color: rgba(255, 210, 235, 0.68);
  color: #fff;
  box-shadow: 0 0 18px rgba(255, 100, 180, 0.45);
}

.record-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  border: 1px solid rgba(255, 160, 210, 0.22);
  border-radius: 16px;
  background: linear-gradient(172deg, rgba(64, 20, 84, 0.55), rgba(24, 8, 40, 0.72));
  box-shadow: 0 18px 44px rgba(30, 4, 44, 0.4), inset 0 0 30px rgba(255, 90, 170, 0.07);
  backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.record-list::-webkit-scrollbar { width: 5px; }
.record-list::-webkit-scrollbar-track { background: transparent; }
.record-list::-webkit-scrollbar-thumb { background: linear-gradient(180deg, rgba(255, 140, 200, 0.4), rgba(160, 110, 255, 0.32)); border-radius: 3px; }

.record-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 11px 12px;
  border: 1px solid transparent;
  border-radius: 12px;
  background: transparent;
  color: inherit;
  text-align: left;
  cursor: pointer;
  transition: all 0.22s ease;
}
.record-row:hover { background: rgba(255, 120, 190, 0.1); }
.record-row.active {
  border-color: rgba(255, 160, 220, 0.45);
  background: linear-gradient(90deg, rgba(255, 100, 180, 0.16), rgba(255, 100, 180, 0.03));
  box-shadow: inset 0 0 24px rgba(255, 120, 200, 0.1);
}
.record-row__medal {
  flex-shrink: 0;
  width: 44px; height: 44px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #5e3c08;
  background: radial-gradient(circle at 35% 30%, #ffe9ad, #f2b93f 55%, #a06f16);
  box-shadow: 0 0 14px rgba(255, 190, 80, 0.35), inset 0 0 0 3px rgba(120, 80, 10, 0.32);
}
.record-row__medal :deep(svg) { width: 22px; height: 22px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.record-row__copy { flex: 1; min-width: 0; }
.record-row__copy b { display: block; font-size: 14.5px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #fff0f7; }
.record-row__copy small { display: block; margin-top: 3px; font-size: 12px; letter-spacing: 1px; color: rgba(255, 208, 232, 0.55); }
.record-row__arrow { flex-shrink: 0; width: 16px; height: 16px; fill: none; stroke: rgba(255, 170, 215, 0.52); stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; transition: all 0.2s ease; }
.record-row:hover .record-row__arrow { transform: translateX(3px); stroke: #ffc4e0; }
.record-empty { margin: auto; padding: 30px 0; font-size: 13px; color: rgba(255, 200, 228, 0.5); }

/* ============ 底部寄语 ============ */
.wall-motto {
  position: absolute;
  left: 50%;
  bottom: clamp(14px, 3vh, 32px);
  transform: translateX(-50%);
  z-index: 9;
  font-family: KaiTi, STKaiti, "DFKai-SB", cursive;
  font-style: italic;
  font-size: clamp(20px, 2.3vw, 33px);
  letter-spacing: clamp(4px, 0.5vw, 8px);
  color: #ffe8f3;
  text-shadow: 0 0 24px rgba(255, 120, 190, 0.52);
  white-space: nowrap;
}
.wall-motto::after {
  content: '';
  display: block;
  margin: 8px auto 0;
  width: 58%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #ff8fc8, transparent);
  box-shadow: 0 0 12px #ff8fc8;
}

/* ============ 详情弹层 ============ */
.detail-mask {
  position: absolute;
  inset: 0;
  z-index: 30;
  display: grid;
  place-items: center;
  background: rgba(20, 4, 28, 0.62);
  backdrop-filter: blur(6px);
}
.detail-card {
  position: relative;
  width: min(560px, 92vw);
  max-height: 86vh;
  overflow-y: auto;
  padding: 30px 34px 26px;
  border: 1px solid rgba(255, 176, 222, 0.42);
  border-radius: 20px;
  background: linear-gradient(172deg, rgba(78, 22, 96, 0.96), rgba(22, 8, 42, 0.97));
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.62), 0 0 60px rgba(255, 90, 170, 0.26);
  text-align: center;
}
.detail-card__close {
  position: absolute;
  top: 14px; right: 14px;
  width: 34px; height: 34px;
  display: grid;
  place-items: center;
  border: 1px solid rgba(255, 160, 210, 0.3);
  border-radius: 50%;
  background: rgba(64, 18, 74, 0.7);
  color: #ffc4de;
  cursor: pointer;
  transition: all 0.22s ease;
}
.detail-card__close svg { width: 15px; height: 15px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; }
.detail-card__close:hover { color: #fff; border-color: rgba(255, 190, 230, 0.6); box-shadow: 0 0 14px rgba(255, 110, 190, 0.42); }
.detail-card__rarity {
  display: inline-block;
  padding: 3px 14px;
  border: 1px solid;
  border-radius: 999px;
  font-size: 12px;
  letter-spacing: 2px;
  background: rgba(255, 255, 255, 0.03);
}
.detail-card__trophy-wrap { position: relative; width: 170px; margin: 8px auto 0; }
.detail-card__trophy { position: relative; z-index: 1; filter: drop-shadow(0 12px 22px rgba(255, 160, 80, 0.4)); }
.detail-card__halo {
  position: absolute;
  inset: -12% -6% 12%;
  border-radius: 50%;
  background: radial-gradient(circle at 50% 42%, rgba(255, 130, 200, 0.32), transparent 62%);
}
.detail-card h3 {
  margin: 12px 0 0;
  font-size: 23px;
  font-weight: 750;
  letter-spacing: 2px;
  text-shadow: 0 0 18px rgba(255, 130, 200, 0.52);
}
.detail-card__chips { display: flex; justify-content: center; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
.chip {
  padding: 3px 12px;
  border: 1px solid rgba(255, 160, 210, 0.28);
  border-radius: 999px;
  background: rgba(100, 30, 110, 0.42);
  color: rgba(255, 220, 238, 0.88);
  font-size: 12px;
  letter-spacing: 1px;
}
.chip--cat { border-color: rgba(255, 180, 225, 0.52); color: #ffc4e0; }
.chip--points { border-color: rgba(255, 200, 107, 0.45); color: #ffc86b; }
.detail-card__desc {
  margin: 16px 0 0;
  font-size: 13.5px;
  line-height: 1.8;
  color: rgba(255, 225, 240, 0.82);
  text-align: justify;
}
.detail-card__evidence {
  margin: 16px 0 0;
  padding: 14px 16px;
  border: 1px solid rgba(255, 160, 210, 0.18);
  border-radius: 12px;
  background: rgba(60, 18, 78, 0.45);
  list-style: none;
  text-align: left;
}
.detail-card__evidence li {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 5px 0;
  font-size: 12.5px;
  color: rgba(255, 220, 238, 0.78);
}
.detail-card__evidence li + li { border-top: 1px dashed rgba(255, 160, 210, 0.12); }
.detail-card__evidence svg { flex-shrink: 0; width: 14px; height: 14px; fill: none; stroke: #7bffcd; stroke-width: 2.4; stroke-linecap: round; stroke-linejoin: round; }
.detail-card__actions { display: flex; justify-content: center; gap: 12px; margin-top: 20px; }
.detail-btn {
  padding: 9px 26px;
  border: 1px solid rgba(255, 160, 210, 0.35);
  border-radius: 10px;
  background: rgba(88, 22, 98, 0.6);
  color: #ffdff0;
  font-size: 13.5px;
  cursor: pointer;
  transition: all 0.25s ease;
}
.detail-btn:hover { color: #fff; border-color: rgba(255, 190, 230, 0.6); box-shadow: 0 0 16px rgba(255, 110, 190, 0.36); }
.detail-btn--primary {
  border-color: transparent;
  background: linear-gradient(135deg, #ff5ab5, #b828a0);
  color: #fff;
}
.detail-btn--primary:hover { box-shadow: 0 0 22px rgba(255, 100, 180, 0.58); }

/* ============ 提示 & 过渡 ============ */
.wall-toast {
  position: absolute;
  left: 50%;
  bottom: clamp(70px, 11vh, 120px);
  transform: translateX(-50%);
  z-index: 40;
  padding: 11px 24px;
  border: 1px solid rgba(255, 170, 218, 0.45);
  border-radius: 999px;
  background: rgba(60, 14, 64, 0.92);
  box-shadow: 0 0 26px rgba(255, 100, 180, 0.36);
  color: #ffe5f3;
  font-size: 13.5px;
  letter-spacing: 1px;
  backdrop-filter: blur(8px);
}

.wall-appear-enter-active { transition: opacity 0.5s ease, transform 0.55s cubic-bezier(0.22, 1, 0.36, 1); }
.wall-appear-leave-active { transition: opacity 0.32s ease, transform 0.32s ease; }
.wall-appear-enter-from,
.wall-appear-leave-to { opacity: 0; transform: scale(1.035); }

.focus-swap-enter-active { transition: opacity 0.32s ease, transform 0.32s ease; }
.focus-swap-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.focus-swap-enter-from { opacity: 0; transform: translateY(14px) scale(0.97); }
.focus-swap-leave-to { opacity: 0; transform: translateY(-8px) scale(0.98); }

.detail-pop-enter-active { transition: opacity 0.3s ease; }
.detail-pop-leave-active { transition: opacity 0.22s ease; }
.detail-pop-enter-active .detail-card { transition: transform 0.34s cubic-bezier(0.22, 1, 0.36, 1); }
.detail-pop-enter-from,
.detail-pop-leave-to { opacity: 0; }
.detail-pop-enter-from .detail-card { transform: translateY(22px) scale(0.94); }

.toast-enter-active,
.toast-leave-active { transition: opacity 0.3s ease, transform 0.3s ease; }
.toast-enter-from,
.toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(10px); }

/* ============ 响应式 ============ */
@media (max-width: 1360px) {
  .stage { width: min(980px, 62vw); }
  .record-panel { width: clamp(290px, 27vw, 380px); }
}
@media (max-width: 1180px) {
  .stat-panel { display: none; }
  .record-panel { width: clamp(270px, 32vw, 360px); }
}
@media (max-width: 860px) {
  .record-panel { top: auto; bottom: 84px; right: 12px; left: 12px; width: auto; height: 34vh; }
  .record-tabs { justify-content: center; }
  .wall-motto { display: none; }
  .podium--s1, .podium--s3 { display: none; }
  .wall-title { left: 20px; }
}
@media (prefers-reduced-motion: reduce) {
  .podium-case__trophy,
  .showcase__trophy,
  .stage-sweep,
  .arch-glow,
  .hall-bg__magenta { animation: none; }
  .wall-appear-enter-active,
  .focus-swap-enter-active,
  .detail-pop-enter-active { transition: none; }
}
</style>
