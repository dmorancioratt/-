<template>
  <div class="cockpit-container" :class="{ 'panel-open': activePanel }">
    <!-- 返回概览按钮已隐藏（通过路由菜单返回） -->
    <button v-if="false && !activePanel" class="exit-cockpit-btn" @click="goToOverview">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
      <span>返回概览</span>
    </button>

    <div class="cockpit-scene" :class="sceneClass">
      <GrowthCabinImage @select="openPanel" />
    </div>

    <GrowthProfileMission
      v-if="activeMissionPanel === 'avatar'"
      @close="closePanel"
      @primary="handlePrimaryAction"
      @assist="switchPanel('ai-suggest')"
    />

    <LearningPathMission
      v-else-if="activeMissionPanel === 'path'"
      @close="closePanel"
    />

    <AchievementWallMission
      v-else-if="activeMissionPanel === 'timeline'"
      @close="closePanel"
    />

    <ImmersiveMissionCabin
      v-else-if="activeMissionPanel"
      :module-id="activeMissionPanel"
      @close="closePanel"
      @primary="handlePrimaryAction"
    />

    <button v-if="false" class="back-hint" :class="panelSide === 'left' ? 'from-right' : ''" @click="closePanel">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
      返回驾驶舱
    </button>

    <div v-if="false" class="detail-panel" :class="{ show: activePanel, 'from-left': panelSide === 'left', 'from-right': panelSide === 'right' }">
      <button class="panel-back-btn" @click="closePanel">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
        <span>返回驾驶舱</span>
      </button>
      <div class="detail-inner">

        <!-- 岗位匹配度详情 -->
        <div v-if="activePanel === 'match'" class="detail-page page-match">
          <div class="page-header">
            <div class="header-icon" style="background: linear-gradient(135deg, #4ed8ff20, #06b6d420); border-color: #4ed8ff60;">
              <svg viewBox="0 0 24 24" fill="none" stroke="#4ed8ff" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
            </div>
            <div class="header-titles">
              <h2>岗位匹配度分析</h2>
              <p>AI算法工程师 · 字节跳动</p>
            </div>
            <div class="header-badge" style="background: linear-gradient(135deg, #4ed8ff, #06b6d4); color: #050d1f;">72%</div>
          </div>

          <div class="hero-ring-section">
            <div class="big-ring-wrap">
              <svg class="big-ring-svg" viewBox="0 0 240 240">
                <defs>
                  <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#4ed8ff"/>
                    <stop offset="50%" stop-color="#22d3ee"/>
                    <stop offset="100%" stop-color="#06b6d4"/>
                  </linearGradient>
                  <filter id="ringGlow"><feGaussianBlur stdDeviation="6" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                </defs>
                <circle cx="120" cy="120" r="100" fill="none" stroke="rgba(78,216,255,0.08)" stroke-width="16"/>
                <circle cx="120" cy="120" r="100" fill="none" stroke="rgba(78,216,255,0.15)" stroke-width="16" stroke-dasharray="30 10" transform="rotate(-90 120 120)"/>
                <circle cx="120" cy="120" r="100" fill="none" stroke="url(#ringGrad)" stroke-width="16" stroke-linecap="round" stroke-dasharray="452 628" transform="rotate(-90 120 120)" filter="url(#ringGlow)"/>
                <circle cx="120" cy="120" r="80" fill="none" stroke="rgba(78,216,255,0.05)" stroke-width="1"/>
                <circle cx="120" cy="120" r="60" fill="none" stroke="rgba(78,216,255,0.05)" stroke-width="1"/>
              </svg>
              <div class="big-ring-center">
                <span class="br-num">72</span>
                <span class="br-pct">%</span>
                <span class="br-lbl">综合匹配度</span>
              </div>
            </div>
            <div class="stats-grid-4">
              <div class="tech-stat-card" v-for="s in matchStats" :key="s.label" :style="{ '--accent': s.color }">
                <div class="tsc-icon">{{ s.icon }}</div>
                <div class="tsc-val" :style="{ color: s.color }">{{ s.value }}</div>
                <div class="tsc-lbl">{{ s.label }}</div>
                <div class="tsc-bar"><div class="tsc-bar-fill" :style="{ width: s.bar + '%', background: s.color }"></div></div>
              </div>
            </div>
          </div>

          <div class="tech-section">
            <h3 class="section-title"><span class="st-line"></span>能力维度拆解</h3>
            <div class="dim-bars">
              <div class="dim-bar-row" v-for="d in matchDims" :key="d.name">
                <div class="dbr-label">{{ d.name }}</div>
                <div class="dbr-track">
                  <div class="dbr-fill" :style="{ width: d.val + '%', background: `linear-gradient(90deg, ${d.color}, ${d.color}80)` }"></div>
                  <div class="dbr-marker" v-for="m in [25,50,75]" :key="m" :style="{ left: m + '%' }"></div>
                </div>
                <div class="dbr-val" :style="{ color: d.color }">{{ d.val }}%</div>
              </div>
            </div>
          </div>

          <div class="tech-section">
            <h3 class="section-title"><span class="st-line"></span>技能缺口分析</h3>
            <div class="gap-cards">
              <div class="gap-card" v-for="(g, i) in skillGaps" :key="i" :class="'level-' + g.level">
                <div class="gc-rank">{{ i + 1 }}</div>
                <div class="gc-body">
                  <div class="gc-title">{{ g.title }}</div>
                  <div class="gc-desc">{{ g.desc }}</div>
                  <div class="gc-tags">
                    <span v-for="t in g.tags" :key="t">{{ t }}</span>
                  </div>
                </div>
                <button class="gc-btn">去学习</button>
              </div>
            </div>
          </div>

          <div class="tech-section">
            <h3 class="section-title"><span class="st-line"></span>匹配度趋势</h3>
            <div class="trend-chart">
              <svg viewBox="0 0 500 160" class="trend-svg">
                <defs>
                  <linearGradient id="trendFill" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#4ed8ff" stop-opacity="0.3"/>
                    <stop offset="100%" stop-color="#4ed8ff" stop-opacity="0"/>
                  </linearGradient>
                </defs>
                <line v-for="y in [40,80,120]" :key="y" x1="40" :y1="y" x2="480" :y2="y" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
                <polyline :points="trendPoints" fill="none" stroke="#4ed8ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0 0 6px #4ed8ff80)"/>
                <polygon :points="trendPoints + ' 480,150 40,150'" fill="url(#trendFill)"/>
                <circle v-for="(p, i) in trendData" :key="i" :cx="40 + i * 62.8" :cy="150 - p.val * 1.1" r="5" fill="#050d1f" stroke="#4ed8ff" stroke-width="2"/>
                <text v-for="(p, i) in trendData" :key="'t'+i" :x="40 + i * 62.8" :y="168" fill="rgba(255,255,255,0.4)" font-size="11" text-anchor="middle">{{ p.month }}</text>
              </svg>
            </div>
          </div>
        </div>

        <!-- 能力图谱详情 -->
        <div v-if="activePanel === 'radar'" class="detail-page page-radar">
          <div class="page-header">
            <div class="header-icon" style="background: linear-gradient(135deg, #4ed8ff20, #22d3ee20); border-color: #4ed8ff60;">
              <svg viewBox="0 0 24 24" fill="none" stroke="#4ed8ff" stroke-width="2"><polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5"/><line x1="12" y1="2" x2="12" y2="22"/><line x1="2" y1="8.5" x2="22" y2="15.5"/><line x1="22" y1="8.5" x2="2" y2="15.5"/></svg>
            </div>
            <div class="header-titles">
              <h2>能力图谱</h2>
              <p>八维技能雷达 · 综合评分 74/100</p>
            </div>
          </div>

          <div class="radar-hero">
            <svg class="radar-big-svg" viewBox="0 0 400 400">
              <defs>
                <radialGradient id="radarFill" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stop-color="#4ed8ff" stop-opacity="0.4"/>
                  <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.1"/>
                </radialGradient>
                <filter id="radarGlow"><feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
              </defs>
              <g transform="translate(200,200)">
                <polygon v-for="lv in [0.25,0.5,0.75,1]" :key="lv" :points="radarGridPts(lv)" fill="none" stroke="rgba(78,216,255,0.12)" stroke-width="1"/>
                <line v-for="(_, i) in radarSkills" :key="'l'+i" x1="0" y1="0" :x2="radarSkills.length > 0 ? 160 * Math.cos(Math.PI*2*i/radarSkills.length - Math.PI/2) : 0" :y2="radarSkills.length > 0 ? 160 * Math.sin(Math.PI*2*i/radarSkills.length - Math.PI/2) : 0" stroke="rgba(78,216,255,0.08)" stroke-width="1"/>
                <polygon :points="radarDataPts" fill="url(#radarFill)" stroke="#4ed8ff" stroke-width="2" filter="url(#radarGlow)"/>
                <circle v-for="(s, i) in radarSkills" :key="'c'+i" :cx="160 * (s.val/100) * Math.cos(Math.PI*2*i/radarSkills.length - Math.PI/2)" :cy="160 * (s.val/100) * Math.sin(Math.PI*2*i/radarSkills.length - Math.PI/2)" r="6" fill="#fff" stroke="#4ed8ff" stroke-width="2.5"/>
                <text v-for="(s, i) in radarSkills" :key="'tx'+i" :x="185 * Math.cos(Math.PI*2*i/radarSkills.length - Math.PI/2)" :y="185 * Math.sin(Math.PI*2*i/radarSkills.length - Math.PI/2) + 4" fill="rgba(255,255,255,0.7)" font-size="13" text-anchor="middle" font-weight="500">{{ s.name }}</text>
              </g>
            </svg>
          </div>

          <div class="tech-section">
            <h3 class="section-title"><span class="st-line"></span>技能掌握详情</h3>
            <div class="skill-cards-grid">
              <div class="skill-card" v-for="s in radarSkills" :key="s.name" :style="{ '--accent': s.val >= 80 ? '#37d6a5' : s.val >= 70 ? '#4ed8ff' : '#ffb65c' }">
                <div class="sc-header">
                  <span class="sc-name">{{ s.name }}</span>
                  <span class="sc-val" :style="{ color: s.val >= 80 ? '#37d6a5' : s.val >= 70 ? '#4ed8ff' : '#ffb65c' }">{{ s.val }}</span>
                </div>
                <div class="sc-mini-ring">
                  <svg viewBox="0 0 60 60">
                    <circle cx="30" cy="30" r="24" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="5"/>
                    <circle cx="30" cy="30" r="24" fill="none" :stroke="s.val >= 80 ? '#37d6a5' : s.val >= 70 ? '#4ed8ff' : '#ffb65c'" stroke-width="5" stroke-linecap="round" :stroke-dasharray="`${150.8 * s.val/100} 150.8`" transform="rotate(-90 30 30)"/>
                  </svg>
                </div>
                <div class="sc-desc">{{ s.desc }}</div>
                <div class="sc-level" :class="s.val >= 80 ? 'lv-good' : s.val >= 70 ? 'lv-mid' : 'lv-weak'">{{ s.val >= 80 ? '精通' : s.val >= 70 ? '熟练' : '待提升' }}</div>
              </div>
            </div>
          </div>

          <div class="tech-section">
            <h3 class="section-title"><span class="st-line"></span>待提升领域</h3>
            <div class="weak-cards">
              <div class="weak-card" v-for="w in weakAreas" :key="w.title">
                <div class="wc-icon" :style="{ background: w.color + '20', color: w.color }">{{ w.icon }}</div>
                <div class="wc-body">
                  <div class="wc-title">{{ w.title }}</div>
                  <div class="wc-desc">{{ w.desc }}</div>
                  <div class="wc-suggest">{{ w.suggest }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 推荐岗位详情 -->
        <div v-if="activePanel === 'resource-library'" class="detail-page page-resource-library">
          <div class="resource-frame">
            <div class="resource-frame__inner">
          <div class="page-header">
            <div class="header-icon resource-library__icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21.5v-16Z"/><path d="M4 19a2.5 2.5 0 0 1 2.5-2.5H20"/><path d="M9 7h7M9 10h5"/></svg>
            </div>
            <div class="header-titles">
              <h2>学习资源库</h2>
              <p>围绕当前 RAG 阶段整理的文档、课程、项目与论文</p>
            </div>
            <span class="resource-library__count">04 CURATED</span>
          </div>

          <section class="resource-library__brief">
            <div>
              <span>FOCUS COLLECTION</span>
              <h3>RAG 知识增强实战</h3>
              <p>从理解检索原理，到完成一个可演示的知识库项目。先读、再练、最后交付。</p>
            </div>
            <div class="resource-library__meter" aria-label="资源完成度 25%">
              <strong>25%</strong><small>COLLECTED</small>
            </div>
          </section>

          <section class="resource-library__grid">
            <article v-for="(resource, index) in resources" :key="resource.title" class="resource-library__card" :style="{ '--resource-color': resource.color }">
              <span class="resource-library__index">0{{ index + 1 }}</span>
              <span class="resource-library__type">{{ resource.type }}</span>
              <h3>{{ resource.title }}</h3>
              <p>{{ resource.source }}</p>
              <footer><span>★ {{ resource.rating }}</span><button type="button">加入本周计划</button></footer>
            </article>
          </section>

          <div class="resource-library__actions">
            <button type="button" @click="router.push('/learning-path')">进入完整学习路径</button>
            <button type="button" class="ghost" @click="closePanel">返回资源舱</button>
          </div>
            </div>
            <div class="resource-frame__base"></div>
          </div>
        </div>

        <div v-if="activePanel === 'jobs'" class="detail-page page-jobs">
          <div class="page-header">
            <div class="header-icon" style="background: linear-gradient(135deg, #4ed8ff20, #06b6d420); border-color: #4ed8ff60;">
              <svg viewBox="0 0 24 24" fill="none" stroke="#4ed8ff" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
            </div>
            <div class="header-titles">
              <h2>智能岗位推荐</h2>
              <p>基于你的能力画像 · 共找到 5 个匹配岗位</p>
            </div>
          </div>

          <div class="filter-tabs">
            <button v-for="(f, i) in ['全部', 'AI算法', 'NLP', 'CV', '大模型', '推荐系统']" :key="f" :class="['ft-btn', { active: i === 0 }]">{{ f }}</button>
          </div>

          <div class="job-list">
            <div class="job-row" v-for="j in jobList" :key="j.rank" :class="'jr-rank-' + j.rank">
              <div class="jr-rank" :class="'rank-badge-' + j.rank">{{ j.rank }}</div>
              <div class="jr-info">
                <div class="jr-top">
                  <span class="jr-name">{{ j.name }}</span>
                  <span class="jr-salary">{{ j.salary }}</span>
                </div>
                <div class="jr-meta">{{ j.company }} · {{ j.city }} · {{ j.exp }}</div>
                <div class="jr-tags">
                  <span v-for="t in j.tags" :key="t" class="jr-tag">{{ t }}</span>
                </div>
                <div class="jr-match-bar">
                  <div class="jrmb-label">匹配度</div>
                  <div class="jrmb-track">
                    <div class="jrmb-fill" :style="{ width: j.score + '%', background: j.score >= 70 ? 'linear-gradient(90deg, #37d6a5, #22d3ee)' : 'linear-gradient(90deg, #4ed8ff, #06b6d4)' }"></div>
                  </div>
                  <div class="jrmb-val" :style="{ color: j.score >= 70 ? '#37d6a5' : '#4ed8ff' }">{{ j.score }}%</div>
                </div>
              </div>
              <div class="jr-action">
                <button class="jr-btn">查看详情</button>
                <button class="jr-btn-outline">收藏</button>
              </div>
            </div>
          </div>
        </div>

        <!-- AI下一步建议 -->
        <div v-if="activePanel === 'ai-suggest'" class="detail-page page-ai">
          <div class="page-header">
            <div class="header-icon" style="background: linear-gradient(135deg, #a855f720, #7c3aed20); border-color: #a855f760;">
              <svg viewBox="0 0 24 24" fill="none" stroke="#c084fc" stroke-width="2"><path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"/><path d="M12 14v8"/><path d="M8 22h8"/><circle cx="12" cy="10" r="1"/></svg>
            </div>
            <div class="header-titles">
              <h2 style="background: linear-gradient(90deg, #c084fc, #4ed8ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AI 智能学习建议</h2>
              <p>基于你的学习轨迹与岗位需求，AI为你定制下一步路径</p>
            </div>
          </div>

          <div class="ai-featured-card">
            <div class="afc-glow"></div>
            <div class="afc-cube">
              <div class="cube-face cf-front"></div>
              <div class="cube-face cf-back"></div>
              <div class="cube-face cf-right"></div>
              <div class="cube-face cf-left"></div>
              <div class="cube-face cf-top"></div>
              <div class="cube-face cf-bottom"></div>
            </div>
            <div class="afc-body">
              <div class="afc-tag">🔥 紧急推荐</div>
              <h3>深入学习 RAG 知识库构建</h3>
              <p>掌握检索增强生成核心技术，完成一个端到端项目。这是当前AI算法岗位的核心技能要求，掌握后匹配度可提升约15%。</p>
              <div class="afc-tags">
                <span>RAG</span><span>知识库构建</span><span>向量检索</span><span>LangChain</span>
              </div>
              <button class="afc-btn">立即开始学习 →</button>
            </div>
          </div>

          <div class="tech-section">
            <h3 class="section-title"><span class="st-line" style="background: linear-gradient(180deg, #a855f7, #7c3aed);"></span>分阶段学习路径</h3>
            <div class="learning-steps">
              <div v-for="(step, i) in learningPath" :key="i" class="ls-item" :class="{ done: step.done, current: step.current }">
                <div class="ls-connector" v-if="i < learningPath.length - 1"></div>
                <div class="ls-node">
                  <svg v-if="step.done" viewBox="0 0 24 24" fill="none" stroke="#050d1f" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                  <span v-else>{{ i + 1 }}</span>
                </div>
                <div class="ls-content">
                  <div class="ls-title">{{ step.title }}</div>
                  <div class="ls-desc">{{ step.desc }}</div>
                  <div class="ls-meta">
                    <span class="ls-time">⏱ {{ step.time }}</span>
                    <span class="ls-diff">难度：{{ step.diff }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="tech-section">
            <h3 class="section-title"><span class="st-line" style="background: linear-gradient(180deg, #a855f7, #7c3aed);"></span>推荐学习资源</h3>
            <div class="resource-cards">
              <div class="res-card" v-for="r in aiResources" :key="r.title">
                <div class="rc-type" :style="{ background: r.color + '20', color: r.color }">{{ r.type }}</div>
                <div class="rc-title">{{ r.title }}</div>
                <div class="rc-source">{{ r.source }}</div>
                <div class="rc-rating">⭐ {{ r.rating }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 本周成长计划 -->
        <div v-if="activePanel === 'weekly-plan'" class="detail-page page-plan">
          <div class="page-header">
            <div class="header-icon" style="background: linear-gradient(135deg, #37d6a520, #22d3ee20); border-color: #37d6a560;">
              <svg viewBox="0 0 24 24" fill="none" stroke="#37d6a5" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            </div>
            <div class="header-titles">
              <h2>本周成长计划</h2>
              <p>2026年第34周 · 8月18日 - 8月24日</p>
            </div>
            <div class="progress-big">
              <svg viewBox="0 0 80 80">
                <circle cx="40" cy="40" r="32" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="6"/>
                <circle cx="40" cy="40" r="32" fill="none" stroke="#37d6a5" stroke-width="6" stroke-linecap="round" stroke-dasharray="120.6 201" transform="rotate(-90 40 40)" style="filter: drop-shadow(0 0 8px #37d6a580)"/>
              </svg>
              <span><b>3</b>/5</span>
            </div>
          </div>

          <div class="week-stats">
            <div class="ws-card" v-for="w in weekStats" :key="w.label">
              <div class="ws-icon" :style="{ background: w.color + '20', color: w.color }">{{ w.icon }}</div>
              <div class="ws-val" :style="{ color: w.color }">{{ w.value }}</div>
              <div class="ws-lbl">{{ w.label }}</div>
            </div>
          </div>

          <div class="tech-section">
            <h3 class="section-title"><span class="st-line"></span>任务清单</h3>
            <div class="task-list">
              <div class="task-item" v-for="(t, i) in weeklyTasks" :key="i" :class="{ done: t.done }" @click="t.done = !t.done">
                <div class="ti-check">
                  <svg v-if="t.done" viewBox="0 0 24 24" fill="none" stroke="#050d1f" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                </div>
                <div class="ti-body">
                  <div class="ti-text">{{ t.text }}</div>
                  <div class="ti-meta">
                    <span class="ti-date">{{ t.date }}</span>
                    <span class="ti-cat" :style="{ background: t.catColor + '20', color: t.catColor }">{{ t.cat }}</span>
                  </div>
                </div>
                <div class="ti-points">+{{ t.points }}XP</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 模拟面试 -->
        <div v-if="activePanel === 'interview'" class="detail-page page-interview">
          <div class="page-header">
            <div class="header-icon" style="background: linear-gradient(135deg, #4ed8ff20, #06b6d420); border-color: #4ed8ff60;">
              <svg viewBox="0 0 24 24" fill="none" stroke="#4ed8ff" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
            </div>
            <div class="header-titles">
              <h2>AI 模拟面试</h2>
              <p>真实面试场景模拟 · 智能评估反馈</p>
            </div>
          </div>

          <div class="interview-hero">
            <div class="ih-score-ring">
              <svg viewBox="0 0 200 200">
                <defs>
                  <linearGradient id="intGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#4ed8ff"/><stop offset="100%" stop-color="#a855f7"/>
                  </linearGradient>
                </defs>
                <circle cx="100" cy="100" r="85" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="12"/>
                <circle cx="100" cy="100" r="85" fill="none" stroke="url(#intGrad)" stroke-width="12" stroke-linecap="round" stroke-dasharray="416 534" transform="rotate(-90 100 100)" style="filter: drop-shadow(0 0 12px #4ed8ff80)"/>
              </svg>
              <div class="ihsr-center">
                <span class="ihsr-num">78</span>
                <span class="ihsr-total">/100</span>
                <span class="ihsr-grade">良好</span>
              </div>
            </div>
            <div class="ih-info">
              <div class="ih-dims">
                <div class="ih-dim" v-for="d in interviewDims" :key="d.name">
                  <span class="ihd-name">{{ d.name }}</span>
                  <div class="ihd-bar"><div class="ihd-fill" :style="{ width: d.val + '%', background: d.color }"></div></div>
                  <span class="ihd-val" :style="{ color: d.color }">{{ d.val }}</span>
                </div>
              </div>
              <button class="ih-start-btn">
                <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                开启新一轮模拟面试
              </button>
              <div class="ih-tips">
                <span>💡 上次面试：45秒平均回答时长</span>
                <span>📊 共完成 15 次模拟</span>
              </div>
            </div>
          </div>

          <div class="tech-section">
            <h3 class="section-title"><span class="st-line"></span>面试历史记录</h3>
            <div class="interview-records">
              <div class="ir-item" v-for="(r, i) in interviewRecords" :key="i">
                <div class="ir-date">{{ r.date }}</div>
                <div class="ir-body">
                  <div class="ir-pos">{{ r.position }}</div>
                  <div class="ir-tags"><span v-for="t in r.tags" :key="t">{{ t }}</span></div>
                </div>
                <div class="ir-score" :style="{ color: r.score >= 75 ? '#37d6a5' : r.score >= 65 ? '#4ed8ff' : '#ffb65c' }">{{ r.score }}分</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 成长时间线 -->
        <div v-if="activePanel === 'timeline'" class="detail-page page-timeline">
          <div class="page-header">
            <div class="header-icon" style="background: linear-gradient(135deg, #4ed8ff20, #a855f720); border-color: #4ed8ff60;">
              <svg viewBox="0 0 24 24" fill="none" stroke="#4ed8ff" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </div>
            <div class="header-titles">
              <h2>成长时间线</h2>
              <p>你的AI学习旅程 · 累计学习 68 天</p>
            </div>
          </div>

          <div class="timeline-container">
            <div class="tl-axis"></div>
            <div class="tl-entry" v-for="(e, i) in timelineEvents" :key="i" :class="'tl-side-' + (i % 2 === 0 ? 'left' : 'right')">
              <div class="tl-dot" :style="{ background: e.color, boxShadow: `0 0 16px ${e.color}` }">
                <span>{{ e.icon }}</span>
              </div>
              <div class="tl-card" :style="{ borderColor: e.color + '40' }">
                <div class="tlc-date" :style="{ color: e.color }">{{ e.date }}</div>
                <div class="tlc-title">{{ e.title }}</div>
                <div class="tlc-desc">{{ e.desc }}</div>
                <div class="tlc-reward" v-if="e.reward">🏆 获得：{{ e.reward }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 成长路径 -->
        <div v-if="activePanel === 'path'" class="detail-page page-path">
          <div class="page-header">
            <div class="header-icon" style="background: linear-gradient(135deg, #4ed8ff20, #a855f720); border-color: #4ed8ff60;">
              <svg viewBox="0 0 24 24" fill="none" stroke="#4ed8ff" stroke-width="2"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>
            </div>
            <div class="header-titles">
              <h2>成长路径</h2>
              <p>从Python入门到AI算法工程师 · 当前进度 50%</p>
            </div>
          </div>

          <div class="path-visual">
            <svg class="path-svg" viewBox="0 0 800 200">
              <defs>
                <linearGradient id="pathGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#4ed8ff"/><stop offset="50%" stop-color="#a855f7"/><stop offset="100%" stop-color="#ec4899"/>
                </linearGradient>
              </defs>
              <path d="M 60 150 Q 150 50 260 120 T 460 100 T 660 130 T 740 80" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="4" stroke-linecap="round" stroke-dasharray="10 8"/>
              <path d="M 60 150 Q 150 50 260 120 T 400 110" fill="none" stroke="url(#pathGrad)" stroke-width="4" stroke-linecap="round" style="filter: drop-shadow(0 0 8px #4ed8ff80)"/>
            </svg>
            <div class="path-nodes-horiz">
              <div v-for="(n, i) in pathNodes" :key="n.name" class="pnh-node" :class="{ done: n.done, current: n.current }" :style="{ '--c': n.color, left: (i * 130 + 40) + 'px' }">
                <div class="pnh-icon">{{ n.icon }}</div>
                <div class="pnh-name">{{ n.name }}</div>
                <div class="pnh-sub">{{ n.sub }}</div>
                <div class="pnh-check" v-if="n.done">✓</div>
              </div>
            </div>
          </div>

          <div class="current-stage-card">
            <div class="csc-header">
              <span class="csc-badge" style="background: linear-gradient(135deg, #60a5fa, #a855f7);">当前阶段</span>
              <h3>RAG 知识增强</h3>
            </div>
            <p>你正在进入RAG（检索增强生成）阶段。这是连接大模型与外部知识库的核心技术，也是当前AI行业最热门的方向之一，岗位需求旺盛。</p>
            <div class="csc-grid">
              <div class="csc-item"><span class="csc-i-label">预计时长</span><span class="csc-i-val">3-4周</span></div>
              <div class="csc-item"><span class="csc-i-label">难度等级</span><span class="csc-i-val">⭐⭐⭐⭐</span></div>
              <div class="csc-item"><span class="csc-i-label">提升匹配度</span><span class="csc-i-val" style="color: #37d6a5;">+15%</span></div>
            </div>
            <div class="csc-resources">
              <h4>📚 推荐资源</h4>
              <ul>
                <li>《LangChain官方文档》- 入门必读</li>
                <li>B站视频：RAG从原理到实战（完整版）</li>
                <li>开源项目：ChatGLM3 + RAG搭建企业知识库问答</li>
                <li>论文：《Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks》</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 个人中心/头像详情 -->
        <div v-if="activePanel === 'avatar'" class="detail-page page-avatar">
          <div class="profile-hero">
            <div class="ph-avatar-ring">
              <svg viewBox="0 0 160 160">
                <defs>
                  <linearGradient id="avGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#4ed8ff"/><stop offset="100%" stop-color="#a855f7"/>
                  </linearGradient>
                </defs>
                <circle cx="80" cy="80" r="72" fill="none" stroke="rgba(78,216,255,0.1)" stroke-width="4"/>
                <circle cx="80" cy="80" r="72" fill="none" stroke="url(#avGrad)" stroke-width="4" stroke-dasharray="354 452" transform="rotate(-90 80 80)" style="filter: drop-shadow(0 0 10px #4ed8ff80)"/>
              </svg>
              <div class="ph-avatar-inner">张</div>
            </div>
            <div class="ph-info">
              <h2>张同学</h2>
              <div class="ph-tags">
                <span class="ph-tag">Lv.18</span>
                <span class="ph-tag">AI算法工程师方向</span>
                <span class="ph-tag" style="background: #37d6a520; color: #37d6a5;">学习中</span>
              </div>
              <div class="ph-level-bar">
                <div class="phlb-label">成长指数</div>
                <div class="phlb-track"><div class="phlb-fill" style="width: 78%"></div></div>
                <div class="phlb-val">78/100</div>
              </div>
              <div class="ph-xp">距离 Lv.19 还需 <b>2,340</b> XP</div>
            </div>
          </div>

          <div class="stats-dashboard">
            <div class="sd-card" v-for="s in profileStats" :key="s.label">
              <div class="sdc-icon" :style="{ background: s.color + '20', color: s.color }">{{ s.icon }}</div>
              <div class="sdc-val">{{ s.value }}</div>
              <div class="sdc-lbl">{{ s.label }}</div>
            </div>
          </div>

          <div class="tech-section tech-section--badge-wall">
            <div class="tech-frame-frame"></div>
            <h3 class="section-title"><span class="st-line"></span>成就徽章</h3>
            <div class="badge-wall">
              <div class="badge-item" v-for="b in badges" :key="b.name" :class="{ locked: !b.unlocked }">
                <div class="bi-icon" :style="{ background: b.unlocked ? b.color + '30' : 'rgba(255,255,255,0.03)', color: b.unlocked ? b.color : 'rgba(255,255,255,0.2)' }">{{ b.icon }}</div>
                <span>{{ b.name }}</span>
              </div>
            </div>
          </div>

          <div class="tech-section">
            <h3 class="section-title"><span class="st-line"></span>学习活动热力图</h3>
            <div class="heatmap">
              <div v-for="(row, ri) in 7" :key="ri" class="hm-row">
                <div v-for="(col, ci) in 20" :key="ci" class="hm-cell" :style="{ background: heatmapData[ri][ci] ? `rgba(78,216,255,${heatmapData[ri][ci]/4})` : 'rgba(255,255,255,0.03)' }"></div>
              </div>
            </div>
            <div class="hm-legend">
              <span>少</span>
              <div class="hml-cell" v-for="i in 5" :key="i" :style="{ background: `rgba(78,216,255,${i/5})` }"></div>
              <span>多</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import GrowthCabinImage from '@/components/cockpit/GrowthCabinImage.vue'
import ImmersiveMissionCabin from '@/components/cockpit/ImmersiveMissionCabin.vue'
import LearningPathMission from '@/components/cockpit/LearningPathMission.vue'
import GrowthProfileMission from '@/components/cockpit/GrowthProfileMission.vue'
import AchievementWallMission from '@/components/cockpit/AchievementWallMission.vue'
import { isMissionCabinId, type MissionCabinId } from '@/components/cockpit/missionCabinData'

const router = useRouter()
const activePanel = ref<string | null>(null)
const panelSide = ref<'left' | 'right'>('right')
const activeMissionPanel = computed<MissionCabinId | null>(() => {
  return activePanel.value && isMissionCabinId(activePanel.value) ? activePanel.value : null
})

const panelSides = [
  { id: 'radar', side: 'left' as const },
  { id: 'path', side: 'left' as const },
  { id: 'avatar', side: 'right' as const },
  { id: 'resource-library', side: 'left' as const },
  { id: 'ai-suggest', side: 'right' as const },
  { id: 'weekly-plan', side: 'right' as const },
  { id: 'timeline', side: 'right' as const },
]

const sceneClass = computed(() => {
  if (!activePanel.value) return ''
  return 'scene-immersive'
})

function openPanel(id: string) {
  if (activePanel.value || !isMissionCabinId(id)) return
  const spot = panelSides.find(s => s.id === id)
  panelSide.value = spot?.side || 'right'
  activePanel.value = id
}

function closePanel() { activePanel.value = null }

function switchPanel(id: MissionCabinId) {
  closePanel()
  void nextTick(() => openPanel(id))
}

function handlePrimaryAction(payload: { id: MissionCabinId; route: string }) {
  if (payload.route === router.currentRoute.value.path) {
    closePanel()
    return
  }
  router.push(payload.route)
}

function goToOverview() {
  router.push('/overview')
}

// ============ 数据 ============

const matchStats = [
  { label: '较上次提升', value: '14%', color: '#37d6a5', icon: '↑', bar: 85 },
  { label: '超过同学', value: '72%', color: '#4ed8ff', icon: '◉', bar: 72 },
  { label: '技能缺口', value: '5项', color: '#ffb65c', icon: '!', bar: 40 },
  { label: '推荐课程', value: '8门', color: '#a855f7', icon: '★', bar: 60 },
]

const matchDims = [
  { name: '技术能力', val: 78, color: '#4ed8ff' },
  { name: '项目经验', val: 65, color: '#22d3ee' },
  { name: '算法基础', val: 82, color: '#37d6a5' },
  { name: '工程实践', val: 58, color: '#ffb65c' },
  { name: '软技能', val: 75, color: '#a855f7' },
  { name: '学习潜力', val: 88, color: '#ec4899' },
]

const skillGaps = [
  { title: 'RAG知识库构建', desc: '检索增强生成是大模型落地必备技能', tags: ['LangChain', '向量检索', 'Embedding'], level: 'high' },
  { title: '大模型微调技术', desc: 'LoRA/QLoRA等高效微调方法亟待掌握', tags: ['LoRA', 'PEFT', 'Transformer'], level: 'high' },
  { title: 'MLOps工程实践', desc: '模型部署与工程化能力需要加强', tags: ['Docker', 'vLLM', 'TensorRT'], level: 'medium' },
]

const trendData = [
  { month: '3月', val: 42 }, { month: '4月', val: 48 }, { month: '5月', val: 55 },
  { month: '6月', val: 58 }, { month: '7月', val: 64 }, { month: '8月', val: 68 }, { month: '现在', val: 72 },
]
const trendPoints = computed(() => trendData.map((p, i) => `${40 + i * 62.8},${150 - p.val * 1.1}`).join(' '))

const radarSkills = [
  { name: '算法', val: 85, desc: '排序、搜索、动态规划熟练' },
  { name: '编程', val: 78, desc: 'Python熟练，C++基础' },
  { name: '机器学习', val: 72, desc: '经典ML算法掌握良好' },
  { name: '深度学习', val: 68, desc: 'CNN/RNN掌握，Transformer进阶中' },
  { name: '工程', val: 60, desc: '需要加强部署能力' },
  { name: '数据分析', val: 80, desc: 'Pandas/NumPy熟练' },
  { name: '沟通表达', val: 70, desc: '表达清晰，仍可提升' },
  { name: '数学', val: 82, desc: '线代/概率/微积分扎实' },
]

function radarGridPts(lv: number) {
  return radarSkills.map((_, i) => {
    const ang = (Math.PI * 2 * i) / radarSkills.length - Math.PI / 2
    const r = 160 * lv
    return `${r * Math.cos(ang)},${r * Math.sin(ang)}`
  }).join(' ')
}
const radarDataPts = computed(() => radarSkills.map((s, i) => {
  const ang = (Math.PI * 2 * i) / radarSkills.length - Math.PI / 2
  const r = 160 * (s.val / 100)
  return `${r * Math.cos(ang)},${r * Math.sin(ang)}`
}).join(' '))

const weakAreas = [
  { title: '工程实践能力', desc: '模型部署、Docker容器化、生产环境经验不足', suggest: '建议参与开源项目，学习vLLM/TensorRT部署', icon: '⚙', color: '#ffb65c' },
  { title: '深度学习理论', desc: 'Transformer内部机制、注意力变种理解不深', suggest: '建议系统学习CS231n/李沐深度学习课程', icon: '🧠', color: '#a855f7' },
  { title: '大模型前沿', desc: 'Agent、多模态、RAG等新技术跟进较慢', suggest: '关注顶会论文，复现最新开源项目', icon: '🚀', color: '#4ed8ff' },
]

const jobList = [
  { rank: 1, name: 'AI算法工程师', company: '字节跳动', city: '北京', salary: '25-40K·15薪', exp: '1-3年', score: 72, tags: ['推荐系统', 'NLP', '大模型'] },
  { rank: 2, name: 'NLP算法工程师', company: '百度', city: '北京', salary: '22-35K·14薪', exp: '1-3年', score: 68, tags: ['大模型', 'RAG', '对话系统'] },
  { rank: 3, name: '机器学习工程师', company: '腾讯', city: '深圳', salary: '20-35K·16薪', exp: '1-3年', score: 65, tags: ['推荐系统', 'CTR预估'] },
  { rank: 4, name: 'CV算法工程师', company: '阿里巴巴', city: '上海', salary: '23-38K·16薪', exp: '1-3年', score: 58, tags: ['多模态', '目标检测'] },
  { rank: 5, name: '大模型算法工程师', company: '华为', city: '上海', salary: '30-50K·14薪', exp: '3-5年', score: 55, tags: ['LLM', 'Agent', '微调'] },
]

const learningPath = [
  { title: '向量数据库基础', desc: '学习Embedding原理、向量索引（HNSW/IVF）、Milvus/Chroma实战', time: '3天', diff: '⭐⭐', done: true, current: false },
  { title: '检索策略', desc: '稠密检索、稀疏检索（BM25）、混合检索、召回排序', time: '4天', diff: '⭐⭐⭐', done: true, current: false },
  { title: 'RAG框架实战', desc: 'LangChain/LlamaIndex搭建完整RAG系统，文档切分与Chunk策略', time: '7天', diff: '⭐⭐⭐⭐', done: false, current: true },
  { title: '高级优化', desc: 'Query改写、重排序（Reranker）、多路召回、Self-RAG', time: '5天', diff: '⭐⭐⭐⭐', done: false, current: false },
  { title: '企业级项目实战', desc: '构建生产级知识库问答系统，含评估与监控', time: '10天', diff: '⭐⭐⭐⭐⭐', done: false, current: false },
]

const resources = [
  { type: '文档', title: 'LangChain官方中文文档', source: 'python.langchain.com', rating: 4.8, color: '#37d6a5' },
  { type: '视频', title: 'RAG从原理到实战完整版', source: 'B站-跟李沐学AI', rating: 4.9, color: '#4ed8ff' },
  { type: '项目', title: 'ChatGLM3+RAG搭建企业知识库', source: 'GitHub - THUDM', rating: 4.7, color: '#a855f7' },
  { type: '论文', title: 'Retrieval-Augmented Generation', source: 'NeurIPS 2020', rating: 4.6, color: '#ffb65c' },
]
const aiResources = resources.slice(0, 2)

const weekStats = [
  { label: '学习时长', value: '12.5h', icon: '⏱', color: '#4ed8ff' },
  { label: '完成任务', value: '3/5', icon: '✓', color: '#37d6a5' },
  { label: '练习题数', value: '28道', icon: '📝', color: '#a855f7' },
  { label: '连续学习', value: '5天', icon: '🔥', color: '#ffb65c' },
]

const weeklyTasks = ref([
  { text: '完成Transformer架构学习', date: '周一', cat: '理论', catColor: '#4ed8ff', points: 100, done: true },
  { text: '阅读《Attention Is All You Need》论文', date: '周二', cat: '论文', catColor: '#a855f7', points: 80, done: true },
  { text: '动手实现Multi-Head Attention机制', date: '周三', cat: '实践', catColor: '#37d6a5', points: 150, done: true },
  { text: '学习向量数据库Milvus基础操作', date: '周四/周五', cat: '工程', catColor: '#ffb65c', points: 120, done: false },
  { text: '完成RAG项目demo（文档问答）', date: '周末', cat: '项目', catColor: '#ec4899', points: 200, done: false },
])

const interviewDims = [
  { name: '技术能力', val: 72, color: '#4ed8ff' },
  { name: '表达能力', val: 72, color: '#37d6a5' },
  { name: '逻辑思维', val: 80, color: '#a855f7' },
  { name: '项目经验', val: 65, color: '#ffb65c' },
]

const interviewRecords = [
  { date: '06-22', position: '字节-AI算法工程师（一面）', tags: ['算法题', '项目深挖'], score: 78 },
  { date: '06-15', position: '百度-NLP工程师（模拟）', tags: ['Transformer', 'RAG'], score: 72 },
  { date: '06-08', position: '腾讯-机器学习岗（模拟）', tags: ['推荐系统', 'LR/GBDT'], score: 65 },
  { date: '06-01', position: '综合能力测评', tags: ['行测', '性格测试'], score: 85 },
]

const timelineEvents = [
  { date: '06-12', title: '深度学习基础课程结业', desc: '完成CNN/RNN/LSTM核心原理学习，通过结业考试（92分）', icon: '🎓', color: '#37d6a5', reward: '深度学习入门徽章' },
  { date: '06-08', title: 'Python技能升级至Lv.18', desc: '累计完成328道编程练习题，进入熟练阶段', icon: '🐍', color: '#4ed8ff', reward: '代码达人' },
  { date: '06-01', title: '匹配度大幅提升', desc: '岗位匹配度提升14%，算法基础能力显著增强', icon: '📈', color: '#ffb65c', reward: null },
  { date: '05-25', title: '第一个ML项目完成', desc: '完成房价预测项目，准确率达到96%', icon: '🏆', color: '#a855f7', reward: '项目新手徽章' },
  { date: '05-18', title: '开始机器学习学习', desc: '完成线性回归、逻辑回归课程', icon: '📚', color: '#ec4899', reward: null },
  { date: '05-10', title: '开启AI学习之旅', desc: '注册账号，完成入学测评，定制学习路径', icon: '🚀', color: '#06b6d4', reward: '初出茅庐徽章' },
]

const pathNodes = [
  { name: 'Python', sub: '入门基础', done: true, current: false, color: '#4ed8ff', icon: 'Py' },
  { name: '机器学习', sub: '基础算法', done: true, current: false, color: '#22d3ee', icon: 'ML' },
  { name: '深度学习', sub: '进阶应用', done: true, current: false, color: '#a855f7', icon: 'DL' },
  { name: 'RAG', sub: '知识增强', done: false, current: true, color: '#60a5fa', icon: 'R' },
  { name: 'Agent', sub: '智能体开发', done: false, current: false, color: '#818cf8', icon: 'A' },
  { name: 'AI算法工程师', sub: '目标岗位', done: false, current: false, color: '#ec4899', icon: '♛' },
]

const profileStats = [
  { label: '学习天数', value: '68天', icon: '📅', color: '#4ed8ff' },
  { label: '完成课程', value: '24门', icon: '📚', color: '#37d6a5' },
  { label: '练习题目', value: '328道', icon: '✏️', color: '#a855f7' },
  { label: '项目数', value: '6个', icon: '🚀', color: '#ffb65c' },
]

const badges = [
  { icon: '🏆', name: '初出茅庐', unlocked: true, color: '#f59e0b' },
  { icon: '⭐', name: '学习达人', unlocked: true, color: '#4ed8ff' },
  { icon: '🔥', name: '连续7天', unlocked: true, color: '#ef4444' },
  { icon: '💎', name: '算法能手', unlocked: false, color: '#a855f7' },
  { icon: '👑', name: '面试通关', unlocked: false, color: '#ec4899' },
  { icon: '🚀', name: '项目大师', unlocked: false, color: '#37d6a5' },
  { icon: '🎯', name: '目标达成', unlocked: true, color: '#22d3ee' },
  { icon: '🌟', name: '知识新星', unlocked: true, color: '#60a5fa' },
]

// 生成热力图模拟数据
const heatmapData: number[][] = []
for (let r = 0; r < 7; r++) {
  const row: number[] = []
  for (let c = 0; c < 20; c++) {
    row.push(Math.random() > 0.3 ? Math.ceil(Math.random() * 4) : 0)
  }
  heatmapData.push(row)
}
</script>

<style scoped>
.cockpit-container {
  position: fixed;
  inset: 0;
  background: #050d1f;
  overflow: hidden;
  perspective: 1800px;
}

.exit-cockpit-btn {
  position: fixed;
  top: 24px;
  left: 24px;
  z-index: 200;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  background: linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.05));
  border: 1.5px solid rgba(255,255,255,0.25);
  border-radius: 14px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  backdrop-filter: blur(20px);
  transition: all 0.3s;
  animation: fadeInLeft 0.6s ease;
  box-shadow: 0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.15);
}
.exit-cockpit-btn svg {
  width: 20px;
  height: 20px;
  transition: transform 0.3s;
}
.exit-cockpit-btn:hover {
  background: linear-gradient(135deg, rgba(78,216,255,0.25), rgba(78,216,255,0.1));
  border-color: rgba(78,216,255,0.5);
  box-shadow: 0 6px 32px rgba(78,216,255,0.3), inset 0 1px 0 rgba(255,255,255,0.2);
  color: #4ed8ff;
  transform: scale(1.05);
}
.exit-cockpit-btn:hover svg {
  transform: translateX(-4px);
}

.cockpit-scene {
  position: absolute;
  inset: 0;
  z-index: 10;
  transform-style: preserve-3d;
  transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.6s ease;
  transform-origin: center center;
}

.cockpit-bg-image {
  position: absolute;
  inset: 0;
  background-size: 100% 100%;
  background-position: center center;
  background-repeat: no-repeat;
}

.hotspots { position: absolute; inset: 0; }

.hotspot {
  position: absolute;
  cursor: pointer;
  border-radius: 12px;
  z-index: 20;
  transition: background 0.3s;
}
.hotspot:hover {
  background: rgba(78, 216, 255, 0.06);
  box-shadow: inset 0 0 30px rgba(78, 216, 255, 0.08), 0 0 40px rgba(78, 216, 255, 0.12);
}
.hotspot-glow {
  position: absolute; inset: 0; border-radius: 12px;
  border: 1.5px solid transparent; opacity: 0; transition: all 0.3s;
}
.hotspot:hover .hotspot-glow {
  opacity: 1; border-color: rgba(78, 216, 255, 0.5);
  animation: hotspotPulse 1.5s ease-in-out infinite;
}
.hotspot-ripple {
  position: absolute; inset: 0; border-radius: 12px; opacity: 0;
}
.hotspot:hover .hotspot-ripple {
  animation: ripple 1.5s ease-out infinite;
  background: radial-gradient(circle at center, rgba(78, 216, 255, 0.15), transparent 70%);
}

@keyframes hotspotPulse {
  0%, 100% { box-shadow: 0 0 10px rgba(78, 216, 255, 0.2); }
  50% { box-shadow: 0 0 30px rgba(78, 216, 255, 0.5); }
}
@keyframes ripple {
  0% { opacity: 0; transform: scale(0.95); }
  50% { opacity: 1; }
  100% { opacity: 0; transform: scale(1.05); }
}

.scene-slide-left {
  transform: translateX(-22%) rotateY(-10deg) scale(0.82);
  opacity: 0.5;
}
.scene-slide-right {
  transform: translateX(22%) rotateY(10deg) scale(0.82);
  opacity: 0.5;
}

.scene-immersive {
  transform: scale(1.045);
  opacity: 0.48;
  filter: blur(5px) saturate(0.82) brightness(0.7);
}

.panel-open .cockpit-scene {
  pointer-events: none;
}

.back-hint {
  position: fixed;
  top: 24px;
  z-index: 200;
  display: flex; align-items: center; gap: 10px;
  padding: 14px 28px;
  background: linear-gradient(135deg, rgba(78,216,255,0.2), rgba(6,182,212,0.1));
  border: 1.5px solid rgba(78, 216, 255, 0.5);
  border-radius: 14px;
  color: #4ed8ff;
  font-size: 15px; font-weight: 600;
  cursor: pointer;
  backdrop-filter: blur(20px);
  transition: all 0.3s;
  animation: fadeInLeft 0.5s ease;
  box-shadow: 0 4px 24px rgba(78,216,255,0.2), inset 0 1px 0 rgba(255,255,255,0.1);
}
.back-hint.from-right { right: 24px; left: auto; animation: fadeInRight 0.5s ease; }
.back-hint:not(.from-right) { left: 24px; }
.back-hint:hover {
  background: linear-gradient(135deg, rgba(78,216,255,0.3), rgba(6,182,212,0.2));
  box-shadow: 0 6px 32px rgba(78,216,255,0.4), inset 0 1px 0 rgba(255,255,255,0.15);
  transform: scale(1.05);
  color: #fff;
}
.back-hint svg { width: 20px; height: 20px; transition: transform 0.3s; }
.back-hint:hover svg { transform: translateX(-3px); }
.back-hint.from-right:hover svg { transform: translateX(3px); }

@keyframes fadeInLeft {
  from { opacity: 0; transform: translateX(-30px); }
  to { opacity: 1; transform: translateX(0); }
}
@keyframes fadeInRight {
  from { opacity: 0; transform: translateX(30px); }
  to { opacity: 1; transform: translateX(0); }
}

/* ============ 详情面板 ============ */
.detail-panel {
  position: absolute;
  top: 0;
  width: 680px;
  max-width: 52vw;
  height: 100%;
  z-index: 30;
  background:
    radial-gradient(130% 50% at 20% -12%, rgba(78, 216, 255, 0.07), transparent 55%),
    radial-gradient(90% 40% at 90% -20%, rgba(143, 124, 255, 0.05), transparent 60%),
    linear-gradient(180deg, rgba(9, 24, 58, 0.96) 0%, rgba(11, 30, 72, 0.97) 46%, rgba(7, 19, 48, 0.97) 100%);
  overflow-y: auto;
  backdrop-filter: blur(44px) saturate(1.22);
  -webkit-backdrop-filter: blur(44px) saturate(1.22);
  transition: transform 0.55s cubic-bezier(0.22, 1, 0.36, 1);
  box-shadow: 0 0 70px rgba(2, 8, 26, 0.55);
}
.detail-panel::-webkit-scrollbar { width: 6px; }
.detail-panel::-webkit-scrollbar-track { background: transparent; }
.detail-panel::-webkit-scrollbar-thumb { background: linear-gradient(180deg, rgba(78,216,255,0.3), rgba(168,85,247,0.3)); border-radius: 3px; }

.detail-panel.from-right {
  right: 0;
  border-left: 1px solid rgba(105, 200, 255, 0.22);
  box-shadow: -30px 0 80px rgba(0, 0, 0, 0.6), inset 1px 0 0 rgba(78, 216, 255, 0.08);
  transform: translateX(calc(100% + 20px));
}
.detail-panel.from-right::before {
  content: "";
  position: absolute;
  top: 0; bottom: 0; left: 0;
  width: 1px;
  background: linear-gradient(180deg, transparent 3%, rgba(78, 216, 255, 0.5) 28%, rgba(143, 124, 255, 0.28) 62%, transparent 97%);
  pointer-events: none;
}
.detail-panel.from-left {
  left: 0;
  border-right: 1px solid rgba(105, 200, 255, 0.22);
  box-shadow: 30px 0 80px rgba(0, 0, 0, 0.6), inset -1px 0 0 rgba(78, 216, 255, 0.08);
  transform: translateX(calc(-100% - 20px));
}
.detail-panel.from-left::before {
  content: "";
  position: absolute;
  top: 0; bottom: 0; right: 0;
  width: 1px;
  background: linear-gradient(180deg, transparent 3%, rgba(78, 216, 255, 0.5) 28%, rgba(143, 124, 255, 0.28) 62%, transparent 97%);
  pointer-events: none;
}
.detail-panel.show { transform: translateX(0) !important; }

.panel-back-btn {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 20px 32px;
  margin: 0;
  background: linear-gradient(180deg, rgba(9, 24, 58, 0.98) 0%, rgba(9, 24, 58, 0.92) 80%, transparent 100%);
  border: none;
  border-bottom: 1px solid rgba(78,216,255,0.1);
  color: #4ed8ff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  backdrop-filter: blur(20px);
  transition: all 0.3s;
}
.panel-back-btn svg {
  width: 22px;
  height: 22px;
  transition: transform 0.3s;
}
.panel-back-btn:hover {
  background: linear-gradient(180deg, rgba(78,216,255,0.1) 0%, rgba(78,216,255,0.05) 80%, transparent 100%);
  color: #fff;
}
.panel-back-btn:hover svg {
  transform: translateX(-4px);
}

.detail-inner {
  padding: 8px 32px 56px;
  min-height: 100%;
}

.detail-page { animation: fadeInUp 0.7s cubic-bezier(0.22, 1, 0.36, 1); }
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(26px); filter: blur(10px); }
  to { opacity: 1; transform: translateY(0); filter: blur(0); }
}

