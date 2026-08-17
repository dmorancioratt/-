<template>
  <div class="growth-cockpit">
    <div class="gc-atmosphere" aria-hidden="true">
      <CosmosBackground />
    </div>
    <button v-if="isStandalone" class="gc-back-btn" @click="goBack" title="返回">
      <el-icon><ArrowLeft /></el-icon>
      <span>返回</span>
    </button>
    <div class="gc-page-header">
      <h1 class="gc-page-title">个人成长驾驶舱</h1>
      <p class="gc-page-subtitle">探索能力边界 · 成就职业未来</p>
    </div>
    <div class="gc-content">
      <div class="gc-left">
        <div class="gc-card match-card animate-card clickable-card" style="--delay:0.1s" @click="navigateTo('/match-analysis')" title="查看匹配详情">
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

        <div class="gc-card radar-card animate-card clickable-card" style="--delay:0.2s" @click="navigateTo('/skill-graph')" title="查看能力图谱">
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

        <div class="gc-card resume-card animate-card clickable-card" style="--delay:0.3s" @click="navigateTo('/resume-parser')" title="查看简历详情">
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
          <div class="resume-skills">
            <span v-for="tag in resume.keySkills" :key="tag" class="resume-tag">{{ tag }}</span>
          </div>
          <button class="resume-detail" @click="navigateTo('/resume-parser')">
            <span>查看详情</span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
          </button>
        </div>

        <div class="gc-card recommend-card animate-card clickable-card" style="--delay:0.35s" @click="navigateTo('/match-analysis')" title="查看岗位匹配">
          <div class="card-corner card-corner-tl"></div>
          <div class="card-corner card-corner-tr"></div>
          <div class="card-corner card-corner-bl"></div>
          <div class="card-corner card-corner-br"></div>
          <div class="card-border-glow" style="background: linear-gradient(135deg, transparent 20%, rgba(143,124,255,0.25) 50%, rgba(78,216,255,0.15) 70%, transparent 90%)"></div>
          <div class="card-header">
            <h3><span class="header-bar"></span>推荐岗位</h3>
          </div>
          <div class="recommend-list">
            <div v-for="(job, i) in recommendJobs" :key="job.name" class="recommend-item" :class="{'top': i===0}" @click.stop="navigateTo('/match-analysis')">
              <div class="rj-rank">{{ i+1 }}</div>
              <div class="rj-info">
                <div class="rj-name">{{ job.name }}</div>
                <div class="rj-meta">{{ job.company }} · {{ job.city }} · {{ job.salary }}</div>
              </div>
              <div class="rj-match">
                <div class="rj-score" :class="job.trend">{{ job.score }}%</div>
                <div class="rj-trend" :class="job.trend">{{ job.trend === 'up' ? '↑' : job.trend === 'down' ? '↓' : '→' }}{{ Math.abs(job.change) }}%</div>
              </div>
            </div>
          </div>
          <div class="match-trend-chart">
            <div class="trend-chart-title">匹配度变化趋势</div>
            <svg class="trend-svg" viewBox="0 0 280 60" preserveAspectRatio="none">
              <defs>
                <linearGradient id="trendArea" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="rgba(78,216,255,0.2)"/>
                  <stop offset="100%" stop-color="rgba(78,216,255,0)"/>
                </linearGradient>
              </defs>
              <path :d="trendAreaPath" fill="url(#trendArea)"/>
              <path :d="trendLinePath" fill="none" stroke="#4ed8ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle v-for="(p, i) in trendPoints" :key="i" :cx="p.x" :cy="p.y" r="3" fill="#061830" stroke="#4ed8ff" stroke-width="1.5"/>
            </svg>
            <div class="trend-labels">
              <span v-for="m in trendMonths" :key="m">{{ m }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="gc-center">
        <div class="galaxy-card animate-card clickable-card" style="--delay:0.15s" @click="navigateTo('/skill-graph')" title="查看完整能力图谱">
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
              <span><strong>{{ galaxySkills.filter(s=>s.status==='improve').length }}</strong> 待提升</span>
              <span><strong>{{ galaxySkills.filter(s=>s.status==='missing').length }}</strong> 缺失</span>
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
            
            <svg class="skill-connectors" viewBox="-240 -240 480 480">
              <defs>
                <linearGradient id="connMastered" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="rgba(55,214,165,0)"/>
                  <stop offset="100%" stop-color="rgba(55,214,165,0.5)"/>
                </linearGradient>
                <linearGradient id="connImprove" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="rgba(143,124,255,0)"/>
                  <stop offset="100%" stop-color="rgba(143,124,255,0.4)"/>
                </linearGradient>
                <linearGradient id="connTransfer" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="rgba(255,182,92,0)"/>
                  <stop offset="100%" stop-color="rgba(255,182,92,0.4)"/>
                </linearGradient>
                <linearGradient id="connMissing" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="rgba(255,112,136,0)"/>
                  <stop offset="100%" stop-color="rgba(255,112,136,0.5)"/>
                </linearGradient>
              </defs>
              <g v-for="(skill, i) in galaxySkills" :key="'conn'+i">
                <line 
                  :x1="0" :y1="0" 
                  :x2="getSkillXY(i).x" :y2="getSkillXY(i).y"
                  :stroke="getConnColor(skill.status)"
                  stroke-width="1.2"
                  :stroke-dasharray="skill.status==='missing' ? '6,6' : 'none'"
                  :opacity="selectedSkill?.name===skill.name ? 1 : 0.3"
                  class="connector-line"
                />
              </g>
            </svg>

            <div class="galaxy-nodes-rotator" :style="{animationDuration: orbitSpeed + 's'}">
              <div class="galaxy-nodes-wrapper">
                <div v-for="(skill, i) in galaxySkills" :key="skill.name" 
                  class="skill-node" :class="[skill.status, {'pulse-node': i%5===0, 'big-node': skill.level>=15, 'selected': selectedSkill?.name===skill.name}]"
                  :style="skillPosStyle(i, galaxySkills.length)"
                  @click="selectSkill(skill)">
                  <div class="node-bg"></div>
                  <div class="node-ring"></div>
                  <div class="node-pulse"></div>
                  <div class="node-short">{{ skill.short }}</div>
                  <div class="node-label">{{ skill.name }}</div>
                </div>
              </div>
            </div>

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
          </div>
          <div class="galaxy-legend">
            <span class="gl-item mastered"><i></i>已掌握</span>
            <span class="gl-item improve"><i></i>待提升</span>
            <span class="gl-item missing"><i></i>缺失（断点）</span>
            <span class="gl-item transfer"><i></i>可迁移</span>
          </div>
        </div>

        <div class="learning-path-wrap animate-card clickable-card" style="--delay:0.35s" @click="navigateTo('/learning-path')" title="查看学习路径">
          <div class="card-corner card-corner-tl"></div>
          <div class="card-corner card-corner-tr"></div>
          <div class="card-corner card-corner-bl"></div>
          <div class="card-corner card-corner-br"></div>
          <div class="card-border-glow"></div>
          <div class="lp-header">
            <h2><span class="title-deco"></span>学习路径</h2>
            <p>登山式成长轨迹 · 你的专属攀登计划</p>
          </div>
          <div class="lp-progress-bar">
            <div class="lp-progress-fill" :style="{width: learningProgress + '%'}"></div>
            <span class="lp-progress-text">已完成 {{ learningProgress }}%</span>
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
              <path class="lp-path" d="M50,290 C150,270 200,250 300,230 S450,180 500,170 S650,130 700,110 S850,70 950,50" fill="none" stroke="url(#pathGrad)" stroke-width="4" stroke-linecap="round" filter="url(#pathGlow)" stroke-dasharray="2000" :stroke-dashoffset="2000 - (2000 * learningProgress / 100)"/>
              <path class="lp-path-glow" d="M50,290 C150,270 200,250 300,230 S450,180 500,170 S650,130 700,110 S850,70 950,50" fill="none" stroke="url(#pathGrad)" stroke-width="8" stroke-linecap="round" opacity="0.3" filter="url(#pathGlow)" stroke-dasharray="2000" :stroke-dashoffset="2000 - (2000 * learningProgress / 100)"/>
            </svg>
            <div v-for="(stop, i) in learningStops" :key="stop.name" class="lp-stop" :class="{done: stop.done, current: stop.current, locked: !stop.done && !stop.current}" :style="{left: stop.x+'%', bottom: stop.y+'%'}" @click.stop="navigateTo('/learning-path')">
              <div class="stop-pulse" v-if="stop.current"></div>
              <div class="stop-glow"></div>
              <div class="stop-dot">{{ i+1 }}</div>
              <div class="stop-label">{{ stop.name }}</div>
            </div>
            <div class="lp-current-pos" v-if="currentStop">
              <div class="pos-ping"></div>
              <div class="pos-dot"></div>
              <div class="pos-label">当前位置</div>
            </div>
          </div>
        </div>
      </div>

      <div class="gc-right">
        <div class="gc-card next-action animate-card clickable-card" style="--delay:0.12s" @click="navigateTo('/learning-path')" title="查看学习计划">
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
          <button class="action-start" @click.stop="navigateTo('/learning-path')">
            <span class="btn-shine"></span>
            <span class="btn-text">立即开始</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
          </button>
        </div>

        <div class="gc-card plan-card animate-card clickable-card" style="--delay:0.22s" @click="navigateTo('/learning-path')" title="查看成长计划">
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
                <svg v-if="item.done" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#041210" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
              </div>
              <div class="pi-content">
                <div class="pi-title">{{ item.title }}</div>
                <div class="pi-time">{{ item.time }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="gc-card interview-card animate-card clickable-card" style="--delay:0.28s" @click="navigateTo('/digital-interviewer')" title="进入模拟面试">
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
          <div class="interview-history">
            <div class="ih-title">最近能力变化</div>
            <div class="ih-bars">
              <div v-for="(score, i) in interview.history" :key="i" class="ih-bar-wrap">
                <div class="ih-bar" :style="{height: score + '%'}"></div>
                <span class="ih-label">{{ i+1 }}月</span>
              </div>
            </div>
          </div>
          <button class="interview-btn" @click.stop="navigateTo('/digital-interviewer')">开始新面试 ></button>
        </div>

        <div class="gc-card timeline-card animate-card clickable-card" style="--delay:0.38s" @click="navigateTo('/capability-evolution')" title="查看能力演化">
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

    <Transition name="skill-detail">
      <div v-if="selectedSkill" class="skill-detail-overlay" @click.self="selectedSkill=null">
        <div class="skill-detail-panel">
          <button class="sdp-close" @click="selectedSkill=null">×</button>
          <div class="sdp-header" :class="selectedSkill.status">
            <div class="sdp-status-badge">
              <span class="sdp-dot"></span>
              {{ statusLabels[selectedSkill.status] }}
            </div>
            <h2>{{ selectedSkill.name }}</h2>
            <p class="sdp-category">{{ selectedSkill.category }}</p>
          </div>
          <div class="sdp-level">
            <div class="sdp-level-label">当前等级</div>
            <div class="sdp-level-bar">
              <div class="sdp-level-fill" :class="selectedSkill.status" :style="{width: selectedSkill.level*5+'%'}"></div>
              <span class="sdp-level-num">Lv.{{ selectedSkill.level }}</span>
            </div>
          </div>
          <div class="sdp-section">
            <h4><span class="sdp-icon">📋</span>技能证据</h4>
            <ul class="sdp-evidence">
              <li v-for="(ev, i) in selectedSkill.evidence" :key="i">
                <span class="ev-dot"></span>{{ ev }}
              </li>
            </ul>
          </div>
          <div class="sdp-section">
            <h4><span class="sdp-icon">📚</span>能力来源</h4>
            <div class="sdp-sources">
              <span v-for="src in selectedSkill.sources" :key="src" class="sdp-source-tag">{{ src }}</span>
            </div>
          </div>
          <div class="sdp-section sdp-suggest" v-if="selectedSkill.suggestion">
            <h4><span class="sdp-icon">💡</span>学习建议</h4>
            <p>{{ selectedSkill.suggestion }}</p>
            <div v-if="selectedSkill.resources" class="sdp-resources">
              <div v-for="res in selectedSkill.resources" :key="res.name" class="sdp-res">
                <span class="res-type">{{ res.type }}</span>
                <span class="res-name">{{ res.name }}</span>
              </div>
            </div>
          </div>
          <div class="sdp-actions">
            <button class="sdp-btn primary" @click.stop="navigateTo('/learning-path')">开始学习</button>
            <button class="sdp-btn" @click="selectedSkill=null">关闭</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import CosmosBackground from '@/components/CosmosBackground.vue'
import { ArrowLeft } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const isStandalone = computed(() => route.meta.public === true || !route.meta.fullscreen)

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/login')
  }
}

