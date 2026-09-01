<template>
  <div class="gcd">
    <!-- 顶部：标题 + 实时数据 -->
    <header class="gcd__header">
      <button class="gcd__back" type="button" @click="router.push('/dashboards/candidate')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        返回概览
      </button>
      <div class="gcd__title">
        <h1>个人成长驾驶舱</h1>
        <p>PERSONAL GROWTH COCKPIT</p>
      </div>
      <div class="gcd__live">
        <span class="gcd__live-badge"><i></i>实时数据</span>
        <time>2025.05.20 10:30:45</time>
      </div>
    </header>

    <!-- 主网格 -->
    <div class="gcd__grid">
      <!-- 第1列：能力星环 + 能力分布均衡度 -->
      <div class="gcd__col gcd__col--1">
        <section class="gcd-panel gcd-panel--grow">
          <h2 class="gcd-panel__title"><span class="gcd-panel__bar"></span>能力星环</h2>
          <div class="gcd-ring">
            <svg viewBox="0 0 200 200" class="gcd-ring__svg">
              <defs>
                <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#52ddff" />
                  <stop offset="55%" stop-color="#0aa7c9" />
                  <stop offset="100%" stop-color="#1f6fae" />
                </linearGradient>
                <filter id="ringGlow"><feGaussianBlur stdDeviation="3" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
              </defs>
              <circle cx="100" cy="100" r="84" fill="none" stroke="rgba(82, 221, 255,0.08)" stroke-width="10" />
              <circle cx="100" cy="100" r="84" fill="none" stroke="url(#ringGrad)" stroke-width="10" stroke-linecap="round"
                stroke-dasharray="452.4 527.8" transform="rotate(-90 100 100)" filter="url(#ringGlow)" />
              <circle cx="100" cy="100" r="60" fill="none" stroke="rgba(82, 221, 255,0.06)" stroke-width="1" stroke-dasharray="3 5" />
            </svg>
            <div class="gcd-ring__center">
              <b>88</b>
              <small>能力体</small>
            </div>
          </div>
          <div class="gcd-ring__foot">
            <span class="gcd-kv"><b>学习力</b><em>92</em></span>
          </div>
        </section>

        <section class="gcd-panel gcd-panel--grow">
          <h2 class="gcd-panel__title"><span class="gcd-panel__bar"></span>能力分布均衡度</h2>
          <div class="gcd-radar">
            <svg viewBox="0 0 260 200" class="gcd-radar__svg">
              <defs>
                <linearGradient id="radarFill" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stop-color="#52ddff" stop-opacity="0.32" />
                  <stop offset="100%" stop-color="#1f6fae" stop-opacity="0.10" />
                </linearGradient>
              </defs>
              <polygon v-for="lv in [1, 0.75, 0.5, 0.25]" :key="lv" :points="radarPts(100 * lv)" fill="none" stroke="rgba(82, 221, 255,0.10)" stroke-width="1" />
              <line v-for="(d, i) in radarDims" :key="'ax' + i" :x1="130" :y1="100" :x2="radarPt(d, 100).x" :y2="radarPt(d, 100).y" stroke="rgba(82, 221, 255,0.10)" stroke-width="1" />
              <polygon :points="radarPtsData" fill="url(#radarFill)" stroke="#52ddff" stroke-width="2" filter="url(#ringGlow)" />
              <circle v-for="(d, i) in radarDims" :key="'pt' + i" :cx="radarPt(d, d.value).x" :cy="radarPt(d, d.value).y" r="3.5" fill="#52ddff" />
              <text v-for="(d, i) in radarDims" :key="'tx' + i" :x="radarPt(d, 120).x" :y="radarPt(d, 120).y + 4" fill="rgba(229,255,255,0.75)" font-size="12" text-anchor="middle">{{ d.name }} {{ d.value }}</text>
            </svg>
          </div>
        </section>
      </div>

      <!-- 第2列：能力维度 / 成长节点 / 关键跃迁 -->
      <div class="gcd__col gcd__col--2">
        <section class="gcd-panel">
          <h2 class="gcd-panel__title"><span class="gcd-panel__bar"></span>能力维度</h2>
          <div class="gcd-span">
            <div class="gcd-span__line"></div>
            <span class="gcd-span__start">2024</span>
            <span class="gcd-span__end">2027</span>
          </div>
        </section>

        <section class="gcd-panel">
          <h2 class="gcd-panel__title"><span class="gcd-panel__bar"></span>成长节点</h2>
          <div class="gcd-node">
            <div class="gcd-node__dot"></div>
            <div class="gcd-node__meta">
              <b>2026</b>
              <span>协同跃迁</span>
            </div>
          </div>
        </section>

        <section class="gcd-panel">
          <h2 class="gcd-panel__title"><span class="gcd-panel__bar"></span>关键跃迁</h2>
          <div class="gcd-node">
            <div class="gcd-node__dot"></div>
            <div class="gcd-node__meta">
              <b>2027</b>
              <span>全面迁</span>
            </div>
          </div>
          <div class="gcd-node gcd-node--accent">
            <div class="gcd-node__dot"></div>
            <div class="gcd-node__meta">
              <b>创新突破</b>
            </div>
          </div>
        </section>

        <section class="gcd-panel">
          <h2 class="gcd-panel__title"><span class="gcd-panel__bar"></span>迁节点</h2>
          <div class="gcd-node">
            <div class="gcd-node__dot"></div>
            <div class="gcd-node__meta">
              <b>2025</b>
              <span>能力突破</span>
            </div>
          </div>
        </section>
      </div>

      <!-- 第3列：能力演化轨迹 + 目标角色 -->
      <div class="gcd__col gcd__col--3">
        <section class="gcd-panel gcd-panel--grow">
          <h2 class="gcd-panel__title"><span class="gcd-panel__bar"></span>能力演化轨迹</h2>
          <div class="gcd-line">
            <div class="gcd-line__axis">
              <span v-for="v in [100, 80, 60, 40, 20, 0]" :key="v">{{ v }}</span>
            </div>
            <svg viewBox="0 0 420 220" preserveAspectRatio="none" class="gcd-line__svg">
              <defs>
                <linearGradient id="lineFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#52ddff" stop-opacity="0.26" />
                  <stop offset="100%" stop-color="#52ddff" stop-opacity="0" />
                </linearGradient>
              </defs>
              <line v-for="g in 5" :key="g" :x1="0" :x2="420" :y1="(g - 1) * 44" :y2="(g - 1) * 44" stroke="rgba(82, 221, 255,0.08)" stroke-width="1" />
              <path d="M10,40 C90,58 140,30 200,96 C260,162 330,130 410,180" fill="none" stroke="#52ddff" stroke-width="2.5" stroke-linecap="round" filter="url(#ringGlow)" />
              <path d="M10,40 C90,58 140,30 200,96 C260,162 330,130 410,180 L410,220 L10,220 Z" fill="url(#lineFill)" />
              <circle cx="10" cy="40" r="4" fill="#0b2237" stroke="#52ddff" stroke-width="2" />
              <circle cx="410" cy="180" r="4" fill="#0b2237" stroke="#52ddff" stroke-width="2" />
            </svg>
          </div>
          <div class="gcd-line__labels">
            <span>2024</span>
            <span>起步</span>
          </div>
        </section>

        <section class="gcd-panel">
          <h2 class="gcd-panel__title"><span class="gcd-panel__bar"></span>目标角色</h2>
          <p class="gcd-role">战略决策专家</p>
        </section>

        <section class="gcd-panel gcd-score">
          <span class="gcd-score__num">84.6</span>
          <div class="gcd-score__meta">
            <b>综合能力</b>
            <span>思维 <em>85</em></span>
          </div>
        </section>
      </div>

      <!-- 第4列：成长跃迁路线 + 关键跃迁与证据链 -->
      <div class="gcd__col gcd__col--4">
        <section class="gcd-panel gcd-panel--grow">
          <h2 class="gcd-panel__title"><span class="gcd-panel__bar"></span>成长跃迁路线</h2>
          <ul class="gcd-route">
            <li v-for="(r, i) in routes" :key="r.name">
              <span class="gcd-route__idx">{{ String(i + 1).padStart(2, '0') }}</span>
              <div class="gcd-route__body">
                <b>{{ r.name }}</b>
                <small>{{ r.desc }}</small>
              </div>
            </li>
          </ul>
        </section>

        <section class="gcd-panel gcd-panel--grow">
          <h2 class="gcd-panel__title"><span class="gcd-panel__bar"></span>关键跃迁与证据链</h2>
          <div class="gcd-evidence">
            <div class="gcd-evidence__head">
              <span class="gcd-evidence__tag">迭代完成</span>
              <time>2025.05.20 10:30:45</time>
            </div>
            <ol class="gcd-evidence__list">
              <li v-for="e in evidence" :key="e.title">
                <span class="gcd-evidence__date">{{ e.date }}</span>
                <div>
                  <b>{{ e.title }}</b>
                  <small>{{ e.desc }}</small>
                </div>
              </li>
            </ol>
          </div>
        </section>
      </div>
    </div>

    <!-- 底部：洞察条 -->
    <div class="gcd__bottom">
      <section class="gcd-panel gcd-resp">
        <h2 class="gcd-panel__title"><span class="gcd-panel__bar"></span>响应效率</h2>
        <p>请求及时高效</p>
        <span class="gcd-resp__stat">平均响应 <b>&lt; 1.2h</b></span>
      </section>

      <section class="gcd-panel gcd-insight">
        <h2 class="gcd-panel__title"><span class="gcd-panel__bar"></span>AI 洞察</h2>
        <ul>
          <li v-for="ins in insights" :key="ins.title">
            <b :class="ins.tone">{{ ins.title }}</b>
            <small>{{ ins.desc }}</small>
          </li>
        </ul>
      </section>

      <div class="gcd-insight__mark">INSIGHT</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const radarDims = [
  { name: '决策力', value: 85 },
  { name: '执行力', value: 90 },
  { name: '沟通力', value: 86 },
  { name: '洞察力', value: 80 },
]

