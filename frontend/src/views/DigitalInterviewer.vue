<template>
  <div class="page digital-page">
    <PageHeader title="数字人面试" desc="按你的回答自然追问，完整保留每一场面试">
      <div class="toolbar">
        <el-select v-model="jobName" :disabled="Boolean(currentSession)" placeholder="选择面试岗位" style="width: 220px">
          <el-option v-for="job in jobs" :key="job.id" :label="job.name" :value="job.name" />
        </el-select>
        <el-select v-model="interviewStyle" :disabled="Boolean(currentSession)" style="width: 140px">
          <el-option v-for="item in interviewStyles" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-button type="primary" plain @click="startNewInterview">新建面试</el-button>
      </div>
    </PageHeader>

    <div class="interview-workspace">
      <aside class="history-panel surface">
        <div class="section-title">
          <div>
            <h3>面试记录</h3>
            <span>{{ sessions.length }} 场</span>
          </div>
        </div>
        <div v-if="sessionsLoading" class="history-empty">正在加载…</div>
        <div v-else-if="!sessions.length" class="history-empty">完成第一场面试后，记录会保存在这里。</div>
        <div v-else class="history-list">
          <button
            v-for="session in sessions"
            :key="session.id"
            type="button"
            class="history-item"
            :class="{ active: currentSession?.id === session.id }"
            @click="loadInterviewSession(session.id)"
          >
            <strong>{{ session.job_name }}</strong>
            <span>
              {{ styleLabel(session.interview_style) }} · {{ session.round_count }} 轮
              <template v-if="session.status === 'completed' && session.final_score"> · {{ session.final_score }} 分</template>
            </span>
            <small>{{ formatTime(session.updated_at) }}</small>
          </button>
        </div>
      </aside>

      <main class="conversation-panel surface">
        <header class="conversation-header">
          <div>
            <div class="conversation-title">
              <h3>{{ currentSession?.job_name || '新面试' }}</h3>
              <span v-if="currentSession">第 {{ currentSession.current_round }} 轮</span>
            </div>
            <p>{{ currentSession ? styleLabel(currentSession.interview_style) : '选择岗位和方式后开始' }}</p>
          </div>
          <div v-if="currentSession" class="session-actions">
            <el-button v-if="currentSession.status !== 'completed'" :disabled="loading" @click="skipCurrentQuestion">换一题</el-button>
            <el-button v-if="currentSession.status !== 'completed'" :disabled="loading" @click="completeInterview">结束面试</el-button>
            <el-button v-else type="primary" @click="reportVisible = true">查看总评</el-button>
          </div>
        </header>

        <div ref="chatScrollRef" class="conversation-scroll">
          <div v-if="!currentSession" class="start-card">
            <span class="start-kicker">准备就绪</span>
            <h2>从一次自然的交流开始</h2>
            <p>面试官会根据你的回答继续追问，也会主动切换角度，不需要套固定模板。</p>
            <div
              class="resume-upload-card"
              :class="{ parsing: resumeParsing }"
              @click="triggerResumeUpload"
              @dragover.prevent
              @drop.prevent="handleResumeDrop"
            >
              <div class="resume-file-icon">简</div>
              <div class="resume-upload-copy">
                <strong>{{ resumeParsing ? '正在解析简历…' : '上传简历自动解析' }}</strong>
                <span>支持 PDF 和 Word（DOCX），也可以把文件拖到这里</span>
              </div>
              <el-button :loading="resumeParsing" @click.stop="triggerResumeUpload">选择文件</el-button>
              <input
                ref="resumeFileInputRef"
                class="hidden-file-input"
                type="file"
                accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                @change="handleResumeFileChange"
              />
            </div>
            <div v-if="parsedResumeFileName" class="parsed-resume-status">
              <span><i></i>{{ parsedResumeFileName }}</span>
              <small v-if="parsedResumeCharacterCount">已提取 {{ parsedResumeCharacterCount }} 个字符</small>
            </div>
            <div v-else-if="lastParsedResumeAvailable" class="recent-resume-row">
              <span>检测到最近解析过的简历</span>
              <el-button link type="primary" @click="useLastParsedResume">直接使用</el-button>
            </div>
            <label>解析后的简历摘要</label>
            <el-input
              v-model="resumeSummary"
              type="textarea"
              :rows="4"
              placeholder="上传简历后会自动生成，也可以在这里微调"
            />
            <el-button type="primary" size="large" :loading="loading" :disabled="resumeParsing" @click="beginInterview">开始面试</el-button>
          </div>

          <template v-else>
            <div v-for="turn in history" :key="turn.id || turn.round_number" class="turn-group">
              <div class="round-label">第 {{ turn.round_number }} 轮</div>
              <div class="chat-row interviewer-row">
                <div class="speaker-mark">面</div>
                <div class="chat-bubble interviewer-bubble">{{ turn.question }}</div>
              </div>
              <div v-if="turn.answer" class="chat-row candidate-row">
                <div class="chat-bubble candidate-bubble">{{ turn.answer }}</div>
                <div class="speaker-mark candidate-mark">我</div>
              </div>
              <div v-if="turn.feedback" class="turn-feedback">
                <span>本轮反馈</span>
                <p>{{ turn.feedback }}</p>
              </div>
            </div>
            <div v-if="loading" class="chat-row interviewer-row thinking-row">
              <div class="speaker-mark">面</div>
              <div class="chat-bubble interviewer-bubble"><i></i><i></i><i></i></div>
            </div>
          </template>
        </div>

        <div v-if="currentSession?.status === 'completed'" class="resume-session-bar">
          <span>这场面试已结束，历史记录已保存。</span>
          <div>
            <el-button @click="reportVisible = true">查看总评</el-button>
            <el-button type="primary" @click="resumeCompletedSession">继续这场面试</el-button>
          </div>
        </div>

        <div v-else-if="currentSession" class="composer">
          <el-input
            v-model="candidateAnswer"
            type="textarea"
            :rows="3"
            resize="none"
            placeholder="说出你的真实思路，不必背标准答案"
            @keydown.ctrl.enter.prevent="sendAnswer"
          />
          <div class="composer-footer">
            <div class="input-state">
              <span v-if="listening" class="voice-listening"><i></i>正在聆听…</span>
              <span v-else>Ctrl + Enter 发送</span>
            </div>
            <div class="composer-actions">
              <el-button :disabled="loading" @click="candidateAnswer = ''">清空</el-button>
              <el-button :type="listening ? 'danger' : 'default'" :disabled="loading" @click="toggleVoiceConversation">
                {{ listening ? '结束并发送' : '语音回答' }}
              </el-button>
              <el-button type="primary" :loading="loading" @click="sendAnswer">发送回答</el-button>
            </div>
          </div>
        </div>
      </main>

      <aside class="right-column">
        <section class="avatar-card surface">
          <div class="avatar-stage" :class="{ connected: digitalState === 'connected' }">
            <video ref="videoRef" class="source-video" autoplay muted playsinline></video>
            <canvas v-show="digitalState === 'connected'" ref="cutoutCanvasRef" class="cutout-canvas" aria-label="数字人形象"></canvas>

            <div v-if="digitalState === 'idle' || digitalState === 'error'" class="connection-empty">
              <strong>数字人未连接</strong>
              <el-button type="primary" :disabled="!virtualHumanConfigured" @click="connectDigitalHuman">连接数字人</el-button>
              <p v-if="digitalError">{{ digitalError }}</p>
            </div>
            <div v-else-if="digitalState === 'connecting'" class="connection-loading">
              <span></span><strong>正在连接</strong>
            </div>
            <template v-else>
              <div class="connection-badge"><i></i>已连接</div>
              <el-button class="stop-button" :loading="stopping" @click="stopDigitalHuman">停止连接</el-button>
            </template>
          </div>
        </section>

        <section class="score-card surface">
          <div class="section-title">
            <div>
              <h3>{{ currentSession?.status === 'completed' ? '最终评分' : '当前表现' }}</h3>
              <span>{{ currentSession?.round_count || 0 }} 轮已回答</span>
            </div>
          </div>
          <div v-if="currentSession?.status === 'completed' && currentSession.final_score" class="final-score-mini">
            <strong>{{ currentSession.final_score }}</strong>
            <div><b>分</b><span>{{ finalReport.level }}</span></div>
          </div>
          <div class="score-list">
            <div v-for="(score, name) in currentScores" :key="name">
              <div><span>{{ name }}</span><b>{{ score }}</b></div>
              <el-progress :percentage="Number(score)" :show-text="false" :stroke-width="8" />
            </div>
          </div>
        </section>
      </aside>
    </div>

    <el-dialog v-model="reportVisible" title="面试总评" width="680px" class="final-report-dialog">
      <div v-if="finalReport.overall_score" class="final-report">
        <div class="report-hero">
          <div class="report-score"><strong>{{ finalReport.overall_score }}</strong><span>分</span></div>
          <div>
            <b>{{ finalReport.level }}</b>
            <p>{{ finalReport.summary }}</p>
          </div>
        </div>
        <div class="report-dimensions">
          <div v-for="(score, name) in finalReport.dimension_scores" :key="name">
            <span>{{ name }}</span><strong>{{ score }}</strong>
            <el-progress :percentage="Number(score)" :show-text="false" :stroke-width="8" />
          </div>
        </div>
        <div class="report-columns">
          <section>
            <h4>表现亮点</h4>
            <p v-for="item in finalReport.strengths || []" :key="item">{{ item }}</p>
          </section>
          <section class="improvement-section">
            <h4>改进方向</h4>
            <p v-for="item in finalReport.improvements || []" :key="item">{{ item }}</p>
          </section>
        </div>
        <div class="report-trend"><b>表现趋势</b><span>{{ finalReport.trend }}</span></div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import Hls from 'hls.js'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'
