<template>
  <div class="login-page" @pointermove="handlePointerMove" @pointerleave="resetTilt">
    <div class="bg-full-image"></div>
    <div class="bg-overlay-gradient"></div>
    <div class="aurora aurora-a"></div>
    <div class="aurora aurora-b"></div>
    <div class="particle-field">
      <i v-for="item in 54" :key="item" :style="particleStyle(item)"></i>
    </div>
    <span class="meteor meteor-a" aria-hidden="true"></span>
    <span class="meteor meteor-b" aria-hidden="true"></span>
    <span class="meteor meteor-c" aria-hidden="true"></span>

    <main class="login-stage">
      <div class="card-zone">
        <div class="orbit-shell" aria-hidden="true">
          <span class="orbit-ring ring-outer"></span>
          <span class="orbit-ring ring-middle"></span>
          <span class="orbit-ring ring-dashed"></span>
          <span class="orbit-ring ring-inner"></span>
          <span class="orbit-runner runner-a"><i></i></span>
          <span class="orbit-runner runner-b"><i></i></span>
          <span class="orbit-runner runner-c"><i></i></span>
          <span class="orbit-dot dot-a"></span>
          <span class="orbit-dot dot-b"></span>
          <span class="orbit-dot dot-c"></span>
          <span class="orbit-cross cross-a"></span>
          <span class="orbit-cross cross-b"></span>
        </div>

        <section ref="cardEl" class="auth-card" :class="{ 'auth-register': mode === 'register', 'auth-login': mode === 'login' }" :style="cardTiltStyle">
          <span class="card-halo" aria-hidden="true"></span>
          <span class="fx-grid" aria-hidden="true"></span>
          <span class="fx-nebula" aria-hidden="true"></span>
          <span class="fx-pointer" aria-hidden="true"></span>
          <span class="fx-corners" aria-hidden="true"><i></i><i></i><i></i><i></i></span>

          <header class="auth-head">
            <div class="brand-chip">
              <img src="/logo.png" alt="" />
              <span>数融智联</span>
            </div>
            <h1>{{ mode === 'login' ? '欢迎登录' : '创建账号' }}</h1>
            <p>{{ mode === 'login' ? '请使用您的账号登录系统' : '填写以下信息完成注册' }}</p>
          </header>

          <div class="mode-switch" :class="{ 'is-register': mode === 'register' }" role="tablist" aria-label="登录方式切换">
            <span class="switch-thumb" aria-hidden="true"></span>
            <button type="button" role="tab" :aria-selected="mode === 'login'" :class="{ active: mode === 'login' }" @click="mode = 'login'">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
                <polyline points="10 17 15 12 10 7" />
                <line x1="15" y1="12" x2="3" y2="12" />
              </svg>
              <span>登录</span>
            </button>
            <button type="button" role="tab" :aria-selected="mode === 'register'" :class="{ active: mode === 'register' }" @click="mode = 'register'">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="8.5" cy="7" r="4" />
                <line x1="20" y1="8" x2="20" y2="14" />
                <line x1="23" y1="11" x2="17" y2="11" />
              </svg>
              <span>注册</span>
            </button>
          </div>

          <transition name="panel-fade" mode="out-in">
            <div v-if="mode === 'login'" key="login" class="auth-form">
              <div class="input-wrap">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
                <input v-model="loginForm.username" type="text" placeholder="用户名" class="form-input" />
              </div>
              <div class="input-wrap">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                <input v-model="loginForm.password" :type="showPwd ? 'text' : 'password'" placeholder="密码" class="form-input" @keyup.enter="submitLogin" />
                <button type="button" class="eye-toggle" @click="showPwd = !showPwd">
                  <svg v-if="!showPwd" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                </button>
              </div>
              <div class="form-options">
                <label class="remember-me">
                  <input type="checkbox" v-model="rememberMe" />
                  <span class="check-box"></span>
                  <span>记住我</span>
                </label>
              </div>
              <button type="button" class="submit-button" :disabled="loading" @click="submitLogin">
                <span>{{ loading ? '登录中...' : '登　录' }}</span>
              </button>
              <div class="role-tip">支持学生 · 求职者 · HR 多角色登录</div>
            </div>

            <div v-else key="register" class="auth-form">
              <div class="input-wrap">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 21a8 8 0 0 0-16 0"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
                <input v-model="registerForm.displayName" type="text" placeholder="真实姓名" class="form-input" autocomplete="name" />
              </div>
              <div class="input-wrap">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
                <input v-model="registerForm.username" type="text" placeholder="用户名（6-20 位字母和数字）" class="form-input" autocomplete="username" />
              </div>
              <div class="input-wrap">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                  <polyline points="22,6 12,13 2,6"/>
                </svg>
                <input v-model="registerForm.email" type="email" placeholder="邮箱" class="form-input" autocomplete="email" />
              </div>
              <div class="input-wrap">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                <input v-model="registerForm.password" type="password" placeholder="设置密码（至少 8 位）" class="form-input" autocomplete="new-password" />
              </div>
              <div class="input-wrap">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                  <path d="M9 12l2 2 4-4"/>
                </svg>
                <input v-model="registerForm.confirmPassword" type="password" placeholder="确认密码" class="form-input" autocomplete="new-password" />
              </div>
              <div class="captcha-row">
                <div class="input-wrap captcha-input">
                  <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9.5 9a3 3 0 1 1 5.2 2c-1.2 1.1-2.7 1.5-2.7 3"/>
                    <path d="M12 18h.01"/>
                    <circle cx="12" cy="12" r="10"/>
                  </svg>
                  <input v-model="registerForm.captchaAnswer" inputmode="numeric" placeholder="验证码结果" class="form-input" @keyup.enter="submitRegister" />
                </div>
                <div class="captcha-question" :class="{ loading: captchaLoading }">
                  <span>{{ captchaQuestion || '加载中...' }}</span>
                  <button type="button" title="刷新验证码" aria-label="刷新验证码" :disabled="captchaLoading" @click="loadCaptcha">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M20 11a8.1 8.1 0 0 0-15.5-2M4 5v4h4"/>
                      <path d="M4 13a8.1 8.1 0 0 0 15.5 2M20 19v-4h-4"/>
                    </svg>
                  </button>
                </div>
              </div>
              <button type="button" class="submit-button" :disabled="loading" @click="submitRegister">
                <span>{{ loading ? '注册中...' : '注　册' }}</span>
              </button>
            </div>
          </transition>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const mode = ref('login')