function navigateTo(path: string) {
  router.push(path)
}

const user = { name: '张同学', edu: '计算机科学与技术 · 大三', targetRole: 'AI算法工程师' }
const targetRole = { name: 'AI算法工程师', level: '中级', city: '北京', score: 72, improve: 4 }
const resume = { 
  score: 85, 
  grade: '优秀', 
  updatedAt: '2天前', 
  comment: '简历结构清晰，项目经历突出，建议补充量化成果和技术栈深度描述。',
  keySkills: ['Python', 'PyTorch', '机器学习', '深度学习', '数据结构']
}
const nextAction = { title: '深入学习RAG知识库问答系统', desc: '掌握检索增强生成核心技术，完成一个端到端的问答项目', duration: '预计14天', impact: 8 }
const weekPlan = { done: 3, total: 5, items: [
  { title: '完成Transformer架构学习', time: '周一', done: true },
  { title: '动手实现Attention机制', time: '周二', done: true },
  { title: '学习向量数据库Milvus', time: '周三', done: true },
  { title: '完成RAG项目demo', time: '周四', done: false },
  { title: '撰写技术博客总结', time: '周五', done: false }
]}
const interview = { score: 78, improve: 12, correctRate: 72, avgTime: 45, count: 15, history: [52, 58, 63, 60, 68, 72, 78] }
const timeline = [
  { date: '08-12', text: '完成深度学习基础课程，掌握CNN/RNN核心原理' },
  { date: '08-08', text: 'Python编程技能达到Lv.18，进入熟练阶段' },
  { date: '08-01', text: '匹配度提升4%，算法基础能力显著增强' },
  { date: '07-25', text: '完成第一个ML项目，鸢尾花分类准确率96%' },
  { date: '07-15', text: '开始系统学习机器学习，完成吴恩达课程' }
]