import { loadPageState, savePageState } from '@/utils/pageState'

type DigitalState = 'idle' | 'connecting' | 'connected' | 'error'

const interviewStyles = [
  { value: 'adaptive', label: '综合面试' },
  { value: 'project', label: '项目深挖' },
  { value: 'scenario', label: '情景应变' },
  { value: 'conversational', label: '轻松交流' }
]
const jobs = ref<any[]>([])
const sessions = ref<any[]>([])
const currentSession = ref<any>()
const history = ref<any[]>([])
const jobName = ref('')
const interviewStyle = ref('adaptive')
const resumeSummary = ref('本科计算机相关专业，熟悉 Python、SQL、RAG，参与过知识库问答和数据分析项目。')
const candidateAnswer = ref('')

type InterviewDraftState = {
  jobName?: string
  interviewStyle?: string
  resumeSummary?: string
  candidateAnswer?: string
  sessionId?: number
}

function persistDraft() {
  savePageState<InterviewDraftState>('digital-interviewer-draft', {
    jobName: jobName.value,
    interviewStyle: interviewStyle.value,
    resumeSummary: resumeSummary.value,
    candidateAnswer: candidateAnswer.value,
    sessionId: currentSession.value?.id
  })
}
const loading = ref(false)
const sessionsLoading = ref(false)
const listening = ref(false)
const reportVisible = ref(false)
const resumeParsing = ref(false)
const parsedResumeFileName = ref('')
const parsedResumeCharacterCount = ref(0)
const lastParsedResumeAvailable = ref(false)
const digitalSession = ref<any>()
const digitalState = ref<DigitalState>('idle')
const digitalError = ref('')
const virtualHumanConfigured = ref(false)
const stopping = ref(false)
const videoRef = ref<HTMLVideoElement>()
const cutoutCanvasRef = ref<HTMLCanvasElement>()
const chatScrollRef = ref<HTMLElement>()
const resumeFileInputRef = ref<HTMLInputElement>()