const loading = ref(false)
const showPwd = ref(false)
const rememberMe = ref(false)
const cardTiltX = ref(0)
const cardTiltY = ref(0)
const cardEl = ref<HTMLElement | null>(null)
const pointerGlow = reactive({ x: 0, y: 0, o: 0 })
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const loginForm = reactive({ username: '', password: '' })
const registerForm = reactive({
  displayName: '',
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  captchaAnswer: ''
})
const captchaQuestion = ref('')
const captchaToken = ref('')
const captchaLoading = ref(false)

const cardTiltStyle = computed(() => ({
  transform: `perspective(1100px) rotateX(${cardTiltX.value}deg) rotateY(${cardTiltY.value}deg)`,
  '--mx': `${pointerGlow.x}px`,
  '--my': `${pointerGlow.y}px`,
  '--go': pointerGlow.o
}))

function particleStyle(i: number) {
  const size = Math.random() * 3 + 1
  const left = Math.random() * 100
  const top = Math.random() * 100
  const dur = Math.random() * 10 + 10
  const delay = Math.random() * -14
  const op = Math.random() * 0.5 + 0.3
  return {
    width: size + 'px',
    height: size + 'px',
    left: left + '%',
    top: top + '%',
    animationDuration: dur + 's',
    animationDelay: delay + 's',
    opacity: op
  }
}

function handlePointerMove(e: MouseEvent) {
  const x = (e.clientX / window.innerWidth - 0.5) * 5
  const y = (e.clientY / window.innerHeight - 0.5) * -5
  cardTiltX.value = y
  cardTiltY.value = x
  const el = cardEl.value
  if (el) {
    const rect = el.getBoundingClientRect()
    pointerGlow.x = e.clientX - rect.left
    pointerGlow.y = e.clientY - rect.top
    pointerGlow.o = 1
  }
}

function resetTilt() {
  cardTiltX.value = 0
  cardTiltY.value = 0
  pointerGlow.o = 0
}