const recommendJobs = [
  { name: 'AI算法工程师', company: '字节跳动', city: '北京', salary: '25-40K', score: 72, trend: 'up', change: 4 },
  { name: 'NLP算法工程师', company: '百度', city: '北京', salary: '22-35K', score: 68, trend: 'up', change: 6 },
  { name: '机器学习工程师', company: '美团', city: '北京', salary: '20-35K', score: 65, trend: 'up', change: 2 },
  { name: 'CV算法工程师', company: '商汤科技', city: '上海', salary: '23-38K', score: 58, trend: 'stable', change: 0 },
]

const trendMonths = ['2月', '3月', '4月', '5月', '6月', '7月', '8月']
const trendScores = [45, 52, 55, 60, 63, 68, 72]
const trendPoints = computed(() => {
  return trendScores.map((score, i) => ({
    x: 20 + i * 40,
    y: 50 - (score - 40) * 0.8
  }))
})
const trendLinePath = computed(() => {
  return trendPoints.value.map((p, i) => `${i===0?'M':'L'}${p.x},${p.y}`).join(' ')
})
const trendAreaPath = computed(() => {
  const line = trendPoints.value.map((p, i) => `${i===0?'M':'L'}${p.x},${p.y}`).join(' ')
  return `${line} L260,55 L20,55 Z`
})