let heartbeatTimer: number | undefined
let cutoutFrame: number | undefined
let hlsPlayer: Hls | undefined
let speechRecognition: any
let speechBaseText = ''
let speechFinalText = ''
let submitWhenRecognitionEnds = false
let lastRenderedAt = 0
let pageIsUnloading = false

const defaultScores = { 专业能力: 0, 项目表达: 0, 岗位匹配: 0, 逻辑沟通: 0 }
const finalReport = computed(() => currentSession.value?.final_report || {})
const currentScores = computed(() => {
  if (currentSession.value?.status === 'completed' && finalReport.value.dimension_scores) {
    return finalReport.value.dimension_scores
  }
  const sessionScores = currentSession.value?.score_preview
  if (sessionScores && Object.keys(sessionScores).length) return sessionScores
  for (let index = history.value.length - 1; index >= 0; index -= 1) {
    const scores = history.value[index]?.score_preview
    if (scores && Object.keys(scores).length) return scores
  }
  return defaultScores
})

function styleLabel(value: string) {
  return interviewStyles.find((item) => item.value === value)?.label || '综合面试'
}

function formatTime(value?: string) {
  if (!value) return ''
  const date = new Date(value)
  const today = new Date()
  const sameDay = date.toDateString() === today.toDateString()
  return new Intl.DateTimeFormat('zh-CN', sameDay
    ? { hour: '2-digit', minute: '2-digit' }
    : { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' }
  ).format(date)
}

function errorMessage(error: any) {
  const detail = String(error?.response?.data?.detail || error?.message || '')
  if (detail.includes('11203')) return '数字人暂时忙，请约一分钟后再试'
  return detail || '操作失败，请稍后重试'
}

function triggerResumeUpload() {
  if (resumeParsing.value) return
  const input = resumeFileInputRef.value
  if (!input) return
  input.value = ''
  input.click()
}

function handleResumeFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) void parseResumeForInterview(file)
}

function handleResumeDrop(event: DragEvent) {
  const file = event.dataTransfer?.files?.[0]
  if (file && !resumeParsing.value) void parseResumeForInterview(file)
}

async function parseResumeForInterview(file: File) {
  const extension = file.name.split('.').pop()?.toLowerCase()
  if (!extension || !['pdf', 'docx'].includes(extension)) {
    ElMessage.warning('请选择 PDF 或 DOCX 格式的简历')
    return
  }
  resumeParsing.value = true
  try {
    const response = await api.parseResumeFile(file)
    const parsed = response.result || {}
    resumeSummary.value = buildInterviewResumeSummary(parsed, response.extracted_text || '')
    parsedResumeFileName.value = response.file?.name || file.name
    parsedResumeCharacterCount.value = Number(response.file?.character_count || 0)
    localStorage.setItem('last_parsed_resume', JSON.stringify(parsed))
    lastParsedResumeAvailable.value = true
    ElMessage.success('简历已解析，可以直接开始面试')
  } catch (error) {
    ElMessage.error(errorMessage(error))
  } finally {
    resumeParsing.value = false
  }
}

function useLastParsedResume() {
  try {
    const parsed = JSON.parse(localStorage.getItem('last_parsed_resume') || '{}')
    if (!parsed || !Object.keys(parsed).length) return
    resumeSummary.value = buildInterviewResumeSummary(parsed, '')
    parsedResumeFileName.value = '最近解析的简历'
    parsedResumeCharacterCount.value = 0
    ElMessage.success('已使用最近解析的简历')
  } catch {
    localStorage.removeItem('last_parsed_resume')
    lastParsedResumeAvailable.value = false
  }
}

function buildInterviewResumeSummary(parsed: any, extractedText: string) {
  const lines: string[] = []
  const identity = [parsed.name, parsed.education, parsed.major, parsed.school].filter(Boolean).join('，')
  if (identity) lines.push(`基本信息：${identity}`)
  if (parsed.intention) lines.push(`求职方向：${parsed.intention}`)
  const skills = (parsed.skills || []).map((item: any) => item?.name || item).filter(Boolean).slice(0, 12)
  if (skills.length) lines.push(`核心技能：${skills.join('、')}`)
  const projects = (parsed.projects || []).filter(Boolean).slice(0, 4)
  if (projects.length) lines.push(`项目经历：${projects.join('；')}`)
  const internships = (parsed.internships || []).filter(Boolean).slice(0, 3)
  if (internships.length) lines.push(`实习经历：${internships.join('；')}`)
  const certificates = (parsed.certificates || []).filter(Boolean).slice(0, 6)
  if (certificates.length) lines.push(`证书：${certificates.join('、')}`)
  if (lines.length) return lines.join('\n')
  return extractedText.trim().slice(0, 1600)
}