onMounted(() => {
  document.documentElement.classList.add('login-active')
  document.body.classList.add('login-active')
})

onBeforeUnmount(() => {
  document.documentElement.classList.remove('login-active')
  document.body.classList.remove('login-active')
})

watch(mode, (value) => {
  if (value === 'register' && !captchaToken.value) void loadCaptcha()
})

async function loadCaptcha() {
  captchaLoading.value = true
  try {
    const data = await api.captcha()
    captchaQuestion.value = data.question || ''
    captchaToken.value = data.token || ''
    registerForm.captchaAnswer = ''
  } catch (error: any) {
    captchaQuestion.value = '加载失败'
    captchaToken.value = ''
    ElMessage.error(error?.response?.data?.detail || '验证码加载失败')
  } finally {
    captchaLoading.value = false
  }
}

async function submitLogin() {
  loading.value = true
  try {
    const user = await auth.login(loginForm.username.trim(), loginForm.password)
    ElMessage.success('登录成功')
    router.push((route.query.redirect as string) || (user.role === 'candidate' ? '/personal-center' : '/overview'))
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '登录失败，请确认后端服务已启动')
  } finally {
    loading.value = false
  }
}

async function submitRegister() {
  if (!registerForm.displayName.trim() || !registerForm.username.trim() || !registerForm.email.trim() || !registerForm.password || !registerForm.captchaAnswer.trim()) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (registerForm.password !== registerForm.confirmPassword) {
    ElMessage.warning('两次密码输入不一致')
    return
  }
  if (!captchaToken.value) {
    ElMessage.warning('请刷新验证码后重试')
    return
  }
  loading.value = true
  try {
    await auth.register({
      username: registerForm.username.trim(),
      password: registerForm.password,
      confirm_password: registerForm.confirmPassword,
      role: 'candidate',
      display_name: registerForm.displayName.trim(),
      email: registerForm.email.trim(),
      captcha_token: captchaToken.value,
      captcha_answer: registerForm.captchaAnswer.trim()
    })
    ElMessage.success('注册成功')
    await router.push((route.query.redirect as string) || '/personal-center')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '注册失败')
    await loadCaptcha()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
:global(html.login-active),
:global(body.login-active) {
  min-width: 0;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

:global(body.login-active::before),
:global(body.login-active::after) {
  display: none;
}

.login-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  perspective: 1100px;
}

.bg-full-image {
  position: absolute;
  inset: 0;
  background: url('/login-bg.png') center center / cover no-repeat;
}

.bg-overlay-gradient {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(120deg, rgba(2, 8, 24, 0.14) 0%, rgba(3, 12, 34, 0.18) 45%, rgba(2, 10, 28, 0.38) 100%),
    radial-gradient(circle at 28% 42%, transparent 0%, rgba(1, 6, 20, 0.26) 78%);
}

.aurora {
  position: absolute;
  width: 50vw;
  height: 50vw;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.28;
  mix-blend-mode: screen;
  pointer-events: none;
}

.aurora-a {
  left: -15vw;
  top: -18vw;
  background: radial-gradient(circle, rgba(0, 194, 255, 0.55), transparent 60%);
  animation: floatAurora 12s ease-in-out infinite;
}

.aurora-b {
  right: -18vw;
  bottom: -18vw;
  background: radial-gradient(circle, rgba(62, 115, 255, 0.45), transparent 60%);
  animation: floatAurora 14s ease-in-out infinite reverse;
}

.particle-field {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.particle-field i {
  position: absolute;
  border-radius: 50%;
  background: rgba(88, 207, 255, 0.8);
  filter: blur(0.5px);
  box-shadow: 0 0 12px rgba(78, 207, 255, 0.5);
  opacity: 0;
  animation: particleDrift 14s linear infinite;
}

.meteor {
  position: absolute;
  width: 170px;
  height: 2px;
  border-radius: 2px;
  background: linear-gradient(90deg, transparent, rgba(150, 235, 255, 0.95));
  filter: drop-shadow(0 0 6px rgba(0, 220, 255, 0.85));
  opacity: 0;
  pointer-events: none;
  animation: meteorFall 7.5s ease-in infinite;
}

.meteor-a {
  left: 46%;
  top: 5%;
  animation-delay: 0.8s;
}

.meteor-b {
  left: 68%;
  top: 13%;
  width: 120px;
  animation-duration: 9s;
  animation-delay: 3.6s;
}

.meteor-c {
  left: 16%;
  top: 26%;
  width: 90px;
  animation-duration: 10.5s;
  animation-delay: 6.2s;
}

.login-stage {
  position: relative;
  z-index: 1;
  display: grid;
  justify-items: end;
  align-items: center;
  min-height: 100vh;
  padding: 42px clamp(28px, 4.5vw, 96px) 42px 24px;
}

.card-zone {
  position: relative;
  display: grid;
  justify-items: center;
}

.orbit-shell {
  position: absolute;
  left: 50%;
  top: 50%;
  width: min(64vw, 780px);
  height: min(64vw, 780px);
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.orbit-shell::before {
  position: absolute;
  inset: 25%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 150, 255, 0.12), transparent 65%);
  content: "";
}

.orbit-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(130, 226, 255, 0.15);
}

