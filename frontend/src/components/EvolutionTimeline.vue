<template>
  <section class="evo-dashboard">
    <div class="scanline-global"></div>

    <section class="summary-row">
      <div v-for="(item, i) in summaryCards" :key="i" class="summary-card">
        <div class="frame"></div>
        <div class="inner">
          <div class="num" :data-target="item.value">{{ item.value }}</div>
          <div class="label">{{ item.label }}</div>
        </div>
      </div>
    </section>

    <section class="middle-row">
      <div class="panel matrix" @mousemove="onPanelMouseMove" @mouseleave="onPanelMouseLeave">
        <div class="panel-title">能力分析矩阵</div>
        <i class="panel-glint"></i>
        <div class="matrix-body">
          <div class="matrix-scale">
            <span v-for="n in 6" :key="n">{{ n }}</span>
          </div>
          <div class="bars3d">
            <div v-for="(h, i) in barHeights" :key="i" class="bar3d" :style="{ '--h': h }"></div>
          </div>
          <div class="radar">
            <svg viewBox="0 0 100 100">
              <g fill="none" stroke="#53e8ff">
                <circle cx="50" cy="50" r="36"/>
                <circle cx="50" cy="50" r="27"/>
                <circle cx="50" cy="50" r="18"/>
                <circle cx="50" cy="50" r="9"/>
                <path d="M50 10V90M10 50H90M22 22L78 78M78 22L22 78"/>
                <polygon points="50,20 72,37 68,65 45,75 25,54 32,33" fill="rgba(76,230,255,.08)"/>
              </g>
            </svg>
          </div>
          <div class="platform"></div>
          <div class="matrix-progress"><i></i></div>
        </div>
      </div>

      <div class="panel trend" @mousemove="onPanelMouseMove" @mouseleave="onPanelMouseLeave">
        <div class="panel-title">能力演化战场态势</div>
        <i class="panel-glint"></i>
        <svg viewBox="0 0 560 300" preserveAspectRatio="none">
          <defs>
            <linearGradient id="blueArea" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stop-color="#51e9ff" stop-opacity=".72"/>
              <stop offset="1" stop-color="#0972ab" stop-opacity=".05"/>
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="b"/>
              <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
          </defs>
          <g stroke="rgba(73,207,244,.14)" stroke-width="1">
            <path v-for="x in [45,125,205,285,365,445,525]" :key="'vx'+x" :d="`M${x} 30V260`"/>
            <path v-for="y in [45,85,125,165,205,245]" :key="'hy'+y" :d="`M45 ${y}H535`"/>
          </g>
          <path d="M45 240 C90 210 115 195 150 205 S220 235 270 205 S335 115 390 132 S450 180 535 142 L535 260 L45 260Z" fill="url(#blueArea)"/>
          <path d="M45 239 C92 210 112 198 150 206 S226 235 274 205 S335 115 391 132 S451 180 535 142" fill="none" stroke="#57eaff" stroke-width="2.4" filter="url(#glow)" class="trend-line cyan-line"/>
          <path d="M45 222 C95 190 110 165 155 150 S215 115 272 105 S345 78 395 69 S455 61 535 48" fill="none" stroke="#ffd778" stroke-width="3" filter="url(#glow)" class="trend-line gold-line"/>
          <g fill="#fff4c4" stroke="#ffd778" stroke-width="2" class="dot-group">
            <circle cx="92" cy="193" r="6"/>
            <circle cx="230" cy="123" r="6"/>
            <circle cx="330" cy="90" r="6"/>
            <circle cx="475" cy="58" r="6"/>
          </g>
          <g fill="#f3f9f9" font-size="13" font-weight="700">
            <text x="74" y="182">2024</text>
            <text x="213" y="112">2025</text>
            <text x="312" y="79">2026</text>
            <text x="458" y="46">2027</text>
          </g>
          <g fill="#91b7c7" font-size="9">
            <text x="28" y="248">0</text>
            <text x="20" y="208">30</text>
            <text x="20" y="168">60</text>
            <text x="20" y="128">90</text>
            <text x="16" y="88">120</text>
            <text x="16" y="48">150</text>
            <text x="42" y="280">2024-01</text>
            <text x="122" y="280">2024-07</text>
            <text x="202" y="280">2025-01</text>
            <text x="282" y="280">2025-07</text>
            <text x="362" y="280">2026-01</text>
            <text x="442" y="280">2026-07</text>
          </g>
        </svg>
        <div class="legend">
          <span><b class="c"></b>能力基线</span>
          <span><b class="g"></b>演化趋势</span>
        </div>
      </div>

      <div class="panel growth" @mousemove="onPanelMouseMove" @mouseleave="onPanelMouseLeave">
        <div class="panel-title">能力成长路径</div>
        <i class="panel-glint"></i>
        <div class="steps">
          <template v-for="(stepItem, idx) in growthSteps" :key="idx">
            <div class="step" :class="{ gold: stepItem.gold }" :style="{ '--x': stepItem.x, '--b': stepItem.b }">
              {{ stepItem.name }}
            </div>
            <div v-if="stepItem.score" class="score" :style="{ '--b': stepItem.b }">
              {{ stepItem.score }}
            </div>
          </template>
        </div>
      </div>

      <div class="panel timeline" @mousemove="onPanelMouseMove" @mouseleave="onPanelMouseLeave">
        <div class="panel-title">关键演化事件</div>
        <i class="panel-glint"></i>
        <div class="viewbtn">查看全部</div>
        <div class="line"></div>
        <div class="datebox"><b>2026-07</b>模型迭代完成</div>
        <div v-for="(evt, i) in events" :key="i" class="event" :class="[evt.gold ? 'gold' : '', 'e' + (i+1)]">
          {{ evt.text }}
        </div>
      </div>
    </section>

    <section class="bottom-row">
      <div v-for="(g, i) in gauges" :key="i" class="gauge-card" :class="g.gold ? 'gold' : ''">
        <div class="gauge" :style="{ '--v': g.value, '--accent': g.color }"></div>
        <div class="gauge-center">{{ g.valueText }}</div>
        <div class="gauge-label">{{ g.label }}</div>
        <div class="gauge-bar" :style="{ '--v': g.value + '%' }"><i></i></div>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
