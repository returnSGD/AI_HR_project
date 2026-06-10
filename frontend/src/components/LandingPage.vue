<template>
  <div class="lp" ref="lpRoot" @mousemove="onMouseMove">

    <!-- ── 鼠标光晕 ── -->
    <div class="cursor-glow" ref="cursorGlow"></div>

    <!-- ── Canvas 粒子背景 ── -->
    <canvas ref="canvas" class="bg-canvas"></canvas>

    <!-- ── Aurora 渐变光球 ── -->
    <div class="aurora" aria-hidden="true">
      <div class="ab ab1"></div>
      <div class="ab ab2"></div>
      <div class="ab ab3"></div>
    </div>

    <!-- ── 导航 ── -->
    <nav class="lp-nav">
      <div class="lp-logo">
        <span class="logo-mark">🎯</span>
        <span class="logo-word">Offer-Catcher</span>
        <span class="logo-badge">Beta</span>
      </div>
      <button class="nav-launch" @click="openModal">
        {{ locale === 'zh' ? '立即使用' : 'Launch App' }}
        <span class="nl-arr">↗</span>
      </button>
    </nav>

    <!-- ── Hero ── -->
    <section class="hero">
      <div class="hero-tag ai-in" style="--d:0s">
        <span class="tag-pulse"></span>
        {{ locale === 'zh' ? 'AI 驱动的求职助手' : 'AI-Powered Career Tool' }}
      </div>

      <h1 class="hero-h1 ai-in" style="--d:.14s">
        <span class="h1-plain">{{ locale === 'zh' ? '让 AI 帮你' : 'Land Your' }}</span>
        <br>
        <span class="h1-grad">{{ locale === 'zh' ? '精准命中梦想工作' : 'Dream Job Faster' }}</span>
      </h1>

      <p class="hero-sub ai-in" style="--d:.28s">
        {{ locale === 'zh'
          ? '上传简历 · 15 秒内匹配顶级岗位 · 获得个性化优化报告'
          : 'Upload resume · match top roles in 15s · get a personalized AI report' }}
      </p>

      <div class="hero-btns ai-in" style="--d:.42s">
        <button class="cta-btn" @click="openModal">
          <span>{{ locale === 'zh' ? '✨ 立即分析简历' : '✨ Analyze My Resume' }}</span>
          <span class="cta-shine"></span>
        </button>
        <span class="cta-note">{{ locale === 'zh' ? '免费 · 无需注册' : 'Free · No sign-up' }}</span>
      </div>

      <!-- 数据统计 -->
      <div class="stats ai-in" style="--d:.56s">
        <div class="stat-item">
          <span class="sn">15s</span>
          <span class="sl">{{ locale === 'zh' ? '平均匹配时间' : 'Avg match time' }}</span>
        </div>
        <div class="stat-sep"></div>
        <div class="stat-item">
          <span class="sn">98%</span>
          <span class="sl">{{ locale === 'zh' ? '用户满意度' : 'Satisfaction' }}</span>
        </div>
        <div class="stat-sep"></div>
        <div class="stat-item">
          <span class="sn">10K+</span>
          <span class="sl">{{ locale === 'zh' ? '收录职位' : 'Jobs indexed' }}</span>
        </div>
      </div>
    </section>

    <!-- ── 特性卡片 ── -->
    <section class="features">
      <p class="sec-eyebrow">{{ locale === 'zh' ? '核心能力' : 'Core Features' }}</p>
      <h2 class="sec-title">
        {{ locale === 'zh' ? '四步完成精准求职' : 'Four steps to your next offer' }}
      </h2>
      <div class="cards-grid">
        <div
          v-for="(c, i) in cards"
          :key="i"
          class="feat-card scroll-reveal"
          :style="`--ci:${i}`"
          :ref="el => { if(el) cardEls[i]=el }"
          @mousemove="tiltCard($event, i)"
          @mouseleave="resetCard(i)"
        >
          <div class="card-border-glow"></div>
          <div class="card-ico">{{ c.ico }}</div>
          <h3 class="card-h">{{ locale === 'zh' ? c.zh : c.en }}</h3>
          <p class="card-p">{{ locale === 'zh' ? c.dzh : c.den }}</p>
          <span class="card-chip">{{ locale === 'zh' ? c.czh : c.cen }}</span>
        </div>
      </div>
    </section>

    <!-- ── AI 演示输入框 ── -->
    <section class="demo scroll-reveal" style="--ci:0">
      <p class="sec-eyebrow">{{ locale === 'zh' ? '体验一下' : 'Try it' }}</p>
      <h2 class="sec-title demo-t">
        {{ locale === 'zh' ? '直接问 AI，拿到答案' : 'Ask AI, get answers instantly' }}
      </h2>
      <div class="ai-box">
        <span class="ai-sparkle">✦</span>
        <input
          class="ai-inp"
          v-model="demoQ"
          :placeholder="locale === 'zh' ? '我的简历适合哪些岗位？' : 'What roles fit my resume?'"
          @keydown.enter="runDemo"
          :disabled="demoLoading"
        />
        <button class="ai-go" @click="runDemo" :class="{spin: demoLoading}">
          {{ demoLoading ? '…' : '→' }}
        </button>
      </div>
      <transition name="resp">
        <div v-if="demoResp" class="demo-resp">
          <span class="resp-dot">✦</span>
          {{ demoResp }}
        </div>
      </transition>
    </section>

    <!-- ── 大 CTA ── -->
    <section class="big-cta scroll-reveal" style="--ci:0">
      <div class="cta-orb"></div>
      <h2 class="big-cta-h">
        {{ locale === 'zh' ? '你的下一份 Offer，从现在开始' : 'Your next offer starts here' }}
      </h2>
      <p class="big-cta-sub">
        {{ locale === 'zh' ? '上传简历，AI 立即为你工作' : 'Upload your resume, let AI do the work' }}
      </p>
      <button class="cta-btn cta-lg" @click="openModal">
        {{ locale === 'zh' ? '🚀 开始使用' : '🚀 Get Started' }}
        <span class="cta-shine"></span>
      </button>
    </section>

    <!-- ── Footer ── -->
    <footer class="lp-footer">
      <span>© 2025 Offer-Catcher · Built with DeepSeek AI</span>
    </footer>

    <!-- ── 意向岗位分流弹窗 ── -->
    <Transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card">
          <button class="modal-close" @click="closeModal">✕</button>
          <div class="modal-icon">🎯</div>
          <h3 class="modal-title">
            {{ locale === 'zh' ? '您是否有心仪的意向岗位？' : 'Do you have a target role in mind?' }}
          </h3>
          <p class="modal-sub">
            {{ locale === 'zh'
              ? '这将决定为您匹配的精准度'
              : 'This shapes how we match you.' }}
          </p>
          <div class="modal-btns">
            <button class="modal-btn modal-btn-primary" @click="chooseMode('jdmatch')">
              <span class="mbtn-ico">📋</span>
              <span class="mbtn-text">
                <strong>{{ locale === 'zh' ? '是，我有明确岗位' : 'Yes, I have a target role' }}</strong>
                <small>{{ locale === 'zh' ? '粘贴 JD，精准匹配' : 'Paste a JD for precision matching' }}</small>
              </span>
              <span class="mbtn-arr">→</span>
            </button>
            <button class="modal-btn modal-btn-secondary" @click="chooseMode('seeker')">
              <span class="mbtn-ico">🤖</span>
              <span class="mbtn-text">
                <strong>{{ locale === 'zh' ? '否，请帮我智能推荐' : 'No, recommend for me' }}</strong>
                <small>{{ locale === 'zh' ? '上传简历，AI 盲投推荐' : 'Upload resume, AI picks the best fits' }}</small>
              </span>
              <span class="mbtn-arr">→</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { useI18n } from 'vue-i18n'

