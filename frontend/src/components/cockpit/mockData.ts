import type { UserProfile, Skill, TargetRole, SkillEvidence, LearningStage, MockInterview, GrowthEvent, SkillOrbit, SkillSize } from './types'

export const mockProfile: UserProfile = {
  id: 'u-001',
  name: '张同学',
  avatar: '张',
  currentIdentity: '计算机科学 · 硕士在读',
  growthStage: '岗位冲刺期',
  currentLevel: '进阶中',
  targetRoleId: 'r-ai-eng',
  updatedAt: '2026-08-03',
  summary: 'AI算法方向求职中'
}

export const mockTargetRoles: TargetRole[] = [
  {
    id: 'r-ai-eng',
    name: 'AI算法工程师',
    icon: '🤖',
    level: '中级',
    city: '北京',
    matchScore: 72,
    matchChange: 4,
    requiredSkills: ['s-pytorch', 's-nlp', 's-rag', 's-ml', 's-python'],
    estimatedReadyDays: 45,
    coreSkillsCount: 6,
    matchedCoreCount: 3,
    categoryName: 'AI/大模型',
    matchDetails: { proSkill: 68, projectExp: 75, toolAbility: 82, generalAbility: 78, jobPrep: 62 }
  },
  {
    id: 'r-nlp-eng',
    name: 'NLP算法工程师',
    icon: '💬',
    level: '中级',
    city: '北京',
    matchScore: 85,
    matchChange: 12,
    requiredSkills: ['s-nlp', 's-rag', 's-python', 's-pytorch', 's-ml'],
    estimatedReadyDays: 30,
    coreSkillsCount: 6,
    matchedCoreCount: 5,
    categoryName: 'NLP',
    matchDetails: { proSkill: 82, projectExp: 88, toolAbility: 86, generalAbility: 80, jobPrep: 75 }
  },
  {
    id: 'r-data-mining',
    name: '数据挖掘工程师',
    icon: '📊',
    level: '初级',
    city: '上海',
    matchScore: 73,
    matchChange: 3,
    requiredSkills: ['s-python', 's-sql', 's-ml', 's-data-analysis'],
    estimatedReadyDays: 20,
    coreSkillsCount: 5,
    matchedCoreCount: 4,
    categoryName: '数据分析',
    matchDetails: { proSkill: 76, projectExp: 70, toolAbility: 85, generalAbility: 72, jobPrep: 60 }
  },
  {
    id: 'r-cv-eng',
    name: 'CV算法工程师',
    icon: '👁️',
    level: '中级',
    city: '深圳',
    matchScore: 61,
    matchChange: -2,
    requiredSkills: ['s-cv', 's-pytorch', 's-ml', 's-deploy'],
    estimatedReadyDays: 75,
    coreSkillsCount: 6,
    matchedCoreCount: 2,
    categoryName: '计算机视觉',
    matchDetails: { proSkill: 52, projectExp: 58, toolAbility: 70, generalAbility: 70, jobPrep: 55 }
  }
]

interface FullSkill extends Skill {
  orbit: SkillOrbit
  size: SkillSize
  angle: number
}

