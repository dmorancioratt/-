<template>
  <div class="login-page" @pointermove="handlePointerMove" @pointerleave="resetTilt">
    <div class="bg-full-image"></div>
    <div class="bg-overlay-gradient"></div>
    <div class="aurora aurora-a"></div>
    <div class="aurora aurora-b"></div>
    <div class="scan-line"></div>
    <div class="matrix-grid"></div>
    <div class="particle-field">
      <i v-for="item in 54" :key="item" :style="particleStyle(item)"></i>
    </div>
    <div class="energy-flow" aria-hidden="true">
      <svg class="energy-flow__svg" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice">
        <defs>
          <linearGradient id="flowLine" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stop-color="#008dff" stop-opacity="0.05" />
            <stop offset="0.38" stop-color="#20c8ff" stop-opacity="0.96" />
            <stop offset="0.74" stop-color="#69f4ff" stop-opacity="0.82" />
            <stop offset="1" stop-color="#008dff" stop-opacity="0.08" />
          </linearGradient>
          <linearGradient id="flowLineSoft" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stop-color="#1d77ff" stop-opacity="0" />
            <stop offset="0.5" stop-color="#1fbaff" stop-opacity="0.58" />
            <stop offset="1" stop-color="#7befff" stop-opacity="0" />
          </linearGradient>
          <filter id="flowGlow" x="-30%" y="-80%" width="160%" height="260%">
            <feGaussianBlur stdDeviation="7" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <g class="flow-ribbons" filter="url(#flowGlow)">
          <path class="flow-ribbon flow-ribbon--wide" d="M-90 790 C350 650 760 850 1110 700 C1330 606 1450 476 1710 548" />
          <path class="flow-ribbon flow-ribbon--wide flow-ribbon--second" d="M-110 850 C370 724 790 918 1160 742 C1370 642 1470 548 1710 606" />
          <path class="flow-ribbon flow-ribbon--thin" d="M-100 818 C330 690 760 862 1135 716 C1370 624 1490 534 1700 584" />
          <path class="flow-ribbon flow-ribbon--thin flow-ribbon--third" d="M-40 872 C420 760 800 930 1195 756 C1408 662 1508 582 1690 638" />
          <path class="flow-ribbon flow-ribbon--fine" d="M-20 746 C370 626 744 810 1094 674 C1328 583 1458 492 1680 528" />
          <path class="flow-ribbon flow-ribbon--fine flow-ribbon--fourth" d="M90 888 C480 792 810 930 1216 786 C1420 712 1530 638 1690 674" />
        </g>

        <g class="flow-network">
          <path d="M1138 304 L1265 176 L1410 242 L1516 128 L1608 208" />
          <path d="M1265 176 L1322 388 L1410 242 L1500 382 L1608 208" />
          <path d="M1322 388 L1454 458 L1500 382 L1622 414" />
          <path d="M1410 242 L1454 458" />
          <path d="M1516 128 L1500 382" />
          <circle cx="1265" cy="176" r="6" />
          <circle cx="1322" cy="388" r="4" />
          <circle cx="1410" cy="242" r="8" />
          <circle cx="1454" cy="458" r="5" />
          <circle cx="1500" cy="382" r="6" />
          <circle cx="1516" cy="128" r="5" />
          <circle cx="1608" cy="208" r="4" />
        </g>
      </svg>
      <span class="flow-haze flow-haze--right"></span>
      <span class="flow-haze flow-haze--bottom"></span>
    </div>

    <main class="login-stage">
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

      <section class="auth-card" :class="{ 'auth-register': mode === 'register', 'auth-login': mode === 'login' }" :style="cardTiltStyle">
        <div class="tech-decoration" aria-hidden="true">
          <span class="corner corner-top-left"></span>
          <span class="corner corner-top-right"></span>
          <span class="corner corner-bottom-left"></span>
          <span class="corner corner-bottom-right"></span>
          <span class="card-scan"></span>
        </div>
        <div class="auth-head">
          <span class="terminal-dot"></span>
          <div>
            <p>{{ mode === 'login' ? 'ACCOUNT ACCESS' : 'CREATE IDENTITY' }}</p>
            <h1>数融智联岗位能力图谱</h1>
          </div>
        </div>

        <div class="mode-switch">
          <button :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</button>
          <button :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</button>
        </div>

        <transition name="panel-fade" mode="out-in">
          <div v-if="mode === 'login'" key="login" class="auth-form">
            <div class="form-item">
              <label class="form-label">用户名</label>
              <div class="input-wrap">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
                <input v-model="loginForm.username" type="text" placeholder="请输入用户名" class="form-input" />
              </div>
            </div>
            <div class="form-item">
              <label class="form-label">密码</label>
              <div class="input-wrap">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                <input v-model="loginForm.password" :type="showPwd ? 'text' : 'password'" placeholder="请输入密码" class="form-input" @keyup.enter="submitLogin" />
                <button type="button" class="eye-toggle" @click="showPwd = !showPwd">
                  <svg v-if="!showPwd" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </button>
              </div>
            </div>
            <div class="form-options">
              <label class="remember-me">
                <input type="checkbox" v-model="rememberMe" />
                <span class="check-box"></span>
                <span>记住我</span>
              </label>
              <a href="#" class="forgot-link">忘记密码？</a>
            </div>
            <button type="button" class="neon-button" :disabled="loading" @click="submitLogin">
              <span>{{ loading ? '登录中...' : '进入系统' }}</span>
            </button>
            <div class="role-tip">
              支持学生 · 求职者 · HR 多角色登录
            </div>
          </div>

          <div v-else key="register" class="auth-form">
            <div class="form-item">
              <label class="form-label">用户名</label>
              <div class="input-wrap">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
                <input v-model="registerForm.username" type="text" placeholder="请输入用户名" class="form-input" />
              </div>
            </div>
            <div class="form-item">
              <label class="form-label">邮箱</label>
              <div class="input-wrap">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                  <polyline points="22,6 12,13 2,6"/>
                </svg>
                <input v-model="registerForm.email" type="email" placeholder="请输入邮箱" class="form-input" />
              </div>
            </div>
            <div class="form-item">
              <label class="form-label">密码</label>
              <div class="input-wrap">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                <input v-model="registerForm.password" type="password" placeholder="请设置密码" class="form-input" />
              </div>
            </div>
            <div class="form-item">
              <label class="form-label">确认密码</label>
              <div class="input-wrap">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                <input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码" class="form-input" @keyup.enter="submitRegister" />
              </div>
            </div>
            <button type="button" class="neon-button" :disabled="loading" @click="submitRegister">
              <span>{{ loading ? '注册中...' : '立即注册' }}</span>
            </button>
          </div>
        </transition>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const mode = ref('login')