async function refreshSessions() {
  sessionsLoading.value = true
  try {
    sessions.value = await api.interviewSessions()
  } finally {
    sessionsLoading.value = false
  }
}

async function loadInterviewSession(id: number) {
  if (currentSession.value?.id === id || loading.value) return
  loading.value = true
  try {
    const data = await api.interviewSession(id)
    currentSession.value = data.session
    history.value = data.history || []
    jobName.value = data.session.job_name
    interviewStyle.value = data.session.interview_style
    resumeSummary.value = data.session.resume_summary || ''
    candidateAnswer.value = ''
    await scrollToLatest()
  } catch (error) {
    ElMessage.error(errorMessage(error))
  } finally {
    loading.value = false
  }
}

function startNewInterview() {
  currentSession.value = undefined
  history.value = []
  candidateAnswer.value = ''
  void nextTick(() => chatScrollRef.value?.scrollTo({ top: 0 }))
}

async function beginInterview() {
  if (!jobName.value) {
    ElMessage.warning('请先选择面试岗位')
    return
  }
  await requestNextTurn('start')
}

async function sendAnswer() {
  if (!currentSession.value) return
  if (!candidateAnswer.value.trim()) {
    ElMessage.warning('请先输入或说出你的回答')
    return
  }
  if (listening.value) stopVoiceRecognition(false)
  await requestNextTurn('answer')
}

async function skipCurrentQuestion() {
  if (!currentSession.value || loading.value) return
  if (listening.value) stopVoiceRecognition(false)
  await requestNextTurn('skip')
}

async function requestNextTurn(action: 'start' | 'answer' | 'skip') {
  loading.value = true
  try {
    if (digitalSession.value) enableSound()
    const response = await api.digitalInterview({
      job_name: currentSession.value?.job_name || jobName.value,
      resume_summary: currentSession.value?.resume_summary || resumeSummary.value,
      candidate_answer: action === 'answer' ? candidateAnswer.value.trim() : '',
      interview_session_id: currentSession.value?.id,
      interview_style: currentSession.value?.interview_style || interviewStyle.value,
      action,
      digital_human_session_id: digitalSession.value?.session_id
    })
    currentSession.value = response.interview_session
    history.value = response.history || []
    candidateAnswer.value = ''
    await refreshSessions()
    await scrollToLatest()
    if (response.digital_human?.status === 'error') ElMessage.warning('问题已生成，数字人播报失败')
  } catch (error) {
    ElMessage.error(errorMessage(error))
  } finally {
    loading.value = false
  }
}

async function completeInterview() {
  if (!currentSession.value || loading.value) return
  try {
    const data = await api.completeInterviewSession(currentSession.value.id)
    currentSession.value = data.session
    history.value = data.history || history.value
    reportVisible.value = true
    await refreshSessions()
  } catch (error) {
    ElMessage.error(errorMessage(error))
  }
}

function resumeCompletedSession() {
  if (!currentSession.value) return
  reportVisible.value = false
  currentSession.value = { ...currentSession.value, status: 'active' }
}

async function scrollToLatest() {
  await nextTick()
  const container = chatScrollRef.value
  if (container) container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' })
}

function speechRecognitionType() {
  const browserWindow = window as any
  return browserWindow.SpeechRecognition || browserWindow.webkitSpeechRecognition
}

function toggleVoiceConversation() {
  if (listening.value) {
    stopVoiceRecognition(true)
    return
  }
  startVoiceRecognition()
}

function startVoiceRecognition() {
  const Recognition = speechRecognitionType()
  if (!Recognition) {
    ElMessage.warning('当前浏览器不支持语音输入，请使用最新版 Chrome 或 Edge')
    return
  }
  speechBaseText = candidateAnswer.value.trim()
  speechFinalText = ''
  submitWhenRecognitionEnds = false
  speechRecognition = new Recognition()
  speechRecognition.lang = 'zh-CN'
  speechRecognition.continuous = true
  speechRecognition.interimResults = true
  speechRecognition.maxAlternatives = 1
  speechRecognition.onstart = () => { listening.value = true }
  speechRecognition.onresult = (event: any) => {
    let interimText = ''
    for (let index = event.resultIndex; index < event.results.length; index += 1) {
      const transcript = String(event.results[index][0]?.transcript || '').trim()
      if (!transcript) continue
      if (event.results[index].isFinal) speechFinalText = joinTranscript(speechFinalText, transcript)
      else interimText = joinTranscript(interimText, transcript)
    }
    candidateAnswer.value = [speechBaseText, speechFinalText, interimText].filter(Boolean).join(' ')
  }
  speechRecognition.onerror = (event: any) => {
    submitWhenRecognitionEnds = false
    const messages: Record<string, string> = {
      'not-allowed': '请允许浏览器使用麦克风后再试',
      'service-not-allowed': '浏览器语音服务不可用',
      'audio-capture': '没有检测到可用的麦克风',
      'no-speech': '没有听到声音，请重新开始',
      network: '语音识别连接失败，请检查网络后重试'
    }
    if (event.error !== 'aborted') ElMessage.warning(messages[event.error] || '语音识别失败，请重试')
  }
  speechRecognition.onend = () => {
    const shouldSubmit = submitWhenRecognitionEnds
    submitWhenRecognitionEnds = false
    listening.value = false
    speechRecognition = undefined
    if (shouldSubmit && candidateAnswer.value.trim()) void sendAnswer()
    else if (shouldSubmit) ElMessage.warning('没有识别到回答，请重新说一次')
  }
  try {
    listening.value = true
    speechRecognition.start()
  } catch {
    listening.value = false
    speechRecognition = undefined
    ElMessage.warning('麦克风启动失败，请稍后重试')
  }
}