.ring-outer {
  inset: 0;
  animation: rotateRing 30s linear infinite;
}

.ring-middle {
  inset: 15%;
  border: 0;
  background: repeating-conic-gradient(from 0deg, rgba(118, 226, 255, 0.2) 0deg 5deg, transparent 5deg 15deg);
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 1px), #000 calc(100% - 1px));
  mask: radial-gradient(farthest-side, transparent calc(100% - 1px), #000 calc(100% - 1px));
  opacity: 0.5;
  animation: rotateRing 28s linear infinite reverse;
}

.ring-dashed {
  inset: 28%;
  border: 0;
  background: repeating-conic-gradient(from 0deg, rgba(145, 238, 255, 0.35) 0deg 6deg, transparent 6deg 16deg);
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 2px), #000 calc(100% - 2px));
  mask: radial-gradient(farthest-side, transparent calc(100% - 2px), #000 calc(100% - 2px));
  opacity: 0.45;
  animation: rotateRing 15s linear infinite;
}

.ring-inner {
  inset: 35%;
  border: 0;
  background: repeating-conic-gradient(from 0deg, rgba(190, 247, 255, 0.3) 0deg 8deg, transparent 8deg 20deg);
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 1px), #000 calc(100% - 1px));
  mask: radial-gradient(farthest-side, transparent calc(100% - 1px), #000 calc(100% - 1px));
  opacity: 0.4;
  animation: rotateRing 10s linear infinite reverse;
}

.orbit-runner {
  position: absolute;
  left: 50%;
  top: 50%;
  border-radius: 50%;
  pointer-events: none;
}

.orbit-runner i {
  position: absolute;
  right: -3px;
  top: 50%;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #8ff3ff;
  box-shadow: 0 0 15px #8ff3ff, 0 0 30px rgba(0, 150, 255, 0.8);
  transform: translateY(-50%);
}

.runner-a {
  width: 100%;
  height: 100%;
  margin: -50% 0 0 -50%;
  animation: orbitParticle 10s linear infinite;
}

.runner-b {
  width: 70%;
  height: 70%;
  margin: -35% 0 0 -35%;
  animation: orbitParticle 14s linear infinite reverse;
}

.runner-b i {
  width: 6px;
  height: 6px;
  background: #43dcff;
}

.runner-c {
  width: 50%;
  height: 50%;
  margin: -25% 0 0 -25%;
  animation: orbitParticle 8s linear infinite;
}

.runner-c i {
  width: 5px;
  height: 5px;
  background: #ffffff;
}

.orbit-dot {
  position: absolute;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #8ff3ff;
  box-shadow: 0 0 18px #8ff3ff;
}

.dot-a {
  left: 50%;
  top: -3px;
  animation: dotFloat 4s ease-in-out infinite;
}

.dot-b {
  right: 15%;
  bottom: 25%;
  animation: dotFloat 5s ease-in-out infinite -1.5s;
}

.dot-c {
  left: 18%;
  bottom: 28%;
  animation: dotFloat 5.5s ease-in-out infinite -2.5s;
}

.orbit-cross {
  position: absolute;
  width: 120px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(132, 232, 255, 0.3), transparent);
}

.cross-a {
  left: 8%;
  top: 45%;
  transform: rotate(15deg);
}