const emit = defineEmits(['launch'])
const { locale } = useI18n()

// ── Intent modal ──────────────────────────────────────────────
const showModal = ref(false)
function openModal()    { showModal.value = true }
function closeModal()   { showModal.value = false }
function chooseMode(mode) { closeModal(); emit('launch', mode) }

// ── refs ────────────────────────────────────────────────────
const lpRoot    = ref(null)
const canvas    = ref(null)
const cursorGlow= ref(null)
const cardEls   = reactive([])

// ── cards data ──────────────────────────────────────────────
const cards = [
  { ico:'📄', zh:'智能简历解析', en:'Resume Parsing',
    dzh:'AI 即时理解你的技能、经历与背景，不遗漏任何关键信息。',
    den:'AI reads your skills and background instantly — nothing missed.',
    czh:'多格式支持', cen:'Multi-format' },
  { ico:'🎯', zh:'精准岗位匹配', en:'Smart Matching',
    dzh:'基于关键词覆盖率，从数千岗位中找出最适合你的前 10 名。',
    den:'Keyword-coverage scoring across thousands of roles, top-10 for you.',
    czh:'实时排名', cen:'Live ranking' },
  { ico:'🎭', zh:'HR 视角模拟', en:'HR Perspective',
    dzh:'模拟招聘官读简历的真实心理，找出你的优势和盲点。',
    den:'See your resume through a recruiter\'s eyes, strengths & blind spots.',
    czh:'AI 内心戏', cen:'AI inner thoughts' },
  { ico:'✨', zh:'个性化优化', en:'Tailored Optimize',
    dzh:'针对每个岗位生成具体的修改建议，让命中率大幅提升。',
    den:'Job-specific revision tips to dramatically boost your hit rate.',
    czh:'逐岗定制', cen:'Per-job advice' },
]