/* ============ 页面头部 ============ */
.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(78, 216, 255, 0.12);
  position: relative;
}
.page-header::after {
  content: '';
  position: absolute;
  bottom: -1px; left: 0;
  width: 80px; height: 2px;
  background: linear-gradient(90deg, #4ed8ff, transparent);
}
.header-icon {
  width: 48px; height: 48px;
  border-radius: 12px;
  border: 1px solid;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.header-icon svg { width: 24px; height: 24px; filter: drop-shadow(0 0 6px rgba(78, 216, 255, 0.35)); }
.header-titles { flex: 1; }
.header-titles h2 {
  margin: 0; font-size: 25px; font-weight: 750; letter-spacing: 0.4px;
  background: linear-gradient(135deg, #ffffff 40%, #a9dcff 100%);
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.header-titles p {
  margin: 4px 0 0; font-size: 13px; color: rgba(255,255,255,0.45);
}
.header-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 20px; font-weight: 800;
}

/* ============ 通用区块 ============ */
.tech-section { margin-top: 32px; }

/* 成就墙 — 平行四边形外框 */
.tech-section--badge-wall {
  position: relative;
  margin-top: 36px;
  padding: 18px 18px 26px;
}
.tech-section--badge-wall .tech-frame-frame {
  position: absolute;
  inset: 0;
  clip-path: polygon(0 0, 100% 0, 100% 100%, 22px 100%);
  border: 1px solid rgba(78, 216, 255, 0.32);
  border-radius: 14px 14px 16px 18px;
  background: linear-gradient(135deg, rgba(78, 216, 255, 0.09), rgba(143, 124, 255, 0.04));
  box-shadow:
    inset 0 1px 0 rgba(208, 243, 255, 0.1),
    inset 0 -1px 0 rgba(78, 216, 255, 0.08);
  pointer-events: none;
}
.tech-section--badge-wall::after {
  /* 左下延伸接"地面"的斜角底座斜边 */
  content: '';
  position: absolute;
  left: 0; bottom: 0;
  width: 22px; height: 18px;
  border-left: 1px solid rgba(78, 216, 255, 0.42);
  border-bottom: 1px solid rgba(78, 216, 255, 0.42);
  transform: skewX(-14deg);
  transform-origin: bottom left;
  pointer-events: none;
}
.tech-section--badge-wall .section-title,
.tech-section--badge-wall .badge-wall {
  position: relative;
  z-index: 1;
}
.section-title {
  margin: 0 0 18px;
  font-size: 15px; font-weight: 600;
  color: rgba(255,255,255,0.9);
  display: flex; align-items: center; gap: 10px;
}
.st-line {
  width: 3px; height: 15px;
  background: linear-gradient(180deg, #4ed8ff, #8f7cff);
  border-radius: 2px;
  box-shadow: 0 0 10px rgba(78, 216, 255, 0.5);
}

/* ============ 匹配度页 ============ */
.hero-ring-section {
  display: flex;
  gap: 20px;
  align-items: center;
  padding: 24px;
  background: linear-gradient(135deg, rgba(78,216,255,0.06), rgba(6,182,212,0.02));
  border: 1px solid rgba(78,216,255,0.15);
  border-radius: 16px;
}
.big-ring-wrap {
  position: relative;
  width: 200px; height: 200px;
  flex-shrink: 0;
}
.big-ring-svg { width: 100%; height: 100%; }
.big-ring-center {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.br-num { font-size: 56px; font-weight: 800; color: #fff; line-height: 1; text-shadow: 0 0 30px rgba(78,216,255,0.5); }
.br-pct { font-size: 20px; color: #4ed8ff; font-weight: 600; margin-top: 2px; }
.br-lbl { font-size: 12px; color: rgba(255,255,255,0.45); margin-top: 4px; letter-spacing: 1px; }

.stats-grid-4 { flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.tech-stat-card {
  padding: 14px;
  background: linear-gradient(160deg, rgba(78,216,255,0.05), rgba(255,255,255,0.02));
  border: 1px solid rgba(78,216,255,0.16);
  border-radius: 13px;
  position: relative;
  overflow: hidden;
  transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
}
.tech-stat-card:hover {
  border-color: rgba(78, 216, 255, 0.38);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(4, 16, 44, 0.5);
}
.tech-stat-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 2px;
  background: var(--accent);
  opacity: 0.6;
}
.tsc-icon { font-size: 16px; }
.tsc-val { font-size: 24px; font-weight: 700; margin-top: 4px; }
.tsc-lbl { font-size: 11px; color: rgba(255,255,255,0.45); margin-top: 2px; }
.tsc-bar { height: 3px; background: rgba(255,255,255,0.06); border-radius: 2px; margin-top: 8px; overflow: hidden; }
.tsc-bar-fill { height: 100%; border-radius: 2px; }

.dim-bars { display: flex; flex-direction: column; gap: 14px; }
.dim-bar-row { display: flex; align-items: center; gap: 12px; }
.dbr-label { width: 70px; font-size: 13px; color: rgba(255,255,255,0.7); flex-shrink: 0; }
.dbr-track { flex: 1; height: 10px; background: rgba(255,255,255,0.05); border-radius: 5px; overflow: hidden; position: relative; }
.dbr-fill { height: 100%; border-radius: 5px; transition: width 1.2s ease; }
.dbr-marker { position: absolute; top: -2px; width: 1px; height: 14px; background: rgba(255,255,255,0.15); }
.dbr-val { width: 44px; text-align: right; font-size: 14px; font-weight: 700; }

.gap-cards { display: flex; flex-direction: column; gap: 10px; }
.gap-card {
  display: flex; align-items: center; gap: 14px;
  padding: 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 13px;
  border-left: 3px solid;
  transition: all 0.28s;
}
.gap-card:hover { transform: translateX(4px); border-color: rgba(255,255,255,0.12); box-shadow: 0 8px 24px rgba(4, 16, 44, 0.45); }
.gap-card.level-high { border-left-color: #ff6b6b; background: linear-gradient(90deg, rgba(255,107,107,0.06), transparent); }
.gap-card.level-medium { border-left-color: #ffb65c; background: linear-gradient(90deg, rgba(255,182,92,0.06), transparent); }
.gc-rank {
  width: 32px; height: 32px; border-radius: 8px;
  background: rgba(255,255,255,0.05);
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 16px; color: rgba(255,255,255,0.6);
  flex-shrink: 0;
}
.gc-body { flex: 1; }
.gc-title { font-size: 14px; color: #fff; font-weight: 600; }
.gc-desc { font-size: 12px; color: rgba(255,255,255,0.45); margin-top: 3px; }
.gc-tags { display: flex; gap: 6px; margin-top: 8px; }
.gc-tags span {
  padding: 2px 8px;
  background: rgba(78,216,255,0.1);
  border-radius: 4px;
  font-size: 11px; color: #4ed8ff;
}
.gc-btn {
  padding: 7px 16px;
  background: linear-gradient(135deg, #4ed8ff, #06b6d4);
  border: none; border-radius: 6px;
  color: #050d1f; font-size: 12px; font-weight: 600;
  cursor: pointer; flex-shrink: 0;
  transition: all 0.3s;
}
.gc-btn:hover { box-shadow: 0 0 15px rgba(78,216,255,0.4); }

.trend-chart {
  padding: 20px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 12px;
}
.trend-svg { width: 100%; height: 170px; }

/* ============ 能力图谱页 ============ */
.radar-hero {
  display: flex; justify-content: center;
  padding: 20px;
  background: radial-gradient(ellipse at center, rgba(78,216,255,0.06), transparent 70%);
  border-radius: 16px;
}
.radar-big-svg { width: 340px; height: 340px; }

.skill-cards-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.skill-card {
  padding: 14px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  position: relative;
}
.sc-header { display: flex; justify-content: space-between; align-items: center; }
.sc-name { font-size: 14px; color: #fff; font-weight: 600; }
.sc-val { font-size: 20px; font-weight: 800; }
.sc-mini-ring { position: absolute; top: 10px; right: 10px; width: 36px; height: 36px; opacity: 0.6; }
.sc-mini-ring svg { width: 100%; height: 100%; }
.sc-desc { font-size: 11px; color: rgba(255,255,255,0.4); margin-top: 6px; line-height: 1.4; }
.sc-level {
  display: inline-block;
  margin-top: 8px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px; font-weight: 600;
}
.sc-level.lv-good { background: #37d6a520; color: #37d6a5; }
.sc-level.lv-mid { background: #4ed8ff20; color: #4ed8ff; }
.sc-level.lv-weak { background: #ffb65c20; color: #ffb65c; }

.weak-cards { display: flex; flex-direction: column; gap: 10px; }
.weak-card {
  display: flex; gap: 14px;
  padding: 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
}
.wc-icon {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; flex-shrink: 0;
}
.wc-body { flex: 1; }
.wc-title { font-size: 14px; color: #fff; font-weight: 600; }
.wc-desc { font-size: 12px; color: rgba(255,255,255,0.5); margin-top: 4px; line-height: 1.5; }
.wc-suggest { font-size: 12px; color: #37d6a5; margin-top: 6px; }

/* ============ 推荐岗位页 ============ */
.filter-tabs { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
.ft-btn {
  padding: 7px 16px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  color: rgba(255,255,255,0.5);
  font-size: 13px; cursor: pointer;
  transition: all 0.3s;
}
.ft-btn.active, .ft-btn:hover {
  background: rgba(78,216,255,0.15);
  border-color: #4ed8ff;
  color: #4ed8ff;
}

.job-list { display: flex; flex-direction: column; gap: 10px; }
.job-row {
  display: flex; align-items: center; gap: 14px;
  padding: 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  transition: all 0.3s;
}
.job-row:hover {
  border-color: rgba(78,216,255,0.3);
  transform: translateX(4px);
  background: rgba(78,216,255,0.04);
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.jr-rank {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 800; flex-shrink: 0;
}
.rank-badge-1 { background: linear-gradient(135deg, #f59e0b, #d97706); color: #fff; box-shadow: 0 0 20px rgba(245,158,11,0.3); }
.rank-badge-2 { background: linear-gradient(135deg, #94a3b8, #64748b); color: #fff; }
.rank-badge-3 { background: linear-gradient(135deg, #b45309, #92400e); color: #fff; }
.rank-badge-4, .rank-badge-5 { background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.4); border: 1px solid rgba(255,255,255,0.1); }
.jr-info { flex: 1; min-width: 0; }
.jr-top { display: flex; justify-content: space-between; align-items: center; }
.jr-name { font-size: 15px; color: #fff; font-weight: 600; }
.jr-salary { font-size: 15px; color: #ff6b6b; font-weight: 700; }
.jr-meta { font-size: 12px; color: rgba(255,255,255,0.4); margin-top: 4px; }
.jr-tags { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }
.jr-tag {
  padding: 2px 8px;
  background: rgba(78,216,255,0.1);
  border-radius: 4px;
  font-size: 11px; color: #4ed8ff;
}
.jr-match-bar { display: flex; align-items: center; gap: 8px; margin-top: 8px; }
.jrmb-label { font-size: 11px; color: rgba(255,255,255,0.4); }
.jrmb-track { flex: 1; height: 5px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; }
.jrmb-fill { height: 100%; border-radius: 3px; transition: width 1s ease; }
.jrmb-val { font-size: 13px; font-weight: 700; width: 36px; text-align: right; }
.jr-action { display: flex; flex-direction: column; gap: 6px; flex-shrink: 0; }
.jr-btn {
  padding: 7px 14px;
  background: linear-gradient(135deg, #4ed8ff, #06b6d4);
  border: none; border-radius: 6px;
  color: #050d1f; font-size: 12px; font-weight: 600;
  cursor: pointer; transition: all 0.3s;
}
.jr-btn:hover { box-shadow: 0 0 15px rgba(78,216,255,0.4); }
.jr-btn-outline {
  padding: 6px 14px;
  background: transparent;
  border: 1px solid rgba(78,216,255,0.3);
  border-radius: 6px;
  color: #4ed8ff; font-size: 12px;
  cursor: pointer; transition: all 0.3s;
}
.jr-btn-outline:hover { background: rgba(78,216,255,0.1); }

/* ============ AI建议页 ============ */
.ai-featured-card {
  position: relative;
  display: flex; gap: 24px;
  padding: 28px;
  background: linear-gradient(135deg, rgba(168,85,247,0.12), rgba(78,216,255,0.05));
  border: 1px solid rgba(168,85,247,0.3);
  border-radius: 20px;
  overflow: hidden;
}
.afc-glow {
  position: absolute;
  top: -50%; right: -20%;
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(168,85,247,0.15), transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}
.afc-cube {
  width: 90px; height: 90px;
  position: relative;
  transform-style: preserve-3d;
  animation: cubeSpin 10s linear infinite;
  flex-shrink: 0;
}
.cube-face {
  position: absolute;
  width: 90px; height: 90px;
  border: 2px solid rgba(168,85,247,0.5);
  background: rgba(168,85,247,0.08);
  border-radius: 4px;
}
.cf-front { transform: translateZ(45px); }
.cf-back { transform: rotateY(180deg) translateZ(45px); }
.cf-right { transform: rotateY(90deg) translateZ(45px); }
.cf-left { transform: rotateY(-90deg) translateZ(45px); }
.cf-top { transform: rotateX(90deg) translateZ(45px); }
.cf-bottom { transform: rotateX(-90deg) translateZ(45px); }
@keyframes cubeSpin { to { transform: rotateX(360deg) rotateY(360deg); } }
.afc-body { position: relative; z-index: 1; flex: 1; }
.afc-tag {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(255,107,107,0.15);
  border: 1px solid rgba(255,107,107,0.3);
  border-radius: 20px;
  font-size: 12px; color: #ff6b6b; font-weight: 600;
  margin-bottom: 10px;
}
.afc-body h3 { margin: 0 0 8px; font-size: 22px; color: #fff; font-weight: 700; }
.afc-body p { margin: 0; font-size: 13px; color: rgba(255,255,255,0.6); line-height: 1.7; }
.afc-tags { display: flex; gap: 8px; margin: 14px 0; flex-wrap: wrap; }
.afc-tags span {
  padding: 4px 12px;
  background: rgba(168,85,247,0.15);
  border: 1px solid rgba(168,85,247,0.3);
  border-radius: 6px;
  font-size: 12px; color: #c084fc;
}
.afc-btn {
  padding: 12px 28px;
  background: linear-gradient(135deg, #a855f7, #7c3aed);
  border: none; border-radius: 10px;
  color: #fff; font-size: 14px; font-weight: 600;
  cursor: pointer; transition: all 0.3s;
  margin-top: 4px;
}
.afc-btn:hover { box-shadow: 0 0 25px rgba(168,85,247,0.4); transform: scale(1.02); }

.learning-steps { position: relative; padding-left: 8px; }
.ls-item {
  display: flex; gap: 16px;
  padding: 12px 0;
  position: relative;
}
.ls-connector {
  position: absolute;
  left: 17px; top: 44px; bottom: -12px;
  width: 2px;
  background: rgba(255,255,255,0.08);
}
.ls-item.done .ls-connector { background: #37d6a540; }
.ls-node {
  width: 36px; height: 36px; border-radius: 50%;
  border: 2px solid rgba(78,216,255,0.4);
  background: rgba(78,216,255,0.1);
  color: #4ed8ff;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700;
  flex-shrink: 0; z-index: 1;
}
.ls-item.done .ls-node { background: #37d6a5; border-color: #37d6a5; color: #050d1f; }
.ls-item.current .ls-node {
  background: rgba(168,85,247,0.2); border-color: #a855f7; color: #c084fc;
  animation: nodePulse 2s ease-in-out infinite;
}
@keyframes nodePulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(168,85,247,0.4); }
  50% { box-shadow: 0 0 0 10px rgba(168,85,247,0); }
}
.ls-content { flex: 1; padding-top: 4px; }
.ls-title { font-size: 15px; color: #fff; font-weight: 600; }
.ls-item.done .ls-title { color: rgba(255,255,255,0.45); text-decoration: line-through; }
.ls-desc { font-size: 12px; color: rgba(255,255,255,0.45); margin-top: 3px; line-height: 1.5; }
.ls-meta { display: flex; gap: 16px; margin-top: 6px; }
.ls-time, .ls-diff { font-size: 11px; color: rgba(255,255,255,0.35); }

.page-resource-library { display: grid; gap: 18px; padding-top: 8px; padding-bottom: 24px; }

/* 资源库 — 长方形外框 + 下方底座（贴在一起） */
.resource-frame {
  position: relative;
  padding: 4px;
  margin-bottom: 6px;
}
.resource-frame__inner {
  position: relative;
  padding: 18px 18px 6px;
  border: 1px solid rgba(78, 216, 255, 0.28);
  border-radius: 18px 18px 4px 4px;
  background:
    linear-gradient(180deg, rgba(10, 42, 80, 0.55), rgba(7, 24, 52, 0.28));
  box-shadow:
    inset 0 1px 0 rgba(210, 241, 255, 0.09),
    inset 0 -1px 0 rgba(78, 216, 255, 0.06);
}
.resource-frame__base {
  position: relative;
  margin: -1px 6px 0;
  height: 22px;
  border: 1px solid rgba(78, 216, 255, 0.22);
  border-top: none;
  border-radius: 0 0 18px 18px;
  background:
    linear-gradient(180deg, rgba(78, 216, 255, 0.12), rgba(10, 30, 64, 0.7));
  box-shadow:
    inset 0 -1px 0 rgba(78, 216, 255, 0.1),
    0 10px 28px rgba(1, 9, 28, 0.5);
}
.resource-frame__base::before {
  content: '';
  position: absolute;
  left: 14%; right: 14%;
  top: 6px;
  height: 3px;
  background: linear-gradient(90deg, transparent, rgba(78, 216, 255, 0.5), transparent);
  border-radius: 3px;
}
.resource-frame__base::after {
  content: '';
  position: absolute;
  left: 22%; right: 22%;
  top: 13px;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(143, 124, 255, 0.35), transparent);
  border-radius: 2px;
}
.resource-library__icon { color: #8ae8ff; background: linear-gradient(135deg, rgba(63, 211, 255, .2), rgba(44, 106, 196, .12)); border-color: rgba(106, 224, 255, .6); }
.resource-library__icon svg { width: 25px; height: 25px; }
.resource-library__count { margin-left: auto; padding: 6px 9px; border: 1px solid rgba(101, 221, 255, .34); border-radius: 2px; color: #7ee9ff; font: 700 10px/1 Bahnschrift, sans-serif; letter-spacing: .11em; }
.resource-library__brief { display: flex; align-items: center; justify-content: space-between; gap: 24px; padding: 22px 24px; border: 1px solid rgba(109, 226, 255, .2); border-radius: 14px; background: linear-gradient(120deg, rgba(7, 54, 86, .76), rgba(13, 31, 59, .54) 64%, rgba(27, 89, 118, .22)); box-shadow: inset 0 1px 0 rgba(216, 249, 255, .08); }
.resource-library__brief span { color: #7de5fb; font: 700 10px/1 Bahnschrift, sans-serif; letter-spacing: .14em; }
.resource-library__brief h3 { margin: 8px 0 7px; color: #f3fcff; font: 700 23px/1.1 "Microsoft YaHei", sans-serif; }
.resource-library__brief p { max-width: 420px; margin: 0; color: rgba(217, 244, 255, .68); font-size: 13px; line-height: 1.7; }
.resource-library__meter { display: grid; min-width: 104px; min-height: 104px; place-items: center; align-content: center; border: 1px solid rgba(117, 230, 255, .65); border-radius: 50%; background: radial-gradient(circle, rgba(54, 197, 246, .28), rgba(14, 72, 104, .15) 57%, transparent 58%); box-shadow: 0 0 22px rgba(49, 207, 255, .18); }
.resource-library__meter strong { color: #e1fbff; font: 800 26px/1 Bahnschrift, sans-serif; }
.resource-library__meter small { margin-top: 5px; color: #83dff4; font: 700 8px/1 Bahnschrift, sans-serif; letter-spacing: .1em; }
.resource-library__grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 11px; }
.resource-library__card { position: relative; min-height: 142px; padding: 18px 18px 15px; overflow: hidden; border: 1px solid color-mix(in srgb, var(--resource-color) 34%, transparent); border-radius: 12px; background: linear-gradient(135deg, color-mix(in srgb, var(--resource-color) 12%, rgba(15, 30, 56, .92)), rgba(9, 22, 43, .88)); transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease; }
.resource-library__card::before { position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: var(--resource-color); content: ''; }
.resource-library__card:hover { transform: translateY(-3px); border-color: var(--resource-color); box-shadow: 0 12px 28px color-mix(in srgb, var(--resource-color) 17%, transparent); }
.resource-library__index { position: absolute; top: 13px; right: 16px; color: rgba(209, 242, 250, .31); font: 800 19px/1 Bahnschrift, sans-serif; }
.resource-library__type { display: inline-block; padding: 3px 7px; border: 1px solid color-mix(in srgb, var(--resource-color) 62%, transparent); color: var(--resource-color); font: 700 10px/1 "Microsoft YaHei", sans-serif; }
.resource-library__card h3 { max-width: 82%; margin: 11px 0 5px; color: #f1fbff; font: 700 15px/1.35 "Microsoft YaHei", sans-serif; }
.resource-library__card p { margin: 0; color: rgba(206, 236, 247, .54); font-size: 11px; }
.resource-library__card footer { display: flex; align-items: center; justify-content: space-between; margin-top: 14px; color: #ffcc70; font-size: 12px; }
.resource-library__card button, .resource-library__actions button { border: 0; background: none; color: #95e9ff; font: 600 11px/1 "Microsoft YaHei", sans-serif; cursor: pointer; }
.resource-library__card button:hover, .resource-library__actions button:hover { color: #fff; }
.resource-library__actions { display: flex; justify-content: flex-end; gap: 9px; }
.resource-library__actions button { padding: 10px 14px; border: 1px solid rgba(100, 225, 255, .6); border-radius: 5px; background: rgba(35, 170, 218, .18); }
.resource-library__actions button.ghost { border-color: rgba(213, 242, 255, .2); background: rgba(255, 255, 255, .025); color: rgba(221, 246, 255, .68); }
.resource-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.res-card {
  padding: 14px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
}
.rc-type {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 11px; font-weight: 600;
}
.rc-title { font-size: 13px; color: #fff; font-weight: 500; margin-top: 8px; line-height: 1.4; }
.rc-source { font-size: 11px; color: rgba(255,255,255,0.35); margin-top: 4px; }
.rc-rating { font-size: 12px; color: #f59e0b; margin-top: 6px; }

/* ============ 本周计划页 ============ */
.progress-big {
  position: relative;
  width: 64px; height: 64px;
  display: flex; align-items: center; justify-content: center;
}
.progress-big svg { width: 100%; height: 100%; }
.progress-big span {
  position: absolute;
  font-size: 14px; font-weight: 700; color: #37d6a5;
}
.progress-big b { font-size: 18px; }

.week-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 8px; }
.ws-card {
  padding: 14px 10px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  text-align: center;
}
.ws-icon {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; margin: 0 auto 6px;
}
.ws-val { font-size: 20px; font-weight: 700; }
.ws-lbl { font-size: 11px; color: rgba(255,255,255,0.4); margin-top: 2px; }

.task-list { display: flex; flex-direction: column; gap: 8px; }
.task-item {
  display: flex; align-items: center; gap: 14px;
  padding: 14px 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  cursor: pointer; transition: all 0.3s;
}
.task-item:hover { background: rgba(78,216,255,0.05); border-color: rgba(78,216,255,0.2); }
.task-item.done { opacity: 0.6; }
.ti-check {
  width: 24px; height: 24px; border-radius: 7px;
  border: 2px solid rgba(78,216,255,0.4);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: all 0.3s;
}
.ti-check svg { width: 14px; height: 14px; }
.task-item.done .ti-check { background: #37d6a5; border-color: #37d6a5; }
.ti-body { flex: 1; }
.ti-text { font-size: 14px; color: #fff; }
.task-item.done .ti-text { text-decoration: line-through; color: rgba(255,255,255,0.4); }
.ti-meta { display: flex; gap: 8px; margin-top: 5px; align-items: center; }
.ti-date { font-size: 11px; color: rgba(255,255,255,0.35); }
.ti-cat {
  padding: 1px 8px;
  border-radius: 4px;
  font-size: 10px; font-weight: 600;
}
.ti-points {
  font-size: 13px; font-weight: 700;
  color: #f59e0b;
  flex-shrink: 0;
}

/* ============ 模拟面试页 ============ */
.interview-hero {
  display: flex; gap: 24px;
  padding: 28px;
  background: linear-gradient(135deg, rgba(78,216,255,0.08), rgba(168,85,247,0.04));
  border: 1px solid rgba(78,216,255,0.2);
  border-radius: 20px;
  align-items: center;
}
.ih-score-ring {
  position: relative;
  width: 180px; height: 180px;
  flex-shrink: 0;
}
.ih-score-ring svg { width: 100%; height: 100%; }
.ihsr-center {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.ihsr-num { font-size: 52px; font-weight: 800; color: #4ed8ff; line-height: 1; text-shadow: 0 0 25px rgba(78,216,255,0.5); }
.ihsr-total { font-size: 18px; color: rgba(255,255,255,0.3); }
.ihsr-grade {
  margin-top: 6px;
  padding: 3px 14px;
  background: rgba(55,214,165,0.15);
  border-radius: 10px;
  font-size: 13px; color: #37d6a5; font-weight: 600;
}
.ih-info { flex: 1; }
.ih-dims { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
.ih-dim { display: flex; align-items: center; gap: 10px; }
.ihd-name { width: 70px; font-size: 13px; color: rgba(255,255,255,0.7); flex-shrink: 0; }
.ihd-bar { flex: 1; height: 8px; background: rgba(255,255,255,0.06); border-radius: 4px; overflow: hidden; }
.ihd-fill { height: 100%; border-radius: 4px; }
.ihd-val { width: 32px; font-size: 14px; font-weight: 700; text-align: right; }
.ih-start-btn {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 32px;
  background: linear-gradient(135deg, #4ed8ff, #06b6d4);
  border: none; border-radius: 12px;
  color: #050d1f; font-size: 15px; font-weight: 700;
  cursor: pointer; transition: all 0.3s;
}
.ih-start-btn svg { width: 18px; height: 18px; }
.ih-start-btn:hover { box-shadow: 0 0 30px rgba(78,216,255,0.5); transform: scale(1.03); }
.ih-tips { display: flex; gap: 16px; margin-top: 12px; }
.ih-tips span { font-size: 12px; color: rgba(255,255,255,0.4); }

.interview-records { display: flex; flex-direction: column; gap: 8px; }
.ir-item {
  display: flex; align-items: center; gap: 16px;
  padding: 14px 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
}
.ir-date { width: 50px; font-size: 13px; color: rgba(255,255,255,0.4); flex-shrink: 0; }
.ir-body { flex: 1; }
.ir-pos { font-size: 14px; color: #fff; font-weight: 500; }
.ir-tags { display: flex; gap: 6px; margin-top: 4px; }
.ir-tags span { font-size: 11px; color: rgba(255,255,255,0.35); }
.ir-score { font-size: 18px; font-weight: 800; }

/* ============ 时间线页 ============ */
.timeline-container { position: relative; padding: 10px 0; }
.tl-axis {
  position: absolute;
  left: 50%; top: 0; bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, rgba(78,216,255,0.4), rgba(168,85,247,0.3), rgba(236,72,153,0.2));
  transform: translateX(-50%);
}
.tl-entry {
  position: relative;
  display: flex;
  margin-bottom: 20px;
  width: 100%;
}
.tl-entry.tl-side-left { justify-content: flex-start; }
.tl-entry.tl-side-right { justify-content: flex-end; }
.tl-entry .tl-card {
  width: calc(50% - 40px);
  padding: 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid;
  border-radius: 12px;
  position: relative;
}
.tl-entry.tl-side-right .tl-card { text-align: left; }
.tl-dot {
  position: absolute;
  left: 50%; top: 18px;
  width: 28px; height: 28px;
  border-radius: 50%;
  border: 3px solid #050d1f;
  transform: translateX(-50%);
  z-index: 2;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px;
}
.tlc-date { font-size: 12px; font-weight: 700; }
.tlc-title { font-size: 15px; color: #fff; font-weight: 600; margin-top: 6px; }
.tlc-desc { font-size: 12px; color: rgba(255,255,255,0.5); margin-top: 6px; line-height: 1.6; }
.tlc-reward {
  margin-top: 8px;
  padding: 5px 10px;
  background: rgba(245,158,11,0.1);
  border-radius: 6px;
  font-size: 11px; color: #f59e0b;
  display: inline-block;
}

/* ============ 成长路径页 ============ */
.path-visual {
  position: relative;
  padding: 30px 0 20px;
  margin-bottom: 24px;
}
.path-svg { width: 100%; height: 200px; position: absolute; top: 0; left: 0; }
.path-nodes-horiz { position: relative; height: 180px; display: flex; justify-content: space-between; }
.pnh-node {
  position: absolute;
  display: flex; flex-direction: column; align-items: center;
  top: 100px;
  transform: translateX(-50%);
}
.pnh-icon {
  width: 56px; height: 64px;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
  background: rgba(255,255,255,0.04);
  border: 2px solid var(--c);
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 700; color: var(--c);
  transition: all 0.3s;
  position: relative;
}
.pnh-node.done .pnh-icon {
  background: rgba(78,216,255,0.25);
  box-shadow: 0 0 20px rgba(78,216,255,0.4);
}
.pnh-node.current .pnh-icon {
  animation: nodePulse2 2s ease-in-out infinite;
}
@keyframes nodePulse2 {
  0%, 100% { box-shadow: 0 0 15px rgba(96,165,250,0.4); transform: translateX(-50%) scale(1); }
  50% { box-shadow: 0 0 30px rgba(96,165,250,0.7); transform: translateX(-50%) scale(1.08); }
}
.pnh-check {
  position: absolute;
  bottom: -4px; right: -4px;
  width: 20px; height: 20px;
  background: #37d6a5;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; color: #050d1f;
  border: 2px solid #050d1f;
}
.pnh-name { font-size: 13px; color: #fff; font-weight: 600; margin-top: 10px; }
.pnh-sub { font-size: 11px; color: rgba(255,255,255,0.4); margin-top: 2px; }

.current-stage-card {
  padding: 24px;
  background: linear-gradient(135deg, rgba(96,165,250,0.08), rgba(168,85,247,0.05));
  border: 1px solid rgba(96,165,250,0.25);
  border-radius: 16px;
}
.csc-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.csc-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px; font-weight: 700;
  color: #fff;
}
.csc-header h3 { margin: 0; font-size: 18px; color: #fff; }
.current-stage-card p { margin: 0; font-size: 13px; color: rgba(255,255,255,0.6); line-height: 1.7; }
.csc-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 16px 0; }
.csc-item {
  padding: 10px;
  background: rgba(255,255,255,0.04);
  border-radius: 8px;
  text-align: center;
}
.csc-i-label { display: block; font-size: 11px; color: rgba(255,255,255,0.4); }
.csc-i-val { display: block; font-size: 16px; font-weight: 700; color: #fff; margin-top: 4px; }
.csc-resources h4 { margin: 16px 0 8px; font-size: 13px; color: #fff; font-weight: 600; }
.csc-resources ul { margin: 0; padding-left: 18px; }
.csc-resources li { font-size: 12px; color: rgba(255,255,255,0.5); line-height: 1.8; }

/* ============ 个人中心页 ============ */
.profile-hero {
  display: flex; gap: 24px; align-items: center;
  padding: 24px;
  background: linear-gradient(135deg, rgba(78,216,255,0.08), rgba(168,85,247,0.05));
  border: 1px solid rgba(78,216,255,0.2);
  border-radius: 20px;
  margin-bottom: 20px;
}
.ph-avatar-ring {
  position: relative;
  width: 130px; height: 130px;
  flex-shrink: 0;
}
.ph-avatar-ring svg { width: 100%; height: 100%; }
.ph-avatar-inner {
  position: absolute; inset: 12px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4ed8ff, #a855f7);
  display: flex; align-items: center; justify-content: center;
  font-size: 48px; font-weight: 800; color: #fff;
}
.ph-info { flex: 1; }
.ph-info h2 { margin: 0; font-size: 28px; color: #fff; font-weight: 800; }
.ph-tags { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
.ph-tag {
  padding: 4px 12px;
  background: rgba(78,216,255,0.12);
  border: 1px solid rgba(78,216,255,0.25);
  border-radius: 20px;
  font-size: 12px; color: #4ed8ff; font-weight: 500;
}
.ph-level-bar { display: flex; align-items: center; gap: 10px; margin-top: 16px; }
.phlb-label { font-size: 12px; color: rgba(255,255,255,0.5); }
.phlb-track { flex: 1; height: 8px; background: rgba(255,255,255,0.06); border-radius: 4px; overflow: hidden; max-width: 200px; }
.phlb-fill { height: 100%; width: 78%; background: linear-gradient(90deg, #4ed8ff, #a855f7); border-radius: 4px; box-shadow: 0 0 10px rgba(78,216,255,0.4); }
.phlb-val { font-size: 14px; font-weight: 700; color: #4ed8ff; }
.ph-xp { font-size: 12px; color: rgba(255,255,255,0.4); margin-top: 8px; }
.ph-xp b { color: #f59e0b; font-weight: 700; }

.stats-dashboard { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 8px; }
.sd-card {
  padding: 16px 10px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  text-align: center;
}
.sdc-icon {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; margin: 0 auto 8px;
}
.sdc-val { font-size: 22px; font-weight: 700; color: #fff; }
.sdc-lbl { font-size: 11px; color: rgba(255,255,255,0.4); margin-top: 2px; }

.badge-wall { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.badge-item {
  padding: 14px 8px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  text-align: center;
  transition: all 0.3s;
}
.badge-item.locked { opacity: 0.4; }
.bi-icon {
  width: 44px; height: 44px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
  margin: 0 auto 8px;
}
.badge-item:not(.locked):hover { transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0,0,0,0.3); }
.badge-item span { font-size: 11px; color: rgba(255,255,255,0.6); }

.heatmap { display: flex; flex-direction: column; gap: 4px; padding: 16px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; }
.hm-row { display: flex; gap: 4px; justify-content: center; }
.hm-cell { width: 16px; height: 16px; border-radius: 3px; transition: all 0.2s; }
.hm-cell:hover { transform: scale(1.3); }
.hm-legend { display: flex; align-items: center; gap: 6px; justify-content: flex-end; margin-top: 10px; font-size: 11px; color: rgba(255,255,255,0.3); }
.hml-cell { width: 14px; height: 14px; border-radius: 2px; }
</style>