.cross-b {
  right: 5%;
  top: 55%;
  transform: rotate(-20deg);
}

.auth-card {
  position: relative;
  width: clamp(430px, 31vw, 540px);
  border-radius: 26px;
  padding: 44px 46px 24px;
  background:
    linear-gradient(160deg, rgba(13, 34, 72, 0.72) 0%, rgba(5, 15, 38, 0.85) 46%, rgba(8, 20, 50, 0.8) 100%);
  box-shadow:
    0 0 0 1px rgba(120, 200, 255, 0.08),
    0 24px 70px rgba(0, 0, 0, 0.55),
    0 0 60px rgba(0, 170, 255, 0.16),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(26px) saturate(1.15);
  transform-style: preserve-3d;
  transition: transform 0.2s ease, box-shadow 0.3s ease;
  z-index: 2;
}

.auth-card::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(155deg, rgba(140, 230, 255, 0.5), rgba(45, 148, 255, 0.2) 45%, rgba(30, 102, 225, 0.34));
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  mask-composite: exclude;
  pointer-events: none;
}

/* 卡片内部：缓慢漂移的科技网格 */
.fx-grid {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  overflow: hidden;
  background-image:
    linear-gradient(rgba(90, 180, 255, 0.055) 1px, transparent 1px),
    linear-gradient(90deg, rgba(90, 180, 255, 0.055) 1px, transparent 1px);
  background-size: 34px 34px;
  -webkit-mask: radial-gradient(ellipse at 50% 0%, #000 0%, transparent 72%);
  mask: radial-gradient(ellipse at 50% 0%, #000 0%, transparent 72%);
  animation: gridShift 14s linear infinite;
  pointer-events: none;
}

/* 卡片内部的低对比度蓝色环境光。 */
.fx-nebula {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  overflow: hidden;
  pointer-events: none;
}

.fx-nebula::before,
.fx-nebula::after {
  content: "";
  position: absolute;
  border-radius: 50%;
  mix-blend-mode: screen;
}

.fx-nebula::before {
  width: 70%;
  height: 46%;
  left: -18%;
  top: -16%;
  background: radial-gradient(circle, rgba(0, 150, 255, 0.22), transparent 65%);
  filter: blur(28px);
  animation: nebulaA 12s ease-in-out infinite alternate;
}

.fx-nebula::after {
  width: 60%;
  height: 42%;
  right: -16%;
  bottom: -14%;
  background: radial-gradient(circle, rgba(40, 126, 255, 0.16), transparent 65%);
  filter: blur(30px);
  animation: nebulaB 15s ease-in-out infinite alternate;
}

/* 鼠标跟随光斑 */
.fx-pointer {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  overflow: hidden;
  background: radial-gradient(320px circle at var(--mx, 50%) var(--my, 50%), rgba(0, 214, 255, 0.12), transparent 62%);
  opacity: var(--go, 0);
  transition: opacity 0.35s ease;
  pointer-events: none;
  z-index: 1;
}

/* HUD 四角呼吸灯 */
.fx-corners {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  z-index: 4;
}

.fx-corners i {
  position: absolute;
  width: 24px;
  height: 24px;
  border: 0 solid rgba(0, 225, 255, 0.75);
  filter: drop-shadow(0 0 6px rgba(0, 220, 255, 0.55));
  animation: cornerPulse 3.4s ease-in-out infinite;
}

.fx-corners i:nth-child(1) {
  left: 9px;
  top: 9px;
  border-left-width: 2px;
  border-top-width: 2px;
  border-top-left-radius: 10px;
}

.fx-corners i:nth-child(2) {
  right: 9px;
  top: 9px;
  border-right-width: 2px;
  border-top-width: 2px;
  border-top-right-radius: 10px;
  animation-delay: 0.85s;
}

.fx-corners i:nth-child(3) {
  right: 9px;
  bottom: 9px;
  border-right-width: 2px;
  border-bottom-width: 2px;
  border-bottom-right-radius: 10px;
  animation-delay: 1.7s;
}

.fx-corners i:nth-child(4) {
  left: 9px;
  bottom: 9px;
  border-left-width: 2px;
  border-bottom-width: 2px;
  border-bottom-left-radius: 10px;
  animation-delay: 2.55s;
}

.card-halo {
  position: absolute;
  inset: -34px;
  border-radius: 60px;
  background: radial-gradient(ellipse at 50% 8%, rgba(0, 196, 255, 0.2), transparent 62%);
  filter: blur(26px);
  pointer-events: none;
}

.auth-card:hover {
  box-shadow:
    0 0 0 1px rgba(120, 200, 255, 0.12),
    0 28px 80px rgba(0, 0, 0, 0.58),
    0 0 84px rgba(0, 190, 255, 0.22),
    inset 0 1px 0 rgba(255, 255, 255, 0.16);
}

@keyframes gridShift {
  to { background-position: 34px 34px; }
}

@keyframes nebulaA {
  to { transform: translate(58%, 42%) scale(1.18); }
}

@keyframes nebulaB {
  to { transform: translate(-52%, -38%) scale(1.12); }
}

@keyframes cornerPulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 1; }
}

