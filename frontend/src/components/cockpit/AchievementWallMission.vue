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

        <div class="trophy-carousel" aria-label="五奖杯旋转展台">
          <button
            v-for="(item, itemIndex) in carouselItems"
            :key="item.achievement.id"
            type="button"
            class="trophy-carousel__item"
            :class="{ 'is-center': itemIndex === carouselIndex }"
            :style="carouselItemStyle(itemIndex)"
            :aria-label="itemIndex === carouselIndex ? `查看 ${item.achievement.name} 详情` : `将 ${item.achievement.name} 转到中央`"
            @click="handleCarouselClick(itemIndex)"
          >
            <span class="trophy-carousel__frame">
              <span v-if="itemIndex === carouselIndex" class="trophy-carousel__meta">
                <strong>{{ item.achievement.name }}</strong>
                <small>{{ item.achievement.date }}</small>
                <i @click.stop="openDetail(item.achievement)">查看详情 ›</i>
              </span>
              <div class="trophy-carousel__svg-wrap">
                <TrophyStatue :variant="item.achievement.variant" />
              </div>
              <span class="trophy-carousel__aura"></span>
            </span>
            <span class="trophy-carousel__plate">
              <b>{{ item.achievement.name }}</b>
              <small>{{ item.achievement.date }}</small>
            </span>
          </button>
        </div>

        <div class="stage-discs" aria-hidden="true">
          <i class="stage-disc stage-disc--base"></i>
          <i class="stage-disc stage-disc--mid"></i>
          <i class="stage-disc stage-disc--top"></i>
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

const emit = defineEmits<{ close: [] }>()
const props = withDefaults(defineProps<{
  activityEvents?: Array<{ type: string; id: string | number; date: string; title: string; detail: string }>
}>(), { activityEvents: () => [] })

let trophyTimer: number | undefined

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

const achievementCatalog: Achievement[] = [
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

const achievements = computed<Achievement[]>(() => {
  const mapped = props.activityEvents.slice(0, 9).map((event, index) => {
    const style = achievementCatalog[index % achievementCatalog.length]
    return {
      ...style,
      id: `${event.type}-${event.id}`,
      name: event.title,
      date: new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: '2-digit' }).format(new Date(event.date)),
      category: event.type === 'interview' ? '实践类' as const : '学习类' as const,
      points: 0,
      rarity: '普通' as const,
      desc: event.detail,
      evidence: [`记录来源：当前账号`, `记录时间：${new Intl.DateTimeFormat('zh-CN').format(new Date(event.date))}`],
      showcase: index < 5,
    }
  })
  return mapped.length ? mapped : [{
    ...achievementCatalog[0], id: 'empty', name: '暂无真实成长记录', date: '等待同步',
    category: '学习类', points: 0, rarity: '普通', desc: '完成简历、岗位匹配或面试后，这里会展示当前账号的真实成长记录。',
    evidence: ['当前账号尚无可展示记录'], showcase: true,
  }]
})
const stats = computed(() => ({ total: props.activityEvents.length, points: 0, rankPercent: 0 }))

const categories = ['全部', '学习类', '竞赛类', '实践类'] as const
type FilterCategory = (typeof categories)[number]
const activeCategory = ref<FilterCategory>('全部')

