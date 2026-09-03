# DeepSeek AI 接入说明

系统通过 `backend/app/services/ai_provider.py` 统一调用 DeepSeek Chat Completions API，并使用 JSON Output 返回结构化结果。

## 配置

复制 `backend/.env.example` 为 `backend/.env`，然后填写配置：

```bash
AI_PROVIDER=deepseek
DEEPSEEK_API_BASE_URL=https://api.deepseek.com
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-v4-flash
AI_TIMEOUT_SECONDS=90
AI_MAX_RETRIES=2
XUNFEI_VIRTUAL_HUMAN_SERVICE_ID=your-xunfei-service-id
XUNFEI_VIRTUAL_HUMAN_APP_ID=your-xunfei-app-id
XUNFEI_VIRTUAL_HUMAN_API_KEY=your-xunfei-api-key
XUNFEI_VIRTUAL_HUMAN_API_SECRET=your-xunfei-api-secret
XUNFEI_VIRTUAL_HUMAN_AVATAR_ID=118801001
XUNFEI_VIRTUAL_HUMAN_VOICE=x3_qianxue
```

`backend/.env` 已被 `.gitignore` 排除，不应提交到版本库。当前默认使用 `deepseek-v4-flash`；如需更强的复杂推理能力，可改为 `deepseek-v4-pro`。

## 已接入任务

- `jd_parse`：JD 结构化解析、置信度和原文证据
- `resume_parse`：教育、项目、技能、证书、竞赛和岗位意向抽取
- `match_analysis`：基于 evidence-v2 确定性评分和逐维证据生成综合结论、风险、简历改写与面试建议；AI 不允许修改数值评分
- `learning_path`：生成阶段、内容、项目、周期和前置技能
- `emerging_job_analysis`：批量分析候选新岗位定义、职责、技能和场景
- `digital_interview`：生成面试问题、追问依据、反馈和维度评分

## API

- `GET /api/ai/status`：返回 Provider、模型、配置状态和支持任务，不返回密钥
- `POST /api/ai/analyze`：统一 AI 分析入口
- `POST /api/jd/parse`：JD 解析
- `POST /api/resume/parse`：简历解析
- `POST /api/resume/parse-file`：PDF、DOCX、TXT、Markdown 简历上传、文本提取与 AI 解析
- `POST /api/match-analysis`：生成证据化评分与 AI 建议，并持久化报告
- `GET /api/match-analysis/history`：当前用户的匹配历史
- `GET /api/match-analysis/{report_id}`：读取指定匹配报告
- `GET /api/learning-path/{report_id}`：基于指定匹配报告生成 AI 学习路径
- `GET /api/emerging-jobs`：AI 新岗位分析
- `POST /api/digital-interviewer/interview`：AI 面试对话

统一分析请求示例：

```json
{
  "task_type": "jd_parse",
  "payload": {
    "text": "这里放 JD 文本"
  }
}
```

## 可靠性与边界

- 请求启用 JSON Output，并在提示词中给出每类任务的准确字段示例。
- Provider 会对空响应、临时网络错误、429 和 5xx 进行有限重试。
- 模型结果会做字段归一化，避免缺失字段导致前端异常。
- JD 证据和置信度继续通过幻觉防控服务检查，低置信度结果进入人工审核。
- 测试环境固定使用 `AI_PROVIDER=mock`，不会调用或消耗 DeepSeek 配额。
- DeepSeek 在此处只负责文本智能能力；数字人的媒体能力由独立的讯飞接口承担，不属于 DeepSeek Chat API 的能力范围。
- 数字人视频流、TTS 和形象驱动已通过 `services/xunfei_virtual_human.py` 接入讯飞 AI 虚拟人服务端 API，包括 HMAC 鉴权、启动、文本驱动、心跳和停止。APIKey/APISecret 只保存在后端 `.env`。
- 讯飞服务端返回 RTMP 流，后端通过 `imageio-ffmpeg` 实时转换为 HLS，前端使用 `hls.js` 在 `<video>` 内直接显示真实数字人画面。会话停止时会同步结束转码进程并清理临时分片。
- 进入数字人面试页后会自动建立视频会话并静音播放；用户点击“开启声音”或“开始 / 生成下一题”后恢复声音。若讯飞并发窗口尚未释放，画面区会显示明确错误和“启动真实数字人”重试按钮。
- 讯飞 AI 虚拟人 API 不包含候选人语音识别，ASR 状态会明确显示“需单独接入”，不会再显示虚假的“已就绪”。
- PDF 使用逐页文本提取；Word DOCX 同时读取正文、表格、页眉和页脚。扫描版 PDF 若无文本层会明确提示先做 OCR，旧版 `.doc` 需另存为 `.docx`。