@keyframes meteorFall {
  0%, 76% { opacity: 0; transform: rotate(158deg) translateX(0); }
  81% { opacity: 1; }
  92%, 100% { opacity: 0; transform: rotate(158deg) translateX(34vw); }
}

.auth-head {
  position: relative;
  z-index: 2;
  text-align: center;
  margin-bottom: 22px;
}

.brand-chip {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 7px 18px 7px 12px;
  border-radius: 999px;
  border: 1px solid rgba(0, 190, 255, 0.22);
  background: linear-gradient(180deg, rgba(10, 28, 62, 0.6), rgba(5, 14, 34, 0.6));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08), 0 6px 18px rgba(0, 10, 30, 0.35);
  margin-bottom: 18px;
}

.brand-chip img {
  width: 26px;
  height: 26px;
  object-fit: contain;
  filter: drop-shadow(0 0 8px rgba(120, 220, 255, 0.6));
}

.brand-chip span {
  color: rgba(196, 234, 255, 0.95);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.3em;
  text-indent: 0.3em;
}

.auth-head h1 {
  margin: 0;
  background: linear-gradient(110deg, #ffffff 22%, #9fd8ff 38%, #e7b8ff 50%, #9fd8ff 62%, #ffffff 78%);
  background-size: 240% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 30px;
  font-weight: 800;
  letter-spacing: 0.1em;
  filter: drop-shadow(0 0 22px rgba(80, 200, 255, 0.35));
  animation: titleShine 5.5s ease-in-out infinite;
}

@keyframes titleShine {
  0%, 100% { background-position: 0% 0; }
  50% { background-position: 100% 0; }
}

.auth-head p {
  margin: 10px 0 0;
  color: rgba(150, 200, 235, 0.6);
  font-size: 13px;
  letter-spacing: 0.12em;
}

.mode-switch {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: 1fr 1fr;
  margin-bottom: 24px;
  padding: 5px;
  border: 1px solid transparent;
  border-radius: 999px;
  background:
    linear-gradient(180deg, rgba(7, 24, 54, 0.88), rgba(4, 14, 34, 0.92)) padding-box,
    linear-gradient(120deg, rgba(0, 209, 255, 0.5), rgba(46, 132, 255, 0.38) 55%, rgba(36, 98, 230, 0.48)) border-box;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    inset 0 -8px 16px rgba(0, 8, 24, 0.5),
    0 12px 32px rgba(0, 10, 30, 0.45);
}

.switch-thumb {
  position: absolute;
  top: 5px;
  bottom: 5px;
  left: 5px;
  width: calc(50% - 5px);
  border-radius: 999px;
  background: linear-gradient(120deg, #52ddff 0%, #0aa9b4 48%, #0aa9b4 100%);
  box-shadow:
    0 6px 18px rgba(47, 124, 255, 0.5),
    0 0 26px rgba(96, 140, 255, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  overflow: hidden;
  transition: transform 0.45s cubic-bezier(0.22, 1.2, 0.36, 1);
  pointer-events: none;
}

.switch-thumb::before {
  content: "";
  position: absolute;
  left: 12%;
  right: 12%;
  top: 3px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.75), transparent);
}

.mode-switch.is-register .switch-thumb {
  transform: translateX(100%);
}

.mode-switch button {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  border: 0;
  border-radius: 999px;
  padding: 10px 0;
  background: transparent;
  color: rgba(158, 204, 236, 0.62);
  font-weight: 700;
  font-size: 15px;
  letter-spacing: 0.18em;
  text-indent: 0.18em;
  cursor: pointer;
  transition: color 0.3s ease, text-shadow 0.3s ease;
  font-family: inherit;
  -webkit-tap-highlight-color: transparent;
}

.mode-switch button svg {
  width: 15px;
  height: 15px;
  flex: 0 0 auto;
  opacity: 0.65;
  transition: opacity 0.3s ease, filter 0.3s ease;
}

.mode-switch button:hover {
  color: rgba(214, 242, 255, 0.92);
}

.mode-switch button.active {
  color: #fff;
  text-shadow: 0 0 16px rgba(255, 255, 255, 0.5);
}

.mode-switch button.active svg {
  opacity: 1;
  filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.55));
}