export const mockSkills: FullSkill[] = [
  { id: 's-pytorch', name: 'PyTorch', category: 'professional', currentLevel: 4, requiredLevel: 4, status: 'mastered', proficiency: 85, importance: 95, evidenceCount: 4, relatedProjects: ['BERT中文情感分类', 'RAG问答系统'], lastUsedAt: '2026-08-02', learningSuggestion: '继续深入分布式训练', orbit: 1, size: 'core', angle: 0 },
  { id: 's-nlp', name: 'NLP基础', category: 'professional', currentLevel: 4, requiredLevel: 4, status: 'mastered', proficiency: 82, importance: 90, evidenceCount: 5, relatedProjects: ['BERT中文情感分类', '文本摘要项目'], lastUsedAt: '2026-08-01', learningSuggestion: '巩固Transformer架构', orbit: 1, size: 'core', angle: 60 },
  { id: 's-rag', name: 'RAG技术', category: 'professional', currentLevel: 2, requiredLevel: 4, status: 'improving', proficiency: 45, importance: 98, evidenceCount: 2, relatedProjects: ['RAG问答系统(进行中)'], lastUsedAt: '2026-08-03', learningSuggestion: '重点学习检索增强生成评估体系', orbit: 1, size: 'core', angle: 120 },
  { id: 's-ml', name: '机器学习', category: 'professional', currentLevel: 3, requiredLevel: 4, status: 'improving', proficiency: 68, importance: 92, evidenceCount: 4, relatedProjects: ['用户流失预测'], lastUsedAt: '2026-07-28', learningSuggestion: '加强集成学习和模型调优', orbit: 1, size: 'core', angle: 180 },
  { id: 's-deploy', name: '模型工程化', category: 'professional', currentLevel: 1, requiredLevel: 3, status: 'missing', proficiency: 20, importance: 85, evidenceCount: 1, relatedProjects: [], lastUsedAt: '2026-06-10', learningSuggestion: '学习ONNX/TensorRT/Flask部署', orbit: 1, size: 'core', angle: 240 },
  { id: 's-eval', name: '评估体系', category: 'professional', currentLevel: 1, requiredLevel: 3, status: 'missing', proficiency: 18, importance: 88, evidenceCount: 0, relatedProjects: [], learningSuggestion: '学习RAGAG、MTEB等评测基准', orbit: 1, size: 'core', angle: 300 },

  { id: 's-python', name: 'Python', category: 'tools', currentLevel: 5, requiredLevel: 4, status: 'mastered', proficiency: 90, importance: 90, evidenceCount: 8, relatedProjects: ['全部项目'], lastUsedAt: '2026-08-04', learningSuggestion: '熟练掌握', orbit: 2, size: 'normal', angle: 30 },
  { id: 's-sql', name: 'SQL', category: 'tools', currentLevel: 4, requiredLevel: 3, status: 'mastered', proficiency: 80, importance: 70, evidenceCount: 3, relatedProjects: ['数据处理相关'], lastUsedAt: '2026-07-30', learningSuggestion: '窗口函数可再强化', orbit: 2, size: 'normal', angle: 72 },
  { id: 's-git', name: 'Git', category: 'tools', currentLevel: 4, requiredLevel: 3, status: 'mastered', proficiency: 85, importance: 65, evidenceCount: 2, relatedProjects: ['GitHub主页更新'], lastUsedAt: '2026-08-03', learningSuggestion: '保持熟练', orbit: 2, size: 'normal', angle: 114 },
  { id: 's-linux', name: 'Linux', category: 'tools', currentLevel: 2, requiredLevel: 3, status: 'improving', proficiency: 50, importance: 72, evidenceCount: 1, relatedProjects: ['云服务器部署'], lastUsedAt: '2026-07-15', learningSuggestion: '加强Shell和服务部署', orbit: 2, size: 'normal', angle: 156 },
  { id: 's-data-analysis', name: '数据分析', category: 'tools', currentLevel: 4, requiredLevel: 3, status: 'mastered', proficiency: 78, importance: 75, evidenceCount: 3, transferableFrom: 's-python', relatedProjects: ['电商用户行为分析'], lastUsedAt: '2026-07-20', learningSuggestion: '业务理解可加强', orbit: 2, size: 'normal', angle: 198 },
  { id: 's-cv', name: '计算机视觉', category: 'professional', currentLevel: 2, requiredLevel: 3, status: 'improving', proficiency: 40, importance: 60, evidenceCount: 1, transferableFrom: 's-pytorch', relatedProjects: ['图像分类项目'], lastUsedAt: '2026-06-01', learningSuggestion: '目标检测可学习', orbit: 2, size: 'normal', angle: 240 },
  { id: 's-mlops', name: 'MLOps', category: 'project', currentLevel: 1, requiredLevel: 3, status: 'missing', proficiency: 15, importance: 70, evidenceCount: 0, transferableFrom: 's-linux', relatedProjects: [], learningSuggestion: '学习MLflow/Docker/CI', orbit: 2, size: 'normal', angle: 282 },
  { id: 's-llm', name: '大模型应用', category: 'project', currentLevel: 2, requiredLevel: 4, status: 'improving', proficiency: 42, importance: 92, evidenceCount: 2, transferableFrom: 's-nlp', relatedProjects: ['RAG问答系统'], lastUsedAt: '2026-08-02', learningSuggestion: 'Prompt工程和Agent开发', orbit: 2, size: 'normal', angle: 324 },
  { id: 's-data-struct', name: '数据结构算法', category: 'professional', currentLevel: 3, requiredLevel: 4, status: 'improving', proficiency: 60, importance: 80, evidenceCount: 2, relatedProjects: ['LeetCode 200+'], lastUsedAt: '2026-08-01', learningSuggestion: '继续刷题保持手感', orbit: 2, size: 'normal', angle: 350 },

  { id: 's-comm', name: '沟通表达', category: 'general', currentLevel: 3, requiredLevel: 3, status: 'mastered', proficiency: 70, importance: 60, evidenceCount: 2, relatedProjects: ['社团负责人'], lastUsedAt: '2026-07-25', learningSuggestion: '面试表达再练', orbit: 3, size: 'minor', angle: 0 },
  { id: 's-paper', name: '论文复现', category: 'project', currentLevel: 3, requiredLevel: 3, status: 'mastered', proficiency: 65, importance: 65, evidenceCount: 2, transferableFrom: 's-pytorch', relatedProjects: ['论文复现2篇'], lastUsedAt: '2026-06-15', learningSuggestion: '保持复现习惯', orbit: 3, size: 'minor', angle: 60 },
  { id: 's-doc', name: '技术文档', category: 'general', currentLevel: 2, requiredLevel: 3, status: 'transferable', proficiency: 48, importance: 55, evidenceCount: 1, transferableFrom: 's-comm', relatedProjects: ['项目文档少量'], lastUsedAt: '2026-07-10', learningSuggestion: 'README和技术方案再规范', orbit: 3, size: 'minor', angle: 120 },
  { id: 's-interview', name: '面试表达', category: 'jobhunt', currentLevel: 2, requiredLevel: 4, status: 'improving', proficiency: 45, importance: 80, evidenceCount: 3, transferableFrom: 's-comm', relatedProjects: ['模拟面试5场'], lastUsedAt: '2026-08-04', learningSuggestion: '项目表达和BQ准备', orbit: 3, size: 'minor', angle: 180 },
  { id: 's-resume', name: '简历优化', category: 'jobhunt', currentLevel: 3, requiredLevel: 4, status: 'improving', proficiency: 60, importance: 75, evidenceCount: 2, relatedProjects: ['简历v3'], lastUsedAt: '2026-08-01', learningSuggestion: '量化成果加强', orbit: 3, size: 'minor', angle: 240 },
  { id: 's-logic', name: '结构化思维', category: 'general', currentLevel: 3, requiredLevel: 4, status: 'transferable', proficiency: 62, importance: 70, evidenceCount: 1, transferableFrom: 's-data-analysis', relatedProjects: [], lastUsedAt: '2026-07-20', learningSuggestion: 'MECE和STAR法则', orbit: 3, size: 'minor', angle: 300 }
]

