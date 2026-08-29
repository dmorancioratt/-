<template>
  <div class="login-page" @pointermove="handlePointerMove" @pointerleave="resetTilt">
    <div class="bg-full-image"></div>
    <div class="bg-overlay-gradient"></div>
    <div class="aurora aurora-a"></div>
    <div class="aurora aurora-b"></div>
    <div class="particle-field">
      <i v-for="item in 54" :key="item" :style="particleStyle(item)"></i>
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
        <span class="card-halo" aria-hidden="true"></span>
        <header class="auth-head">
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
              <a href="#" class="forgot-link">忘记密码？</a>
            </div>
            <button type="button" class="submit-button" :disabled="loading" @click="submitLogin">
              <span>{{ loading ? '登录中...' : '登　录' }}</span>
            </button>
            <div class="alt-login">
              <span class="alt-divider"><i>其他登录方式</i></span>
              <div class="alt-icons">
                <button type="button" title="账号登录" @click="otherLogin('账号登录')">
                  <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                    <line x1="8" y1="21" x2="16" y2="21"/>
                    <line x1="12" y1="17" x2="12" y2="21"/>
                  </svg>
                </button>
                <button type="button" title="安全密钥" @click="otherLogin('安全密钥')">
                  <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    <path d="M9 12l2 2 4-4"/>
                  </svg>
                </button>
                <button type="button" title="消息登录" @click="otherLogin('消息登录')">
                  <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
                  </svg>
                </button>
              </div>
            </div>
            <div class="role-tip">支持学生 · 求职者 · HR 多角色登录</div>
          </div>

          <div v-else key="register" class="auth-form">
            <div class="input-wrap">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              <input v-model="registerForm.username" type="text" placeholder="用户名" class="form-input" />
            </div>
            <div class="input-wrap">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
              <input v-model="registerForm.email" type="email" placeholder="邮箱" class="form-input" />
            </div>
            <div class="input-wrap">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              <input v-model="registerForm.password" type="password" placeholder="设置密码" class="form-input" />
            </div>
            <div class="input-wrap">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                <path d="M9 12l2 2 4-4"/>
              </svg>
              <input v-model="registerForm.confirmPassword" type="password" placeholder="确认密码" class="form-input" @keyup.enter="submitRegister" />
            </div>
            <button type="button" class="submit-button" :disabled="loading" @click="submitRegister">
              <span>{{ loading ? '注册中...' : '注　册' }}</span>
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

function otherLogin(name: string) {
  ElMessage.info(`${name}即将开放，敬请期待`)
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
  background: url('/login-bg.png') center center / cover no-repeat;
}