function radarPt(d: { name: string; value: number }, radius: number) {
  const i = radarDims.indexOf(d)
  const ang = (Math.PI * 2 * i) / radarDims.length - Math.PI / 2
  return { x: 130 + radius * Math.cos(ang), y: 100 + radius * Math.sin(ang) }
}

function radarPts(radius: number) {
  return radarDims.map((d) => {
    const p = radarPt(d, radius)
    return `${p.x},${p.y}`
  }).join(' ')
}

const radarPtsData = computed(() => radarDims.map((d) => {
  const p = radarPt(d, d.value)
  return `${p.x},${p.y}`
}).join(' '))

const routes = [
  { name: '推理能力', desc: '效能，放大成' },
  { name: '协同能力', desc: '整合信息做决策' },
  { name: '决策协同力', desc: '整合信息做决策' },
  { name: '创新能力', desc: '打破常规到创新' },
  { name: '泛化能力', desc: '拓展边界' },
]

const evidence = [
  { date: '2026.07', title: '迭代优化生成', desc: '生成多维模型，提升效果与效率' },
  { date: '2026.01', title: '目标提升', desc: '核心能力提升23%，稳步增长' },
  { date: '2025.07', title: '系统稳定性增强', desc: '系统升至99%，保持稳健' },
  { date: '2024.12', title: '起步', desc: '能力基线建立' },
]