export const mockEvidences: SkillEvidence[] = [
  { id: 'e1', skillId: 's-pytorch', sourceType: 'project', sourceId: 'p1', sourceTitle: 'BERT中文情感分类项目', content: '使用PyTorch实现BERT微调，F1达到0.91', credibility: 0.9, createdAt: '2026-06-10' },
  { id: 'e2', skillId: 's-rag', sourceType: 'project', sourceId: 'p2', sourceTitle: 'RAG知识库问答系统', content: '基于LangChain+Chroma实现，Top-3准确率82%', credibility: 0.85, createdAt: '2026-08-02' },
  { id: 'e3', skillId: 's-python', sourceType: 'certificate', sourceId: 'c1', sourceTitle: 'PyTorch官方开发者认证', content: '通过PyTorch官方认证考试', credibility: 0.95, createdAt: '2026-05-20' },
  { id: 'e4', skillId: 's-nlp', sourceType: 'project', sourceId: 'p1', sourceTitle: 'BERT中文情感分类项目', content: 'NLP预处理、分词、模型构建全流程', credibility: 0.9, createdAt: '2026-06-10' },
  { id: 'e5', skillId: 's-ml', sourceType: 'project', sourceId: 'p3', sourceTitle: '电商用户流失预测', content: 'XGBoost+LR，AUC 0.87', credibility: 0.8, createdAt: '2026-04-20' },
  { id: 'e6', skillId: 's-interview', sourceType: 'interview', sourceId: 'i5', sourceTitle: '第5次模拟面试', content: '得分78分，项目表达有进步', credibility: 0.85, createdAt: '2026-08-04' },
  { id: 'e7', skillId: 's-sql', sourceType: 'project', sourceId: 'p4', sourceTitle: '电商用户行为分析', content: '复杂查询、窗口函数应用', credibility: 0.75, createdAt: '2026-03-15' },
  { id: 'e8', skillId: 's-git', sourceType: 'portfolio', sourceId: 'c2', sourceTitle: 'GitHub主页', content: '2个完整项目，完善README', credibility: 0.8, createdAt: '2026-08-03' },
  { id: 'e9', skillId: 's-resume', sourceType: 'resume', sourceId: 'cv3', sourceTitle: '简历v3.2', content: '补充RAG学习项目，优化项目量化描述', credibility: 1.0, createdAt: '2026-08-01' },
  { id: 'e10', skillId: 's-llm', sourceType: 'project', sourceId: 'p2', sourceTitle: 'RAG知识库问答系统', content: '大模型应用、Prompt工程、向量检索', credibility: 0.85, createdAt: '2026-08-02' },
  { id: 'e11', skillId: 's-paper', sourceType: 'project', sourceId: 'p5', sourceTitle: '论文复现', content: '复现2篇NLP领域论文', credibility: 0.8, createdAt: '2026-06-15' },
  { id: 'e12', skillId: 's-data-struct', sourceType: 'assessment', sourceId: 'c3', sourceTitle: 'LeetCode刷题记录', content: '完成200+题，覆盖主要算法', credibility: 0.7, createdAt: '2026-08-01' }
]