.bg-overlay-gradient {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(120deg, rgba(2, 8, 24, 0.18) 0%, rgba(3, 12, 34, 0.22) 45%, rgba(2, 10, 28, 0.42) 100%),
    radial-gradient(circle at 28% 42%, transparent 0%, rgba(1, 6, 20, 0.3) 78%);
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

@property --flow-angle {
  syntax: "<angle>";
  initial-value: 0deg;
  inherits: false;
}

.auth-card {
  position: relative;
  width: min(48vw, 650px);
  border-radius: 92px 72px 88px 76px / 76px 92px 72px 88px;
  padding: 50px 52px 30px;
  background: linear-gradient(172deg, rgba(6, 24, 58, 0.82) 0%, rgba(3, 12, 36, 0.88) 52%, rgba(9, 22, 56, 0.82) 100%);
  box-shadow: 0 0 46px rgba(0, 185, 255, 0.26), 0 30px 80px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(24px);
  transform-style: preserve-3d;
  transition: transform 0.2s ease, box-shadow 0.3s ease;
  z-index: 2;
}

.auth-card::after {
  content: "";
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  padding: 1.5px;
  background: linear-gradient(140deg, rgba(0, 214, 255, 0.45), rgba(64, 118, 255, 0.16) 40%, rgba(146, 98, 255, 0.4) 72%, rgba(0, 214, 255, 0.35));
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  mask-composite: exclude;
  pointer-events: none;
}

.auth-card::before {
  content: "";
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  padding: 2.5px;
  background: conic-gradient(
    from var(--flow-angle),
    rgba(0, 228, 255, 0) 0deg,
    rgba(0, 228, 255, 0) 235deg,
    rgba(0, 216, 255, 0.9) 295deg,
    #b8f7ff 322deg,
    rgba(168, 122, 255, 0.85) 346deg,
    rgba(0, 228, 255, 0) 360deg
  );
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  mask-composite: exclude;
  filter: drop-shadow(0 0 7px rgba(0, 220, 255, 0.6));
  animation: borderFlow 4.2s linear infinite;
  pointer-events: none;
}

.card-halo {
  position: absolute;
  inset: -30px;
  border-radius: 120px;
  background: radial-gradient(ellipse at 50% 10%, rgba(0, 196, 255, 0.2), transparent 62%);
  filter: blur(22px);
  pointer-events: none;
}

.auth-card:hover {
  box-shadow: 0 0 68px rgba(0, 200, 255, 0.34), 0 34px 90px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

@keyframes borderFlow {
  to { --flow-angle: 360deg; }
}

.auth-head {
  position: relative;
  z-index: 1;
  text-align: center;
  margin-bottom: 24px;
}

.auth-head h1 {
  margin: 0;
  color: #fff;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-shadow: 0 0 26px rgba(80, 200, 255, 0.5);
}

.auth-head p {
  margin: 10px 0 0;
  color: rgba(150, 200, 235, 0.6);
  font-size: 13px;
  letter-spacing: 0.1em;
}

.mode-switch {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  margin-bottom: 24px;
  padding: 5px;
  border: 1px solid transparent;
  border-radius: 999px;
  background:
    linear-gradient(180deg, rgba(7, 24, 54, 0.88), rgba(4, 14, 34, 0.92)) padding-box,
    linear-gradient(120deg, rgba(0, 209, 255, 0.6), rgba(46, 92, 255, 0.28) 45%, rgba(147, 96, 255, 0.55)) border-box;
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
  background: linear-gradient(120deg, #1f7bff 0%, #3f8cff 42%, #8b5cf6 100%);
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

.switch-thumb::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(105deg, transparent 32%, rgba(255, 255, 255, 0.38) 50%, transparent 68%);
  transform: translateX(-130%);
  animation: thumbShine 3.8s ease-in-out infinite;
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
  padding: 11px 0;
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
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 52px;
  border: 1px solid rgba(0, 190, 255, 0.22);
  border-radius: 14px;
  background: rgba(5, 18, 44, 0.55);
  padding: 0 16px;
  transition: all 0.25s ease;
}

.input-wrap:focus-within {
  border-color: rgba(0, 224, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(0, 180, 255, 0.12), 0 0 24px rgba(0, 190, 255, 0.12);
  background: rgba(7, 24, 56, 0.65);
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

.submit-button {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 50px;
  overflow: hidden;
  border: 0;
  border-radius: 999px;
  background: linear-gradient(90deg, #2e8bff 0%, #4f7dff 48%, #8a5cff 100%);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.4em;
  text-indent: 0.4em;
  cursor: pointer;
  font-family: inherit;
  box-shadow: 0 12px 32px rgba(70, 110, 255, 0.42), inset 0 1px 0 rgba(255, 255, 255, 0.35);
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}

.submit-button::before {
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

.submit-button:hover {
  transform: translateY(-2px);
  filter: brightness(1.08);
  box-shadow: 0 18px 42px rgba(90, 120, 255, 0.52), 0 0 28px rgba(138, 92, 255, 0.32);
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

@keyframes buttonShine {
  0%, 45% { left: -45%; }
  70%, 100% { left: 120%; }
}

@keyframes thumbShine {
  0%, 55% { transform: translateX(-130%); }
  85%, 100% { transform: translateX(130%); }
}

@media (max-width: 600px) {
  .login-stage {
    place-items: center;
    padding: 28px 16px;
  }

  .auth-card {
    width: min(90vw, 440px);
    padding: 42px 26px 22px;
    border-radius: 58px 46px 54px 48px / 48px 58px 46px 54px;
  }
  .auth-head h1 {
    font-size: 24px;
  }
  .orbit-shell {
    width: 120vw;
    height: 120vw;
  }
}
</style>