// ── demo ─────────────────────────────────────────────────────
const demoQ       = ref('')
const demoResp    = ref('')
const demoLoading = ref(false)
const demoAnswers = {
  zh: [
    '根据您简历中的技能分布，推荐：产品经理、数据分析师、算法工程师等方向，匹配度在 72%~89% 之间。',
    '您的经历与互联网大厂的校招岗位高度契合，建议优先投递技术方向的实习岗，可大幅提升转正概率。',
    '关键词分析显示您在「Python / 数据分析 / 机器学习」方向具备优势，补充一份实习项目会让简历竞争力翻倍。',
  ],
  en: [
    'Based on your skill profile: Product Manager, Data Analyst, and ML Engineer roles match you at 72–89%.',
    'Your background aligns closely with top-tier tech internships. Applying to technical roles first maximizes conversion.',
    'Your keywords indicate strong Python / Data Analysis aptitude. Adding one more internship project doubles competitiveness.',
  ],
}

function runDemo() {
  if (demoLoading.value || !demoQ.value.trim()) return
  demoLoading.value = true
  demoResp.value = ''
  const answers = locale.value === 'zh' ? demoAnswers.zh : demoAnswers.en
  const pick = answers[Math.floor(Math.random() * answers.length)]
  let i = 0
  setTimeout(() => {
    demoLoading.value = false
    const id = setInterval(() => {
      demoResp.value += pick[i++]
      if (i >= pick.length) clearInterval(id)
    }, 28)
  }, 900)
}

// ── cursor glow ──────────────────────────────────────────────
let mx = 0, my = 0, cx = 0, cy = 0, rafCursor = 0
function onMouseMove(e) {
  mx = e.clientX; my = e.clientY
}
function animCursor() {
  cx += (mx - cx) * 0.09
  cy += (my - cy) * 0.09
  if (cursorGlow.value)
    cursorGlow.value.style.transform = `translate(${cx - 200}px, ${cy - 200}px)`
  rafCursor = requestAnimationFrame(animCursor)
}