.auth-form {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.auth-register {
  padding-top: 28px;
  padding-bottom: 22px;
}

.auth-register .auth-head {
  margin-bottom: 16px;
}

.auth-register .mode-switch {
  margin-bottom: 16px;
}

.auth-register .auth-form {
  gap: 10px;
}

.auth-register .input-wrap {
  height: 46px;
}

.captcha-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 154px;
  gap: 10px;
}

.captcha-question {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 0;
  height: 46px;
  padding: 0 8px 0 14px;
  border: 1px solid rgba(0, 190, 255, 0.24);
  border-radius: 13px;
  background: rgba(4, 16, 40, 0.72);
  color: #dff8ff;
  font-weight: 700;
  letter-spacing: 0;
}

.captcha-question.loading {
  opacity: 0.7;
}

.captcha-question button {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  flex: 0 0 32px;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: #65dcff;
  cursor: pointer;
}

.captcha-question button:hover {
  background: rgba(69, 199, 255, 0.12);
}

.captcha-question button:disabled {
  cursor: progress;
  opacity: 0.45;
}

.captcha-question svg {
  width: 17px;
  height: 17px;
}

.input-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 52px;
  border: 1px solid rgba(0, 190, 255, 0.2);
  border-radius: 13px;
  background:
    linear-gradient(180deg, rgba(9, 26, 56, 0.55), rgba(4, 13, 32, 0.62));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
  padding: 0 16px;
  transition: all 0.25s ease;
}

.input-wrap:hover {
  border-color: rgba(0, 200, 255, 0.38);
}

.input-wrap:focus-within {
  border-color: rgba(0, 224, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(0, 180, 255, 0.13), 0 0 26px rgba(0, 190, 255, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.06);
  background: linear-gradient(180deg, rgba(10, 30, 64, 0.66), rgba(5, 16, 40, 0.72));
}

.input-icon {
  color: rgba(100, 200, 255, 0.5);
  flex-shrink: 0;
}

.input-wrap:focus-within .input-icon {
  color: #00d4ff;
}

.form-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #fff;
  font-size: 15px;
  padding: 0;
  font-family: inherit;
}

.form-input::placeholder {
  color: rgba(150, 190, 220, 0.4);
}

.eye-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: rgba(120, 170, 210, 0.5);
  cursor: pointer;
  padding: 6px;
  transition: color 0.2s ease;
}

.eye-toggle:hover {
  color: #00d4ff;
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 0 4px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
  color: rgba(180, 210, 240, 0.7);
}

.remember-me input {
  display: none;
}

.check-box {
  width: 16px;
  height: 16px;
  border: 1.5px solid rgba(100, 180, 230, 0.4);
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  background: transparent;
}

.remember-me:hover .check-box {
  border-color: rgba(0, 210, 255, 0.6);
}