const loading = ref(false)
const showPwd = ref(false)
const rememberMe = ref(false)
const cardTiltX = ref(0)
const cardTiltY = ref(0)
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const loginForm = reactive({ username: 'hr_admin', password: 'Demo@123' })
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const cardTiltStyle = computed(() => ({
  transform: `perspective(1100px) rotateX(${cardTiltX.value}deg) rotateY(${cardTiltY.value}deg)`
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
  const x = (e.clientX / window.innerWidth - 0.5) * 4
  const y = (e.clientY / window.innerHeight - 0.5) * -4
  cardTiltX.value = y
  cardTiltY.value = x
}

function resetTilt() {
  cardTiltX.value = 0
  cardTiltY.value = 0
}

onMounted(() => {
  document.documentElement.classList.add('login-active')
  document.body.classList.add('login-active')
})

onBeforeUnmount(() => {
  document.documentElement.classList.remove('login-active')
  document.body.classList.remove('login-active')
})

async function submitLogin() {
  loading.value = true
  try {
    const user = await auth.login(loginForm.username, loginForm.password)
    ElMessage.success('登录成功')
    router.push((route.query.redirect as string) || (user.role === 'candidate' ? '/personal-center' : '/overview'))
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '登录失败，请确认后端服务已启动')
  } finally {
    loading.value = false
  }
}

async function submitRegister() {
  if (!registerForm.username || !registerForm.email || !registerForm.password) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (registerForm.password !== registerForm.confirmPassword) {
    ElMessage.warning('两次密码输入不一致')
    return
  }
  loading.value = true
  try {
    ElMessage.success('注册成功')
    mode.value = 'login'
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '注册失败')
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
  background: url('/ChatGPT%20Image%202026%E5%B9%B48%E6%9C%8824%E6%97%A5%2010_25_59.png') center center / cover no-repeat;
}

.bg-overlay-gradient {
  position: absolute;
  inset: 0;
  background: 
    linear-gradient(135deg, rgba(3, 10, 28, 0.55) 0%, rgba(4, 15, 40, 0.6) 50%, rgba(3, 12, 30, 0.7) 100%),
    radial-gradient(circle at 50% 50%, rgba(0, 15, 35, 0.4) 0%, transparent 50%);
}

.aurora {
  position: absolute;
  width: 50vw;
  height: 50vw;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.3;
  mix-blend-mode: screen;
  pointer-events: none;
}

.aurora-a {
  left: -15vw;
  top: -18vw;
  background: radial-gradient(circle, rgba(0, 194, 255, 0.6), transparent 60%);
  animation: floatAurora 12s ease-in-out infinite;
}

.aurora-b {
  right: -18vw;
  bottom: -18vw;
  background: radial-gradient(circle, rgba(62, 115, 255, 0.5), transparent 60%);
  animation: floatAurora 14s ease-in-out infinite reverse;
}

.scan-line {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.02) 0 1px, transparent 1px 5px);
  opacity: 0.15;
}