const learningStops = [
  { name: '基础巩固', x: 8, y: 12, done: true, current: false },
  { name: '算法进阶', x: 25, y: 28, done: true, current: false },
  { name: 'ML实战', x: 42, y: 45, done: true, current: false },
  { name: 'DL专精', x: 58, y: 58, done: false, current: true },
  { name: '大模型', x: 75, y: 72, done: false, current: false },
  { name: '就业准备', x: 92, y: 88, done: false, current: false }
]
const learningProgress = computed(() => {
  const done = learningStops.filter(s => s.done).length
  const total = learningStops.length
  const currentIdx = learningStops.findIndex(s => s.current)
  return Math.round((done + (currentIdx >= 0 ? 0.5 : 0)) / total * 100)
})
const currentStop = computed(() => learningStops.find(s => s.current))

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
    return `${120 + Math.cos(angle) * v},${120 + Math.sin(angle) * v}`
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

const statusLabels: Record<string, string> = {
  mastered: '已掌握',
  improve: '待提升',
  missing: '缺失技能',
  transfer: '可迁移'
}

const galaxySkills = ref([
  { name: 'Python', short: 'Py', level: 18, status: 'mastered', category: '编程语言', 
    evidence: ['完成15个Python项目', 'LeetCode刷题200+', '技术博客12篇'],
    sources: ['项目实践', '课程学习', '开源贡献'],
    suggestion: '继续深入Python高级特性，关注性能优化和工程化实践。'
  },
  { name: '机器学习', short: 'ML', level: 16, status: 'mastered', category: 'AI核心',
    evidence: ['完成吴恩达ML课程', '实现6种经典算法', 'Kaggle比赛铜牌'],
    sources: ['课程认证', '竞赛经历', '项目实践'],
    suggestion: '可以尝试更复杂的集成学习方法，参与更多实战项目。'
  },
  { name: '深度学习', short: 'DL', level: 14, status: 'improve', category: 'AI核心',
    evidence: ['掌握CNN/RNN基础', '完成图像分类项目'],
    sources: ['课程学习', '项目实践'],
    suggestion: '建议深入学习Transformer架构，多动手复现经典论文。',
    resources: [{type: '课程', name: '李沐深度学习'}, {type: '书籍', name: 'Dive into Deep Learning'}]
  },
  { name: 'PyTorch', short: 'PT', level: 15, status: 'mastered', category: '框架工具',
    evidence: ['使用PyTorch完成8个项目', '自定义模型训练流程'],
    sources: ['项目实践', '官方文档'],
    suggestion: '继续探索TorchScript部署和分布式训练。'
  },
  { name: 'NLP', short: 'NLP', level: 12, status: 'improve', category: 'AI领域',
    evidence: ['完成文本分类任务', '了解Word2Vec原理'],
    sources: ['课程学习', '项目实践'],
    suggestion: '建议系统学习Transformer和大模型相关技术。',
    resources: [{type: '课程', name: 'CS224N'}, {type: '书籍', name: 'Speech and Language Processing'}]
  },
  { name: 'CV', short: 'CV', level: 10, status: 'improve', category: 'AI领域',
    evidence: ['了解ResNet架构', '完成简单目标检测'],
    sources: ['课程学习'],
    suggestion: '建议学习YOLO系列和检测Transformer，多做实战项目。'
  },
  { name: 'TensorFlow', short: 'TF', level: 11, status: 'transfer', category: '框架工具',
    evidence: ['有PyTorch基础可快速迁移', '了解Keras API'],
    sources: ['迁移学习'],
    suggestion: 'PyTorch基础扎实，TensorFlow可快速上手，建议按需学习。'
  },
  { name: 'RAG', short: 'RAG', level: 6, status: 'missing', category: '前沿技术',
    evidence: [],
    sources: [],
    suggestion: 'RAG是当前大模型应用热门方向，建议系统学习：向量数据库、检索策略、Prompt工程。',
    resources: [{type: '教程', name: 'LangChain官方文档'}, {type: '项目', name: '构建个人知识库问答'}]
  },
  { name: 'LangChain', short: 'LC', level: 5, status: 'missing', category: '前沿技术',
    evidence: [],
    sources: [],
    suggestion: 'LangChain是LLM应用开发框架，建议结合RAG项目一起学习。'
  },
  { name: '向量数据库', short: 'VDB', level: 8, status: 'improve', category: '工程能力',
    evidence: ['了解向量检索原理', '使用过FAISS'],
    sources: ['技术调研'],
    suggestion: '建议深入学习Milvus/Chroma等向量数据库，掌握索引优化技巧。'
  },
  { name: '数据结构', short: 'DS', level: 17, status: 'mastered', category: '计算机基础',
    evidence: ['LeetCode刷题300+', '掌握常见数据结构'],
    sources: ['刷题训练', '课程学习'],
    suggestion: '基础扎实，可以开始挑战Hard题目，学习高级数据结构。'
  },
  { name: 'SQL', short: 'SQL', level: 14, status: 'mastered', category: '工程能力',
    evidence: ['熟练使用SQL查询', '了解数据库索引原理'],
    sources: ['项目实践'],
    suggestion: '建议学习查询优化和分布式数据库相关知识。'
  },
  { name: 'Linux', short: 'LX', level: 13, status: 'improve', category: '工程能力',
    evidence: ['熟悉常用Linux命令', '能在Linux环境开发'],
    sources: ['日常使用'],
    suggestion: '建议学习Shell脚本编程和系统性能调优。'
  },
  { name: 'Git', short: 'Git', level: 15, status: 'mastered', category: '工程能力',
    evidence: ['熟练使用Git版本控制', '了解Git Flow工作流'],
    sources: ['项目实践'],
    suggestion: '可以学习Git高级功能，如rebase、cherry-pick等。'
  },
  { name: 'Docker', short: 'Doc', level: 9, status: 'improve', category: '工程能力',
    evidence: ['了解Docker基本命令', '能编写简单Dockerfile'],
    sources: ['技术学习'],
    suggestion: '建议学习Docker Compose和K8s基础，掌握容器化部署。'
  },
  { name: '算法', short: 'Alg', level: 16, status: 'mastered', category: '计算机基础',
    evidence: ['掌握常见算法设计模式', '算法竞赛校赛获奖'],
    sources: ['竞赛训练', '刷题'],
    suggestion: '继续保持刷题习惯，关注算法在实际工程中的应用。'
  },
  { name: '大模型', short: 'LLM', level: 7, status: 'missing', category: '前沿技术',
    evidence: ['了解GPT基本原理'],
    sources: ['技术阅读'],
    suggestion: '大模型是AI核心方向，建议学习：预训练、SFT、RLHF、LoRA微调。',
    resources: [{type: '课程', name: 'CS224W/CS229N'}, {type: '论文', name: '必读论文100篇'}]
  },
  { name: 'Prompt工程', short: 'PR', level: 11, status: 'transfer', category: '前沿技术',
    evidence: ['了解基本Prompt技巧', '使用过CoT'],
    sources: ['实践探索'],
    suggestion: '可以系统学习Prompt工程方法论，这是大模型时代的核心技能。'
  },
  { name: 'MLOps', short: 'MLO', level: 6, status: 'missing', category: '工程能力',
    evidence: [],
    sources: [],
    suggestion: 'MLOps是AI工程化关键能力，建议学习：MLflow、Kubeflow、CI/CD for ML。'
  },
  { name: '统计学', short: 'Sta', level: 13, status: 'improve', category: '数学基础',
    evidence: ['掌握概率论基础', '了解假设检验'],
    sources: ['课程学习'],
    suggestion: '建议加强贝叶斯统计和实验设计能力，对数据分析和建模很有帮助。'
  },
])
const selectedSkill = ref<any>(null)
const orbitSpeed = ref(180)