.remember-me input:checked + .check-box {
  background: linear-gradient(135deg, #0099ff, #00ddff);
  border-color: transparent;
  box-shadow: 0 0 12px rgba(0, 190, 255, 0.45);
}

.remember-me input:checked + .check-box::after {
  content: '';
  width: 4px;
  height: 7px;
  border: solid #fff;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
  margin-bottom: 1px;
}

.forgot-link {
  font-size: 13px;
  color: #00c8ff;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.2s ease;
}

.forgot-link:hover {
  opacity: 0.8;
}

.submit-button {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 52px;
  overflow: hidden;
  border: 0;
  border-radius: 999px;
  background: linear-gradient(90deg, #52ddff 0%, #066a72 52%, #0aa9b4 100%);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.4em;
  text-indent: 0.4em;
  cursor: pointer;
  font-family: inherit;
  box-shadow: 0 12px 32px rgba(35, 112, 240, 0.42), inset 0 1px 0 rgba(255, 255, 255, 0.35);
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}

.submit-button::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  box-shadow: inset 0 -8px 18px rgba(20, 20, 90, 0.28);
  pointer-events: none;
}

.submit-button:hover {
  transform: translateY(-2px);
  filter: brightness(1.08);
  box-shadow: 0 18px 42px rgba(45, 126, 245, 0.52), 0 0 28px rgba(28, 139, 255, 0.28);
}

.submit-button:active {
  transform: translateY(0);
}

.submit-button:disabled {
  cursor: progress;
  opacity: 0.75;
}

.alt-login {
  margin-top: 2px;
}

.alt-divider {
  position: relative;
  display: flex;
  align-items: center;
  margin: 8px 0 14px;
}

.alt-divider::before,
.alt-divider::after {
  content: "";
  flex: 1;
  height: 1px;
}

.alt-divider::before {
  background: linear-gradient(90deg, transparent, rgba(120, 200, 255, 0.28));
}

.alt-divider::after {
  background: linear-gradient(90deg, rgba(120, 200, 255, 0.28), transparent);
}

.alt-divider i {
  font-style: normal;
  font-size: 12px;
  color: rgba(140, 190, 225, 0.55);
  padding: 0 14px;
  letter-spacing: 0.14em;
  white-space: nowrap;
}

.alt-icons {
  display: flex;
  justify-content: center;
  gap: 22px;
}

.alt-icons button {
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 1px solid rgba(0, 190, 255, 0.28);
  background: rgba(6, 20, 48, 0.6);
  color: rgba(140, 210, 250, 0.85);
  cursor: pointer;
  transition: all 0.25s ease;
}

.alt-icons button:hover {
  color: #fff;
  border-color: rgba(0, 224, 255, 0.65);
  box-shadow: 0 0 18px rgba(0, 190, 255, 0.35), inset 0 0 12px rgba(0, 190, 255, 0.12);
  transform: translateY(-2px);
}

.role-tip {
  text-align: center;
  margin-top: 14px;
  font-size: 12px;
  color: rgba(120, 170, 210, 0.5);
  padding-top: 14px;
  border-top: 1px solid rgba(100, 180, 230, 0.1);
}

.panel-fade-enter-active,
.panel-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.panel-fade-enter-from,
.panel-fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@keyframes floatAurora {
  0%, 100% { transform: translate3d(0, 0, 0) scale(1); }
  50% { transform: translate3d(6vw, 4vh, 0) scale(1.1); }
}

@keyframes particleDrift {
  0%, 100% { opacity: 0.1; transform: translate3d(0, 0, 0) scale(0.7); }
  50% { opacity: 0.7; transform: translate3d(60px, -70px, 0) scale(1); }
}

@keyframes rotateRing {
  to { transform: rotate(360deg); }
}

@keyframes orbitParticle {
  to { transform: rotate(360deg); }
}

@keyframes dotFloat {
  0%, 100% { opacity: 0.6; transform: translateY(0); }
  50% { opacity: 1; transform: translateY(-10px); }
}

@media (max-width: 1600px) {
  .auth-card {
    width: clamp(430px, 36vw, 520px);
  }
}

@media (max-width: 1280px) {
  .login-stage {
    justify-items: center;
    padding: 36px 24px;
  }

  .auth-card {
    width: min(88vw, 480px);
  }

  .orbit-shell {
    width: 130vw;
    height: 130vw;
  }
}

@media (max-width: 600px) {
  .login-stage {
    padding: 28px 16px;
  }

  .auth-card {
    width: min(92vw, 440px);
    padding: 36px 26px 20px;
  }
  .auth-head h1 {
    font-size: 25px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .fx-grid,
  .fx-nebula::before,
  .fx-nebula::after,
  .fx-corners i,
  .meteor,
  .auth-head h1,
  .aurora {
    animation: none !important;
  }
}
</style>