const insights = [
  { title: '决策能力提升', desc: '决策深度和准确性显著增强，议持续强化复杂应用', tone: 'up' },
  { title: '协同能力增强', desc: '团队协作效率提升明显，建议推动更多协同项目', tone: 'up' },
  { title: '创新能力待加', desc: '创新次数较低，建议拓展创新机制与实践', tone: 'warn' },
]
</script>

<style scoped>
.gcd {
  --gcd-bg: #0b2237;
  --gcd-panel: rgba(4, 52, 62, 0.20);
  --gcd-border: rgba(82, 221, 255, 0.09);
  --gcd-cyan: #52ddff;
  --gcd-blue: #52ddff;
  --gcd-teal: #0aa9b4;
  --gcd-amber: #ffc048;
  --gcd-text: #e5ffff;
  --gcd-muted: #7aadb2;

  position: relative;
  min-height: calc(100vh - 68px);
  overflow: hidden;
  padding: 22px 24px 30px;
  color: var(--gcd-text);
  background:
    radial-gradient(120% 90% at 50% 0%, rgba(82, 221, 255, 0.06), transparent 55%),
    linear-gradient(180deg, #0b2237 0%, #071a2b 100%);
}

/* 顶部 */
.gcd__header { display: flex; align-items: flex-end; justify-content: space-between; gap: 24px; margin-bottom: 18px; }
.gcd__back { display: inline-flex; align-items: center; gap: 6px; border: 1px solid rgba(82, 221, 255, 0.32); border-radius: 10px; padding: 8px 14px; color: var(--gcd-cyan); background: rgba(10, 169, 180, 0.10); font: inherit; font-size: 12px; font-weight: 700; cursor: pointer; transition: all 0.25s; flex-shrink: 0; }
.gcd__back:hover { background: rgba(10, 169, 180, 0.20); border-color: rgba(82, 221, 255, 0.55); }
.gcd__back svg { width: 16px; height: 16px; }
.gcd__title h1 { margin: 0; color: #eaffff; font-size: clamp(24px, 2vw, 32px); font-weight: 850; letter-spacing: 0.02em; }
.gcd__title p { margin: 6px 0 0; color: var(--gcd-cyan); font-size: 11px; font-weight: 800; letter-spacing: 0.32em; text-transform: uppercase; text-shadow: 0 0 8px rgba(82, 221, 255, 0.55); }
.gcd__live { display: flex; align-items: center; gap: 16px; }
.gcd__live-badge { display: inline-flex; align-items: center; gap: 7px; border: 1px solid rgba(82, 221, 255, 0.32); border-radius: 999px; padding: 6px 12px; color: var(--gcd-cyan); font-size: 11px; font-weight: 700; background: rgba(10, 169, 180, 0.10); box-shadow: 0 0 14px rgba(82, 221, 255, 0.12); }
.gcd__live-badge i { width: 7px; height: 7px; border-radius: 50%; background: var(--gcd-cyan); box-shadow: 0 0 7px rgba(82, 221, 255, 0.8); animation: gcd-pulse 1.6s ease-in-out infinite; }
.gcd__live time { color: var(--gcd-muted); font-size: 12px; font-variant-numeric: tabular-nums; }
@keyframes gcd-pulse { 50% { opacity: 0.35; } }

/* 网格 */
.gcd__grid { display: grid; grid-template-columns: 1.05fr 0.92fr 1.15fr 1.15fr; gap: 14px; }
.gcd__col { display: flex; flex-direction: column; gap: 14px; }

/* 面板 */
.gcd-panel { position: relative; border: 1px solid var(--gcd-border); border-radius: 12px; padding: 16px 18px; background: linear-gradient(145deg, rgba(4, 46, 54, 0.36), rgba(2, 20, 24, 0.38)); box-shadow: inset 0 1px 0 rgba(141, 255, 255, 0.025); backdrop-filter: blur(20px) saturate(1.15); }
.gcd-panel--grow { flex: 1; }
.gcd-panel__title { display: flex; align-items: center; gap: 9px; margin: 0 0 14px; color: rgba(229, 255, 255, 0.92); font-size: 14px; font-weight: 700; }
.gcd-panel__bar { width: 3px; height: 14px; border-radius: 2px; background: linear-gradient(180deg, var(--gcd-cyan), #1f6fae); box-shadow: 0 0 10px rgba(82, 221, 255, 0.5); }

/* 星环 */
.gcd-ring { position: relative; display: grid; place-items: center; }
.gcd-ring__svg { width: 170px; height: 170px; }
.gcd-ring__center { position: absolute; inset: 0; display: grid; place-content: center; text-align: center; }
.gcd-ring__center b { color: #eaffff; font-size: 46px; line-height: 1; text-shadow: 0 0 22px rgba(82, 221, 255, 0.55); }
.gcd-ring__center small { margin-top: 4px; color: var(--gcd-muted); font-size: 11px; }
.gcd-ring__foot { margin-top: 6px; display: flex; justify-content: center; }
.gcd-kv { display: inline-flex; align-items: baseline; gap: 8px; }
.gcd-kv b { color: var(--gcd-muted); font-size: 12px; }
.gcd-kv em { color: var(--gcd-cyan); font-size: 20px; font-weight: 800; font-style: normal; text-shadow: 0 0 10px rgba(82, 221, 255, 0.5); }

/* 折线图 */
.gcd-line { display: grid; grid-template-columns: 24px 1fr; gap: 6px; }
.gcd-line__axis { display: flex; flex-direction: column; justify-content: space-between; color: var(--gcd-muted); font-size: 10px; text-align: right; height: 200px; }
.gcd-line__svg { width: 100%; height: 200px; overflow: visible; }
.gcd-line__labels { display: flex; justify-content: space-between; margin-top: 4px; padding-left: 30px; color: var(--gcd-muted); font-size: 11px; }

/* 雷达 */
.gcd-radar { display: grid; place-items: center; }
.gcd-radar__svg { width: 100%; max-width: 260px; }

/* 时间跨度 */
.gcd-span { position: relative; padding: 10px 0 6px; }
.gcd-span__line { height: 2px; background: linear-gradient(90deg, var(--gcd-cyan), rgba(10, 169, 180, 0.18)); box-shadow: 0 0 8px rgba(82, 221, 255, 0.5); }
.gcd-span__start, .gcd-span__end { position: absolute; top: 2px; color: var(--gcd-muted); font-size: 11px; }
.gcd-span__start { left: 0; }
.gcd-span__end { right: 0; }

/* 节点 */
.gcd-node { display: flex; align-items: center; gap: 10px; padding: 5px 0; }
.gcd-node + .gcd-node { margin-top: 2px; }
.gcd-node__dot { width: 9px; height: 9px; border-radius: 50%; background: var(--gcd-cyan); box-shadow: 0 0 10px rgba(82, 221, 255, 0.7); flex-shrink: 0; }
.gcd-node__meta b { display: block; color: var(--gcd-text); font-size: 13px; }
.gcd-node__meta span { color: var(--gcd-muted); font-size: 11px; }
.gcd-node--accent .gcd-node__dot { background: var(--gcd-amber); box-shadow: 0 0 10px rgba(255, 192, 72, 0.7); }

/* 目标角色 */
.gcd-role { margin: 0; color: var(--gcd-text); font-size: 20px; font-weight: 800; text-shadow: 0 0 14px rgba(82, 221, 255, 0.35); }

/* 跃迁路线 */
.gcd-route { display: grid; gap: 10px; margin: 0; padding: 0; list-style: none; }
.gcd-route li { display: flex; align-items: center; gap: 12px; }
.gcd-route__idx { display: grid; place-items: center; width: 26px; height: 26px; border: 1px solid rgba(82, 221, 255, 0.28); border-radius: 7px; color: var(--gcd-cyan); font-size: 11px; font-weight: 700; flex-shrink: 0; }
.gcd-route__body b { display: block; color: var(--gcd-text); font-size: 13px; }
.gcd-route__body small { color: var(--gcd-muted); font-size: 11px; }

/* 证据链 */
.gcd-evidence__head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.gcd-evidence__tag { border-radius: 5px; padding: 3px 8px; color: var(--gcd-cyan); background: rgba(10, 169, 180, 0.12); font-size: 11px; font-weight: 700; }
.gcd-evidence__head time { color: var(--gcd-muted); font-size: 11px; font-variant-numeric: tabular-nums; }
.gcd-evidence__list { display: grid; gap: 10px; margin: 0; padding: 0; list-style: none; }
.gcd-evidence__list li { display: grid; grid-template-columns: 62px 1fr; gap: 10px; align-items: start; }
.gcd-evidence__date { color: var(--gcd-cyan); font-size: 11px; font-weight: 700; font-variant-numeric: tabular-nums; }
.gcd-evidence__list b { display: block; color: var(--gcd-text); font-size: 12px; }
.gcd-evidence__list small { color: var(--gcd-muted); font-size: 10px; line-height: 1.5; }

/* 底部条 */
.gcd__bottom { position: relative; display: grid; grid-template-columns: 0.8fr 1.6fr; gap: 14px; margin-top: 14px; }
.gcd-score { display: flex; align-items: center; gap: 14px; }
.gcd-score__num { color: var(--gcd-text); font-size: 40px; font-weight: 850; letter-spacing: -0.02em; text-shadow: 0 0 18px rgba(82, 221, 255, 0.4); }
.gcd-score__meta b { display: block; color: var(--gcd-text); font-size: 13px; }
.gcd-score__meta span { color: var(--gcd-muted); font-size: 11px; }
.gcd-score__meta em { color: var(--gcd-cyan); font-size: 16px; font-weight: 800; font-style: normal; margin-left: 4px; }

.gcd-resp p { margin: 0 0 8px; color: var(--gcd-muted); font-size: 12px; }
.gcd-resp__stat { color: var(--gcd-muted); font-size: 12px; }
.gcd-resp__stat b { color: var(--gcd-text); font-size: 18px; }

.gcd-insight ul { display: grid; gap: 8px; margin: 0; padding: 0; list-style: none; }
.gcd-insight li { display: grid; grid-template-columns: 96px 1fr; gap: 10px; align-items: start; }
.gcd-insight li b { font-size: 12px; }
.gcd-insight li b.up { color: #8cc8d8; }
.gcd-insight li b.warn { color: var(--gcd-amber); }
.gcd-insight li small { color: var(--gcd-muted); font-size: 11px; line-height: 1.5; }

.gcd-insight__mark { position: absolute; right: 0; bottom: -2px; color: rgba(82, 221, 255, 0.16); font-size: 40px; font-weight: 900; letter-spacing: 0.2em; line-height: 1; pointer-events: none; }

@media (max-width: 1280px) {
  .gcd__grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 760px) {
  .gcd__grid { grid-template-columns: 1fr; }
  .gcd__bottom { grid-template-columns: 1fr; }
}
</style>