const filteredAchievements = computed(() => {
  const sorted = [...achievements.value].sort((a, b) => (a.date < b.date ? 1 : -1))
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

const focusId = ref('')
const focusAchievement = computed(() => achievements.value.find(item => item.id === focusId.value) ?? achievements.value[0])

function selectAchievement(ach: Achievement) {
  focusId.value = ach.id
  const showcaseIndex = showcaseAchievements.value.findIndex(item => item.id === ach.id)
  if (showcaseIndex >= 0) selectCarouselItem(showcaseIndex)
}

const showcaseAchievements = computed(() => achievements.value.filter(item => item.showcase))
const carouselItems = computed(() => showcaseAchievements.value.map((achievement) => ({
  achievement,
})))
const carouselIndex = ref(0)

const carouselSlots = [
  { x: -43, y: 34, scale: 0.58, depth: -260, rotate: 17, opacity: 0.58, zIndex: 1 },
  { x: -24, y: 20, scale: 0.78, depth: -110, rotate: 10, opacity: 0.9, zIndex: 3 },
  { x: 0, y: 4, scale: 1.08, depth: 120, rotate: 0, opacity: 1, zIndex: 6 },
  { x: 24, y: 20, scale: 0.78, depth: -110, rotate: -10, opacity: 0.9, zIndex: 3 },
  { x: 43, y: 34, scale: 0.58, depth: -260, rotate: -17, opacity: 0.58, zIndex: 1 },
]

function carouselSlotIndex(itemIndex: number) {
  const offset = (itemIndex - carouselIndex.value + carouselItems.value.length) % carouselItems.value.length
  return [2, 3, 4, 0, 1][offset]
}

function carouselItemStyle(itemIndex: number) {
  const slot = carouselSlots[carouselSlotIndex(itemIndex)]
  return {
    left: `${50 + slot.x}%`,
    top: `${slot.y}%`,
    opacity: slot.opacity,
    zIndex: slot.zIndex,
    transform: `translate(-50%, 0) translateZ(${slot.depth}px) rotateY(${slot.rotate}deg) scale(${slot.scale})`,
  }
}

function startTrophyCycle() {
  if (trophyTimer) window.clearInterval(trophyTimer)
  trophyTimer = window.setInterval(() => {
    carouselIndex.value = (carouselIndex.value + 1) % carouselItems.value.length
    focusId.value = carouselItems.value[carouselIndex.value].achievement.id
  }, 4800)
}

function selectCarouselItem(index: number) {
  carouselIndex.value = index
  focusId.value = carouselItems.value[index].achievement.id
  startTrophyCycle()
}

function handleCarouselClick(index: number) {
  if (index === carouselIndex.value) {
    openDetail(carouselItems.value[index].achievement)
    return
  }
  selectCarouselItem(index)
}

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

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  startTrophyCycle()
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
  if (toastTimer) window.clearTimeout(toastTimer)
  if (trophyTimer) window.clearInterval(trophyTimer)
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
  .arch-glow,
  .hall-bg__magenta { animation: none; }
  .wall-appear-enter-active,
  .focus-swap-enter-active,
  .detail-pop-enter-active { transition: none; }
}

/* ============ 蓝金展厅还原层：纯 CSS 场景，不使用参考图 ============ */
.achv-wall {
  background: #020817;
  color: #eef8ff;
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
}
.hall-bg { background: #020817; isolation: isolate; }
.hall-bg__shell {
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 54% 46% at 50% 43%, rgba(13, 76, 170, .28), transparent 72%),
    radial-gradient(ellipse 94% 74% at 50% 72%, rgba(0, 75, 183, .16), transparent 70%),
    linear-gradient(180deg, #020817 0%, #04132e 46%, #020817 100%);
}
.hall-bg__shell::before {
  content: ''; position: absolute; inset: 5% 7% 22%; border-radius: 46% 46% 10% 10% / 23% 23% 8% 8%;
  border: 2px solid rgba(34, 157, 255, .22);
  background:
    repeating-linear-gradient(90deg, transparent 0 8%, rgba(44, 141, 255, .07) 8.15% 8.35%, transparent 8.5% 16%),
    radial-gradient(ellipse at 50% 68%, rgba(6, 31, 78, .22), rgba(1, 8, 25, .84) 74%);
  box-shadow: inset 0 0 90px rgba(5, 71, 174, .25), 0 0 70px rgba(0, 91, 255, .12);
}
.hall-bg__ceiling {
  position: absolute; left: 50%; top: -28%; width: 132%; height: 58%; transform: translateX(-50%);
  border-radius: 0 0 50% 50%; border-bottom: 3px solid rgba(53, 160, 255, .34);
  background:
    repeating-radial-gradient(ellipse at 50% 100%, transparent 0 8%, rgba(31, 91, 172, .23) 8.3% 8.8%, transparent 9.1% 13%),
    linear-gradient(180deg, #01050f, #07162f 70%, #061f47);
  box-shadow: 0 20px 70px rgba(7, 83, 196, .36), inset 0 -4px 20px rgba(57, 171, 255, .18);
}
.hall-bg__ceiling i {
  --lamp-x: calc(14% + (var(--lamp-index) - 1) * 12%);
  position: absolute; left: var(--lamp-x); bottom: -7px; width: 15px; height: 15px; border-radius: 50%;
  background: #fff4c8; border: 2px solid #ffc75c;
  box-shadow: 0 0 8px #fff, 0 0 22px #ffb43f, 0 0 48px rgba(255, 174, 50, .58);
}
.hall-bg__ceiling i::after {
  content: ''; position: absolute; left: 50%; top: 12px; width: 72px; height: 250px; transform: translateX(-50%);
  background: linear-gradient(180deg, rgba(255, 202, 104, .2), transparent 78%); clip-path: polygon(43% 0, 57% 0, 100% 100%, 0 100%); filter: blur(8px);
}
.hall-bg__arch {
  position: absolute; left: 50%; top: 14%; width: 72%; height: 59%; transform: translateX(-50%);
  border: 14px solid rgba(9, 35, 79, .72); border-radius: 50% 50% 8% 8% / 28% 28% 8% 8%;
  box-shadow: 0 0 0 2px rgba(36, 160, 255, .34), inset 0 0 36px rgba(18, 121, 255, .24), 0 0 46px rgba(2, 66, 176, .28);
}
.hall-bg__arch::before {
  content: ''; position: absolute; inset: 14px; border-radius: inherit; border: 2px solid rgba(62, 198, 255, .2);
  box-shadow: inset 0 0 55px rgba(0, 96, 255, .12);
}
.hall-bg__horizon {
  position: absolute; left: 0; right: 0; top: 48%; height: 2px;
  background: linear-gradient(90deg, transparent, rgba(26, 145, 255, .78) 18%, #70dfff 50%, rgba(26, 145, 255, .78) 82%, transparent);
  box-shadow: 0 0 22px rgba(34, 154, 255, .66);
}
.hall-bg__floor {
  position: absolute; left: -8%; right: -8%; bottom: -20%; height: 65%;
  background:
    repeating-conic-gradient(from 0deg at 50% 0%, rgba(24, 113, 255, .16) 0 1deg, transparent 1.5deg 12deg),
    repeating-radial-gradient(ellipse at 50% 0%, transparent 0 9%, rgba(43, 148, 255, .18) 9.3% 9.7%, transparent 10% 16%),
    radial-gradient(ellipse at 50% 0%, #0a2b61, #030b1c 68%);
  transform: perspective(650px) rotateX(58deg); transform-origin: 50% 0;
  filter: drop-shadow(0 -16px 36px rgba(13, 105, 255, .22));
}
.hall-bg__stars { position: absolute; inset: 14% 10% 25%; }
.hall-bg__stars i { position: absolute; width: 2px; height: 2px; border-radius: 50%; background: #b9edff; box-shadow: 0 0 8px #56c8ff; animation: blue-star 3.8s ease-in-out infinite; }
@keyframes blue-star { 50% { transform: scale(2.2); opacity: 1; } }
.hall-bg__vignette { background: radial-gradient(ellipse 70% 70% at 50% 45%, transparent 42%, rgba(0, 4, 15, .76) 100%); }
.hall-bg__spot { top: -2%; width: 54%; height: 56%; background: radial-gradient(ellipse at 50% 0%, rgba(72, 171, 255, .24), rgba(20, 91, 255, .08) 42%, transparent 72%); }
.hall-bg__magenta { bottom: 21%; width: 42%; height: 34%; background: radial-gradient(ellipse, rgba(50, 164, 255, .24), rgba(255, 189, 75, .08) 38%, transparent 70%); }

.stage { width: min(1120px, 68vw); height: min(88vh, 850px); perspective: 1700px; }
.stage::before { content: ''; position: absolute; left: 50%; top: 9%; width: 58%; height: 65%; transform: translateX(-50%); border-radius: 28px; background: radial-gradient(ellipse, rgba(3, 29, 74, .92), rgba(2, 13, 38, .76) 62%, transparent 78%); filter: blur(2px); }
.arch-glow { bottom: 14%; width: clamp(430px, 39vw, 650px); border-color: rgba(54, 183, 255, .36); box-shadow: 0 0 72px rgba(23, 133, 255, .34), inset 0 0 96px rgba(20, 118, 255, .18); }
.podium-row { bottom: 31%; z-index: 3; gap: clamp(8px, 1vw, 18px); }
.podium--s0, .podium--s4 { display: flex; transform: translateY(18px) scale(.72) translateZ(-180px); opacity: .72; }
.podium--s1 { transform: translateY(4px) scale(.86) translateZ(-90px) rotateY(9deg); }
.podium--s3 { transform: translateY(4px) scale(.86) translateZ(-90px) rotateY(-9deg); }
.podium--center { transform: translateZ(110px); }
.stage-discs { bottom: 2%; z-index: 1; width: min(82%, 900px); opacity: 1; mix-blend-mode: normal; }
.stage-disc--base { background: linear-gradient(180deg, rgba(16, 48, 97, .96), rgba(2, 12, 32, .98)); border-color: rgba(63, 174, 255, .62); box-shadow: 0 0 36px rgba(27, 132, 255, .48), inset 0 12px 24px rgba(102, 196, 255, .16); }
.stage-disc--mid { background: linear-gradient(180deg, rgba(24, 66, 119, .96), rgba(4, 18, 46, .98)); border-color: rgba(255, 202, 94, .55); box-shadow: 0 0 32px rgba(37, 152, 255, .42); }
.stage-disc--top { background: radial-gradient(ellipse, rgba(255, 210, 126, .28), rgba(15, 57, 112, .92) 58%, rgba(2, 17, 46, .98)); border-color: rgba(255, 217, 139, .72); box-shadow: 0 0 38px rgba(255, 183, 68, .22), 0 0 70px rgba(31, 143, 255, .42); }
.stage-crest { z-index: 4; bottom: 13%; background: linear-gradient(180deg, #5b3b12, #19130d); border-color: rgba(255, 213, 132, .76); color: #ffe2a6; box-shadow: 0 0 22px rgba(255, 176, 50, .28); }

.trophy-carousel { position: absolute; inset: 5% -4% 22%; z-index: 3; perspective: 1500px; transform-style: preserve-3d; pointer-events: none; }
.trophy-carousel::before { content: ''; position: absolute; left: 50%; bottom: 1%; width: 88%; height: 35%; transform: translateX(-50%) rotateX(68deg); border: 1px solid rgba(54, 177, 255, .3); border-radius: 50%; box-shadow: 0 0 34px rgba(28, 137, 255, .25), inset 0 0 35px rgba(30, 128, 255, .12); }
.trophy-carousel__item { position: absolute; width: clamp(220px, 17vw, 282px); height: clamp(400px, 55vh, 520px); padding: 0; border: 0; background: transparent; color: #eefaff; pointer-events: auto; cursor: pointer; transform-style: preserve-3d; transition: left .9s cubic-bezier(.22, 1, .36, 1), top .9s cubic-bezier(.22, 1, .36, 1), transform .9s cubic-bezier(.22, 1, .36, 1), opacity .7s ease, filter .7s ease; }
.trophy-carousel__frame { position: absolute; inset: 0 0 72px; display: block; overflow: hidden; border: 1px solid rgba(63, 179, 255, .36); border-radius: 13px; background: linear-gradient(165deg, rgba(7, 43, 88, .9), rgba(2, 17, 46, .94)); box-shadow: 0 18px 38px rgba(0, 5, 24, .48), inset 0 0 34px rgba(25, 130, 255, .09); backdrop-filter: blur(10px); transition: border-color .5s ease, box-shadow .5s ease, background .5s ease; }
.trophy-carousel__frame::before { content: ''; position: absolute; top: -45%; left: -36%; width: 42%; height: 190%; background: linear-gradient(180deg, rgba(184, 235, 255, .18), transparent); transform: rotate(18deg); }
.trophy-carousel__item.is-center .trophy-carousel__frame { border-color: rgba(105, 211, 255, .74); background: linear-gradient(180deg, rgba(5, 39, 86, .98), rgba(1, 14, 42, .98)); box-shadow: 0 0 48px rgba(34, 151, 255, .4), inset 0 0 50px rgba(37, 148, 255, .12); }
.trophy-carousel__svg-wrap { position: absolute; left: 50%; bottom: 4%; z-index: 2; width: 96%; height: 84%; max-width: none; transform: translateX(-50%); filter: drop-shadow(0 18px 20px rgba(0, 4, 18, .58)) drop-shadow(0 0 14px rgba(255, 184, 50, .42)) drop-shadow(0 0 22px rgba(39, 164, 255, .28)); animation: carousel-trophy-float 4.4s ease-in-out infinite; transition: height .6s ease, bottom .6s ease, filter .5s ease; display: flex; align-items: flex-end; justify-content: center; }
.trophy-carousel__svg-wrap :deep(.trophy-svg) { width: 100%; height: 100%; object-fit: contain; display: block; }
.trophy-carousel__item.is-center .trophy-carousel__svg-wrap { bottom: 1%; height: 70%; filter: drop-shadow(0 22px 24px rgba(0, 4, 18, .68)) drop-shadow(0 0 18px rgba(255, 193, 62, .62)) drop-shadow(0 0 34px rgba(42, 174, 255, .42)); }
.trophy-carousel__aura { position: absolute; left: 50%; bottom: 5%; width: 86%; height: 42%; transform: translateX(-50%); border-radius: 50%; background: radial-gradient(ellipse, rgba(56, 186, 255, .28), rgba(255, 194, 64, .1) 38%, transparent 72%); filter: blur(8px); }
.trophy-carousel__meta { position: absolute; left: 14px; right: 14px; top: 16px; z-index: 4; display: grid; justify-items: center; gap: 6px; }
.trophy-carousel__meta strong { font-size: clamp(17px, 1.45vw, 23px); letter-spacing: 2px; text-shadow: 0 0 16px rgba(63, 181, 255, .52); }
.trophy-carousel__meta small { color: #b5d9ef; font-size: 13px; letter-spacing: 3px; }
.trophy-carousel__meta i { margin-top: 3px; padding: 6px 18px; border: 1px solid rgba(72, 192, 255, .58); border-radius: 999px; background: rgba(5, 78, 139, .72); color: #e8faff; font-size: 12px; font-style: normal; }
.trophy-carousel__plate { position: absolute; left: 6%; right: 6%; bottom: 0; min-height: 54px; display: grid; place-content: center; gap: 4px; border: 1px solid rgba(67, 180, 255, .45); border-radius: 9px; background: linear-gradient(180deg, rgba(5, 37, 81, .98), rgba(2, 17, 46, .98)); box-shadow: 0 10px 24px rgba(0, 7, 28, .54), 0 0 16px rgba(39, 151, 255, .14); }
.trophy-carousel__plate b { font-size: 14px; letter-spacing: 1px; white-space: nowrap; }
.trophy-carousel__plate small { color: rgba(165, 211, 236, .68); font-size: 11px; letter-spacing: 1px; }
.trophy-carousel__item.is-center .trophy-carousel__plate { opacity: 0; transform: translateY(8px); pointer-events: none; }
.trophy-carousel__item:hover .trophy-carousel__frame { border-color: #80dcff; box-shadow: 0 0 34px rgba(35, 157, 255, .42), inset 0 0 34px rgba(42, 163, 255, .14); }
@keyframes carousel-trophy-float { 0%, 100% { transform: translateX(-50%) translateY(4px); } 50% { transform: translateX(-50%) translateY(-6px); } }

.wall-back { top: 22px; left: 28px; border-color: rgba(82, 193, 255, .55); background: linear-gradient(180deg, rgba(8, 43, 88, .94), rgba(3, 20, 50, .96)); color: #dff8ff; box-shadow: 0 10px 30px rgba(0, 7, 25, .46), inset 0 1px rgba(255, 255, 255, .1); }
.wall-back:hover { border-color: #7ddfff; background: linear-gradient(180deg, rgba(12, 79, 139, .96), rgba(4, 35, 78, .98)); box-shadow: 0 0 22px rgba(41, 169, 255, .36); }
.wall-title { top: clamp(58px, 7.5vh, 78px); left: clamp(38px, 4.6vw, 78px); }
.wall-title h1 { font-size: clamp(34px, 3.25vw, 52px); background: linear-gradient(135deg, #fff 18%, #c9edff 58%, #63c7ff); -webkit-background-clip: text; background-clip: text; filter: drop-shadow(0 0 20px rgba(64, 174, 255, .45)); }
.wall-title p { color: rgba(178, 226, 255, .84); text-shadow: 0 0 12px rgba(62, 170, 255, .32); }

.stat-panel { left: clamp(28px, 3vw, 52px); top: 50%; width: clamp(174px, 13.2vw, 222px); border-color: rgba(73, 181, 255, .5); border-radius: 10px; background: linear-gradient(160deg, rgba(6, 36, 78, .96), rgba(2, 18, 48, .97)); box-shadow: 0 24px 55px rgba(0, 5, 22, .58), inset 0 0 34px rgba(30, 134, 255, .1); backdrop-filter: blur(14px); }
.stat-panel::before, .stat-panel::after { border-color: rgba(193, 239, 255, .9); filter: drop-shadow(0 0 7px #2cb8ff); }
.sp-item + .sp-item { border-top-color: rgba(79, 181, 255, .18); }
.sp-label { color: rgba(154, 205, 234, .72); }
.sp-value { background: linear-gradient(135deg, #fff 30%, #9edcff 88%); -webkit-background-clip: text; background-clip: text; filter: drop-shadow(0 0 16px rgba(61, 173, 255, .38)); }
.sp-value small { color: #e7f8ff; -webkit-text-fill-color: #e7f8ff; }
.sp-delta { border-color: rgba(255, 193, 72, .52); background: rgba(255, 177, 42, .1); color: #ffc65d; }

.podium-case { border-color: rgba(58, 171, 255, .42); border-radius: 9px; background: linear-gradient(165deg, rgba(8, 45, 91, .94), rgba(2, 19, 50, .97)); box-shadow: inset 0 0 30px rgba(28, 131, 255, .12), 0 18px 34px rgba(0, 5, 24, .55); }
.podium-case::before { background: linear-gradient(180deg, rgba(172, 231, 255, .2), transparent); }
.podium-case:hover, .podium-case:focus-visible { border-color: #72d5ff; box-shadow: inset 0 0 34px rgba(35, 151, 255, .2), 0 0 30px rgba(29, 144, 255, .42); }
.podium-case__trophy { filter: drop-shadow(0 12px 18px rgba(255, 176, 45, .34)) drop-shadow(0 0 9px rgba(68, 177, 255, .28)); }
.podium-case__trophy--real { width: 92%; height: 92%; object-fit: contain; transform-origin: 50% 78%; }
.trophy-side-cycle-enter-active { transition: opacity .38s ease, transform .44s cubic-bezier(.22, 1, .36, 1), filter .44s ease; }
.trophy-side-cycle-leave-active { position: absolute; transition: opacity .25s ease, transform .25s ease, filter .25s ease; }
.trophy-side-cycle-enter-from { opacity: 0; transform: translateY(12px) scale(.82); filter: blur(6px); }
.trophy-side-cycle-leave-to { opacity: 0; transform: translateY(-8px) scale(1.08); filter: blur(5px); }
.podium-plate { border-color: rgba(67, 180, 255, .48); background: linear-gradient(180deg, rgba(5, 37, 81, .98), rgba(2, 17, 46, .98)); box-shadow: 0 10px 24px rgba(0, 7, 28, .56), 0 0 16px rgba(39, 151, 255, .16); }
.podium-plate b { color: #effaff; }
.podium-plate span { color: rgba(167, 213, 238, .7); }

.showcase { width: clamp(270px, 22vw, 354px); padding-top: clamp(18px, 2.2vh, 25px); border-color: rgba(70, 190, 255, .66); border-radius: 10px; background: linear-gradient(180deg, rgba(4, 34, 78, .98), rgba(2, 16, 46, .98) 58%, rgba(4, 31, 72, .98)); box-shadow: 0 0 42px rgba(30, 139, 255, .36), inset 0 0 46px rgba(35, 139, 255, .1); overflow: hidden; }
.showcase:hover { border-color: #91e5ff; box-shadow: 0 0 58px rgba(38, 158, 255, .5), inset 0 0 54px rgba(50, 167, 255, .14); }
.showcase__corner { border-color: #8ae1ff; filter: drop-shadow(0 0 7px #1aa9ff); }
.showcase h3 { color: #f4fbff; text-shadow: 0 0 18px rgba(67, 181, 255, .5); }
.showcase__date { color: #b9dcf2; }
.showcase__btn { border-color: rgba(70, 192, 255, .62); background: linear-gradient(180deg, rgba(9, 91, 155, .78), rgba(3, 52, 105, .85)); color: #eafaff; }
.showcase__btn:hover { background: linear-gradient(135deg, #078fe4, #0758bb); border-color: #b2edff; box-shadow: 0 0 20px rgba(36, 168, 255, .56); }
.showcase__stage-area { min-height: clamp(245px, 34vh, 355px); perspective: 1000px; }
.showcase__stage-area::before { content: ''; position: absolute; inset: 8% 8% 4%; border-radius: 50%; background: radial-gradient(circle at 50% 46%, rgba(56, 190, 255, .22), rgba(18, 92, 255, .08) 42%, transparent 70%); filter: blur(5px); animation: hero-aura 4.5s ease-in-out infinite; }
.showcase__trophy--real { position: relative; z-index: 2; width: auto; height: clamp(245px, 33vh, 350px); max-width: 94%; object-fit: contain; filter: drop-shadow(0 20px 24px rgba(0, 4, 18, .62)) drop-shadow(0 0 14px rgba(255, 184, 49, .5)) drop-shadow(0 0 28px rgba(34, 155, 255, .34)); transform-origin: 50% 78%; animation: real-trophy-float 4.8s ease-in-out infinite; }
.showcase:hover .showcase__trophy--real { filter: drop-shadow(0 24px 28px rgba(0, 4, 18, .68)) drop-shadow(0 0 20px rgba(255, 195, 68, .66)) drop-shadow(0 0 36px rgba(43, 177, 255, .48)); }
.showcase__pedestal { z-index: 1; bottom: 3px; width: 74%; height: 24px; background: radial-gradient(ellipse, rgba(255, 199, 91, .38), rgba(49, 176, 255, .25) 38%, transparent 72%); }
@keyframes real-trophy-float { 0%, 100% { transform: translateY(3px) rotateX(0deg) scale(1); } 50% { transform: translateY(-7px) rotateX(2deg) scale(1.015); } }
@keyframes hero-aura { 50% { transform: scale(1.08); opacity: .72; } }
.showcase__trophy-dots { position: absolute; left: 50%; bottom: 2px; z-index: 5; display: flex; gap: 7px; transform: translateX(-50%); }
.showcase__trophy-dots button { width: 18px; height: 4px; padding: 0; border: 0; border-radius: 999px; background: rgba(91, 173, 224, .36); box-shadow: 0 0 7px rgba(49, 166, 255, .16); cursor: pointer; transition: width .24s ease, background .24s ease, box-shadow .24s ease; }
.showcase__trophy-dots button:hover { background: rgba(137, 220, 255, .8); }
.showcase__trophy-dots button.active { width: 32px; background: linear-gradient(90deg, #2dcaff, #ffd067); box-shadow: 0 0 10px rgba(52, 190, 255, .72); }
.trophy-cycle-enter-active { transition: opacity .46s ease, transform .52s cubic-bezier(.22, 1, .36, 1), filter .52s ease; }
.trophy-cycle-leave-active { position: absolute; transition: opacity .3s ease, transform .3s ease, filter .3s ease; }
.trophy-cycle-enter-from { opacity: 0; transform: translateY(18px) scale(.9) rotateY(-8deg); filter: blur(8px) drop-shadow(0 0 24px rgba(48, 180, 255, .5)); }
.trophy-cycle-leave-to { opacity: 0; transform: translateY(-12px) scale(1.06) rotateY(8deg); filter: blur(7px) drop-shadow(0 0 28px rgba(255, 190, 64, .5)); }

.record-panel { right: clamp(24px, 2.4vw, 42px); top: clamp(94px, 11vh, 118px); bottom: clamp(70px, 9vh, 96px); width: clamp(320px, 22vw, 390px); }
.record-tabs { gap: 4px; margin-bottom: 10px; padding: 5px; border: 1px solid rgba(57, 177, 255, .42); border-radius: 12px 12px 0 0; background: rgba(2, 22, 55, .92); }
.record-tabs__btn { flex: 1; padding: 8px 10px; border-color: transparent; border-radius: 10px; background: transparent; color: rgba(190, 224, 244, .78); }
.record-tabs__btn:hover { color: #eefbff; border-color: rgba(70, 185, 255, .4); }
.record-tabs__btn.active { background: linear-gradient(135deg, #0d9ae9, #0759ba); border-color: rgba(143, 226, 255, .74); color: #fff; box-shadow: 0 0 18px rgba(31, 158, 255, .48), inset 0 1px rgba(255, 255, 255, .18); }
.record-list { padding: 10px; gap: 2px; border-color: rgba(55, 176, 255, .5); border-radius: 0 0 12px 12px; background: linear-gradient(170deg, rgba(3, 31, 72, .97), rgba(1, 15, 42, .98)); box-shadow: 0 22px 48px rgba(0, 5, 24, .58), inset 0 0 34px rgba(27, 129, 255, .08); backdrop-filter: blur(16px); }
.record-list::-webkit-scrollbar-thumb { background: linear-gradient(180deg, rgba(70, 193, 255, .65), rgba(20, 94, 204, .5)); }
.record-row { gap: 13px; padding: 10px 11px; border-radius: 7px; }
.record-row:hover { background: rgba(24, 119, 205, .18); }
.record-row.active { border-color: rgba(72, 193, 255, .44); background: linear-gradient(90deg, rgba(18, 126, 219, .28), rgba(8, 69, 143, .08)); box-shadow: inset 0 0 24px rgba(39, 151, 255, .12); }
.record-row__medal { color: #664108; background: radial-gradient(circle at 35% 28%, #fff3c7, #ffc857 50%, #c0821d 76%, #77470b); box-shadow: 0 0 14px rgba(255, 190, 70, .42), inset 0 0 0 3px rgba(111, 68, 6, .3); }
.record-row__copy b { color: #eef8ff; }
.record-row__copy small { color: rgba(163, 207, 232, .66); }
.record-row__arrow { stroke: rgba(65, 184, 255, .66); }
.record-row:hover .record-row__arrow { stroke: #8ee2ff; }
.record-empty { color: rgba(168, 215, 240, .58); }

.wall-motto { bottom: clamp(15px, 2.2vh, 24px); color: #f3fbff; text-shadow: 0 0 22px rgba(59, 171, 255, .58); }
.wall-motto::after { background: linear-gradient(90deg, transparent, #22caff, transparent); box-shadow: 0 0 12px #22caff; }

.detail-mask { background: rgba(0, 7, 22, .76); backdrop-filter: blur(10px); }
.detail-card { border-color: rgba(66, 186, 255, .55); background: linear-gradient(165deg, rgba(4, 38, 84, .98), rgba(1, 14, 40, .99)); box-shadow: 0 30px 80px rgba(0, 0, 0, .68), 0 0 58px rgba(26, 137, 255, .3); }
.detail-card__close { border-color: rgba(72, 189, 255, .4); background: rgba(4, 39, 83, .82); color: #aee8ff; }
.detail-card__close:hover { border-color: #8de4ff; box-shadow: 0 0 14px rgba(45, 172, 255, .48); }
.detail-card__halo { background: radial-gradient(circle at 50% 42%, rgba(50, 181, 255, .3), rgba(255, 190, 64, .08) 42%, transparent 66%); }
.detail-card h3 { text-shadow: 0 0 18px rgba(63, 180, 255, .5); }
.chip { border-color: rgba(61, 177, 255, .35); background: rgba(7, 58, 112, .48); color: rgba(214, 240, 255, .9); }
.chip--cat { border-color: rgba(68, 192, 255, .58); color: #9ee7ff; }
.detail-card__desc { color: rgba(211, 235, 248, .84); }
.detail-card__evidence { border-color: rgba(55, 174, 255, .22); background: rgba(4, 39, 82, .48); }
.detail-card__evidence li { color: rgba(207, 233, 247, .82); }
.detail-card__evidence li + li { border-top-color: rgba(65, 177, 255, .14); }
.detail-btn { border-color: rgba(66, 183, 255, .42); background: rgba(6, 58, 113, .68); color: #dff7ff; }
.detail-btn:hover { border-color: #8ce2ff; box-shadow: 0 0 16px rgba(41, 165, 255, .4); }
.detail-btn--primary { background: linear-gradient(135deg, #109fe9, #0757b9); }
.detail-btn--primary:hover { box-shadow: 0 0 22px rgba(35, 161, 255, .58); }
.wall-toast { border-color: rgba(68, 187, 255, .5); background: rgba(3, 34, 76, .96); box-shadow: 0 0 26px rgba(34, 155, 255, .4); color: #e7f9ff; }

@media (max-width: 1500px) {
  .podium--s0, .podium--s4 { display: none; }
  .stage { width: min(980px, 64vw); }
}
@media (max-width: 1180px) {
  .stat-panel { display: none; }
  .stage { left: 36%; width: 66vw; }
  .record-panel { width: min(350px, 31vw); }
}
@media (max-width: 860px) {
  .stage { left: 50%; top: 80px; bottom: auto; width: 100vw; height: 68vh; }
  .record-panel { top: auto; bottom: 18px; left: 12px; right: 12px; width: auto; height: 32vh; }
  .record-tabs { border-radius: 10px; }
  .record-list { border-radius: 10px; }
  .wall-title { top: 64px; left: 20px; }
  .wall-title p { display: none; }
  .showcase { width: min(300px, 78vw); }
  .showcase__stage-area { min-height: 220px; }
  .showcase__trophy--real { height: 230px; }
}
</style>
