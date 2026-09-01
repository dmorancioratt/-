export const cockpitMock = {
  student: { name: '张同学', level: 'Lv.18', role: 'AI算法工程师', growth: 78, days: 326, hours: 208, skills: 36, projects: 7 },
  match: { score: 72, change: 4 },
  roadmap: [
    { id: 'python', label: 'Python', state: 'done', level: 'Lv.5', x: 13, y: 74 },
    { id: 'ml', label: '机器学习', state: 'done', level: '已掌握', x: 25, y: 60 },
    { id: 'dl', label: '深度学习', state: 'done', level: '进行中', x: 42, y: 44 },
    { id: 'rag', label: 'RAG', state: 'active', level: '待学习', x: 59, y: 30 },
    { id: 'agent', label: 'Agent', state: 'locked', level: '待学习', x: 72, y: 17 },
    { id: 'goal', label: 'AI算法工程师', state: 'goal', level: '目标岗位', x: 86, y: 8 }
  ],
  jobMatches: [
    { rank: 1, name: 'AI算法工程师', company: '字节跳动 · 北京', salary: '25–40K', score: 72, reason: 'RAG 项目经验匹配' },
    { rank: 2, name: '机器学习工程师', company: '阿里巴巴 · 杭州', salary: '22–35K', score: 68, reason: '算法基础扎实' },
    { rank: 3, name: '算法研究员', company: '腾讯 · 深圳', salary: '30–45K', score: 65, reason: '研究潜力突出' }
  ],
  plan: [
    { id: 'transformer', label: 'Transformer 原理学习', done: true },
    { id: 'attention', label: 'Attention 机制实现', done: true },
    { id: 'milvus', label: '学习向量数据库 Milvus', done: true },
    { id: 'rag-demo', label: '完成 RAG 项目 Demo', done: false },
    { id: 'blog', label: '撰写技术博客总结', done: false }
  ],
  timeline: [
    { date: '今天', text: '完成 RAG 知识库项目，成长指数 +6' },
    { date: '05-08', text: '学习深度学习基础，成长指数 +5' },
    { date: '05-01', text: '完成机器学习项目实践，成长指数 +8' },
    { date: '04-25', text: '通过模拟面试训练，成长指数 +4' }
  ]
}

export const skillDetail = {
  RAG: {
    level: 'Lv.3', target: 'Lv.5', gaps: ['向量数据库', 'Embedding 优化', 'Agent 调用'], boost: '+8 能力值', suggestion: '完成一个 RAG 知识库问答项目'
  },
  默认: {
    level: 'Lv.4', target: 'Lv.5', gaps: ['项目实践', '性能优化'], boost: '+4 能力值', suggestion: '用一个可展示的项目验证你的能力'
  }
}