function stopVoiceRecognition(submitAnswer: boolean) {
  if (!speechRecognition) return
  submitWhenRecognitionEnds = submitAnswer
  speechRecognition.stop()
}

function joinTranscript(current: string, addition: string) {
  return [current.trim(), addition.trim()].filter(Boolean).join(' ')
}

async function connectDigitalHuman() {
  if (!virtualHumanConfigured.value || digitalState.value === 'connecting') return
  digitalState.value = 'connecting'
  digitalError.value = ''
  try {
    digitalSession.value = await api.startVirtualHuman()
    await nextTick()
    attachVideoStream()
    startHeartbeat()
  } catch (error) {
    digitalSession.value = undefined
    digitalState.value = 'error'
    digitalError.value = errorMessage(error)
  }
}

function attachVideoStream() {
  destroyVideoPlayer()
  const video = videoRef.value
  const playbackUrl = digitalSession.value?.playback_url
  if (!video || !playbackUrl) return
  video.muted = true
  const onReady = () => {
    void video.play().then(() => {
      digitalState.value = 'connected'
      startCutoutRendering()
    }).catch(() => {
      digitalState.value = 'error'
      digitalError.value = '数字人画面启动失败，请重新连接'
    })
  }
  if (Hls.isSupported()) {
    const token = localStorage.getItem('auth_token')
    hlsPlayer = new Hls({
      lowLatencyMode: true,
      liveSyncDurationCount: 2,
      liveMaxLatencyDurationCount: 5,
      xhrSetup(xhr) { if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`) }
    })
    hlsPlayer.loadSource(playbackUrl)
    hlsPlayer.attachMedia(video)
    hlsPlayer.on(Hls.Events.MANIFEST_PARSED, onReady)
    hlsPlayer.on(Hls.Events.ERROR, (_event, data) => {
      if (!data.fatal) return
      if (data.type === Hls.ErrorTypes.NETWORK_ERROR) hlsPlayer?.startLoad()
      else if (data.type === Hls.ErrorTypes.MEDIA_ERROR) hlsPlayer?.recoverMediaError()
      else {
        digitalState.value = 'error'
        digitalError.value = '数字人画面连接中断，请重新连接'
        destroyVideoPlayer()
      }
    })
  } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = playbackUrl
    video.addEventListener('loadedmetadata', onReady, { once: true })
  } else {
    digitalState.value = 'error'
    digitalError.value = '当前浏览器无法显示数字人'
  }
}

function startCutoutRendering() {
  stopCutoutRendering()
  const render = (timestamp: number) => {
    cutoutFrame = window.requestAnimationFrame(render)
    if (timestamp - lastRenderedAt < 50) return
    const video = videoRef.value
    const canvas = cutoutCanvasRef.value
    if (!video || !canvas || video.readyState < 2 || !video.videoWidth || !video.videoHeight) return
    lastRenderedAt = timestamp
    const height = 640
    const width = Math.round(height * video.videoWidth / video.videoHeight)
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width
      canvas.height = height
    }
    const context = canvas.getContext('2d', { willReadFrequently: true })
    if (!context) return
    context.drawImage(video, 0, 0, width, height)
    const frame = context.getImageData(0, 0, width, height)
    removeBackground(frame.data, width, height)
    context.putImageData(frame, 0, 0)
  }
  cutoutFrame = window.requestAnimationFrame(render)
}

function removeBackground(pixels: Uint8ClampedArray, width: number, height: number) {
  const edgeWidth = Math.max(4, Math.floor(width * 0.08))
  for (let y = 0; y < height; y += 1) {
    let red = 0; let green = 0; let blue = 0; let samples = 0
    for (let x = 0; x < edgeWidth; x += 2) {
      const left = (y * width + x) * 4
      const right = (y * width + width - 1 - x) * 4
      red += pixels[left] + pixels[right]
      green += pixels[left + 1] + pixels[right + 1]
      blue += pixels[left + 2] + pixels[right + 2]
      samples += 2
    }
    red /= samples; green /= samples; blue /= samples
    for (let x = 0; x < width; x += 1) {
      const index = (y * width + x) * 4
      const dr = pixels[index] - red; const dg = pixels[index + 1] - green; const db = pixels[index + 2] - blue
      const distance = Math.sqrt(dr * dr + dg * dg + db * db)
      if (distance <= 11) pixels[index + 3] = 0
      else if (distance < 34) pixels[index + 3] = Math.round(255 * (distance - 11) / 23)
    }
  }
}

function stopCutoutRendering() {
  if (cutoutFrame !== undefined) window.cancelAnimationFrame(cutoutFrame)
  cutoutFrame = undefined
  lastRenderedAt = 0
  const canvas = cutoutCanvasRef.value
  canvas?.getContext('2d')?.clearRect(0, 0, canvas.width, canvas.height)
}

function enableSound() {
  const video = videoRef.value
  if (!video) return
  video.muted = false
  video.volume = 1
  void video.play().catch(() => undefined)
}

function startHeartbeat() {
  stopHeartbeat()
  const seconds = Number(digitalSession.value?.heartbeat_interval_seconds || 30)
  heartbeatTimer = window.setInterval(async () => {
    if (!digitalSession.value?.session_id) return
    try { await api.pingVirtualHuman(digitalSession.value.session_id) }
    catch (error) {
      digitalState.value = 'error'
      digitalError.value = errorMessage(error)
      stopHeartbeat()
    }
  }, seconds * 1000)
}

function stopHeartbeat() {
  if (heartbeatTimer !== undefined) window.clearInterval(heartbeatTimer)
  heartbeatTimer = undefined
}

function destroyVideoPlayer() {
  stopCutoutRendering()
  hlsPlayer?.destroy()
  hlsPlayer = undefined
  const video = videoRef.value
  if (video) {
    video.pause()
    video.removeAttribute('src')
    video.load()
  }
}

async function stopDigitalHuman(showMessage = true) {
  const sessionId = digitalSession.value?.session_id
  if (!sessionId) return
  stopping.value = true
  stopHeartbeat()
  destroyVideoPlayer()
  try {
    await api.stopVirtualHuman(sessionId)
    if (showMessage) ElMessage.success('数字人已停止连接')
  } catch (error) {
    if (showMessage) ElMessage.error(errorMessage(error))
  } finally {
    digitalSession.value = undefined
    digitalState.value = 'idle'
    digitalError.value = ''
    stopping.value = false
  }
}

onMounted(async () => {
  window.addEventListener('beforeunload', markPageUnloading)
  lastParsedResumeAvailable.value = Boolean(localStorage.getItem('last_parsed_resume'))
  const cachedDraft = loadPageState<InterviewDraftState>('digital-interviewer-draft')
  try {
    const [jobRows, status] = await Promise.all([api.jobs(), api.virtualHumanStatus(), refreshSessions()])
    jobs.value = jobRows
    jobName.value = cachedDraft?.jobName || jobs.value[0]?.name || ''
    if (cachedDraft?.interviewStyle) interviewStyle.value = cachedDraft.interviewStyle
    if (typeof cachedDraft?.resumeSummary === 'string') resumeSummary.value = cachedDraft.resumeSummary
    virtualHumanConfigured.value = Boolean(status.configured)
    if (!status.configured) {
      digitalState.value = 'error'
      digitalError.value = '数字人服务未配置'
    }
    if (sessions.value.length) {
      const sessionToRestore = sessions.value.find((item) => item.id === cachedDraft?.sessionId) || sessions.value[0]
      await loadInterviewSession(sessionToRestore.id)
    }
    if (typeof cachedDraft?.candidateAnswer === 'string') candidateAnswer.value = cachedDraft.candidateAnswer
  } catch (error) {
    ElMessage.error(errorMessage(error))
  }
})

function markPageUnloading() { pageIsUnloading = true }

watch([jobName, interviewStyle, resumeSummary, candidateAnswer], persistDraft)

onBeforeUnmount(() => {
  submitWhenRecognitionEnds = false
  speechRecognition?.abort()
  speechRecognition = undefined
  listening.value = false
  stopHeartbeat()
  destroyVideoPlayer()
  const sessionId = digitalSession.value?.session_id
  window.removeEventListener('beforeunload', markPageUnloading)
  if (sessionId && !pageIsUnloading) void api.stopVirtualHuman(sessionId)
})
</script>

<style scoped>
.interview-workspace { display: grid; grid-template-columns: 230px minmax(440px, 1fr) 310px; gap: 16px; min-height: 720px; }
.surface { border: 1px solid rgba(190,213,242,.78); border-radius: 22px; background: rgba(255,255,255,.78); box-shadow: 0 16px 42px rgba(42,76,128,.07); }
.section-title { display: flex; align-items: center; justify-content: space-between; }
.section-title>div { display: flex; align-items: baseline; gap: 8px; }
.section-title h3 { margin: 0; color: #132f58; font-size: 17px; }
.section-title span { color: #94a3b8; font-size: 11px; }
.history-panel { display: flex; min-height: 0; flex-direction: column; padding: 18px 12px; }
.history-panel .section-title { padding: 0 7px 14px; }
.history-list { display: grid; gap: 8px; overflow: auto; }
.history-item { display: grid; gap: 5px; width: 100%; border: 1px solid transparent; border-radius: 14px; padding: 12px; background: transparent; color: inherit; cursor: pointer; text-align: left; transition: .18s ease; }
.history-item:hover { background: #f3f8ff; }
.history-item.active { border-color: rgba(37,99,235,.2); background: #edf5ff; box-shadow: inset 3px 0 #2563eb; }
.history-item strong { overflow: hidden; color: #1c3559; font-size: 13px; text-overflow: ellipsis; white-space: nowrap; }
.history-item span { color: #64748b; font-size: 11px; }
.history-item small { color: #a3afc0; font-size: 10px; }
.history-empty { padding: 30px 12px; color: #94a3b8; font-size: 12px; line-height: 1.7; text-align: center; }
.conversation-panel { display: grid; grid-template-rows: auto minmax(0,1fr) auto; min-width: 0; overflow: hidden; }
.conversation-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; border-bottom: 1px solid rgba(190,213,242,.55); padding: 17px 20px; }
.conversation-title { display: flex; align-items: center; gap: 10px; }
.conversation-title h3 { margin: 0; color: #132f58; font-size: 18px; }
.conversation-title span { border-radius: 999px; padding: 3px 8px; background: #edf5ff; color: #2563eb; font-size: 10px; font-weight: 800; }
.conversation-header p { margin: 5px 0 0; color: #8492a6; font-size: 11px; }
.session-actions { display: flex; gap: 8px; }
.conversation-scroll { min-height: 0; max-height: 590px; overflow-y: auto; padding: 24px; scroll-behavior: smooth; }
.start-card { display: grid; justify-items: start; max-width: 540px; margin: 54px auto; }
.start-kicker { color: #2563eb; font-size: 12px; font-weight: 900; }
.start-card h2 { margin: 10px 0 8px; color: #132f58; font-size: 26px; }
.start-card p { margin: 0 0 22px; color: #64748b; line-height: 1.8; }
.start-card label { margin-bottom: 8px; color: #405572; font-size: 12px; font-weight: 800; }
.start-card :deep(.el-textarea) { width: 100%; }
.start-card .el-button { margin-top: 16px; }
.resume-upload-card { display: flex; align-items: center; gap: 13px; width: 100%; margin-bottom: 10px; border: 1px dashed #9bbce8; border-radius: 16px; padding: 14px 15px; background: #f6faff; cursor: pointer; transition: .18s ease; }
.resume-upload-card:hover { border-color: #377be3; background: #f0f6ff; box-shadow: 0 9px 24px rgba(37,99,235,.08); }
.resume-upload-card.parsing { cursor: wait; opacity: .78; }
.resume-file-icon { display: grid; flex: 0 0 38px; place-items: center; width: 38px; height: 38px; border-radius: 12px; background: linear-gradient(135deg,#2563eb,#20a6d8); color: #fff; font-size: 13px; font-weight: 900; }
.resume-upload-copy { display: grid; flex: 1; gap: 4px; min-width: 0; }
.resume-upload-copy strong { color: #254467; font-size: 13px; }
.resume-upload-copy span { color: #8391a5; font-size: 10px; }
.resume-upload-card .el-button { margin-top: 0; }
.hidden-file-input { display: none; }
.parsed-resume-status,.recent-resume-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; width: 100%; margin: -1px 0 13px; border-radius: 10px; padding: 8px 10px; background: #f0faf6; }
.parsed-resume-status span { display: flex; align-items: center; gap: 7px; overflow: hidden; color: #24775d; font-size: 11px; font-weight: 800; text-overflow: ellipsis; white-space: nowrap; }
.parsed-resume-status i { flex: 0 0 6px; width: 6px; height: 6px; border-radius: 50%; background: #25ae80; }
.parsed-resume-status small { flex: 0 0 auto; color: #729487; font-size: 9px; }
.recent-resume-row { background: #f7f9fc; color: #718096; font-size: 10px; }
.recent-resume-row .el-button { margin-top: 0; }
.turn-group { margin-bottom: 28px; }
.round-label { margin: 0 0 12px 42px; color: #a0acbc; font-size: 10px; }
.chat-row { display: flex; align-items: flex-start; gap: 10px; }
.candidate-row { justify-content: flex-end; margin-top: 13px; }
.speaker-mark { display: grid; flex: 0 0 30px; place-items: center; width: 30px; height: 30px; border-radius: 10px; background: linear-gradient(135deg,#2563eb,#16a9d8); color: #fff; font-size: 11px; font-weight: 900; }
.candidate-mark { background: #dce8f7; color: #36557f; }
.chat-bubble { max-width: 78%; border-radius: 6px 18px 18px; padding: 12px 15px; color: #23354e; font-size: 14px; line-height: 1.75; }
.interviewer-bubble { border: 1px solid #dbe8f7; background: #f5f9fe; }
.candidate-bubble { border-radius: 18px 6px 18px 18px; background: #2563eb; color: #fff; }
.turn-feedback { margin: 10px 40px 0; border-left: 3px solid #8fc9b5; padding: 4px 0 4px 12px; }
.turn-feedback span { color: #389678; font-size: 10px; font-weight: 900; }
.turn-feedback p { margin: 4px 0 0; color: #617087; font-size: 12px; line-height: 1.7; }
.thinking-row i { display: inline-block; width: 5px; height: 5px; margin-right: 4px; border-radius: 50%; background: #8aa2c1; animation: bounce 1s infinite; }
.thinking-row i:nth-child(2) { animation-delay: .15s; }.thinking-row i:nth-child(3) { animation-delay: .3s; }
.composer { border-top: 1px solid rgba(190,213,242,.55); padding: 14px 18px 16px; background: rgba(249,252,255,.86); }
.composer-footer { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-top: 10px; }
.input-state { color: #9aa7b8; font-size: 10px; }
.composer-actions { display: flex; gap: 8px; }
.voice-listening { display: flex; align-items: center; gap: 6px; color: #dc2626; font-size: 11px; font-weight: 800; }
.voice-listening i { width: 7px; height: 7px; border-radius: 50%; background: #ef4444; animation: voicePulse 1.1s ease-in-out infinite; }
.resume-session-bar { display: flex; align-items: center; justify-content: space-between; gap: 16px; border-top: 1px solid rgba(190,213,242,.55); padding: 18px 20px; color: #64748b; font-size: 12px; }
.resume-session-bar>div { display: flex; gap: 8px; }
.right-column { display: grid; align-content: start; gap: 16px; }
.avatar-card { padding: 12px; }
.avatar-stage { position: relative; display: grid; place-items: center; height: 390px; overflow: hidden; border-radius: 16px; background: linear-gradient(180deg,#f9fcff,#eef6ff); }
.avatar-stage.connected { background: transparent; }
.source-video { position: absolute; width: 1px; height: 1px; opacity: 0; pointer-events: none; }
.cutout-canvas { position: absolute; bottom: 0; left: 50%; z-index: 1; width: auto; height: 96%; transform: translateX(-50%); pointer-events: none; }
.connection-empty,.connection-loading { position: relative; z-index: 2; display: grid; justify-items: center; gap: 16px; color: #52647d; }
.connection-empty strong,.connection-loading strong { color: #183258; font-size: 16px; }
.connection-empty p { max-width: 240px; margin: -5px 10px 0; color: #b42318; font-size: 11px; line-height: 1.5; text-align: center; }
.connection-loading span { width: 25px; height: 25px; border: 3px solid rgba(37,99,235,.18); border-top-color: #2563eb; border-radius: 50%; animation: spin .8s linear infinite; }
.connection-badge { position: absolute; top: 12px; left: 12px; z-index: 3; display: flex; align-items: center; gap: 6px; border-radius: 999px; padding: 6px 9px; background: rgba(255,255,255,.88); color: #047857; font-size: 11px; font-weight: 800; box-shadow: 0 7px 20px rgba(15,23,42,.08); }
.connection-badge i { width: 6px; height: 6px; border-radius: 50%; background: #10b981; }
.stop-button { position: absolute; top: 10px; right: 10px; z-index: 3; }
.score-card { padding: 18px; }
.final-score-mini { display: flex; align-items: center; gap: 10px; margin-top: 18px; border-radius: 16px; padding: 14px 16px; background: linear-gradient(135deg,#edf5ff,#f2fbf7); }
.final-score-mini>strong { color: #175fd3; font-size: 40px; line-height: 1; }
.final-score-mini>div { display: grid; gap: 3px; }
.final-score-mini b { color: #175fd3; font-size: 11px; }
.final-score-mini span { color: #3b8068; font-size: 12px; font-weight: 900; }
.score-list { display: grid; gap: 14px; margin-top: 18px; }
.score-list>div>div { display: flex; align-items: center; justify-content: space-between; margin-bottom: 7px; }
.score-list span { color: #53657e; font-size: 12px; font-weight: 800; }
.score-list b { color: #2563eb; font-size: 12px; }
.final-report { display: grid; gap: 22px; }
.report-hero { display: flex; align-items: center; gap: 18px; border-radius: 20px; padding: 20px; background: linear-gradient(135deg,#edf5ff,#f0faf6); }
.report-score { display: flex; flex: 0 0 96px; align-items: baseline; justify-content: center; }
.report-score strong { color: #175fd3; font-size: 46px; line-height: 1; }
.report-score span { margin-left: 3px; color: #4776b7; font-size: 12px; font-weight: 800; }
.report-hero>div:last-child>b { color: #187556; font-size: 18px; }
.report-hero p { margin: 7px 0 0; color: #637289; font-size: 12px; line-height: 1.7; }
.report-dimensions { display: grid; grid-template-columns: repeat(2,1fr); gap: 16px 22px; }
.report-dimensions>div { display: grid; grid-template-columns: 1fr auto; gap: 7px; }
.report-dimensions span { color: #52647d; font-size: 12px; font-weight: 800; }
.report-dimensions strong { color: #2563eb; font-size: 12px; }
.report-dimensions :deep(.el-progress) { grid-column: 1 / -1; }
.report-columns { display: grid; grid-template-columns: repeat(2,1fr); gap: 14px; }
.report-columns section { border-radius: 16px; padding: 15px 16px; background: #f1faf6; }
.report-columns .improvement-section { background: #fff8ed; }
.report-columns h4 { margin: 0 0 9px; color: #20795e; font-size: 13px; }
.report-columns .improvement-section h4 { color: #a96513; }
.report-columns p { position: relative; margin: 7px 0; padding-left: 13px; color: #5b687c; font-size: 11px; line-height: 1.65; }
.report-columns p::before { position: absolute; top: 8px; left: 0; width: 5px; height: 5px; border-radius: 50%; background: #5ab393; content: ''; }
.improvement-section p::before { background: #e2a54f; }
.report-trend { display: grid; gap: 5px; border-top: 1px solid #e7edf5; padding-top: 15px; }
.report-trend b { color: #304968; font-size: 12px; }
.report-trend span { color: #6d7c90; font-size: 11px; line-height: 1.6; }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes bounce { 50% { transform: translateY(-3px); opacity: .45; } }
@keyframes voicePulse { 50% { opacity: .25; transform: scale(.75); } }
@media (max-width: 1250px) { .interview-workspace { grid-template-columns: 210px minmax(420px,1fr) 270px; } }
@media (max-width: 1050px) { .interview-workspace { grid-template-columns: 210px minmax(0,1fr); }.right-column { grid-column: 1 / -1; grid-template-columns: 1fr 1fr; }.avatar-stage { height: 340px; } }
@media (max-width: 760px) { .toolbar { align-items: stretch; flex-direction: column; }.toolbar :deep(.el-select) { width: 100% !important; }.interview-workspace { grid-template-columns: 1fr; }.history-panel { max-height: 220px; }.right-column { grid-template-columns: 1fr; }.conversation-scroll { max-height: 520px; padding: 18px 14px; }.conversation-header,.composer-footer,.resume-session-bar { align-items: stretch; flex-direction: column; }.session-actions,.composer-actions { display: grid; grid-template-columns: repeat(2,1fr); }.composer-actions .el-button { margin-left: 0; }.chat-bubble { max-width: 84%; }.resume-upload-card { align-items: flex-start; flex-wrap: wrap; }.resume-upload-copy { min-width: 180px; }.resume-upload-card .el-button { width: 100%; }.report-dimensions,.report-columns { grid-template-columns: 1fr; }:global(.final-report-dialog) { width: calc(100% - 24px) !important; }.report-hero { align-items: flex-start; flex-direction: column; }.report-score { justify-content: flex-start; } }
</style>