const summaryCards = [
  { value: 12, label: '能力维度' },
  { value: 24, label: '成长节点' },
  { value: 12, label: '关键跃迁' },
  { value: 12, label: '优化方向' }
]

const barHeights = ['88%', '98%', '83%']

const growthSteps = [
  { name: '演化能力', x: '0%', b: '0%', score: 15 },
  { name: '创新能力', x: '10%', b: '12%', score: 30 },
  { name: '创新驱动力', x: '20%', b: '24%', score: 45 },
  { name: '决策能力', x: '30%', b: '36%', score: 60 },
  { name: '决策协同力', x: '40%', b: '48%', score: 75, gold: true },
  { name: '协同能力', x: '50%', b: '60%', score: 90, gold: true },
  { name: '推理能力', x: '60%', b: '72%', gold: true }
]

const events = [
  { text: '模型迭代提升' },
  { text: '策略优化生成', gold: true },
  { text: '核心指标提升' },
  { text: '系统稳定性增强', gold: true },
  { text: '系统鲁棒性增强' }
]

const gauges = [
  { value: 84.6, valueText: '84.6', label: '综合能力', color: '#64efff' },
  { value: 92, valueText: '92%', label: '稳定性', color: '#68f2ff' },
  { value: 92, valueText: '92%', label: '可靠性', color: '#67ecff' },
  { value: 91, valueText: '91%', label: '响应效率', color: '#66efff' },
  { value: 87, valueText: '87%', label: '演化效率', color: '#ffd46f', gold: true },
  { value: 87, valueText: '87%', label: '优化效率', color: '#72f0ff' }
]

let rafId: number | null = null
let ctx: CanvasRenderingContext2D | null = null
let W = 0, H = 0, dpr = 1
let pts: Array<{x:number,y:number,r:number,v:number,a:number,p:number}> = []

function onPanelMouseMove(e: MouseEvent) {
  const el = e.currentTarget as HTMLElement
  const r = el.getBoundingClientRect()
  el.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100).toFixed(1) + '%')
  el.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100).toFixed(1) + '%')
}

function onPanelMouseLeave(e: MouseEvent) {
  const el = e.currentTarget as HTMLElement
  el.style.setProperty('--mx', '50%')
  el.style.setProperty('--my', '50%')
}
</script>