function getSkillXY(i: number) {
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
  return { x: Math.cos(angle) * r, y: Math.sin(angle) * r }
}

function skillPosStyle(i: number, total: number) {
  const pos = getSkillXY(i)
  return { '--x': `${pos.x}px`, '--y': `${pos.y}px` } as any
}

function getConnColor(status: string) {
  const colors: Record<string, string> = {
    mastered: 'url(#connMastered)',
    improve: 'url(#connImprove)',
    missing: 'url(#connMissing)',
    transfer: 'url(#connTransfer)'
  }
  return colors[status] || colors.mastered
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

function starStyle(s: number) {
  return {
    left: (Math.sin(s * 73.3) * 0.5 + 0.5) * 100 + '%',
    top: (Math.cos(s * 197.7) * 0.5 + 0.5) * 100 + '%',
    animationDelay: (s * 0.07) % 5 + 's',
    animationDuration: (2 + (s%3)) + 's'
  } as any
}

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

.gc-atmosphere {
  position: fixed;
  z-index: 0;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.gc-back-btn {
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(10, 25, 60, 0.75);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(0, 245, 255, 0.3);
  border-radius: 8px;
  color: #00f5ff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 0 20px rgba(0, 245, 255, 0.15);
}
.gc-back-btn:hover {
  background: rgba(0, 245, 255, 0.15);
  border-color: rgba(0, 245, 255, 0.6);
  box-shadow: 0 0 30px rgba(0, 245, 255, 0.3);
  transform: translateX(-2px);
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

.clickable-card { cursor: pointer; }
.clickable-card:hover { border-color: rgba(78,216,255,0.35); box-shadow: 0 12px 40px rgba(0,0,0,0.4), 0 0 20px rgba(78,216,255,0.1); }

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
  background: linear-gradient(180deg, #fff, #4ed8ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  filter: drop-shadow(0 0 15px rgba(78,216,255,0.4));
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
.resume-desc { font-size: 12px; color: rgba(200,216,238,0.85); line-height: 1.7; margin-bottom: 10px; }
.resume-skills { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.resume-tag {
  font-size: 10px;
  padding: 3px 8px;
  background: rgba(78,216,255,0.1);
  border: 1px solid rgba(78,216,255,0.2);
  border-radius: 4px;
  color: #4ed8ff;
}
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

.recommend-card {}
.recommend-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }
.recommend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: rgba(7,20,40,0.4);
  border-radius: 8px;
  border: 1px solid rgba(78,216,255,0.08);
  transition: all 0.3s;
}
.recommend-item:hover { border-color: rgba(78,216,255,0.2); background: rgba(78,216,255,0.05); }
.recommend-item.top { border-color: rgba(255,182,92,0.3); background: rgba(255,182,92,0.05); }
.rj-rank {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  background: rgba(78,216,255,0.15);
  color: #4ed8ff;
  flex-shrink: 0;
}
.recommend-item.top .rj-rank { background: linear-gradient(135deg, #ffb65c, #ff8c00); color: #1a0f00; }
.rj-info { flex: 1; min-width: 0; }
.rj-name { font-size: 13px; font-weight: 600; color: #e8f4ff; }
.rj-meta { font-size: 10px; color: rgba(168,180,200,0.6); margin-top: 2px; }
.rj-match { text-align: right; flex-shrink: 0; }
.rj-score { font-size: 16px; font-weight: 700; }
.rj-score.up { color: #37d6a5; }
.rj-score.down { color: #ff7088; }
.rj-score.stable { color: #4ed8ff; }
.rj-trend { font-size: 10px; font-weight: 600; }
.rj-trend.up { color: #37d6a5; }
.rj-trend.down { color: #ff7088; }
.rj-trend.stable { color: rgba(168,180,200,0.6); }
.match-trend-chart {}
.trend-chart-title { font-size: 11px; color: rgba(168,180,200,0.7); margin-bottom: 8px; }
.trend-svg { width: 100%; height: 60px; }
.trend-labels { display: flex; justify-content: space-between; font-size: 9px; color: rgba(168,180,200,0.5); margin-top: 4px; }

.galaxy-card { padding: 20px; }
.galaxy-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 8px; flex-wrap: wrap; gap: 8px; }
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
.galaxy-stats { display: flex; gap: 12px; flex-wrap: wrap; }
.galaxy-stats span { font-size: 11px; color: rgba(168,180,200,0.7); }
.galaxy-stats strong { color: #4ed8ff; font-size: 14px; font-weight: 700; margin-right: 3px; text-shadow: 0 0 8px rgba(78,216,255,0.5); }

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

.skill-connectors {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 480px;
  height: 480px;
  margin: -240px 0 0 -240px;
  z-index: 2;
  pointer-events: none;
}
.connector-line {
  transition: opacity 0.3s ease;
}

.orbit-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  border-radius: 50%;
  border: 1px dashed;
  pointer-events: none;
}
.orbit-ring-1 { width: 390px; height: 390px; margin: -195px 0 0 -195px; border-color: rgba(78,216,255,0.1); }
.orbit-ring-2 { width: 290px; height: 290px; margin: -145px 0 0 -145px; border-color: rgba(143,124,255,0.1); }
.orbit-ring-3 { width: 180px; height: 180px; margin: -90px 0 0 -90px; border-color: rgba(55,214,165,0.1); }

.galaxy-nodes-rotator {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 0;
  height: 0;
  animation: orbitRotate var(--duration, 180s) linear infinite;
}
.galaxy-nodes-wrapper {
  position: absolute;
  left: 0;
  top: 0;
  animation: orbitRotateRev var(--duration, 180s) linear infinite;
}
@keyframes orbitRotate { to { transform: rotate(360deg); } }
@keyframes orbitRotateRev { to { transform: rotate(-360deg); } }

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
.skill-node:hover { transform: translate(calc(-50% + var(--x)), calc(-50% + var(--y))) scale(1.2); z-index: 20; }
.skill-node.selected { transform: translate(calc(-50% + var(--x)), calc(-50% + var(--y))) scale(1.15); z-index: 20; }
.skill-node:hover .node-ring, .skill-node.selected .node-ring { border-width: 2.5px; }
.skill-node:hover .node-label, .skill-node.selected .node-label { opacity: 1; }
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
.mastered .node-bg { background: linear-gradient(135deg, rgba(55,214,165,0.2), rgba(6,18,40,0.95)); }
.improve .node-bg { background: linear-gradient(135deg, rgba(143,124,255,0.2), rgba(6,18,40,0.95)); }
.missing .node-bg { background: linear-gradient(135deg, rgba(255,112,136,0.2), rgba(6,18,40,0.95)); }
.transfer .node-bg { background: linear-gradient(135deg, rgba(255,182,92,0.2), rgba(6,18,40,0.95)); }
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
.mastered .node-ring { border-color: rgba(55,214,165,0.6); box-shadow: 0 0 12px rgba(55,214,165,0.3); }
.improve .node-ring { border-color: rgba(143,124,255,0.6); box-shadow: 0 0 12px rgba(143,124,255,0.3); }
.missing .node-ring { border-color: rgba(255,112,136,0.6); box-shadow: 0 0 12px rgba(255,112,136,0.3); border-style: dashed; }
.transfer .node-ring { border-color: rgba(255,182,92,0.6); box-shadow: 0 0 12px rgba(255,182,92,0.3); }
.skill-node.selected.mastered .node-ring { box-shadow: 0 0 20px rgba(55,214,165,0.6); }
.skill-node.selected.improve .node-ring { box-shadow: 0 0 20px rgba(143,124,255,0.6); }
.skill-node.selected.missing .node-ring { box-shadow: 0 0 20px rgba(255,112,136,0.6); }
.skill-node.selected.transfer .node-ring { box-shadow: 0 0 20px rgba(255,182,92,0.6); }
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

.galaxy-legend {
  display: flex;
  justify-content: center;
  gap: 18px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(78,216,255,0.06);
  flex-wrap: wrap;
}
.gl-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: rgba(140,165,195,0.8); }
.gl-item i { width: 8px; height: 8px; border-radius: 50%; }
.gl-item.mastered i { background: #37d6a5; box-shadow: 0 0 6px #37d6a5; }
.gl-item.improve i { background: #8f7cff; box-shadow: 0 0 6px #8f7cff; }
.gl-item.missing i { background: #ff7088; box-shadow: 0 0 6px #ff7088; border-radius: 2px; }
.gl-item.transfer i { background: #ffb65c; box-shadow: 0 0 6px #ffb65c; }

.lp-header { margin-bottom: 12px; }
.lp-header h2 { margin: 0 0 2px; font-size: 18px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 10px; }
.lp-header p { margin: 0; font-size: 12px; color: rgba(168,180,200,0.6); margin-left: 28px; }
.lp-progress-bar {
  position: relative;
  height: 20px;
  background: rgba(7,20,40,0.5);
  border-radius: 10px;
  margin-bottom: 12px;
  overflow: hidden;
  border: 1px solid rgba(78,216,255,0.1);
}
.lp-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4ed8ff, #8f7cff);
  border-radius: 10px;
  transition: width 1s ease;
  box-shadow: 0 0 10px rgba(78,216,255,0.4);
}
.lp-progress-text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  text-shadow: 0 1px 3px rgba(0,0,0,0.8);
}
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
  animation: pathDraw 3s ease-out forwards;
}
@keyframes pathDraw {
  from { stroke-dashoffset: 2000; }
}
.lp-stop {
  position: absolute;
  transform: translateX(-50%);
  text-align: center;
}
.stop-pulse {
  position: absolute;
  top: 0;
  left: 50%;
  width: 28px;
  height: 28px;
  margin: -4px 0 0 -14px;
  border-radius: 50%;
  background: rgba(255,182,92,0.3);
  animation: stopPulse 2s ease-out infinite;
}
@keyframes stopPulse {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(2.5); opacity: 0; }
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
  z-index: 2;
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
  margin: 0 auto;
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
  transform: translate(-50%,-50%);
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
  margin-bottom: 12px;
  padding: 12px 8px;
  background: rgba(7,20,40,0.5);
  border-radius: 8px;
  border: 1px solid rgba(78,216,255,0.06);
}
.stat-item { text-align: center; }
.stat-val { font-size: 18px; font-weight: 700; }
.stat-lbl { font-size: 10px; color: rgba(168,180,200,0.6); margin-top: 2px; }
.interview-history { margin-bottom: 12px; }
.ih-title { font-size: 11px; color: rgba(168,180,200,0.7); margin-bottom: 8px; }
.ih-bars { display: flex; align-items: flex-end; gap: 6px; height: 50px; padding: 0 4px; }
.ih-bar-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; }
.ih-bar {
  width: 100%;
  background: linear-gradient(180deg, #4ed8ff, rgba(78,216,255,0.3));
  border-radius: 3px 3px 0 0;
  min-height: 4px;
  transition: height 0.5s ease;
}
.ih-label { font-size: 8px; color: rgba(168,180,200,0.5); }
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

.skill-detail-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(0,5,15,0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.skill-detail-panel {
  position: relative;
  width: 100%;
  max-width: 420px;
  max-height: 80vh;
  overflow-y: auto;
  background: linear-gradient(180deg, rgba(10,25,55,0.98) 0%, rgba(5,15,35,0.99) 100%);
  border: 1px solid rgba(78,216,255,0.25);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(78,216,255,0.1);
}
.sdp-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid rgba(78,216,255,0.2);
  background: rgba(78,216,255,0.1);
  color: #8fa4c0;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.sdp-close:hover { background: rgba(255,112,136,0.2); border-color: rgba(255,112,136,0.4); color: #ff7088; }
.sdp-header { margin-bottom: 20px; }
.sdp-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 12px;
}
.sdp-status-badge.mastered { background: rgba(55,214,165,0.15); color: #37d6a5; border: 1px solid rgba(55,214,165,0.3); }
.sdp-status-badge.improve { background: rgba(143,124,255,0.15); color: #a78bfa; border: 1px solid rgba(143,124,255,0.3); }
.sdp-status-badge.missing { background: rgba(255,112,136,0.15); color: #ff7088; border: 1px solid rgba(255,112,136,0.3); }
.sdp-status-badge.transfer { background: rgba(255,182,92,0.15); color: #ffb65c; border: 1px solid rgba(255,182,92,0.3); }
.sdp-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}
.sdp-header h2 { margin: 0; font-size: 24px; font-weight: 700; color: #fff; }
.sdp-category { margin: 4px 0 0; font-size: 13px; color: rgba(168,180,200,0.7); }
.sdp-level { margin-bottom: 20px; }
.sdp-level-label { font-size: 12px; color: rgba(168,180,200,0.7); margin-bottom: 8px; }
.sdp-level-bar {
  position: relative;
  height: 24px;
  background: rgba(7,20,40,0.6);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(78,216,255,0.1);
}
.sdp-level-fill {
  height: 100%;
  border-radius: 12px;
  transition: width 0.8s ease;
}
.sdp-level-fill.mastered { background: linear-gradient(90deg, #37d6a5, #5ae8bc); box-shadow: 0 0 10px rgba(55,214,165,0.4); }
.sdp-level-fill.improve { background: linear-gradient(90deg, #8f7cff, #b0a0ff); box-shadow: 0 0 10px rgba(143,124,255,0.4); }
.sdp-level-fill.missing { background: linear-gradient(90deg, #ff7088, #ff9aab); box-shadow: 0 0 10px rgba(255,112,136,0.4); }
.sdp-level-fill.transfer { background: linear-gradient(90deg, #ffb65c, #ffcc88); box-shadow: 0 0 10px rgba(255,182,92,0.4); }
.sdp-level-num {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 1px 3px rgba(0,0,0,0.5);
}
.sdp-section { margin-bottom: 18px; }
.sdp-section h4 {
  margin: 0 0 10px;
  font-size: 13px;
  font-weight: 600;
  color: #c8d8ee;
  display: flex;
  align-items: center;
  gap: 6px;
}
.sdp-icon { font-size: 14px; }
.sdp-evidence {
  list-style: none;
  padding: 0;
  margin: 0;
}
.sdp-evidence li {
  font-size: 12px;
  color: rgba(200,216,238,0.8);
  padding: 6px 0;
  padding-left: 16px;
  position: relative;
  line-height: 1.5;
}
.ev-dot {
  position: absolute;
  left: 0;
  top: 12px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4ed8ff;
}
.sdp-sources { display: flex; flex-wrap: wrap; gap: 6px; }
.sdp-source-tag {
  font-size: 11px;
  padding: 4px 10px;
  background: rgba(78,216,255,0.1);
  border: 1px solid rgba(78,216,255,0.2);
  border-radius: 4px;
  color: #4ed8ff;
}
.sdp-suggest p {
  margin: 0;
  font-size: 12px;
  color: rgba(200,216,238,0.85);
  line-height: 1.7;
  padding: 12px;
  background: rgba(143,124,255,0.08);
  border-radius: 8px;
  border-left: 3px solid #8f7cff;
}
.sdp-resources { margin-top: 10px; display: flex; flex-direction: column; gap: 6px; }
.sdp-res {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: rgba(7,20,40,0.5);
  border-radius: 6px;
  font-size: 11px;
}
.res-type {
  padding: 2px 6px;
  background: rgba(78,216,255,0.15);
  border-radius: 3px;
  color: #4ed8ff;
  font-weight: 600;
  flex-shrink: 0;
}
.res-name { color: rgba(200,216,238,0.8); }
.sdp-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}
.sdp-btn {
  flex: 1;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid rgba(78,216,255,0.2);
  background: rgba(78,216,255,0.08);
  color: #4ed8ff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.sdp-btn:hover { background: rgba(78,216,255,0.15); }
.sdp-btn.primary {
  background: linear-gradient(135deg, #4ed8ff, #8f7cff);
  border: none;
  color: #041020;
  box-shadow: 0 4px 15px rgba(78,216,255,0.3);
}
.sdp-btn.primary:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(78,216,255,0.4); }

.skill-detail-enter-active, .skill-detail-leave-active { transition: all 0.3s ease; }
.skill-detail-enter-from, .skill-detail-leave-to { opacity: 0; }
.skill-detail-enter-from .skill-detail-panel, .skill-detail-leave-to .skill-detail-panel { transform: scale(0.9) translateY(20px); opacity: 0; }

@media (max-width: 1400px) {
  .gc-content { grid-template-columns: 250px 1fr 280px; gap: 12px; padding: 12px 14px; }
}
@media (max-width: 1100px) {
  .gc-content { grid-template-columns: 230px 1fr 260px; gap: 10px; padding: 10px 12px; }
}
@media (max-width: 900px) {
  .gc-content { grid-template-columns: 1fr; max-width: 700px; }
  .galaxy-scene { height: 400px; }
}
</style>
