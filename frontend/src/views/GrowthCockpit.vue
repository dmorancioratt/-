<template>
  <div class="growth-cockpit">
    <div class="gc-page-header">
      <h1 class="gc-page-title">个人成长驾驶舱</h1>
      <p class="gc-page-subtitle">探索能力边界 · 成就职业未来</p>
    </div>
    <div class="gc-content">
      <div class="gc-left">
        <div class="gc-card match-card animate-card" style="--delay:0.1s">
          <div class="card-corner card-corner-tl"></div>
          <div class="card-corner card-corner-tr"></div>
          <div class="card-corner card-corner-bl"></div>
          <div class="card-corner card-corner-br"></div>
          <div class="card-border-glow"></div>
          <div class="card-scan"></div>
          <div class="card-header">
            <h3><span class="header-bar"></span>目标岗位匹配度</h3>
          </div>
          <div class="match-role">
            <div class="role-name">{{ targetRole.name }}</div>
            <div class="role-meta">{{ targetRole.level }} · {{ targetRole.city }}</div>
          </div>
          <div class="match-circle-wrap">
            <div class="match-circle-outer-glow"></div>
            <svg class="match-circle" viewBox="0 0 200 200">
              <defs>
                <linearGradient id="matchGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#4ed8ff"/>
                  <stop offset="30%" stop-color="#00ffff"/>
                  <stop offset="70%" stop-color="#7c3aed"/>
                  <stop offset="100%" stop-color="#4ed8ff"/>
                </linearGradient>
                <filter id="matchGlow">
                  <feGaussianBlur stdDeviation="6" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
                <filter id="matchNumGlow">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
                </filter>
              </defs>
              <circle cx="100" cy="100" r="88" fill="none" stroke="rgba(78,216,255,0.03)" stroke-width="2"/>
              <circle cx="100" cy="100" r="82" fill="none" stroke="rgba(78,216,255,0.08)" stroke-width="10" stroke-dasharray="2 6"/>
              <circle cx="100" cy="100" r="72" fill="none" stroke="rgba(78,216,255,0.05)" stroke-width="1"/>
              <circle cx="100" cy="100" r="82" fill="none" stroke="url(#matchGrad)" stroke-width="10" stroke-linecap="round"
                :stroke-dasharray="matchDash" stroke-dashoffset="0" transform="rotate(-90 100 100)" filter="url(#matchGlow)" class="match-progress-circle"/>
              <g v-for="i in 36" :key="'tick'+i">
                <line :x1="100 + Math.cos((i*10-90)*Math.PI/180)*88" :y1="100 + Math.sin((i*10-90)*Math.PI/180)*88"
                  :x2="100 + Math.cos((i*10-90)*Math.PI/180)*(i%3===0?92:90)" :y2="100 + Math.sin((i*10-90)*Math.PI/180)*(i%3===0?92:90)"
                  :stroke="i%3===0?'rgba(78,216,255,0.4)':'rgba(78,216,255,0.2)'" stroke-width="1"/>
              </g>
            </svg>
            <div class="match-num">
              <span class="num-big" filter="url(#matchNumGlow)">{{ targetRole.score }}</span>
              <span class="num-pct">%</span>
              <span class="num-label">综合匹配度</span>
              <div class="num-particles">
                <span v-for="n in 8" :key="'np'+n" class="num-particle" :style="{delay: n*0.3+'s', angle: n*45+'deg'}"></span>
              </div>
            </div>
          </div>
          <div class="match-trend up">
            <span class="trend-arrow">↑</span>
            <span class="trend-val">{{ targetRole.improve }}%</span>
            <label>较上次提升</label>
          </div>
        </div>

        <div class="gc-card radar-card animate-card" style="--delay:0.2s">
          <div class="card-corner card-corner-tl"></div>
          <div class="card-corner card-corner-tr"></div>
          <div class="card-corner card-corner-bl"></div>
          <div class="card-corner card-corner-br"></div>
          <div class="card-border-glow"></div>
          <div class="card-scan"></div>
          <div class="card-header">
            <h3><span class="header-bar"></span>能力雷达</h3>
          </div>
          <svg class="radar-chart" viewBox="0 0 240 240">
            <defs>
              <filter id="radarGlow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
              </filter>
              <radialGradient id="radarBg" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="rgba(78,216,255,0.08)"/>
                <stop offset="100%" stop-color="transparent"/>
              </radialGradient>
            </defs>
            <circle cx="120" cy="120" r="100" fill="url(#radarBg)"/>
            <g v-for="n in 5" :key="'grid'+n">
              <polygon :points="hexPoints(240, 240, 25 + n*18)" fill="none" :stroke="n===5?'rgba(78,216,255,0.2)':'rgba(78,216,255,0.06)'" stroke-width="1"/>
            </g>
            <line v-for="(axis, i) in radarAxes" :key="'axis'+i" 
              x1="120" y1="120" :x2="axis.x" :y2="axis.y" stroke="rgba(78,216,255,0.12)" stroke-width="1"/>
            <polygon :points="requiredRadarPoints" fill="rgba(255,182,92,0.04)" stroke="rgba(255,182,92,0.3)" stroke-width="1.5" stroke-dasharray="4,3"/>
            <polygon :points="currentRadarPoints" fill="rgba(78,216,255,0.15)" stroke="#4ed8ff" stroke-width="2.5" filter="url(#radarGlow)" class="radar-polygon-anim"/>
            <circle v-for="(p, i) in currentRadarPointsArr" :key="'pt'+i" :cx="p.x" :cy="p.y" r="6" fill="#061830" stroke="#4ed8ff" stroke-width="2" filter="url(#radarGlow)"/>
            <circle v-for="(p, i) in currentRadarPointsArr" :key="'pt-core'+i" :cx="p.x" :cy="p.y" r="2.5" fill="#4ed8ff"/>
            <text v-for="(axis, i) in radarAxes" :key="'label'+i" :x="axis.lx" :y="axis.ly" fill="#8fa4c0" font-size="11" text-anchor="middle" font-weight="500">{{ radarLabels[i] }}</text>
            <text v-for="(v, i) in radarVals" :key="'val'+i" :x="currentRadarPointsArr[i].x" :y="currentRadarPointsArr[i].y - 14" fill="#4ed8ff" font-size="11" text-anchor="middle" font-weight="700" filter="url(#radarGlow)">{{ v }}</text>
          </svg>
          <div class="radar-legend">
            <span class="lg-item"><i style="background:#4ed8ff;box-shadow:0 0 8px #4ed8ff"></i>当前水平</span>
            <span class="lg-item"><i style="border-color:rgba(255,182,92,0.7)"></i>岗位要求</span>
          </div>
        </div>

        <div class="gc-card resume-card animate-card" style="--delay:0.3s">
          <div class="card-corner card-corner-tl"></div>
          <div class="card-corner card-corner-tr"></div>
          <div class="card-corner card-corner-bl"></div>
          <div class="card-corner card-corner-br"></div>
          <div class="card-border-glow"></div>
          <div class="card-scan"></div>
          <div class="card-header">
            <h3><span class="header-bar"></span>简历解析</h3>
            <span class="resume-score">{{ resume.score }}<em>分</em><label>{{ resume.grade }}</label></span>
          </div>
          <div class="resume-meta">最近更新：{{ resume.updatedAt }}</div>
          <div class="resume-desc">{{ resume.comment }}</div>
          <button class="resume-detail">
            <span>查看详情</span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
          </button>
        </div>
      </div>

      <div class="gc-center">
        <div class="galaxy-card animate-card" style="--delay:0.15s">
          <div class="card-corner card-corner-tl"></div>
          <div class="card-corner card-corner-tr"></div>
          <div class="card-corner card-corner-bl"></div>
          <div class="card-corner card-corner-br"></div>
          <div class="card-border-glow galaxy-border-glow"></div>
          <div class="galaxy-header">
            <div>
              <h2><span class="title-deco"></span>我的能力星系</h2>
              <p>点击探索技能详情与成长建议</p>
            </div>
            <div class="galaxy-stats">
              <span><strong>{{ galaxySkills.filter(s=>s.status==='mastered').length }}</strong> 已掌握</span>
              <span><strong>{{ galaxySkills.length }}</strong> 技能点</span>
            </div>
          </div>
          <div class="galaxy-scene" ref="galaxyRef">
            <div class="galaxy-bg-radial"></div>
            <div class="galaxy-bg">
              <div v-for="s in 50" :key="'gstar'+s" class="star" :class="{'star-bright': s%20===0}" :style="starStyle(s)"></div>
            </div>
            <div class="orbit-ring orbit-ring-1"></div>
            <div class="orbit-ring orbit-ring-2"></div>
            <div class="orbit-ring orbit-ring-3"></div>
            <div class="core-user">
              <div class="core-shockwave"></div>
              <div class="core-energy-ring core-energy-ring-1"></div>
              <div class="core-energy-ring core-energy-ring-2"></div>
              <div class="core-glow-outer"></div>
              <div class="core-glow"></div>
              <div class="core-glow-inner"></div>
              <div class="core-avatar-ring"></div>
              <div class="core-avatar">{{ user.name.charAt(0) }}</div>
              <div class="core-info">
                <div class="core-name">{{ user.name }}</div>
                <div class="core-meta">{{ user.edu }}</div>
              </div>
            </div>
            <div v-for="(skill, i) in galaxySkills" :key="skill.name" 
              class="skill-node" :class="[skill.status, {'pulse-node': i%5===0, 'big-node': skill.level>=15}]"
              :style="skillPosStyle(i, galaxySkills.length)"
              @click="selectSkill(skill)">
              <div class="node-bg"></div>
              <div class="node-ring"></div>
              <div class="node-pulse"></div>
              <div class="node-short">{{ skill.short }}</div>
              <div class="node-label">{{ skill.name }}</div>
            </div>
            <div v-if="selectedSkill" class="skill-tip" :style="tipPosStyle(selectedSkill)">
              <div class="tip-arrow"></div>
              <div class="tip-inner">
                <div class="tip-header">
                  <span class="tip-status-dot" :class="selectedSkill.status"></span>
                  <span class="tip-name">{{ selectedSkill.name }}</span>
                </div>
                <div class="tip-cat">{{ selectedSkill.category }}</div>
                <div class="tip-level-row">
                  <span class="tip-level-val">Lv.{{ selectedSkill.level }}</span>
                  <div class="tip-bar"><div class="tip-bar-fill" :class="selectedSkill.status" :style="{width: selectedSkill.level*5+'%'}"></div></div>
                </div>
              </div>
            </div>
          </div>
          <div class="galaxy-legend">
            <span class="gl-item mastered"><i></i>已掌握</span>
            <span class="gl-item improve"><i></i>待提升</span>
            <span class="gl-item missing"><i></i>缺失</span>
            <span class="gl-item transfer"><i></i>可迁移</span>
          </div>
        </div>

        <div class="learning-path-wrap animate-card" style="--delay:0.35s">
          <div class="card-corner card-corner-tl"></div>
          <div class="card-corner card-corner-tr"></div>
          <div class="card-corner card-corner-bl"></div>
          <div class="card-corner card-corner-br"></div>
          <div class="card-border-glow"></div>
          <div class="lp-header">
            <h2><span class="title-deco"></span>学习路径</h2>
            <p>登山式成长轨迹 · 你的专属攀登计划</p>
          </div>
          <div class="lp-mountain">
            <svg class="lp-svg" viewBox="0 0 1000 320" preserveAspectRatio="none">
              <defs>
                <linearGradient id="mtnGrad1" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="rgba(26,74,122,0.6)"/>
                  <stop offset="100%" stop-color="rgba(8,26,53,0.3)"/>
                </linearGradient>
                <linearGradient id="mtnGrad2" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="rgba(42,106,170,0.5)"/>
                  <stop offset="100%" stop-color="rgba(10,42,85,0.2)"/>
                </linearGradient>
                <linearGradient id="pathGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#4ed8ff"/>
                  <stop offset="20%" stop-color="#00ffff"/>
                  <stop offset="45%" stop-color="#4ed8ff"/>
                  <stop offset="55%" stop-color="#ffb65c"/>
                  <stop offset="80%" stop-color="#ff7088"/>
                  <stop offset="100%" stop-color="#8f7cff"/>
                </linearGradient>
                <filter id="pathGlow">
                  <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                  <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
                </filter>
              </defs>
              <path d="M0,320 L0,260 L80,220 L160,240 L240,180 L320,200 L400,140 L480,160 L560,100 L640,120 L720,70 L800,90 L880,50 L960,70 L1000,40 L1000,320 Z" fill="url(#mtnGrad2)"/>
              <path d="M0,320 L0,280 L100,250 L200,270 L300,210 L400,230 L500,170 L600,190 L700,130 L800,150 L900,100 L1000,120 L1000,320 Z" fill="url(#mtnGrad1)"/>
              <path d="M0,320 L0,290 L200,275 L400,250 L600,220 L800,180 L1000,150 L1000,320 Z" fill="rgba(7,20,40,0.8)"/>
              <path class="lp-path" d="M50,290 C150,270 200,250 300,230 S450,180 500,170 S650,130 700,110 S850,70 950,50" fill="none" stroke="url(#pathGrad)" stroke-width="4" stroke-linecap="round" filter="url(#pathGlow)" stroke-dasharray="2000" stroke-dashoffset="0"/>
              <path class="lp-path-glow" d="M50,290 C150,270 200,250 300,230 S450,180 500,170 S650,130 700,110 S850,70 950,50" fill="none" stroke="url(#pathGrad)" stroke-width="8" stroke-linecap="round" opacity="0.3" filter="url(#pathGlow)"/>
            </svg>
            <div v-for="(stop, i) in learningStops" :key="stop.name" class="lp-stop" :class="{done: stop.done, current: stop.current, locked: !stop.done && !stop.current}" :style="{left: stop.x+'%', bottom: stop.y+'%'}">
              <div class="stop-pulse" v-if="stop.current"></div>
              <div class="stop-glow"></div>
              <div class="stop-dot">{{ i+1 }}</div>
              <div class="stop-label">{{ stop.name }}</div>
            </div>
            <div class="lp-current-pos">
              <div class="pos-ping"></div>
              <div class="pos-dot"></div>
              <div class="pos-label">当前位置</div>
            </div>
          </div>
        </div>
      </div>

      <div class="gc-right">
        <div class="gc-card next-action animate-card" style="--delay:0.12s">
          <div class="card-corner card-corner-tl"></div>
          <div class="card-corner card-corner-tr"></div>
          <div class="card-corner card-corner-bl"></div>
          <div class="card-corner card-corner-br"></div>
          <div class="card-border-glow action-glow"></div>
          <div class="card-scan"></div>
          <div class="card-header">
            <h3><span class="header-bar"></span>下一步行动</h3>
            <span class="action-badge">AI推荐</span>
          </div>
          <div class="action-priority">
            <span class="prio-label">优先级</span>
            <span class="prio-high">最高</span>
          </div>
          <div class="action-title">{{ nextAction.title }}</div>
          <div class="action-desc">{{ nextAction.desc }}</div>
          <div class="action-meta">
            <div class="meta-item">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              {{ nextAction.duration }}
            </div>
            <div class="meta-item">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              预计提升 {{ nextAction.impact }}%
            </div>
          </div>
          <button class="action-start">
            <span class="btn-shine"></span>
            <span class="btn-text">立即开始</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
          </button>
        </div>

        <div class="gc-card plan-card animate-card" style="--delay:0.22s">
          <div class="card-corner card-corner-tl"></div>
          <div class="card-corner card-corner-tr"></div>
          <div class="card-corner card-corner-bl"></div>
          <div class="card-corner card-corner-br"></div>
          <div class="card-border-glow"></div>
          <div class="card-scan"></div>
          <div class="card-header">
            <h3><span class="header-bar"></span>本周成长计划</h3>
            <span class="progress-label">{{ weekPlan.done }}/{{ weekPlan.total }}</span>
          </div>
          <div class="plan-progress">
            <div class="pp-bar"><div class="pp-fill" :style="{width: (weekPlan.done/weekPlan.total*100)+'%'}"></div></div>
          </div>
          <div class="plan-list">
            <div v-for="item in weekPlan.items" :key="item.title" class="plan-item" :class="{done: item.done}">
              <div class="pi-check">
                <svg v-if="item.done" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#061830" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
              </div>
              <div class="pi-content">
                <div class="pi-title">{{ item.title }}</div>
                <div class="pi-time">{{ item.time }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="gc-card interview-card animate-card" style="--delay:0.28s">
          <div class="card-corner card-corner-tl"></div>
          <div class="card-corner card-corner-tr"></div>
          <div class="card-corner card-corner-bl"></div>
          <div class="card-corner card-corner-br"></div>
          <div class="card-border-glow"></div>
          <div class="card-scan"></div>
          <div class="card-header">
            <h3><span class="header-bar"></span>模拟面试</h3>
            <span class="interview-trend up">↑{{ interview.improve }}%</span>
          </div>
          <div class="interview-score-wrap">
            <div class="is-glow"></div>
            <div class="is-num">{{ interview.score }}</div>
            <div class="is-label">综合得分</div>
          </div>
          <div class="interview-stats">
            <div class="stat-item">
              <div class="stat-val" style="color:#37d6a5">{{ interview.correctRate }}%</div>
              <div class="stat-lbl">正确率</div>
            </div>
            <div class="stat-item">
              <div class="stat-val" style="color:#4ed8ff">{{ interview.avgTime }}s</div>
              <div class="stat-lbl">平均用时</div>
            </div>
            <div class="stat-item">
              <div class="stat-val" style="color:#ffb65c">{{ interview.count }}</div>
              <div class="stat-lbl">已完成</div>
            </div>
          </div>
          <button class="interview-btn">开始新面试 ></button>
        </div>

        <div class="gc-card timeline-card animate-card" style="--delay:0.38s">
          <div class="card-corner card-corner-tl"></div>
          <div class="card-corner card-corner-tr"></div>
          <div class="card-corner card-corner-bl"></div>
          <div class="card-corner card-corner-br"></div>
          <div class="card-border-glow"></div>
          <div class="card-header">
            <h3><span class="header-bar"></span>成长时间线</h3>
          </div>
          <div class="timeline">
            <div v-for="(item, i) in timeline" :key="item.date" class="tl-item" :class="{first: i===0}">
              <div class="tl-dot"></div>
              <div class="tl-line" v-if="i < timeline.length-1"></div>
              <div class="tl-content">
                <div class="tl-date">{{ item.date }}</div>
                <div class="tl-text">{{ item.text }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const activeTab = ref('overview')

const navTabs = [
  { id: 'overview', name: '概览', icon: '📊' },
  { id: 'value', name: '个人价值成长仓', icon: '💎' },
  { id: 'match', name: '人岗匹配', icon: '🎯' },
  { id: 'ai', name: 'AI互动', icon: '🤖' },
  { id: 'settings', name: '设置', icon: '⚙️' }
]

const user = { name: '张同学', edu: '计算机科学与技术 · 大三', targetRole: 'AI算法工程师' }
const targetRole = { name: 'AI算法工程师', level: '中级', city: '北京', score: 72, improve: 4 }
const resume = { score: 85, grade: '优秀', updatedAt: '2天前', comment: '简历结构清晰，项目经历突出，建议补充量化成果和技术栈深度描述。' }
const nextAction = { title: '深入学习RAG知识库问答系统', desc: '掌握检索增强生成核心技术，完成一个端到端的问答项目', duration: '预计14天', impact: 8 }
const weekPlan = { done: 3, total: 5, items: [
  { title: '完成Transformer架构学习', time: '周一', done: true },
  { title: '动手实现Attention机制', time: '周二', done: true },
  { title: '学习向量数据库Milvus', time: '周三', done: true },
  { title: '完成RAG项目demo', time: '周四', done: false },
  { title: '撰写技术博客总结', time: '周五', done: false }
]}
const interview = { score: 78, improve: 12, correctRate: 72, avgTime: 45, count: 15 }
const timeline = [
  { date: '08-12', text: '完成深度学习基础课程，掌握CNN/RNN核心原理' },
  { date: '08-08', text: 'Python编程技能达到Lv.15，进入熟练阶段' },
  { date: '08-01', text: '匹配度提升4%，算法基础能力显著增强' }
]

const radarVals = [80, 65, 55, 70, 60, 75]
const radarLabels = ['算法', '编程', '工程', '数学', '沟通', '业务']
const radarAxes = computed(() => {
  const pts: any[] = []
  for (let i = 0; i < 6; i++) {
    const angle = (i * 60 - 90) * Math.PI / 180
    pts.push({ x: 120 + Math.cos(angle) * 100, y: 120 + Math.sin(angle) * 100, lx: 120 + Math.cos(angle) * 115, ly: 120 + Math.sin(angle) * 115 + 4 })
  }
  return pts
})

function hexPoints(cx: number, cy: number, r: number) {
  return radarAxes.value.map(a => `${cx + (a.x-cx)/100*r},${cy + (a.y-cy)/100*r}`).join(' ')
}
function radarPoints(vals: number[]) {
  return vals.map((v, i) => {
    const angle = (i * 60 - 90) * Math.PI / 180
    const r = v
    return `${120 + Math.cos(angle) * r},${120 + Math.sin(angle) * r}`
  }).join(' ')
}
function radarPointsArr(vals: number[]) {
  return vals.map((v, i) => {
    const angle = (i * 60 - 90) * Math.PI / 180
    return { x: 120 + Math.cos(angle) * v, y: 120 + Math.sin(angle) * v }
  })
}
const currentRadarPoints = computed(() => radarPoints(radarVals))
const requiredRadarPoints = computed(() => radarPoints([85,80,75,80,70,75]))
const currentRadarPointsArr = computed(() => radarPointsArr(radarVals))
const matchDash = computed(() => `${targetRole.score * 5.15} ${515 - targetRole.score * 5.15}`)

const galaxySkills = ref([
  { name: 'Python', short: 'Py', level: 18, status: 'mastered', category: '编程语言' },
  { name: '机器学习', short: 'ML', level: 16, status: 'mastered', category: 'AI核心' },
  { name: '深度学习', short: 'DL', level: 14, status: 'improve', category: 'AI核心' },
  { name: 'PyTorch', short: 'PT', level: 15, status: 'mastered', category: '框架工具' },
  { name: 'NLP', short: 'NLP', level: 12, status: 'improve', category: 'AI领域' },
  { name: 'CV', short: 'CV', level: 10, status: 'improve', category: 'AI领域' },
  { name: 'TensorFlow', short: 'TF', level: 11, status: 'transfer', category: '框架工具' },
  { name: 'RAG', short: 'RAG', level: 6, status: 'missing', category: '前沿技术' },
  { name: 'LangChain', short: 'LC', level: 5, status: 'missing', category: '前沿技术' },
  { name: '向量数据库', short: 'VDB', level: 8, status: 'improve', category: '工程能力' },
  { name: '数据结构', short: 'DS', level: 17, status: 'mastered', category: '计算机基础' },
  { name: 'SQL', short: 'SQL', level: 14, status: 'mastered', category: '工程能力' },
  { name: 'Linux', short: 'LX', level: 13, status: 'improve', category: '工程能力' },
  { name: 'Git', short: 'Git', level: 15, status: 'mastered', category: '工程能力' },
  { name: 'Docker', short: 'Doc', level: 9, status: 'improve', category: '工程能力' },
  { name: '算法', short: 'Alg', level: 16, status: 'mastered', category: '计算机基础' },
  { name: '大模型', short: 'LLM', level: 7, status: 'missing', category: '前沿技术' },
  { name: 'Prompt工程', short: 'PR', level: 11, status: 'transfer', category: '前沿技术' },
  { name: 'MLOps', short: 'MLO', level: 6, status: 'missing', category: '工程能力' },
  { name: '统计学', short: 'Sta', level: 13, status: 'improve', category: '数学基础' },
])
const selectedSkill = ref<any>(null)

function skillPosStyle(i: number, total: number) {
  const layerCount = [6, 7, 7]
  const layerRadii = [90, 145, 195]
  let layer = 0
  let idxInLayer = i
  for (let l = 0; l < layerCount.length; l++) {
    if (idxInLayer < layerCount[l]) { layer = l; break }
    idxInLayer -= layerCount[l]
  }
  const count = layerCount[layer]
  const angle = (idxInLayer / count) * Math.PI * 2 - Math.PI / 2 + (layer * 0.25)
  const r = layerRadii[layer]
  const x = Math.cos(angle) * r
  const y = Math.sin(angle) * r
  return { '--x': `${x}px`, '--y': `${y}px` } as any
}

function connectorStyle(i: number, total: number) {
  return {} as any
}

function tipPosStyle(skill: any) {
  const i = galaxySkills.value.indexOf(skill)
  const layerCount = [6, 7, 7]
  const layerRadii = [90, 145, 195]
  let layer = 0
  let idxInLayer = i
  for (let l = 0; l < layerCount.length; l++) {
    if (idxInLayer < layerCount[l]) { layer = l; break }
    idxInLayer -= layerCount[l]
  }
  const count = layerCount[layer]
  const angle = (idxInLayer / count) * Math.PI * 2 - Math.PI / 2 + (layer * 0.25)
  const r = layerRadii[layer] + 55
  let x = Math.cos(angle) * r
  let y = Math.sin(angle) * r
  return { left: `calc(50% + ${x}px)`, top: `calc(50% + ${y}px - 50px)` }
}

function selectSkill(skill: any) { selectedSkill.value = skill }

function bgParticleStyle(s: number) {
  const size = 1 + (s%2)*0.5
  return {
    left: (Math.sin(s * 127.1) * 0.5 + 0.5) * 100 + '%',
    top: (Math.cos(s * 311.7) * 0.5 + 0.5) * 100 + '%',
    width: size + 'px',
    height: size + 'px',
    animationDelay: (s * 0.2) % 10 + 's',
    animationDuration: (8 + (s%6)) + 's'
  } as any
}

function orbStyle(o: number) {
  const colors = ['rgba(78,216,255,0.08)', 'rgba(143,124,255,0.06)', 'rgba(0,255,255,0.05)', 'rgba(55,214,165,0.06)', 'rgba(255,182,92,0.05)', 'rgba(78,216,255,0.07)']
  return {
    left: (10 + o*15) + '%',
    top: (15 + (o%3)*25) + '%',
    width: (200 + o*80) + 'px',
    height: (200 + o*80) + 'px',
    background: `radial-gradient(circle, ${colors[o-1]} 0%, transparent 70%)`,
    animationDelay: o*2 + 's',
    animationDuration: (10 + o*3) + 's'
  } as any
}

function starStyle(s: number) {
  return {
    left: (Math.sin(s * 73.3) * 0.5 + 0.5) * 100 + '%',
    top: (Math.cos(s * 197.7) * 0.5 + 0.5) * 100 + '%',
    animationDelay: (s * 0.07) % 5 + 's',
    animationDuration: (2 + (s%3)) + 's'
  } as any
}

const learningStops = [
  { name: '基础巩固', x: 8, y: 12, done: true, current: false },
  { name: '算法进阶', x: 25, y: 28, done: true, current: false },
  { name: 'ML实战', x: 42, y: 45, done: true, current: false },
  { name: 'DL专精', x: 58, y: 58, done: false, current: true },
  { name: '大模型', x: 75, y: 72, done: false, current: false },
  { name: '就业准备', x: 92, y: 88, done: false, current: false }
]

onMounted(() => {
  setTimeout(() => { if (!selectedSkill.value) selectSkill(galaxySkills.value[7]) }, 800)
})
</script>

<style scoped>
.growth-cockpit {
  width: 100%;
  min-height: 100vh;
  background: transparent;
  color: #e8f4ff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  overflow-x: hidden;
  position: relative;
}

.gc-page-header {
  position: relative;
  z-index: 10;
  text-align: center;
  padding: 24px 24px 8px;
}
.gc-page-title {
  margin: 0;
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #ffffff 0%, #4ed8ff 50%, #8f7cff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 2px;
  text-shadow: 0 0 30px rgba(78,216,255,0.3);
}
.gc-page-subtitle {
  margin: 6px 0 0;
  font-size: 13px;
  color: rgba(168,180,200,0.7);
  letter-spacing: 3px;
}

.gc-content {
  position: relative;
  z-index: 10;
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  gap: 16px;
  padding: 16px 20px 30px;
  max-width: 1920px;
  margin: 0 auto;
}
.gc-left, .gc-center, .gc-right { display: flex; flex-direction: column; gap: 14px; min-width: 0; }

.gc-card {
  position: relative;
  background: linear-gradient(180deg, rgba(8,20,45,0.45) 0%, rgba(5,12,30,0.55) 100%);
  border: 1px solid rgba(78,216,255,0.12);
  border-radius: 12px;
  padding: 16px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  overflow: hidden;
  transition: all 0.3s ease;
}
.gc-card:hover {
  border-color: rgba(78,216,255,0.25);
  box-shadow: 0 8px 32px rgba(0,0,0,0.3), 0 0 0 1px rgba(78,216,255,0.08);
  transform: translateY(-2px);
}

.card-corner {
  position: absolute;
  width: 12px;
  height: 12px;
  border-color: rgba(78,216,255,0.4);
  z-index: 5;
}
.card-corner-tl { top: 6px; left: 6px; border-top: 1.5px solid; border-left: 1.5px solid; border-radius: 3px 0 0 0; }
.card-corner-tr { top: 6px; right: 6px; border-top: 1.5px solid; border-right: 1.5px solid; border-radius: 0 3px 0 0; }
.card-corner-bl { bottom: 6px; left: 6px; border-bottom: 1.5px solid; border-left: 1.5px solid; border-radius: 0 0 0 3px; }
.card-corner-br { bottom: 6px; right: 6px; border-bottom: 1.5px solid; border-right: 1.5px solid; border-radius: 0 0 3px 0; }

.card-border-glow {
  position: absolute;
  inset: 0;
  border-radius: 14px;
  padding: 1px;
  background: linear-gradient(135deg, transparent 30%, rgba(78,216,255,0.15) 50%, transparent 70%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  animation: borderGlowRotate 6s linear infinite;
  opacity: 0.6;
}
.galaxy-border-glow { opacity: 1; }
.action-glow { background: linear-gradient(135deg, transparent 20%, rgba(78,216,255,0.25) 50%, rgba(143,124,255,0.15) 70%, transparent 90%); }
@keyframes borderGlowRotate {
  0% { background-position: 0% 0%; }
  100% { background-position: 200% 200%; }
}

.card-scan {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(78,216,255,0.03), transparent);
  animation: cardScan 8s ease-in-out infinite;
  pointer-events: none;
}
@keyframes cardScan {
  0%, 100% { left: -100%; }
  50% { left: 100%; }
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.card-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #c8d8ee;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 0.3px;
}
.header-bar {
  width: 3px;
  height: 14px;
  background: linear-gradient(180deg, #4ed8ff, #8f7cff);
  border-radius: 2px;
  box-shadow: 0 0 6px rgba(78,216,255,0.5);
}
.title-deco {
  width: 18px;
  height: 18px;
  background: conic-gradient(from 0deg, transparent, #4ed8ff, transparent, #8f7cff, transparent);
  border-radius: 3px;
  animation: titleDecoSpin 4s linear infinite;
  opacity: 0.7;
}
@keyframes titleDecoSpin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.animate-card {
  opacity: 0;
  transform: translateY(20px);
  animation: cardEnter 0.7s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  animation-delay: var(--delay);
}
@keyframes cardEnter {
  to { opacity: 1; transform: translateY(0); }
}

.match-role { margin-bottom: 12px; }
.role-name { font-size: 18px; font-weight: 700; color: #fff; text-shadow: 0 0 20px rgba(78,216,255,0.3); }
.role-meta { font-size: 12px; color: rgba(168,180,200,0.7); margin-top: 3px; }

.match-circle-wrap {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 0 auto 12px;
}
.match-circle-outer-glow {
  position: absolute;
  inset: -20px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(78,216,255,0.08) 0%, transparent 60%);
  animation: matchOuterGlow 3s ease-in-out infinite;
}
@keyframes matchOuterGlow {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}
.match-circle { width: 100%; height: 100%; }
.match-progress-circle {
  animation: progressReveal 2s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}
@keyframes progressReveal {
  from { stroke-dashoffset: 515; }
}
.match-num {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.num-big {
  font-size: 56px;
  font-weight: 900;
  background: linear-gradient(180deg, #ffffff 0%, #00f5ff 40%, #4ed8ff 70%, #8f7cff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  filter: drop-shadow(0 0 20px rgba(0,245,255,0.6)) drop-shadow(0 0 40px rgba(78,216,255,0.3));
  animation: numGlow 2s ease-in-out infinite;
}
@keyframes numGlow {
  0%, 100% { filter: drop-shadow(0 0 15px rgba(0,245,255,0.5)) drop-shadow(0 0 30px rgba(78,216,255,0.2)); }
  50% { filter: drop-shadow(0 0 30px rgba(0,245,255,0.8)) drop-shadow(0 0 60px rgba(78,216,255,0.5)); }
}
.num-pct { font-size: 20px; font-weight: 600; color: #4ed8ff; margin-left: 2px; margin-top: 8px; }
.num-label { font-size: 11px; color: rgba(168,180,200,0.7); margin-top: 4px; letter-spacing: 1px; }
.num-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.num-particle {
  position: absolute;
  width: 3px;
  height: 3px;
  background: #4ed8ff;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  animation: numParticleBurst 3s ease-out infinite;
  animation-delay: var(--delay);
  box-shadow: 0 0 6px #4ed8ff;
}
@keyframes numParticleBurst {
  0% { transform: translate(-50%,-50%) rotate(var(--angle)) translateY(30px) scale(0); opacity: 0; }
  20% { opacity: 1; }
  100% { transform: translate(-50%,-50%) rotate(var(--angle)) translateY(70px) scale(0); opacity: 0; }
}
.match-trend {
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: center;
  padding: 8px;
  background: rgba(55,214,165,0.08);
  border-radius: 8px;
  border: 1px solid rgba(55,214,165,0.15);
}
.match-trend.up { color: #37d6a5; }
.trend-arrow { font-size: 14px; font-weight: 700; }
.trend-val { font-size: 15px; font-weight: 700; }
.match-trend label { font-size: 11px; color: rgba(168,180,200,0.7); font-weight: 400; }

.radar-chart { width: 100%; max-width: 260px; margin: 0 auto; }
.radar-polygon-anim { animation: radarPulse 4s ease-in-out infinite; }
@keyframes radarPulse {
  0%, 100% { opacity: 0.9; }
  50% { opacity: 1; filter: url(#radarGlow) drop-shadow(0 0 8px rgba(78,216,255,0.4)); }
}
.radar-legend {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 8px;
}
.lg-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: rgba(168,180,200,0.8); }
.lg-item i { width: 8px; height: 8px; border-radius: 2px; }
.lg-item i[style*="background"] { border-radius: 50%; }
.lg-item i:not([style*="background"]) { background: transparent; border: 1.5px solid; border-radius: 50%; }

.resume-score {
  font-size: 22px;
  font-weight: 800;
  color: #37d6a5;
  text-shadow: 0 0 12px rgba(55,214,165,0.4);
}
.resume-score em { font-size: 12px; font-style: normal; font-weight: 500; }
.resume-score label { font-size: 11px; color: rgba(168,180,200,0.7); margin-left: 6px; padding: 2px 8px; background: rgba(55,214,165,0.1); border-radius: 4px; font-weight: 400; }
.resume-meta { font-size: 11px; color: rgba(168,180,200,0.6); margin-bottom: 10px; }
.resume-desc { font-size: 12px; color: rgba(200,216,238,0.85); line-height: 1.7; margin-bottom: 14px; }
.resume-detail {
  width: 100%;
  padding: 10px;
  background: linear-gradient(135deg, rgba(78,216,255,0.12), rgba(0,200,255,0.06));
  border: 1px solid rgba(78,216,255,0.2);
  border-radius: 8px;
  color: #4ed8ff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.3s;
}
.resume-detail:hover { background: linear-gradient(135deg, rgba(78,216,255,0.2), rgba(0,200,255,0.1)); box-shadow: 0 0 20px rgba(78,216,255,0.15); }

.galaxy-card { padding: 20px; }
.galaxy-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 8px; }
.galaxy-header h2 {
  margin: 0 0 2px;
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 10px;
  text-shadow: 0 0 30px rgba(78,216,255,0.3);
}
.galaxy-header p { margin: 0; font-size: 12px; color: rgba(168,180,200,0.6); margin-left: 28px; }
.galaxy-stats { display: flex; gap: 16px; }
.galaxy-stats span { font-size: 11px; color: rgba(168,180,200,0.7); }
.galaxy-stats strong { color: #4ed8ff; font-size: 16px; font-weight: 700; margin-right: 3px; text-shadow: 0 0 8px rgba(78,216,255,0.5); }

.galaxy-scene {
  position: relative;
  width: 100%;
  height: 480px;
  border-radius: 12px;
  overflow: hidden;
  background: radial-gradient(ellipse at center, rgba(8,20,50,0.3) 0%, rgba(4,10,25,0.5) 100%);
  border: 1px solid rgba(78,216,255,0.08);
}
.galaxy-bg-radial {
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(circle at center, rgba(78,216,255,0.03) 0%, transparent 50%),
    radial-gradient(circle at 30% 40%, rgba(143,124,255,0.04) 0%, transparent 40%);
  pointer-events: none;
}
.galaxy-bg { position: absolute; inset: 0; }
.star {
  position: absolute;
  width: 1px;
  height: 1px;
  background: rgba(255,255,255,0.4);
  border-radius: 50%;
  animation: starTwinkle ease-in-out infinite;
}
.star-bright {
  width: 2px;
  height: 2px;
  background: #4ed8ff;
  box-shadow: 0 0 4px #4ed8ff;
}
@keyframes starTwinkle {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 1; }
}

.orbit-particles {
  position: absolute;
  left: 50%;
  top: 50%;
  border-radius: 50%;
  pointer-events: none;
}
.orbit-particle {
  position: absolute;
  width: 3px;
  height: 3px;
  background: #4ed8ff;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  margin: -1.5px 0 0 -1.5px;
  box-shadow: 0 0 6px #4ed8ff;
  animation: orbitParticleMove linear infinite;
}
.orbit-particles-1 { width: 290px; height: 290px; margin: -145px 0 0 -145px; animation: orbitRotate 30s linear infinite; }
.orbit-particles-1 .orbit-particle { animation-duration: 30s; }
.orbit-particles-2 { width: 210px; height: 210px; margin: -105px 0 0 -105px; animation: orbitRotateRev 22s linear infinite; }
.orbit-particles-2 .orbit-particle { background: rgba(143,124,255,0.8); box-shadow: 0 0 6px #8f7cff; animation-duration: 22s; }
.orbit-particles-3 { width: 130px; height: 130px; margin: -65px 0 0 -65px; animation: orbitRotate 15s linear infinite; }
.orbit-particles-3 .orbit-particle { background: rgba(55,214,165,0.7); box-shadow: 0 0 5px #37d6a5; animation-duration: 15s; }
@keyframes orbitParticleMove {
  0% { transform: rotate(var(--angle)) translateX(0) scale(0); opacity: 0; }
  10% { transform: rotate(calc(var(--angle) + 36deg)) translateX(0) scale(1); opacity: 1; }
  90% { opacity: 1; }
  100% { transform: rotate(calc(var(--angle) + 324deg)) translateX(0) scale(0); opacity: 0; }
}
@keyframes orbitRotate { to { transform: rotate(360deg); } }
@keyframes orbitRotateRev { to { transform: rotate(-360deg); } }

.orbit-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  border-radius: 50%;
  border: 1px dashed;
  pointer-events: none;
}
.orbit-ring-1 { width: 390px; height: 390px; margin: -195px 0 0 -195px; border-color: rgba(78,216,255,0.1); animation: orbitRotate 80s linear infinite; }
.orbit-ring-2 { width: 290px; height: 290px; margin: -145px 0 0 -145px; border-color: rgba(143,124,255,0.1); animation: orbitRotateRev 60s linear infinite; }
.orbit-ring-3 { width: 180px; height: 180px; margin: -90px 0 0 -90px; border-color: rgba(55,214,165,0.1); animation: orbitRotate 40s linear infinite; }

.core-user {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 10;
}
.core-shockwave {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 70px;
  height: 70px;
  margin: -35px 0 0 -35px;
  border-radius: 50%;
  border: 1px solid rgba(78,216,255,0.3);
  animation: shockwave 4s ease-out infinite;
}
@keyframes shockwave {
  0% { width: 70px; height: 70px; margin: -35px 0 0 -35px; opacity: 0.6; }
  100% { width: 160px; height: 160px; margin: -80px 0 0 -80px; opacity: 0; }
}
.core-energy-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  border-radius: 50%;
  border: 1px solid;
  animation: energyRingRotate linear infinite;
}
.core-energy-ring-1 {
  width: 85px; height: 85px; margin: -42px 0 0 -42px;
  border-color: rgba(78,216,255,0.2) transparent rgba(78,216,255,0.2) transparent;
  animation-duration: 8s;
}
.core-energy-ring-2 {
  width: 105px; height: 105px; margin: -52px 0 0 -52px;
  border-color: transparent rgba(143,124,255,0.15) transparent rgba(143,124,255,0.15);
  animation-duration: 12s;
  animation-direction: reverse;
}
@keyframes energyRingRotate { to { transform: rotate(360deg); } }
.core-glow-outer {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 110px;
  height: 110px;
  margin: -55px 0 0 -55px;
  background: radial-gradient(circle, rgba(78,216,255,0.12) 0%, rgba(78,216,255,0.03) 40%, transparent 70%);
  border-radius: 50%;
  animation: corePulse 4s ease-in-out infinite;
}
.core-glow {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 85px;
  height: 85px;
  margin: -42px 0 0 -42px;
  background: radial-gradient(circle, rgba(78,216,255,0.2) 0%, rgba(0,200,255,0.06) 40%, transparent 70%);
  border-radius: 50%;
  animation: corePulse 3s ease-in-out infinite 0.8s;
}
.core-glow-inner {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 60px;
  height: 60px;
  margin: -30px 0 0 -30px;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(78,216,255,0.06) 50%, transparent 70%);
  border-radius: 50%;
  animation: corePulse 2.5s ease-in-out infinite 1.5s;
}
@keyframes corePulse {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.1); opacity: 0.9; }
}
.core-avatar-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 58px;
  height: 58px;
  margin: -29px 0 0 -29px;
  border-radius: 50%;
  border: 2px solid transparent;
  border-top-color: rgba(78,216,255,0.6);
  animation: ringRotate 6s linear infinite;
}
@keyframes ringRotate { to { transform: rotate(360deg); } }
.core-avatar {
  position: relative;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4ed8ff 0%, #00a8cc 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  color: #041220;
  z-index: 2;
  margin: 0 auto;
  box-shadow: 0 0 24px rgba(78,216,255,0.4), inset 0 1px 2px rgba(255,255,255,0.3);
}
.core-info { margin-top: 12px; }
.core-name { font-size: 14px; font-weight: 600; color: #e8f4ff; text-shadow: 0 0 12px rgba(78,216,255,0.3); letter-spacing: 0.5px; }
.core-meta { font-size: 10px; color: rgba(140,165,195,0.8); margin-top: 3px; }

.skill-node {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(calc(-50% + var(--x)), calc(-50% + var(--y)));
  text-align: center;
  cursor: pointer;
  z-index: 5;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.skill-node.big-node .node-bg { width: 52px; height: 52px; }
.skill-node.big-node .node-ring { width: 58px; height: 58px; margin: -55px 0 0 -29px; }
.skill-node.big-node .node-short { font-size: 13px; }
.skill-node.big-node .node-label { font-size: 10px; }
.skill-node:hover { transform: translate(calc(-50% + var(--x)), calc(-50% + var(--y))) scale(1.15); z-index: 20; }
.skill-node:hover .node-ring { border-width: 2px; }
.skill-node:hover .node-label { opacity: 1; }
.node-bg {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(6,18,40,0.9);
  margin: 0 auto 4px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}
.mastered .node-bg { background: linear-gradient(135deg, rgba(55,214,165,0.15), rgba(6,18,40,0.95)); }
.improve .node-bg { background: linear-gradient(135deg, rgba(143,124,255,0.15), rgba(6,18,40,0.95)); }
.missing .node-bg { background: linear-gradient(135deg, rgba(255,112,136,0.15), rgba(6,18,40,0.95)); }
.transfer .node-bg { background: linear-gradient(135deg, rgba(255,182,92,0.15), rgba(6,18,40,0.95)); }
.node-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 50px;
  height: 50px;
  margin: -50px 0 0 -25px;
  border-radius: 50%;
  border: 1.5px solid;
  transition: all 0.3s;
}
.mastered .node-ring { border-color: rgba(55,214,165,0.5); box-shadow: 0 0 8px rgba(55,214,165,0.2); }
.improve .node-ring { border-color: rgba(143,124,255,0.5); box-shadow: 0 0 8px rgba(143,124,255,0.2); }
.missing .node-ring { border-color: rgba(255,112,136,0.5); box-shadow: 0 0 8px rgba(255,112,136,0.2); }
.transfer .node-ring { border-color: rgba(255,182,92,0.5); box-shadow: 0 0 8px rgba(255,182,92,0.2); }
.node-pulse {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 50px;
  height: 50px;
  margin: -25px 0 0 -25px;
  border-radius: 50%;
  pointer-events: none;
  opacity: 0;
}
.pulse-node .node-pulse {
  animation: nodePulse 3s ease-out infinite;
}
.mastered.pulse-node .node-pulse { border: 1px solid rgba(55,214,165,0.4); }
.improve.pulse-node .node-pulse { border: 1px solid rgba(143,124,255,0.4); }
.missing.pulse-node .node-pulse { border: 1px solid rgba(255,112,136,0.4); }
.transfer.pulse-node .node-pulse { border: 1px solid rgba(255,182,92,0.4); }
@keyframes nodePulse {
  0% { transform: scale(0.9); opacity: 0.7; }
  100% { transform: scale(1.6); opacity: 0; }
}
.node-short {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  position: relative;
  z-index: 1;
}
.mastered .node-short { color: #5ae8bc; text-shadow: 0 0 8px rgba(55,214,165,0.4); }
.improve .node-short { color: #b0a0ff; text-shadow: 0 0 8px rgba(143,124,255,0.4); }
.missing .node-short { color: #ff9aab; text-shadow: 0 0 8px rgba(255,112,136,0.4); }
.transfer .node-short { color: #ffcc88; text-shadow: 0 0 8px rgba(255,182,92,0.4); }
.node-label {
  font-size: 9px;
  color: rgba(180,200,225,0.7);
  white-space: nowrap;
  font-weight: 500;
  opacity: 0.7;
  transition: opacity 0.3s;
  text-shadow: 0 1px 4px rgba(0,0,0,0.8);
}

.skill-tip {
  position: absolute;
  transform: translate(-50%, -100%);
  z-index: 30;
  animation: tipIn 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
@keyframes tipIn {
  from { opacity: 0; transform: translate(-50%, -90%) scale(0.95); }
  to { opacity: 1; transform: translate(-50%, -100%) scale(1); }
}
.tip-arrow {
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%) rotate(45deg);
  width: 10px;
  height: 10px;
  background: rgba(10,28,55,0.98);
  border-right: 1px solid rgba(78,216,255,0.25);
  border-bottom: 1px solid rgba(78,216,255,0.25);
}
.tip-inner {
  background: linear-gradient(180deg, rgba(12,32,62,0.97) 0%, rgba(8,22,48,0.98) 100%);
  border: 1px solid rgba(78,216,255,0.2);
  border-radius: 8px;
  padding: 10px 14px;
  min-width: 130px;
  backdrop-filter: blur(16px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 20px rgba(78,216,255,0.08);
}
.tip-header {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 3px;
}
.tip-status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.tip-status-dot.mastered { background: #37d6a5; box-shadow: 0 0 6px #37d6a5; }
.tip-status-dot.improve { background: #8f7cff; box-shadow: 0 0 6px #8f7cff; }
.tip-status-dot.missing { background: #ff7088; box-shadow: 0 0 6px #ff7088; }
.tip-status-dot.transfer { background: #ffb65c; box-shadow: 0 0 6px #ffb65c; }
.tip-name { font-size: 13px; font-weight: 600; color: #fff; }
.tip-cat { font-size: 10px; color: rgba(140,165,195,0.7); margin-bottom: 8px; padding-left: 14px; }
.tip-level-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.tip-level-val { font-size: 11px; font-weight: 700; color: rgba(78,216,255,0.9); flex-shrink: 0; }
.tip-bar { flex: 1; height: 4px; background: rgba(78,216,255,0.1); border-radius: 2px; overflow: hidden; }
.tip-bar-fill { height: 100%; border-radius: 2px; transition: width 0.5s ease; }
.tip-bar-fill.mastered { background: linear-gradient(90deg, #37d6a5, #5ae8bc); box-shadow: 0 0 6px rgba(55,214,165,0.5); }
.tip-bar-fill.improve { background: linear-gradient(90deg, #8f7cff, #b0a0ff); box-shadow: 0 0 6px rgba(143,124,255,0.5); }
.tip-bar-fill.missing { background: linear-gradient(90deg, #ff7088, #ff9aab); box-shadow: 0 0 6px rgba(255,112,136,0.5); }
.tip-bar-fill.transfer { background: linear-gradient(90deg, #ffb65c, #ffcc88); box-shadow: 0 0 6px rgba(255,182,92,0.5); }

.galaxy-legend {
  display: flex;
  justify-content: center;
  gap: 18px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(78,216,255,0.06);
}
.gl-item { display: flex; align-items: center; gap: 5px; font-size: 10px; color: rgba(140,165,195,0.8); }
.gl-item i { width: 7px; height: 7px; border-radius: 50%; }
.gl-item.mastered i { background: #37d6a5; box-shadow: 0 0 5px #37d6a5; }
.gl-item.improve i { background: #8f7cff; box-shadow: 0 0 5px #8f7cff; }
.gl-item.missing i { background: #ff7088; box-shadow: 0 0 5px #ff7088; }
.gl-item.transfer i { background: #ffb65c; box-shadow: 0 0 5px #ffb65c; }

.lp-header { margin-bottom: 12px; }
.lp-header h2 { margin: 0 0 2px; font-size: 18px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 10px; }
.lp-header p { margin: 0; font-size: 12px; color: rgba(168,180,200,0.6); margin-left: 28px; }

.lp-mountain {
  position: relative;
  height: 200px;
  border-radius: 10px;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(8,20,45,0.2) 0%, rgba(4,12,30,0.4) 100%);
  border: 1px solid rgba(78,216,255,0.08);
}
.lp-svg { width: 100%; height: 100%; }
.lp-path {
  stroke-dasharray: 2000;
  animation: pathDraw 3s ease-out forwards;
}
@keyframes pathDraw { from { stroke-dashoffset: 2000; } to { stroke-dashoffset: 0; } }
.lp-stop {
  position: absolute;
  transform: translateX(-50%);
  text-align: center;
}
.stop-pulse {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 28px;
  height: 28px;
  margin: -4px 0 0 -14px;
  border-radius: 50%;
  border: 2px solid #ffb65c;
  animation: stopPulse 2s ease-out infinite;
}
@keyframes stopPulse {
  0% { transform: translateX(-50%) scale(1); opacity: 1; }
  100% { transform: translateX(-50%) scale(2.5); opacity: 0; }
}
.stop-glow {
  position: absolute;
  top: 0;
  left: 50%;
  width: 32px;
  height: 32px;
  margin: -6px 0 0 -16px;
  border-radius: 50%;
  pointer-events: none;
}
.lp-stop.current .stop-glow { background: radial-gradient(circle, rgba(255,182,92,0.4) 0%, transparent 60%); }
.lp-stop.done .stop-glow { background: radial-gradient(circle, rgba(55,214,165,0.3) 0%, transparent 60%); }
.stop-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  margin: 0 auto 4px;
  position: relative;
}
.lp-stop.done .stop-dot {
  background: linear-gradient(135deg, #37d6a5, #2ab890);
  color: #041210;
  box-shadow: 0 0 12px rgba(55,214,165,0.5);
}
.lp-stop.current .stop-dot {
  background: linear-gradient(135deg, #ffb65c, #ff9500);
  color: #1a0f00;
  box-shadow: 0 0 16px rgba(255,182,92,0.6);
  animation: stopCurrentPulse 1.5s ease-in-out infinite;
}
.lp-stop.locked .stop-dot {
  background: rgba(30,50,80,0.8);
  color: rgba(168,180,200,0.5);
  border: 1px solid rgba(78,216,255,0.15);
}
@keyframes stopCurrentPulse {
  0%, 100% { box-shadow: 0 0 12px rgba(255,182,92,0.5); }
  50% { box-shadow: 0 0 24px rgba(255,182,92,0.8); }
}
.stop-label { font-size: 10px; color: rgba(168,180,200,0.7); white-space: nowrap; }
.lp-stop.current .stop-label { color: #ffb65c; font-weight: 600; }
.lp-stop.done .stop-label { color: #37d6a5; }
.lp-current-pos {
  position: absolute;
  left: 58%;
  bottom: 58%;
  transform: translate(-50%, 50%);
}
.pos-ping {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 20px;
  height: 20px;
  margin: -10px 0 0 -10px;
  border-radius: 50%;
  background: rgba(255,182,92,0.3);
  animation: posPing 1.5s ease-out infinite;
}
@keyframes posPing {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(3); opacity: 0; }
}
.pos-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ffb65c;
  box-shadow: 0 0 12px #ffb65c;
  position: relative;
  z-index: 2;
}
.pos-label {
  position: absolute;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 9px;
  color: #ffb65c;
  white-space: nowrap;
  font-weight: 600;
}

.action-badge {
  font-size: 10px;
  padding: 2px 8px;
  background: linear-gradient(135deg, rgba(143,124,255,0.2), rgba(78,216,255,0.2));
  border: 1px solid rgba(143,124,255,0.3);
  border-radius: 4px;
  color: #a78bfa;
  font-weight: 600;
}
.action-priority { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.prio-label { font-size: 11px; color: rgba(168,180,200,0.6); }
.prio-high {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  background: rgba(255,112,136,0.1);
  border: 1px solid rgba(255,112,136,0.3);
  border-radius: 4px;
  color: #ff7088;
  letter-spacing: 1px;
}
.action-title { font-size: 16px; font-weight: 700; color: #fff; line-height: 1.4; margin-bottom: 8px; text-shadow: 0 0 20px rgba(78,216,255,0.2); }
.action-desc { font-size: 12px; color: rgba(200,216,238,0.75); line-height: 1.6; margin-bottom: 14px; }
.action-meta { display: flex; gap: 14px; margin-bottom: 14px; }
.meta-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: rgba(168,180,200,0.7); }
.meta-item svg { color: #4ed8ff; }
.action-start {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #4ed8ff 0%, #00e5ff 30%, #00b8d4 60%, #8f7cff 100%);
  border: none;
  border-radius: 12px;
  color: #041020;
  font-size: 15px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 
    0 0 20px rgba(78,216,255,0.5), 
    0 0 40px rgba(78,216,255,0.25),
    0 4px 15px rgba(0,0,0,0.3),
    inset 0 1px 0 rgba(255,255,255,0.4);
  letter-spacing: 1px;
}
.action-start:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 
    0 0 30px rgba(78,216,255,0.7), 
    0 0 60px rgba(78,216,255,0.4),
    0 8px 25px rgba(0,0,0,0.4);
}
.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: btnShine 3s ease-in-out infinite;
}
@keyframes btnShine {
  0%, 100% { left: -100%; }
  50% { left: 100%; }
}

.progress-label { font-size: 13px; font-weight: 700; color: #4ed8ff; }
.plan-progress { margin-bottom: 14px; }
.pp-bar { height: 6px; background: rgba(78,216,255,0.08); border-radius: 3px; overflow: hidden; }
.pp-fill {
  height: 100%;
  background: linear-gradient(90deg, #4ed8ff, #8f7cff);
  border-radius: 3px;
  box-shadow: 0 0 10px rgba(78,216,255,0.4);
  animation: ppFill 1.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}
@keyframes ppFill { from { width: 0; } }
.plan-list { display: flex; flex-direction: column; gap: 8px; }
.plan-item { display: flex; align-items: flex-start; gap: 10px; }
.pi-check {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 1.5px solid rgba(78,216,255,0.3);
  flex-shrink: 0;
  margin-top: 1px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}
.plan-item.done .pi-check {
  background: linear-gradient(135deg, #37d6a5, #2ab890);
  border-color: #37d6a5;
  box-shadow: 0 0 8px rgba(55,214,165,0.4);
}
.pi-title { font-size: 12px; color: #c8d8ee; line-height: 1.4; }
.plan-item.done .pi-title { color: rgba(168,180,200,0.5); text-decoration: line-through; }
.pi-time { font-size: 10px; color: rgba(168,180,200,0.5); margin-top: 2px; }

.interview-trend.up { color: #37d6a5; font-size: 12px; font-weight: 700; }
.interview-score-wrap {
  position: relative;
  text-align: center;
  padding: 16px 0;
  margin-bottom: 12px;
}
.is-glow {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
  background: radial-gradient(circle, rgba(78,216,255,0.15) 0%, transparent 60%);
  border-radius: 50%;
  animation: isGlow 3s ease-in-out infinite;
}
@keyframes isGlow {
  0%, 100% { transform: translate(-50%,-50%) scale(1); opacity: 0.5; }
  50% { transform: translate(-50%,-50%) scale(1.3); opacity: 1; }
}
.is-num {
  font-size: 48px;
  font-weight: 900;
  background: linear-gradient(180deg, #fff, #4ed8ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  filter: drop-shadow(0 0 15px rgba(78,216,255,0.4));
}
.is-label { font-size: 11px; color: rgba(168,180,200,0.6); margin-top: 4px; letter-spacing: 1px; }
.interview-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 14px;
  padding: 12px 8px;
  background: rgba(7,20,40,0.5);
  border-radius: 8px;
  border: 1px solid rgba(78,216,255,0.06);
}
.stat-item { text-align: center; }
.stat-val { font-size: 18px; font-weight: 700; }
.stat-lbl { font-size: 10px; color: rgba(168,180,200,0.6); margin-top: 2px; }
.interview-btn {
  width: 100%;
  padding: 10px;
  background: linear-gradient(135deg, rgba(143,124,255,0.15), rgba(78,216,255,0.1));
  border: 1px solid rgba(143,124,255,0.25);
  border-radius: 8px;
  color: #a78bfa;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}
.interview-btn:hover { background: linear-gradient(135deg, rgba(143,124,255,0.25), rgba(78,216,255,0.15)); box-shadow: 0 0 20px rgba(143,124,255,0.15); }

.timeline { padding: 4px 0; }
.tl-item {
  position: relative;
  padding-left: 20px;
  padding-bottom: 16px;
}
.tl-item.first .tl-dot { background: #4ed8ff; box-shadow: 0 0 10px #4ed8ff; }
.tl-dot {
  position: absolute;
  left: 0;
  top: 4px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(78,216,255,0.3);
  border: 2px solid rgba(78,216,255,0.5);
}
.tl-line {
  position: absolute;
  left: 4px;
  top: 16px;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, rgba(78,216,255,0.2), rgba(78,216,255,0.05));
}
.tl-date { font-size: 10px; color: #4ed8ff; font-weight: 600; margin-bottom: 3px; }
.tl-text { font-size: 11px; color: rgba(200,216,238,0.75); line-height: 1.5; }

@media (max-width: 1400px) {
  .gc-content { grid-template-columns: 260px 1fr 290px; gap: 14px; padding: 14px 16px; }
}
@media (max-width: 1200px) {
  .gc-content { grid-template-columns: 1fr; max-width: 700px; }
  .galaxy-scene { height: 400px; }
}
</style>