.matrix-grid {
  position: absolute;
  left: 15%;
  bottom: -30%;
  width: 70vw;
  height: 50vh;
  border-radius: 50%;
  background: linear-gradient(rgba(46, 189, 255, 0.12) 1px, transparent 1px), linear-gradient(90deg, rgba(46, 189, 255, 0.12) 1px, transparent 1px);
  background-size: 40px 40px;
  transform: perspective(800px) rotateX(65deg);
  transform-origin: center bottom;
  opacity: 0.12;
  animation: gridMove 10s linear infinite;
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

.energy-flow {
  position: absolute;
  z-index: 0;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  opacity: 0.7;
  mask-image: linear-gradient(180deg, transparent 0%, #000 15%, #000 100%);
}

.energy-flow__svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: visible;
}

.flow-ribbons path {
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dasharray: 720 360;
  animation: ribbonFlow 13s linear infinite;
}

.flow-ribbon--wide {
  stroke: url(#flowLine);
  stroke-width: 16;
  opacity: 0.15;
}

.flow-ribbon--second {
  stroke-width: 12;
  opacity: 0.1;
  animation-duration: 17s;
  animation-delay: -5s;
}

.flow-ribbon--thin {
  stroke: url(#flowLine);
  stroke-width: 4;
  opacity: 0.6;
  animation-duration: 10s;
  animation-delay: -3s;
}

.flow-ribbon--third {
  opacity: 0.35;
  animation-duration: 15s;
  animation-delay: -9s;
}

.flow-ribbon--fine {
  stroke: url(#flowLineSoft);
  stroke-width: 2;
  opacity: 0.55;
  animation-duration: 8s;
  animation-delay: -1s;
}

.flow-ribbon--fourth {
  opacity: 0.3;
  animation-duration: 19s;
  animation-delay: -12s;
}

.flow-network {
  opacity: 0.6;
  transform-origin: 1450px 300px;
  animation: networkPulse 7.5s ease-in-out infinite;
}

.flow-network path {
  fill: none;
  stroke: rgba(48, 197, 255, 0.35);
  stroke-width: 1.4;
  stroke-dasharray: 5 14;
  animation: networkTrace 11s linear infinite;
}

.flow-network circle {
  fill: #b7f7ff;
  filter: drop-shadow(0 0 7px rgba(55, 211, 255, 0.8));
  animation: nodePulse 3.8s ease-in-out infinite;
}

.flow-haze {
  position: absolute;
  border-radius: 50%;
  filter: blur(45px);
  mix-blend-mode: screen;
  pointer-events: none;
}

.flow-haze--right {
  right: -12vw;
  top: 10vh;
  width: 35vw;
  height: 35vw;
  background: radial-gradient(circle, rgba(0, 182, 255, 0.25), transparent 65%);
  animation: flowHaze 12s ease-in-out infinite;
}

.flow-haze--bottom {
  left: 20vw;
  bottom: -15vw;
  width: 55vw;
  height: 30vw;
  background: radial-gradient(ellipse, rgba(0, 148, 255, 0.2), transparent 65%);
  animation: flowHaze 15s ease-in-out infinite reverse;
}

.login-stage {
  position: relative;
  z-index: 1;
  display: grid;
  justify-items: end;
  align-items: center;
  min-height: 100vh;
  padding: 42px clamp(12px, 2vw, 36px) 42px 24px;
}

.orbit-shell {
  position: absolute;
  left: 50%;
  top: 50%;
  width: min(90vw, 700px);
  height: min(90vw, 700px);
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
  width: min(48vw, 650px);
  border: 1px solid rgba(102, 207, 255, 0.3);
  border-radius: 20px;
  padding: 36px 34px 30px;
  background: linear-gradient(145deg, rgba(4, 18, 48, 0.98), rgba(5, 31, 72, 0.96));
  box-shadow: 0 0 30px rgba(64, 188, 255, 0.18), 0 25px 70px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  transform-style: preserve-3d;
  transition: transform 0.2s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  z-index: 2;
}

.auth-card:hover {
  border-color: rgba(121, 226, 255, 0.45);
  box-shadow: 0 0 45px rgba(69, 198, 255, 0.25), 0 30px 80px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.tech-decoration {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  border-radius: inherit;
  pointer-events: none;
}

.corner {
  position: absolute;
  width: 28px;
  height: 28px;
  border: 2px solid rgba(0, 180, 255, 0.7);
}

.corner-top-left {
  left: 10px;
  top: 10px;
  border-right: none;
  border-bottom: none;
}

.corner-top-right {
  right: 10px;
  top: 10px;
  border-left: none;
  border-bottom: none;
}

.corner-bottom-left {
  left: 10px;
  bottom: 10px;
  border-right: none;
  border-top: none;
}

.corner-bottom-right {
  right: 10px;
  bottom: 10px;
  border-left: none;
  border-top: none;
}

.card-scan {
  position: absolute;
  left: 15px;
  right: 15px;
  top: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(105, 228, 255, 0.6), transparent);
  opacity: 0.4;
  box-shadow: 0 0 12px rgba(68, 202, 255, 0.3);
  animation: cardScan 5s linear infinite;
}

.auth-head {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 26px;
}

.terminal-dot {
  flex: 0 0 auto;
  width: 12px;
  height: 12px;
  margin-top: 8px;
  border-radius: 50%;
  background: #51f2ff;
  box-shadow: 0 0 18px #51f2ff;
  animation: dotPulse 2s ease-in-out infinite;
}

@keyframes dotPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.auth-head p {
  margin: 0;
  color: rgba(142, 228, 255, 0.7);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.2em;
}

.auth-head h1 {
  margin: 6px 0 0;
  color: #fff;
  font-size: 22px;
  font-weight: 800;
  line-height: 1.3;
}

.mode-switch {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  margin-bottom: 24px;
  border: 1px solid rgba(128, 224, 255, 0.2);
  border-radius: 14px;
  padding: 5px;
  background: rgba(10, 30, 60, 0.4);
}

.mode-switch button {
  border: 0;
  border-radius: 10px;
  padding: 10px;
  background: transparent;
  color: rgba(205, 236, 249, 0.6);
  font-weight: 700;
  font-size: 15px;
  cursor: pointer;
  transition: 0.25s ease;
  font-family: inherit;
}

.mode-switch button.active {
  background: linear-gradient(135deg, rgba(30, 136, 255, 0.9), rgba(31, 212, 255, 0.7));
  color: #fff;
  box-shadow: 0 8px 22px rgba(28, 178, 255, 0.25);
}

.auth-form {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 12px;
  font-weight: 600;
  color: rgba(180, 220, 255, 0.7);
  padding-left: 4px;
}

.input-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(100, 200, 255, 0.2);
  border-radius: 12px;
  background: rgba(8, 25, 55, 0.5);
  padding: 0 14px;
  transition: all 0.25s ease;
}

.input-wrap:focus-within {
  border-color: rgba(80, 220, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(60, 180, 255, 0.12), 0 0 20px rgba(60, 180, 255, 0.1);
  background: rgba(10, 30, 65, 0.6);
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
  font-size: 14px;
  padding: 13px 0;
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
  margin: 2px 0 6px;
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
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  background: transparent;
}

.remember-me input:checked + .check-box {
  background: linear-gradient(135deg, #0099ff, #00ddff);
  border-color: transparent;
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

.neon-button {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  min-height: 46px;
  overflow: hidden;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, #1779ff, #00d7ff);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 12px 30px rgba(0, 179, 255, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  font-family: inherit;
  letter-spacing: 1px;
}

.neon-button::before {
  position: absolute;
  top: -40%;
  left: -30%;
  width: 34%;
  height: 180%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
  transform: rotate(18deg);
  animation: buttonShine 3s ease-in-out infinite;
  content: "";
}

.neon-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 40px rgba(0, 194, 255, 0.4), 0 0 25px rgba(77, 225, 255, 0.2);
}

.neon-button:disabled {
  cursor: progress;
  opacity: 0.7;
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

@keyframes ribbonFlow {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: -1080; }
}

@keyframes networkTrace {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: -152; }
}

@keyframes networkPulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

@keyframes nodePulse {
  0%, 100% { opacity: 0.4; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.3); }
}

@keyframes flowHaze {
  0%, 100% { opacity: 0.5; transform: translate3d(0, 0, 0) scale(1); }
  50% { opacity: 0.8; transform: translate3d(-3vw, 2vh, 0) scale(1.08); }
}

@keyframes gridMove {
  from { background-position: 0 0, 0 0; }
  to { background-position: 0 40px, 40px 0; }
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

@keyframes cardScan {
  from { transform: translateY(0); }
  to { transform: translateY(600px); }
}

@keyframes buttonShine {
  0%, 45% { left: -45%; }
  70%, 100% { left: 120%; }
}

@media (max-width: 600px) {
  .login-stage {
    place-items: center;
    padding: 28px 16px;
  }

  .auth-card {
    width: min(90vw, 440px);
    padding: 28px 22px 24px;
  }
  .auth-head h1 {
    font-size: 19px;
  }
  .orbit-shell {
    width: 120vw;
    height: 120vw;
  }
}
</style>