export const mockGrowthStages: LearningStage[] = [
  { id: 'st1', name: '基础补齐', description: '补齐岗位必备基础技能', status: 'completed', progress: 100, tasks: [], unlockCondition: '', estimatedDays: 0, expectedMatchIncrease: 10, icon: '📚' },
  { id: 'st2', name: '核心技能强化', description: '深度学习核心技术栈', status: 'in-progress', progress: 60, tasks: [], unlockCondition: '', estimatedDays: 15, expectedMatchIncrease: 12, icon: '🎯' },
  { id: 'st3', name: '项目实战', description: '完成2-3个高质量项目', status: 'available', progress: 20, tasks: [], unlockCondition: '完成核心技能强化', estimatedDays: 20, expectedMatchIncrease: 15, icon: '🚀' },
  { id: 'st4', name: '作品集完善', description: '整理GitHub和技术博客', status: 'locked', progress: 0, tasks: [], unlockCondition: '项目实战阶段', estimatedDays: 7, expectedMatchIncrease: 5, icon: '📁' },
  { id: 'st5', name: '模拟面试', description: '10场模拟面试训练', status: 'locked', progress: 50, tasks: [], unlockCondition: '作品集完成', estimatedDays: 10, expectedMatchIncrease: 8, icon: '🎤' },
  { id: 'st6', name: '求职冲刺', description: '投递简历、笔试面试', status: 'locked', progress: 0, tasks: [], unlockCondition: '模拟面试达标', estimatedDays: 30, expectedMatchIncrease: 5, icon: '🏆' }
]

export const mockNextTask = {
  title: '完成 RAG 知识库问答系统',
  reason: '这是目标岗位核心技能缺口，完成后将显著提升匹配度',
  duration: '3.5小时',
  skills: ['RAG技术', '向量数据库', '大模型应用', '项目表达'],
  currentMatch: 72,
  expectedMatch: 76
}

export const mockWeekPlan = {
  tasksLeft: 3,
  hoursNeeded: 6.5,
  skillsBoosted: 3,
  matchBoost: 7
}

export const mockCoreGaps = [
  { id: 'g1', skillId: 's-eval', name: 'RAG评估体系', current: 1, required: 3, gap: 2, impact: '+5%', desc: '检索评估和答案质量评测是RAG核心' },
  { id: 'g2', skillId: 's-deploy', name: '大模型工程化', current: 1, required: 3, gap: 2, impact: '+4%', desc: '模型部署、推理优化是工程落地关键' },
  { id: 'g3', skillId: 's-interview', name: '项目业务表达', current: 2, required: 4, gap: 2, impact: '+3%', desc: '面试中清晰讲出项目业务价值' }
]

export const mockResumeStats = {
  fileName: '张同学_算法岗_2026届_v3.2.pdf',
  version: 'v3.2',
  updatedDays: 2,
  skillsExtracted: 18,
  projectsExtracted: 2,
  quantifiedAchievements: 5,
  recentUpdates: [
    { date: '08-01', action: '更新简历', detail: '补充RAG学习项目，优化项目量化描述' },
    { date: '07-25', action: '新增技能', detail: '补充大模型应用和RAG技能证据' },
    { date: '07-15', action: '项目更新', detail: 'BERT项目添加对比实验和消融分析' }
  ]
}