// ── card 3D tilt ─────────────────────────────────────────────
function tiltCard(e, i) {
  const el = cardEls[i]
  if (!el) return
  const r = el.getBoundingClientRect()
  const x = (e.clientX - r.left) / r.width  - 0.5
  const y = (e.clientY - r.top)  / r.height - 0.5
  el.style.transform = `perspective(700px) rotateX(${-y*10}deg) rotateY(${x*10}deg) scale(1.04) translateZ(8px)`
  el.style.transition = 'transform .08s linear'
}
function resetCard(i) {
  const el = cardEls[i]
  if (!el) return
  el.style.transform = ''
  el.style.transition = 'transform .55s cubic-bezier(0.22,1,0.36,1)'
}

// ── canvas particles ─────────────────────────────────────────
let ctx, pts = [], rafCanvas = 0
const N = 70, MAX_DIST = 130

function initCanvas() {
  const c = canvas.value
  c.width  = window.innerWidth
  c.height = window.innerHeight
  ctx = c.getContext('2d')
  pts = Array.from({length: N}, () => ({
    x: Math.random() * c.width,
    y: Math.random() * c.height,
    vx: (Math.random() - 0.5) * 0.4,
    vy: (Math.random() - 0.5) * 0.4,
    r:  Math.random() * 1.5 + 0.5,
  }))
}

function drawCanvas() {
  const c = canvas.value
  ctx.clearRect(0, 0, c.width, c.height)
  for (const p of pts) {
    p.x += p.vx; p.y += p.vy
    if (p.x < 0 || p.x > c.width)  p.vx *= -1
    if (p.y < 0 || p.y > c.height) p.vy *= -1
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
    ctx.fillStyle = 'rgba(129,140,248,.7)'
    ctx.fill()
  }
  for (let i = 0; i < pts.length; i++) {
    for (let j = i + 1; j < pts.length; j++) {
      const dx = pts[i].x - pts[j].x
      const dy = pts[i].y - pts[j].y
      const d  = Math.sqrt(dx*dx + dy*dy)
      if (d < MAX_DIST) {
        ctx.beginPath()
        ctx.moveTo(pts[i].x, pts[i].y)
        ctx.lineTo(pts[j].x, pts[j].y)
        ctx.strokeStyle = `rgba(129,140,248,${.12 * (1 - d / MAX_DIST)})`
        ctx.lineWidth = 0.8
        ctx.stroke()
      }
    }
  }
  rafCanvas = requestAnimationFrame(drawCanvas)
}

// ── scroll reveal ─────────────────────────────────────────────
let observer
function setupObserver() {
  observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('revealed')
        observer.unobserve(e.target)
      }
    })
  }, { threshold: 0.12 })
  document.querySelectorAll('.scroll-reveal').forEach(el => observer.observe(el))
}

function onResize() {
  if (canvas.value) {
    canvas.value.width  = window.innerWidth
    canvas.value.height = window.innerHeight
  }
}