<style scoped>
.evo-dashboard {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 78vh;
  min-height: 650px;
  padding: 8px 7px 7px;
  display: grid;
  grid-template-rows: 20% 56% 24%;
  gap: 7px;
  background: rgba(4, 22, 50, 0.06);
  color: #edfaff;
  font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
  overflow: hidden;
  isolation: isolate;
  border-radius: 12px;
  backdrop-filter: blur(6px) saturate(1.05);
  border: 1px solid rgba(70, 200, 255, 0.15);
}

.evo-dashboard::before,
.evo-dashboard::after {
  content: "";
  position: absolute;
  left: 1.2%;
  right: 1.2%;
  height: 1px;
  pointer-events: none;
  background: linear-gradient(90deg,transparent,#2bcfec 8%,transparent 22%,transparent 78%,#2bcfec 92%,transparent);
  opacity: .38;
  z-index: 10;
}
.evo-dashboard::before { top: 2px; }
.evo-dashboard::after { bottom: 3px; }

.scanline-global {
  position: absolute;
  left: 0;
  right: 0;
  top: -8%;
  height: 7%;
  z-index: 3;
  pointer-events: none;
  background: linear-gradient(180deg,transparent,rgba(87,239,255,.035),transparent);
  animation: globalScan 9s linear infinite;
  mix-blend-mode: screen;
}
@keyframes globalScan { to { top: 108%; } }

.summary-row {
  display: grid;
  grid-template-columns: repeat(4,1fr);
  gap: 20px;
  align-items: center;
  padding: 0 22px;
  position: relative;
  z-index: 2;
}
.summary-row::before {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 1px;
  background: repeating-linear-gradient(90deg,#ff5e64 0 2px,transparent 2px 37px);
  opacity: .45;
}

.summary-card {
  height: 78%;
  min-height: 70px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: skewX(-9deg);
  filter: drop-shadow(0 0 8px rgba(43,226,255,.26));
  transition: transform .35s cubic-bezier(.2,.75,.2,1),filter .35s;
  will-change: transform;
}
.summary-card:hover {
  transform: skewX(-9deg) translateY(-3px) scale(1.012);
  filter: drop-shadow(0 0 14px rgba(58,229,255,.46));
}
.summary-card .frame {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg,rgba(18,86,116,.12),rgba(2,18,33,.18)),
    repeating-linear-gradient(90deg,transparent 0 24px,rgba(96,240,255,.02) 25px 26px);
  clip-path: polygon(7% 4%,88% 0,97% 18%,100% 82%,91% 97%,10% 91%,0 74%,2% 19%);
  border: 1px solid transparent;
  box-shadow: inset 0 0 30px rgba(22,187,229,.05);
  backdrop-filter: blur(8px);
}
.summary-card .frame::before {
  content: "";
  position: absolute;
  inset: 6px;
  clip-path: inherit;
  border: 1px solid rgba(135,248,255,.73);
  box-shadow: inset 0 0 22px rgba(61,233,255,.12),0 0 3px rgba(74,231,255,.4);
}
.summary-card::before {
  content: "";
  position: absolute;
  z-index: 2;
  left: 8%;
  right: 8%;
  top: 12%;
  height: 1px;
  background: linear-gradient(90deg,transparent,#95faff,transparent);
  opacity: .5;
  animation: summarySweep 4.8s ease-in-out infinite;
  transform: skewX(9deg);
}
.summary-card:nth-child(2)::before { animation-delay: .7s; }
.summary-card:nth-child(3)::before { animation-delay: 1.4s; }
.summary-card:nth-child(4)::before { animation-delay: 2.1s; }
@keyframes summarySweep {
  0%,100% { transform: skewX(9deg) translateX(-28%); opacity: .06; }
  50% { transform: skewX(9deg) translateX(28%); opacity: .72; }
}
.summary-card .inner {
  position: relative;
  z-index: 2;
  transform: skewX(9deg);
  text-align: center;
  text-shadow: 0 0 10px rgba(128,245,255,.65);
}
.summary-card .inner::before {
  content: "SYSTEM / CAPABILITY";
  display: block;
  font-size: 8px;
  letter-spacing: 2px;
  color: #5fcbe3;
  opacity: .64;
  margin-bottom: 3px;
  font-family: Consolas,monospace;
}
.summary-card .num {
  font-size: clamp(22px,2.8vw,44px);
  font-weight: 900;
  line-height: 1;
  letter-spacing: 1px;
  text-shadow: 0 0 8px rgba(131,247,255,.62),0 0 22px rgba(35,213,255,.28);
}
.summary-card .label {
  font-size: clamp(11px,1.1vw,17px);
  font-weight: 800;
  margin-top: 6px;
  letter-spacing: .8px;
}
.summary-card::after {
  content: "";
  position: absolute;
  width: 6px;
  height: 3px;
  background: #ff5560;
  right: 16%;
  top: 22%;
  box-shadow: 0 0 8px #ff5560;
  transform: skewX(9deg);
}

.middle-row {
  display: grid;
  grid-template-columns: 20% 32% 24% 24%;
  gap: 8px;
  min-height: 0;
  position: relative;
  z-index: 2;
}

.panel {
  position: relative;
  background:
    radial-gradient(circle at var(--mx,50%) var(--my,50%),rgba(73,225,255,.04),transparent 28%),
    linear-gradient(180deg,rgba(6,32,49,.12),rgba(2,13,24,.15));
  border: 1px solid rgba(110,240,255,.28);
  box-shadow: inset 0 0 34px rgba(24,157,192,.05),inset 0 0 0 1px rgba(90,229,255,.03),0 0 8px rgba(37,221,255,.04);
  overflow: hidden;
  transition: border-color .25s,box-shadow .25s,transform .25s;
  backdrop-filter: blur(8px) saturate(1.05);
  --mx: 50%;
  --my: 50%;
}
.panel:hover {
  border-color: rgba(142,248,255,.98);
  box-shadow: inset 0 0 38px rgba(32,178,216,.13),0 0 14px rgba(38,219,255,.12);
}
.panel::before,
.panel::after {
  content: "";
  position: absolute;
  width: 25px;
  height: 17px;
  z-index: 4;
}
.panel::before {
  left: -1px;
  top: -1px;
  border-top: 2px solid #74f5ff;
  border-left: 2px solid #74f5ff;
  filter: drop-shadow(0 0 4px #4eeaff);
}
.panel::after {
  right: -1px;
  bottom: -1px;
  border-right: 2px solid #74f5ff;
  border-bottom: 2px solid #74f5ff;
  filter: drop-shadow(0 0 4px #4eeaff);
}

.panel-glint {
  position: absolute;
  z-index: 1;
  pointer-events: none;
  inset: 0;
  background: linear-gradient(90deg,transparent,rgba(125,245,255,.04),transparent) 0 0/180px 100% no-repeat;
  animation: panelGlint 8s linear infinite;
  mix-blend-mode: screen;
}
.panel-glint::before,
.panel-glint::after {
  content: "";
  position: absolute;
  top: 7px;
  width: 52px;
  height: 6px;
  border-top: 1px solid rgba(100,239,255,.28);
}
.panel-glint::before {
  left: 42px;
  border-left: 1px solid rgba(100,239,255,.22);
  transform: skewX(-35deg);
}
.panel-glint::after {
  right: 42px;
  border-right: 1px solid rgba(100,239,255,.22);
  transform: skewX(35deg);
}
@keyframes panelGlint {
  0% { background-position: -220px 0; }
  100% { background-position: calc(100% + 220px) 0; }
}

.panel-title {
  position: absolute;
  top: 11px;
  left: 14px;
  right: 80px;
  font-weight: 900;
  font-size: clamp(11px,1vw,15px);
  z-index: 4;
  text-shadow: 0 0 8px rgba(96,238,255,.52),0 0 18px rgba(23,187,226,.17);
  letter-spacing: .4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.panel-title::before {
  content: "";
  display: inline-block;
  width: 3px;
  height: 13px;
  margin-right: 7px;
  vertical-align: -2px;
  background: linear-gradient(#b6fdff,#39dff9);
  box-shadow: 0 0 7px #56edff;
}
.panel-title::after {
  content: "  /  REAL-TIME";
  font: 500 8px/1 Consolas,monospace;
  letter-spacing: 1px;
  color: #5fa9bc;
  opacity: .62;
}

.matrix { padding-top: 40px; }
.matrix-body {
  position: absolute;
  inset: 46px 12px 10px 10px;
}
.matrix-body::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg,transparent 45%,rgba(38,216,255,.035));
  pointer-events: none;
}
.matrix-scale {
  position: absolute;
  left: 0;
  top: 20%;
  bottom: 23%;
  width: 34px;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  font-size: 10px;
  color: #dffaff;
}
.matrix-scale span { position: relative; padding-left: 3px; }
.matrix-scale span::after {
  content: "";
  position: absolute;
  left: 22px;
  top: 50%;
  width: 28px;
  height: 2px;
  background: linear-gradient(90deg,#58edff,transparent);
  box-shadow: 0 0 5px #58edff;
}
.bars3d {
  position: absolute;
  left: 24%;
  bottom: 16%;
  width: 42%;
  height: 61%;
  display: flex;
  gap: 6px;
  align-items: flex-end;
  perspective: 400px;
  filter: drop-shadow(0 0 9px rgba(60,232,255,.28));
}
.bar3d {
  width: 26%;
  height: var(--h);
  position: relative;
  background: linear-gradient(90deg,rgba(33,184,226,.07),rgba(129,250,255,.42) 50%,rgba(39,190,230,.08));
  border: 1px solid #80f7ff;
  box-shadow: 0 0 12px rgba(52,231,255,.42),inset 0 0 9px rgba(89,240,255,.18);
  animation: barBreath 3.8s ease-in-out infinite;
  overflow: visible;
}
.bar3d:nth-child(2) { animation-delay: .65s; }
.bar3d:nth-child(3) { animation-delay: 1.3s; }
.bar3d::before {
  content: "";
  position: absolute;
  left: 8px;
  right: -8px;
  top: -8px;
  height: 8px;
  border: 1px solid #81f8ff;
  transform: skewX(-35deg);
  background: rgba(90,238,255,.08);
}
.bar3d::after {
  content: "";
  position: absolute;
  top: -4px;
  bottom: -1px;
  right: -9px;
  width: 8px;
  border: 1px solid #75efff;
  transform: skewY(-45deg);
  background: rgba(85,230,255,.08);
}
@keyframes barBreath {
  50% { box-shadow: 0 0 19px rgba(65,235,255,.55),inset 0 0 14px rgba(112,249,255,.25); }
}
.radar {
  position: absolute;
  right: 6%;
  top: 28%;
  width: 45%;
  aspect-ratio: 1;
  border: 1px solid rgba(87,220,255,.42);
  background: radial-gradient(circle at center,rgba(0,127,179,.12),transparent 68%);
  box-shadow: inset 0 0 20px rgba(26,176,212,.08);
}
.radar svg {
  width: 100%;
  height: 100%;
  opacity: .55;
  animation: radarPulse 5s ease-in-out infinite;
  transform-origin: center;
}
@keyframes radarPulse {
  0%,100% { opacity: .42; transform: scale(.98); }
  50% { opacity: .72; transform: scale(1.01); }
}
.platform {
  position: absolute;
  left: 13%;
  right: 12%;
  bottom: 5%;
  height: 17%;
  border-radius: 50%;
  border: 2px solid #8af7ff;
  box-shadow: 0 0 18px #29d9f4,inset 0 0 18px rgba(100,244,255,.25);
  animation: platformPulse 3.2s ease-in-out infinite;
}
.platform::before,
.platform::after {
  content: "";
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(89,238,255,.85);
  left: 10%;
  right: 10%;
  top: 22%;
  bottom: 22%;
}
.platform::after {
  left: 25%;
  right: 25%;
  top: 35%;
  bottom: 35%;
  box-shadow: 0 0 8px #59efff;
  animation: ringPulse 2.5s .5s ease-in-out infinite;
}
.platform::before { animation: ringPulse 2.5s ease-in-out infinite; }
@keyframes platformPulse { 50% { filter: brightness(1.22); } }
@keyframes ringPulse { 50% { transform: scale(1.06); opacity: .48; } }
.matrix-progress {
  position: absolute;
  left: 18%;
  right: 18%;
  bottom: 0;
  height: 4px;
  border: 1px solid rgba(95,235,255,.35);
  background: rgba(12,48,63,.6);
  border-radius: 5px;
  overflow: hidden;
}
.matrix-progress i {
  display: block;
  width: 74%;
  height: 100%;
  background: linear-gradient(90deg,#59efff 0 75%,#ffd568 100%);
  box-shadow: 0 0 7px rgba(93,240,255,.42);
  position: relative;
  border-radius: 5px;
}
.matrix-progress i::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg,transparent,white,transparent);
  animation: barSweep 2.2s linear infinite;
}
@keyframes barSweep { from { transform: translateX(-100%); } to { transform: translateX(100%); } }

.trend { padding: 0; }
.trend svg {
  position: absolute;
  inset: 52px 12px 34px 16px;
  width: calc(100% - 28px);
  height: calc(100% - 86px);
  filter: drop-shadow(0 0 1px rgba(83,230,255,.2));
}
.trend-line.cyan-line {
  stroke-dasharray: 900;
  stroke-dashoffset: 900;
  animation: drawLine 2.6s 1.1s ease forwards;
}
.trend-line.gold-line {
  stroke-dasharray: 900;
  stroke-dashoffset: 900;
  animation: drawLine 2.8s .65s ease forwards;
}
@keyframes drawLine { to { stroke-dashoffset: 0; } }
.dot-group circle {
  transform-box: fill-box;
  transform-origin: center;
  animation: dotPulse 2.3s ease-in-out infinite;
}
@keyframes dotPulse { 50% { transform: scale(1.35); filter: drop-shadow(0 0 5px #ffd778); } }
.legend {
  position: absolute;
  bottom: 8px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 32px;
  font-size: 10px;
  color: #cbeef7;
  letter-spacing: .4px;
}
.legend span {
  padding: 3px 8px;
  border: 1px solid rgba(83,221,255,.18);
  background: rgba(4,35,49,.25);
  backdrop-filter: blur(6px);
}
.legend b {
  display: inline-block;
  width: 23px;
  height: 2px;
  margin-right: 6px;
  vertical-align: middle;
  box-shadow: 0 0 4px currentColor;
}
.legend .c { color: #52e9ff; background: #52e9ff; }
.legend .g { color: #ffd875; background: #ffd875; }

.growth { overflow: hidden; }
.growth::before {
  content: "";
  position: absolute;
  left: 4%;
  right: 3%;
  bottom: 5%;
  height: 27%;
  background:
    repeating-linear-gradient(90deg,rgba(71,220,255,.08) 0 1px,transparent 1px 29px),
    repeating-linear-gradient(0deg,rgba(71,220,255,.08) 0 1px,transparent 1px 22px);
  transform: perspective(260px) rotateX(64deg);
  transform-origin: bottom;
  opacity: .45;
}
.growth::after {
  content: "";
  position: absolute;
  right: -24%;
  top: -16%;
  width: 92%;
  height: 90%;
  background: radial-gradient(circle at 55% 52%,rgba(255,198,74,.32),transparent 52%);
  filter: blur(5px);
  animation: goldAura 3.5s ease-in-out infinite;
}
@keyframes goldAura { 50% { opacity: .62; transform: scale(1.04); } }
.steps {
  position: absolute;
  left: 6%;
  right: 22%;
  bottom: 8%;
  height: 76%;
  display: flex;
  align-items: flex-end;
  gap: 0;
  perspective: 500px;
  transform: skewY(-2deg);
}
.step {
  position: absolute;
  left: var(--x);
  bottom: var(--b);
  width: 38%;
  height: 13%;
  border: 1px solid rgba(121,244,255,.86);
  background: linear-gradient(90deg,rgba(31,181,227,.42),rgba(75,231,255,.13));
  box-shadow: inset 0 0 16px rgba(83,235,255,.10),0 6px 18px rgba(1,7,15,.28);
  padding: 4px 6px;
  font-weight: 800;
  font-size: 9px;
  color: #eaffff;
  transform: skewY(2deg);
  transition: transform .25s,filter .25s;
  clip-path: polygon(0 10%,90% 0,100% 12%,100% 100%,0 100%);
}
.step::before {
  content: "";
  position: absolute;
  left: 8%;
  right: 10%;
  top: 3px;
  height: 1px;
  background: linear-gradient(90deg,transparent,currentColor,transparent);
  opacity: .48;
}
.step:hover { transform: skewY(2deg) translateY(-2px); filter: brightness(1.16); }
.step.gold {
  border-color: #ffe79d;
  background: linear-gradient(90deg,rgba(255,195,67,.42),rgba(255,229,143,.12));
  box-shadow: 0 0 15px rgba(255,198,82,.35);
  color: #fff0b2;
  text-shadow: 0 0 6px rgba(255,220,117,.45);
}
.step::after {
  content: "";
  position: absolute;
  left: 100%;
  top: 4px;
  width: 40px;
  height: 1px;
  border-top: 1px dashed rgba(210,232,239,.45);
}
.score {
  position: absolute;
  right: 2%;
  bottom: calc(var(--b) + 1%);
  font-size: 8px;
  border: 1px solid rgba(159,225,243,.4);
  padding: 2px 3px;
  border-radius: 2px;
  color: #f4ffff;
  background: rgba(4,21,31,.15);
  box-shadow: inset 0 0 8px rgba(69,217,255,.04);
  z-index: 3;
  backdrop-filter: blur(4px);
}

.timeline { padding: 0; }
.viewbtn {
  position: absolute;
  right: 8px;
  top: 36px;
  border: 1px solid rgba(86,222,255,.4);
  padding: 3px 6px;
  font-size: 8px;
  color: #9dd7eb;
  background: linear-gradient(180deg,rgba(13,75,99,.12),rgba(2,31,44,.12));
  box-shadow: inset 0 0 8px rgba(77,225,255,.04);
  cursor: pointer;
  z-index: 5;
  backdrop-filter: blur(4px);
}
.line {
  position: absolute;
  left: 40%;
  top: 25%;
  bottom: 8%;
  width: 1px;
  background: linear-gradient(transparent,#8af6ff 7%,#5fe9ff 92%,transparent);
  box-shadow: 0 0 8px rgba(86,238,255,.85);
}
.line::after {
  content: "";
  position: absolute;
  bottom: -5px;
  left: -4px;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 8px solid #67edff;
}
.datebox {
  position: absolute;
  top: 20%;
  left: 6%;
  width: 34%;
  padding: 6px 4px;
  border: 1px solid #65efff;
  border-radius: 4px;
  text-align: center;
  background: rgba(2,35,50,.15);
  box-shadow: inset 0 0 14px rgba(58,217,255,.04),0 0 13px rgba(77,234,255,.12);
  font-size: 9px;
  font-weight: 800;
  clip-path: polygon(5px 0,100% 0,100% calc(100% - 5px),calc(100% - 5px) 100%,0 100%,0 5px);
  backdrop-filter: blur(6px);
}
.datebox b {
  display: block;
  color: #74ecff;
  font-size: 11px;
}
.datebox::after {
  content: "";
  position: absolute;
  right: -21%;
  bottom: -11px;
  width: 21%;
  height: 1px;
  background: #71efff;
}
.datebox::before {
  content: "";
  position: absolute;
  right: -21%;
  bottom: -20px;
  width: 1px;
  height: 10px;
  background: #71efff;
}
.event {
  position: absolute;
  left: 45%;
  width: 48%;
  padding: 5px 6px;
  border: 1px solid rgba(70,222,255,.4);
  border-radius: 3px;
  background: linear-gradient(90deg,rgba(5,40,57,.18),rgba(2,21,34,.18));
  font-size: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  box-shadow: inset 0 0 12px rgba(59,210,245,.03);
  transition: transform .2s,border-color .2s;
  backdrop-filter: blur(6px);
}
.event::before {
  content: "";
  position: absolute;
  left: -15px;
  top: 50%;
  width: 12px;
  height: 1px;
  background: rgba(88,231,255,.3);
}
.event::after {
  content: "";
  position: absolute;
  left: -19px;
  top: calc(50% - 4px);
  width: 7px;
  height: 7px;
  border-radius: 50%;
  border: 2px solid #62efff;
  background: transparent;
  box-shadow: 0 0 7px #62efff;
  animation: nodePulse 2.2s ease-in-out infinite;
}
.event.gold::after {
  border-color: #ffe07e;
  box-shadow: 0 0 7px #ffe07e;
}
.event.e2::after { animation-delay: .4s; }
.event.e3::after { animation-delay: .8s; }
.event.e4::after { animation-delay: 1.2s; }
.event.e5::after { animation-delay: 1.6s; }
@keyframes nodePulse {
  50% { box-shadow: 0 0 14px currentColor; transform: scale(1.18); }
}
.event:hover { transform: translateX(3px); border-color: #8af6ff; }
.event.e1 { top: 31%; }
.event.e2 { top: 46%; }
.event.e3 { top: 61%; }
.event.e4 { top: 78%; }
.event.e5 { top: 90%; transform: translateY(-100%); }

.bottom-row {
  position: relative;
  border: 1px solid rgba(99,235,255,.28);
  display: grid;
  grid-template-columns: repeat(6,1fr);
  gap: 1px;
  background: linear-gradient(180deg,rgba(4,24,38,.1),rgba(2,13,24,.15));
  overflow: hidden;
  z-index: 2;
  box-shadow: inset 0 0 24px rgba(20,137,172,.04);
  backdrop-filter: blur(8px) saturate(1.05);
  border-radius: 8px;
}
.bottom-row::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 0%,rgba(24,91,124,.14),transparent 40%);
  pointer-events: none;
}
.bottom-row::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 1px;
  background: linear-gradient(90deg,transparent,#67efff 15%,transparent 50%,#67efff 85%,transparent);
  opacity: .55;
}
.gauge-card {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid rgba(61,171,205,.18);
  transition: background .2s;
}
.gauge-card:hover {
  background: radial-gradient(circle at 50% 43%,rgba(56,224,255,.07),transparent 48%);
}
.gauge {
  width: min(9vw,102px);
  aspect-ratio: 1;
  border-radius: 50%;
  position: relative;
  display: grid;
  place-items: center;
  background: conic-gradient(var(--accent,#5ceeff) calc(var(--v)*1%),rgba(63,133,157,.22) 0);
  mask: radial-gradient(circle,transparent 0 54%,#000 56%);
  filter: drop-shadow(0 0 7px rgba(62,225,255,.22));
  animation: gaugeIn 1.3s ease both;
}
.gauge::before {
  content: "";
  position: absolute;
  inset: 7px;
  border-radius: 50%;
  border: 2px dashed rgba(126,240,255,.35);
}
.gauge::after {
  content: "";
  position: absolute;
  inset: -9px;
  border-radius: 50%;
  border: 1px dashed rgba(89,229,255,.20);
  animation: spinRing 16s linear infinite;
}
.gauge-card:nth-child(even) .gauge::after { animation-direction: reverse; }
@keyframes gaugeIn {
  from { transform: scale(.75) rotate(-28deg); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
@keyframes spinRing { to { transform: rotate(360deg); } }
.gauge-center {
  position: absolute;
  top: 33%;
  left: 0;
  right: 0;
  text-align: center;
  font-weight: 900;
  font-size: clamp(15px,1.6vw,26px);
  text-shadow: 0 0 8px rgba(114,244,255,.45),0 0 24px rgba(51,221,255,.12);
}
.gauge-label {
  position: absolute;
  top: 70%;
  left: 0;
  right: 0;
  text-align: center;
  font-weight: 800;
  font-size: clamp(9px,.9vw,13px);
  letter-spacing: .5px;
}
.gauge-label::before {
  display: inline-block;
  margin-right: 6px;
  color: #5eeeff;
  text-shadow: 0 0 5px #45e3ff;
  font-weight: 400;
}
.gauge-card:nth-child(1) .gauge-label::before { content: "▥"; }
.gauge-card:nth-child(2) .gauge-label::before { content: "◇"; }
.gauge-card:nth-child(3) .gauge-label::before { content: "ϟ"; }
.gauge-card:nth-child(4) .gauge-label::before { content: "◷"; }
.gauge-card:nth-child(5) .gauge-label::before { content: "↗"; }
.gauge-card:nth-child(6) .gauge-label::before { content: "⬡"; }
.gauge-bar {
  position: absolute;
  left: 12%;
  right: 12%;
  bottom: 8%;
  height: 4px;
  border: 1px solid rgba(72,220,255,.25);
  background: rgba(7,38,52,.55);
  overflow: hidden;
  border-radius: 4px;
}
.gauge-bar i {
  display: block;
  height: 100%;
  width: var(--v);
  background: linear-gradient(90deg,#46e8ff,#8dfcff 75%,#ffd369);
  box-shadow: 0 0 6px rgba(85,238,255,.4);
  position: relative;
  border-radius: 4px;
}
.gauge-bar i::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg,transparent,rgba(255,255,255,.9),transparent);
  animation: barSweep 2.8s linear infinite;
}

@media (max-width: 1200px) {
  .evo-dashboard { grid-template-rows: 18% 56% 26%; }
  .summary-row { gap: 10px; padding: 0 10px; }
  .middle-row { grid-template-columns: 22% 34% 20% 24%; }
  .event { font-size: 8px; }
  .step { font-size: 9px; padding: 5px 7px; }
}
</style>