export const mockInterviews: MockInterview[] = [
  { id: 'i1', roleName: 'AI算法工程师', date: '2026-06-12', totalScore: 55, dimensionScores: [{ name: '专业知识', score: 50 }, { name: '项目经验', score: 52 }, { name: '逻辑思维', score: 60 }, { name: '业务理解', score: 48 }, { name: '沟通表达', score: 58 }], strengths: ['态度认真', '基础概念有印象'], weaknesses: ['项目表达不清晰', '算法细节不扎实'], suggestions: ['加强项目STAR表达', '复习Transformer细节'], questionCount: 8 },
  { id: 'i2', roleName: 'NLP算法工程师', date: '2026-06-28', totalScore: 62, dimensionScores: [{ name: '专业知识', score: 60 }, { name: '项目经验', score: 58 }, { name: '逻辑思维', score: 68 }, { name: '业务理解', score: 55 }, { name: '沟通表达', score: 65 }], strengths: ['基础有所提升', 'NLP概念比较清楚'], weaknesses: ['代码能力一般', '业务理解不够'], suggestions: ['加强手撕代码', '准备项目业务价值'], questionCount: 10 },
  { id: 'i3', roleName: 'AI算法工程师', date: '2026-07-12', totalScore: 67, dimensionScores: [{ name: '专业知识', score: 65 }, { name: '项目经验', score: 68 }, { name: '逻辑思维', score: 70 }, { name: '业务理解', score: 60 }, { name: '沟通表达', score: 68 }], strengths: ['项目表达有进步', '逻辑结构较好'], weaknesses: ['手撕代码卡壳', '大模型知识偏理论'], suggestions: ['继续刷题', '结合项目谈大模型应用'], questionCount: 10 },
  { id: 'i4', roleName: '数据挖掘工程师', date: '2026-07-25', totalScore: 73, dimensionScores: [{ name: '专业知识', score: 72 }, { name: '项目经验', score: 70 }, { name: '逻辑思维', score: 78 }, { name: '业务理解', score: 68 }, { name: '沟通表达', score: 75 }], strengths: ['SQL和数据分析表现好', '逻辑清晰'], weaknesses: ['算法深度不够', '业务案例少'], suggestions: ['保持优势', '补充业务场景理解'], questionCount: 10 },
  { id: 'i5', roleName: 'AI算法工程师', date: '2026-08-04', totalScore: 78, dimensionScores: [{ name: '专业知识', score: 76 }, { name: '项目经验', score: 80 }, { name: '逻辑思维', score: 80 }, { name: '业务理解', score: 72 }, { name: '沟通表达', score: 80 }], strengths: ['项目表达流畅', 'RAG项目讲述清楚'], weaknesses: ['模型部署了解不多', 'BQ问题准备不足'], suggestions: ['了解部署基本概念', '准备5-8个BQ故事'], questionCount: 12 }
]