onMounted(() => {
  initCanvas()
  drawCanvas()
  animCursor()
  setupObserver()
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  cancelAnimationFrame(rafCanvas)
  cancelAnimationFrame(rafCursor)
  observer?.disconnect()
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
/* ─── Root & Background ───────────────────────────────────── */
.lp {
  min-height: 100vh;
  background: #050510;
  color: #e2e8f0;
  font-family: -apple-system, 'SF Pro Text', 'Inter', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
  position: relative;
}
.bg-canvas {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

/* ─── Aurora blobs ────────────────────────────────────────── */
.aurora { position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
.ab {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  opacity: .13;
  animation: float 9s ease-in-out infinite;
}
.ab1 { width:700px; height:700px; background:#6366f1; top:-250px; left:-180px; }
.ab2 { width:550px; height:550px; background:#8b5cf6; top:35%; right:-200px; animation-delay:-3.5s; }
.ab3 { width:450px; height:450px; background:#06b6d4; bottom:5%; left:15%;  animation-delay:-6s; }

@keyframes float {
  0%,100% { transform: translateY(0) scale(1); }
  50%      { transform: translateY(-40px) scale(1.04); }
}

/* ─── Cursor glow ─────────────────────────────────────────── */
.cursor-glow {
  position: fixed;
  top: 0; left: 0;
  width: 400px; height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99,102,241,.18) 0%, transparent 70%);
  pointer-events: none;
  z-index: 1;
  will-change: transform;
}

/* ─── Nav ─────────────────────────────────────────────────── */
.lp-nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 36px; height: 60px;
  background: rgba(5,5,16,.72);
  backdrop-filter: saturate(180%) blur(24px);
  -webkit-backdrop-filter: saturate(180%) blur(24px);
  border-bottom: 1px solid rgba(255,255,255,.06);
}
.lp-logo { display:flex; align-items:center; gap:10px; }
.logo-mark { font-size:1.1rem; }
.logo-word { font-weight:700; font-size:.95rem; letter-spacing:-.01em; color:#f1f5f9; }
.logo-badge {
  font-size:.56rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase;
  background: rgba(99,102,241,.25); border: 1px solid rgba(99,102,241,.45);
  color: #a5b4fc; padding: 2px 8px; border-radius: 20px;
}
.nav-launch {
  display:flex; align-items:center; gap:5px;
  background: rgba(99,102,241,.18);
  border: 1px solid rgba(99,102,241,.35);
  color: #a5b4fc;
  border-radius: 980px; padding: 7px 18px;
  font-size:.82rem; font-weight:600; cursor:pointer;
  transition: all .4s cubic-bezier(0.22,1,0.36,1);
}
.nav-launch:hover { background: rgba(99,102,241,.32); border-color: rgba(99,102,241,.6); transform: scale(1.04); color:#c7d2fe; }
.nl-arr { transition: transform .3s cubic-bezier(0.22,1,0.36,1); }
.nav-launch:hover .nl-arr { transform: translate(2px,-2px); }

/* ─── Hero ────────────────────────────────────────────────── */
.hero {
  position: relative; z-index: 10;
  min-height: 100vh;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 120px 24px 80px;
  text-align: center;
}
/* staggered entrance */
.ai-in {
  opacity: 0;
  transform: translateY(30px);
  animation: fadeUp 1s cubic-bezier(0.22,1,0.36,1) both;
  animation-delay: var(--d, 0s);
}
@keyframes fadeUp {
  to { opacity:1; transform:translateY(0); }
}

.hero-tag {
  display:inline-flex; align-items:center; gap:8px;
  font-size:.75rem; font-weight:600; letter-spacing:.06em; text-transform:uppercase;
  color: #818cf8;
  background: rgba(99,102,241,.1); border: 1px solid rgba(99,102,241,.25);
  padding: 6px 16px; border-radius: 20px; margin-bottom: 28px;
}
.tag-pulse {
  width:7px; height:7px; border-radius:50%; background:#818cf8;
  animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%,100% { opacity:1; transform:scale(1); }
  50%      { opacity:.4; transform:scale(.8); }
}

.hero-h1 {
  font-size: clamp(2.4rem, 7vw, 4.8rem);
  font-weight: 800; line-height: 1.06; letter-spacing: -.04em;
  margin: 0 0 22px;
}
.h1-plain { color: #f1f5f9; display:block; }
.h1-grad {
  display: inline-block;
  background: linear-gradient(135deg, #818cf8 0%, #c084fc 40%, #67e8f9 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  animation: grad-shift 6s ease-in-out infinite alternate;
  background-size: 200% 200%;
}
@keyframes grad-shift {
  from { background-position: 0% 50%; }
  to   { background-position: 100% 50%; }
}

.hero-sub {
  font-size: clamp(.9rem, 2.2vw, 1.1rem);
  color: #94a3b8; max-width: 520px; line-height:1.7;
  margin: 0 auto 38px;
}

.hero-btns { display:flex; flex-direction:column; align-items:center; gap:14px; }
.cta-note  { font-size:.72rem; color:#64748b; }

/* CTA Button */
.cta-btn {
  position: relative; overflow: hidden;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border: none; border-radius: 980px;
  padding: 14px 36px;
  font-size: .95rem; font-weight:700; color:#fff; letter-spacing:-.01em;
  cursor: pointer;
  box-shadow: 0 4px 24px rgba(99,102,241,.4), 0 0 0 0 rgba(99,102,241,.3);
  transition: transform .45s cubic-bezier(0.22,1,0.36,1), box-shadow .45s cubic-bezier(0.22,1,0.36,1);
  will-change: transform;
}
.cta-btn:hover { transform: scale(1.05) translateY(-2px); box-shadow: 0 8px 36px rgba(99,102,241,.55), 0 0 0 4px rgba(99,102,241,.15); }
.cta-btn:active { transform: scale(.97); transition-duration:.12s; }
.cta-shine {
  position:absolute; inset:0;
  background: linear-gradient(110deg, transparent 30%, rgba(255,255,255,.22) 50%, transparent 70%);
  transform: translateX(-100%);
  transition: transform 0s;
}
.cta-btn:hover .cta-shine { transform: translateX(100%); transition: transform .55s ease; }

.cta-lg { padding: 16px 44px; font-size:1rem; }

/* Stats */
.stats {
  display:flex; align-items:center; gap:28px;
  margin-top: 52px;
  padding: 20px 32px;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.07);
  border-radius: 20px;
  backdrop-filter: blur(12px);
}
.stat-item { display:flex; flex-direction:column; align-items:center; gap:4px; }
.sn { font-size:1.6rem; font-weight:800; letter-spacing:-.03em; color:#f1f5f9; }
.sl { font-size:.68rem; color:#64748b; font-weight:500; white-space:nowrap; }
.stat-sep { width:1px; height:32px; background:rgba(255,255,255,.1); }

/* ─── Section shared ──────────────────────────────────────── */
section { position:relative; z-index:10; }
.sec-eyebrow {
  text-align:center; text-transform:uppercase; letter-spacing:.1em;
  font-size:.68rem; font-weight:700; color:#6366f1; margin-bottom:12px;
}
.sec-title {
  text-align:center; font-size:clamp(1.5rem,4vw,2.4rem);
  font-weight:800; letter-spacing:-.03em; color:#f1f5f9; margin:0 0 48px;
}

/* ─── Features ────────────────────────────────────────────── */
.features { padding: 100px 24px; max-width:1100px; margin:0 auto; }
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

/* scroll-reveal base state */
.scroll-reveal {
  opacity: 0;
  transform: translateY(28px);
  transition:
    opacity .7s cubic-bezier(0.22,1,0.36,1) calc(var(--ci, 0) * .1s),
    transform .7s cubic-bezier(0.22,1,0.36,1) calc(var(--ci, 0) * .1s);
}
.scroll-reveal.revealed { opacity:1; transform:translateY(0); }

.feat-card {
  position: relative; overflow: hidden;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 20px;
  padding: 28px 24px;
  cursor: default;
  transition: transform .55s cubic-bezier(0.22,1,0.36,1), box-shadow .55s cubic-bezier(0.22,1,0.36,1);
  will-change: transform;
}
.feat-card:hover { box-shadow: 0 12px 44px rgba(99,102,241,.18), 0 0 0 1px rgba(99,102,241,.25); }

/* animated border glow */
.card-border-glow {
  position:absolute; inset:-1px; border-radius:21px; z-index:0;
  background: linear-gradient(135deg, rgba(99,102,241,.0), rgba(139,92,246,.0), rgba(6,182,212,.0));
  transition: background .4s;
  pointer-events:none;
}
.feat-card:hover .card-border-glow {
  background: linear-gradient(135deg, rgba(99,102,241,.35), rgba(139,92,246,.2), rgba(6,182,212,.25));
  animation: border-rot 3s linear infinite;
}
@keyframes border-rot {
  to { filter: hue-rotate(30deg); }
}

.card-ico  { font-size:2rem; margin-bottom:14px; display:block; position:relative; z-index:1; }
.card-h    { font-size:1rem; font-weight:700; color:#f1f5f9; margin:0 0 8px; position:relative; z-index:1; }
.card-p    { font-size:.8rem; color:#94a3b8; line-height:1.65; margin:0 0 16px; position:relative; z-index:1; }
.card-chip {
  display:inline-block; font-size:.62rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase;
  background: rgba(99,102,241,.15); border:1px solid rgba(99,102,241,.3);
  color:#818cf8; padding:3px 10px; border-radius:20px; position:relative; z-index:1;
}

/* ─── AI Demo ─────────────────────────────────────────────── */
.demo { padding: 80px 24px; max-width: 680px; margin: 0 auto; text-align:center; }
.demo-t { margin-bottom:32px; }

.ai-box {
  display:flex; align-items:center; gap:10px;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(99,102,241,.3);
  border-radius: 980px;
  padding: 6px 8px 6px 20px;
  transition: border-color .4s cubic-bezier(0.22,1,0.36,1), box-shadow .4s cubic-bezier(0.22,1,0.36,1);
}
.ai-box:focus-within {
  border-color: rgba(99,102,241,.7);
  box-shadow: 0 0 0 4px rgba(99,102,241,.12), 0 0 24px rgba(99,102,241,.2);
}
.ai-sparkle { font-size:.9rem; color:#818cf8; flex-shrink:0; }
.ai-inp {
  flex:1; background:none; border:none; outline:none; font-size:.88rem;
  color:#e2e8f0; placeholder-color:#475569;
  font-family:inherit;
}
.ai-inp::placeholder { color:#475569; }
.ai-go {
  width:36px; height:36px; flex-shrink:0;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border:none; border-radius:50%; color:#fff; font-size:.95rem; font-weight:700;
  cursor:pointer; transition: transform .4s cubic-bezier(0.22,1,0.36,1), box-shadow .4s;
  display:flex; align-items:center; justify-content:center;
}
.ai-go:hover { transform: scale(1.1); box-shadow: 0 4px 16px rgba(99,102,241,.5); }
.ai-go.spin { animation: spin-btn .8s linear infinite; }
@keyframes spin-btn { to { transform: rotate(360deg); } }

.demo-resp {
  display:flex; align-items:flex-start; gap:10px;
  margin-top:20px; padding:18px 22px;
  background: rgba(99,102,241,.07); border:1px solid rgba(99,102,241,.18);
  border-radius:16px; text-align:left;
}
.resp-dot { color:#818cf8; flex-shrink:0; margin-top:2px; }
.demo-resp p, .demo-resp span { font-size:.84rem; color:#cbd5e1; line-height:1.7; }
.resp-enter-active { transition: opacity .5s cubic-bezier(0.22,1,0.36,1), transform .5s cubic-bezier(0.22,1,0.36,1); }
.resp-enter-from   { opacity:0; transform:translateY(10px); }

/* ─── Big CTA ─────────────────────────────────────────────── */
.big-cta {
  padding: 120px 24px;
  text-align:center; position:relative; overflow:hidden;
}
.cta-orb {
  position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
  width:500px; height:500px; border-radius:50%;
  background: radial-gradient(circle, rgba(99,102,241,.18) 0%, transparent 70%);
  pointer-events:none; z-index:0;
  animation: orb-pulse 4s ease-in-out infinite;
}
@keyframes orb-pulse {
  0%,100% { transform: translate(-50%,-50%) scale(1); opacity:.8; }
  50%      { transform: translate(-50%,-50%) scale(1.15); opacity:.5; }
}
.big-cta-h {
  font-size:clamp(1.6rem,4.5vw,2.8rem); font-weight:800; letter-spacing:-.04em;
  color:#f1f5f9; position:relative; z-index:1; margin-bottom:14px;
}
.big-cta-sub { color:#64748b; font-size:.95rem; margin-bottom:36px; position:relative; z-index:1; }

/* ─── Footer ──────────────────────────────────────────────── */
.lp-footer {
  text-align:center; padding:32px 24px;
  font-size:.72rem; color:#334155;
  border-top: 1px solid rgba(255,255,255,.05);
  position:relative; z-index:10;
}

/* ─── Responsive ──────────────────────────────────────────── */
@media (max-width: 600px) {
  .stats { gap:18px; padding:16px 20px; flex-wrap:wrap; justify-content:center; }
  .lp-nav { padding:0 18px; }
  .hero-h1 { letter-spacing:-.02em; }
  .cards-grid { grid-template-columns: 1fr; }
}

/* ─── Intent Modal ─────────────────────────────────────────── */
.modal-overlay {
  position: fixed; inset: 0; z-index: 9000;
  background: rgba(0,0,0,.65);
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.modal-card {
  position: relative;
  background: rgba(10,10,28,.92);
  border: 1px solid rgba(255,255,255,.1);
  border-radius: 24px;
  padding: 40px 36px 36px;
  max-width: 460px; width: 100%;
  box-shadow: 0 32px 80px rgba(0,0,0,.5), 0 0 0 1px rgba(255,255,255,.06);
  text-align: center;
}
.modal-close {
  position: absolute; top: 16px; right: 18px;
  background: none; border: none; color: #64748b;
  font-size: .9rem; cursor: pointer;
  transition: color .2s;
}
.modal-close:hover { color: #f1f5f9; }
.modal-icon { font-size: 2.4rem; margin-bottom: 12px; }
.modal-title {
  font-size: 1.18rem; font-weight: 700; color: #f1f5f9;
  letter-spacing: -.02em; margin-bottom: 8px;
}
.modal-sub { font-size: .83rem; color: #64748b; margin-bottom: 28px; }
.modal-btns { display: flex; flex-direction: column; gap: 12px; }
.modal-btn {
  display: flex; align-items: center; gap: 14px;
  padding: 16px 18px; border-radius: 16px;
  border: 1px solid transparent; cursor: pointer;
  text-align: left; transition: all .28s cubic-bezier(.22,1,.36,1);
}
.modal-btn-primary {
  background: rgba(245,166,35,.1);
  border-color: rgba(245,166,35,.3);
}
.modal-btn-primary:hover {
  background: rgba(245,166,35,.18);
  border-color: rgba(245,166,35,.6);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(245,166,35,.2);
}
.modal-btn-secondary {
  background: rgba(255,255,255,.04);
  border-color: rgba(255,255,255,.1);
}
.modal-btn-secondary:hover {
  background: rgba(255,255,255,.09);
  border-color: rgba(255,255,255,.22);
  transform: translateY(-2px);
}
.mbtn-ico { font-size: 1.5rem; flex-shrink: 0; }
.mbtn-text { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.mbtn-text strong { font-size: .88rem; color: #f1f5f9; font-weight: 600; }
.mbtn-text small  { font-size: .76rem; color: #64748b; }
.mbtn-arr { color: #64748b; font-size: .85rem; transition: transform .2s, color .2s; }
.modal-btn:hover .mbtn-arr { color: #f1f5f9; transform: translateX(4px); }

/* modal transition */
.modal-enter-active, .modal-leave-active { transition: opacity .25s ease, transform .3s cubic-bezier(.22,1,.36,1); }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-card { transform: scale(.92) translateY(16px); }
.modal-leave-to .modal-card { transform: scale(.95) translateY(8px); }
</style>