export const mockGrowthEvents: GrowthEvent[] = [
  { id: 'ge1', type: 'resume_upload', title: '完善个人画像', description: '补充项目和实习细节', date: '2026-03-15', relatedSkills: [], matchScoreChange: 0, source: '简历' },
  { id: 'ge2', type: 'course_completed', title: '完成深度学习课程', description: '系统学习PyTorch和神经网络基础', date: '2026-04-02', relatedSkills: ['s-pytorch', 's-python'], matchScoreChange: 5, source: '课程' },
  { id: 'ge3', type: 'project_completed', title: '电商用户行为分析项目', description: '第一个完整数据分析项目', date: '2026-04-20', relatedSkills: ['s-python', 's-sql', 's-data-analysis'], matchScoreChange: 6, source: '项目' },
  { id: 'ge4', type: 'interview', title: '第1次模拟面试', description: '得分55分，发现面试表达薄弱', date: '2026-05-08', relatedSkills: ['s-interview'], matchScoreChange: 0, source: '面试' },
  { id: 'ge5', type: 'certificate', title: '通过PyTorch开发者认证', description: '官方认证证书', date: '2026-05-20', relatedSkills: ['s-pytorch'], matchScoreChange: 3, source: '证书' },
  { id: 'ge6', type: 'project_completed', title: 'BERT中文情感分类项目', description: '完成NLP课程项目，F1=0.91', date: '2026-06-10', relatedSkills: ['s-nlp', 's-pytorch', 's-paper'], matchScoreChange: 8, source: '项目' },
  { id: 'ge7', type: 'skill_added', title: '新增技能：RAG技术', description: '开始学习检索增强生成', date: '2026-07-05', relatedSkills: ['s-rag', 's-llm'], matchScoreChange: 2, source: '课程' },
  { id: 'ge8', type: 'match_increased', title: '匹配度提升15%', description: '推荐岗位更新，NLP方向更匹配', date: '2026-07-25', relatedSkills: [], matchScoreChange: 15, source: '系统' },
  { id: 'ge9', type: 'skill_added', title: '新增技能：模型部署与服务化', description: '开始学习Flask+ONNX部署', date: '2026-07-28', relatedSkills: ['s-linux', 's-deploy'], matchScoreChange: 1, source: '课程' },
  { id: 'ge10', type: 'interview', title: '第5次模拟面试78分', description: '连续进步，项目表达显著提升', date: '2026-08-01', relatedSkills: ['s-interview', 's-comm'], matchScoreChange: 6, source: '面试' },
  { id: 'ge11', type: 'stage_completed', title: '进入项目实战阶段', description: '开始RAG知识库问答系统开发', date: '2026-08-03', relatedSkills: ['s-rag', 's-llm'], matchScoreChange: 0, source: '学习路径' },
  { id: 'ge12', type: 'portfolio', title: 'GitHub主页更新', description: '整理2个项目，完善README', date: '2026-08-04', relatedSkills: ['s-git', 's-doc'], matchScoreChange: 2, source: '简历' }
]

export const mockRecommendedRoles = [
  { id: 'rr1', name: 'NLP算法工程师', company: '字节跳动', currentMatch: 85, matchChange: 12, recommendReason: 'NLP基础扎实，RAG项目经验匹配', transferableSkills: ['PyTorch', 'Python', 'NLP'], skillGaps: ['大模型工程化'], estimatedDays: 30, tag: 'current' as const },
  { id: 'rr2', name: 'AI算法工程师（大模型方向）', company: '百度', currentMatch: 72, matchChange: 4, recommendReason: '核心目标岗位，技能匹配度持续提升', transferableSkills: ['机器学习', 'Python'], skillGaps: ['RAG评估', '模型部署'], estimatedDays: 45, tag: 'current' as const },
  { id: 'rr3', name: '数据挖掘工程师', company: '美团', currentMatch: 73, matchChange: 3, recommendReason: '数据分析和SQL能力突出，门槛适中', transferableSkills: ['Python', 'SQL', '数据分析'], skillGaps: ['业务理解'], estimatedDays: 20, tag: 'easier' as const }
]

export function getSkillsByCategory(category: string) {
  return mockSkills.filter(s => s.category === category)
}

export function getSkillById(id: string) {
  return mockSkills.find(s => s.id === id)
}

export function getEvidencesBySkill(skillId: string) {
  return mockEvidences.filter(e => e.skillId === skillId)
}

export function getCurrentRole(roleId: string) {
  return mockTargetRoles.find(r => r.id === roleId) || mockTargetRoles[0]
}

export function getGaps() {
  return mockSkills.filter(s => s.status === 'missing' || s.status === 'improving')
    .sort((a, b) => b.importance * (b.requiredLevel - b.currentLevel) - a.importance * (a.requiredLevel - a.currentLevel))
}

export function getMatchDimensions(role: TargetRole) {
  const dims = (role as any).matchDetails || { proSkill: 70, projectExp: 70, toolAbility: 70, generalAbility: 70, jobPrep: 60 }
  return [
    { key: 'proSkill', name: '专业技能', val: dims.proSkill, color: '#4ed8ff' },
    { key: 'projectExp', name: '项目经验', val: dims.projectExp, color: '#36d7ff' },
    { key: 'toolAbility', name: '工具能力', val: dims.toolAbility, color: '#8f7cff' },
    { key: 'generalAbility', name: '通用能力', val: dims.generalAbility, color: '#ffb65c' },
    { key: 'jobPrep', name: '求职准备度', val: dims.jobPrep, color: '#ff7088' }
  ]
}
