<template>
  <div class="jdm" ref="root" @mousemove="onMouse">

    <!-- ── Fixed BG layer ── -->
    <div class="cursor-glow" ref="cursorGlow"></div>
    <canvas ref="canvas" class="bg-canvas"></canvas>
    <div class="aurora" aria-hidden="true">
      <div class="ab ab1"></div>
      <div class="ab ab2"></div>
      <div class="ab ab3"></div>
    </div>

    <!-- ── Sticky nav ── -->
    <nav class="jdm-nav">
      <button class="back-btn" @click="$emit('close')">
        <span class="back-ico">←</span>
        {{ locale === 'zh' ? '返回' : 'Back' }}
      </button>
      <div class="nav-brand">
        <span class="brand-ico">🎯</span>
        <span class="brand-word">Offer-Catcher</span>
      </div>
    </nav>

    <!-- ── Scrollable content ── -->
    <div class="jdm-body">

      <!-- Hero -->
      <header class="jdm-hero ai-in" style="--d:0s">
        <div class="hero-tag">
          <span class="tag-dot"></span>
          {{ locale === 'zh' ? 'AI 驱动 · 求职利器' : 'AI-Powered Career Tool' }}
        </div>
        <h1 class="jdm-h1">
          <span class="h1-plain">{{ locale === 'zh' ? 'JD 精准' : 'Smart JD' }}&nbsp;</span><span class="h1-grad">{{ locale === 'zh' ? '匹配' : 'Match' }}</span>
          <br>
          <span class="h1-plain">{{ locale === 'zh' ? '&amp; 简历' : '&amp; Resume' }}&nbsp;</span><span class="h1-grad2">{{ locale === 'zh' ? '智能生成' : 'AI Draft' }}</span>
        </h1>
        <p class="jdm-sub">
          {{ locale === 'zh'
            ? '粘贴职位描述，AI 深度分析你的简历契合度；或者还没简历？让 AI 帮你从零写一份'
            : 'Paste a JD to analyze your fit — or no resume yet? Let AI draft one from scratch.' }}
        </p>
      </header>

      <!-- Tab bar -->
      <div class="tabs ai-in" style="--d:.13s">
        <button :class="['tab-btn', {active: tab==='match'}]" @click="tab='match'">
          <span class="tab-ico">🔍</span>
          {{ locale === 'zh' ? 'JD 匹配分析' : 'JD Fit Analysis' }}
        </button>
        <button :class="['tab-btn', {active: tab==='draft'}]" @click="tab='draft'">
          <span class="tab-ico">✍️</span>
          {{ locale === 'zh' ? 'AI 帮我写简历' : 'AI Draft Resume' }}
        </button>
      </div>

      <!-- Error -->
      <transition name="err-fade">
        <div v-if="err" class="err-box">⚠ {{ err }}</div>
      </transition>

      <!-- Two-column panels -->
      <div class="panels ai-in" style="--d:.24s">

        <!-- LEFT: JD input (shared) -->
        <div class="panel" ref="panelL"
          @mousemove="e => tilt(e, panelL)" @mouseleave="e => resetTilt(panelL)">
          <div class="panel-glow"></div>
          <div class="panel-hd">
            <div class="panel-ico">📋</div>
            <div>
              <div class="panel-title">{{ locale === 'zh' ? '职位描述 (JD)' : 'Job Description (JD)' }}</div>
              <div class="panel-hint">{{ locale === 'zh' ? '从任意招聘网站复制完整内容' : 'Copy full JD from any job board' }}</div>
            </div>
          </div>
          <div class="ta-wrap" :class="{focused: jdFocus}">
            <textarea class="glass-ta"
              v-model="jdText"
              :placeholder="locale === 'zh'
                ? '将职位描述粘贴到这里…\n\n可从 BOSS 直聘、猎聘、招聘官网等复制完整 JD 内容'
                : 'Paste the full job description here…\n\nCopy from LinkedIn, Indeed, or any career page'"
              @focus="jdFocus=true" @blur="jdFocus=false"
            />
          </div>
          <div class="ta-bar">
            <span :class="['char-cnt', {warn: jdText.length > 2800}]">{{ jdText.length }} / 3000</span>
            <button v-if="jdText" class="clear-btn" @click="jdText=''">
              {{ locale === 'zh' ? '清空' : 'Clear' }}
            </button>
          </div>
        </div>

        <!-- RIGHT: tab-dependent -->
        <div class="panel panel-r" ref="panelR"
          @mousemove="e => tilt(e, panelR)" @mouseleave="e => resetTilt(panelR)">
          <div class="panel-glow"></div>

          <!-- ══ TAB: MATCH ══ -->
          <template v-if="tab === 'match'">
            <div class="panel-hd">
              <div class="panel-ico">📄</div>
              <div>
                <div class="panel-title">{{ locale === 'zh' ? '我的简历' : 'My Resume' }}</div>
                <div class="panel-hint">PDF · Word · 图片 · TXT</div>
              </div>
            </div>

            <label class="drop-zone" :class="{'has-file': mFile}">
              <input type="file"
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/*"
                @change="pickFile" hidden />
              <template v-if="!mFile">
                <span class="dz-cloud">☁</span>
                <span class="dz-main">{{ locale === 'zh' ? '点击上传简历文件' : 'Click to upload resume' }}</span>
                <span class="dz-sub">PDF · Word · 图片 · TXT · MD</span>
              </template>
              <template v-else>
                <span class="dz-check">✓</span>
                <span class="dz-main">{{ mFile.name }}</span>
              </template>
            </label>

            <button class="cta-btn"
              :disabled="!canMatch || mPhase==='loading' || mPhase==='streaming'"
              @click="runMatch">
              <span>{{ mPhase==='loading' || mPhase==='streaming'
                ? (locale==='zh' ? '分析中…' : 'Analyzing…')
                : (locale==='zh' ? '🔍 分析匹配度' : '🔍 Analyze Fit') }}</span>
              <span class="btn-shine"></span>
            </button>

            <div v-if="!canMatch && mPhase==='idle'" class="req-note">
              {{ locale === 'zh' ? '请先粘贴 JD（≥20 字）并上传简历' : 'Paste a JD (20+ chars) and upload your resume' }}
            </div>

            <transition name="pill-in">
              <div v-if="mPhase==='loading'" class="status-pill">
                <span class="spin-ring"></span> {{ mStatus }}
              </div>
            </transition>

            <transition name="res-in">
              <div v-if="mResult" class="result-card" v-html="md(mResult)" />
            </transition>

            <button v-if="mPhase==='done'" class="ghost-btn" @click="resetMatch">
              {{ locale === 'zh' ? '↺ 重新分析' : '↺ Analyze Again' }}
            </button>
          </template>

          <!-- ══ TAB: DRAFT ══ -->
          <template v-else>
            <div class="panel-hd">
              <div class="panel-ico">✍️</div>
              <div>
                <div class="panel-title">{{ locale === 'zh' ? '我的背景' : 'My Background' }}</div>
                <div class="panel-hint">{{ locale === 'zh' ? '简单描述你的经历和技能即可' : 'Briefly describe your experience' }}</div>
              </div>
            </div>

            <div class="ta-wrap" :class="{focused: bgFocus}">
              <textarea class="glass-ta bg-ta"
                v-model="bgText"
                :placeholder="locale === 'zh'
                  ? '简单描述你的背景，例如：\n\n大三学生，软件工程专业，GPA 3.7\n做过电商推荐系统毕业设计，用了 Python / PyTorch\n有腾讯小程序开发实习经历（3 个月）\n熟悉 Vue / React，了解 SQL 和 Docker'
                  : 'Briefly describe your background, e.g.:\n\nJunior CS student, GPA 3.7\nBuilt a recommendation system (Python / PyTorch)\n3-month internship at Tencent Mini Programs\nFamiliar with Vue, React, SQL, Docker'"
                @focus="bgFocus=true" @blur="bgFocus=false"
              />
            </div>

            <button class="cta-btn"
              :disabled="!canDraft || dPhase==='loading' || dPhase==='streaming'"
              @click="runDraft">
              <span>{{ dPhase==='loading' || dPhase==='streaming'
                ? (locale==='zh' ? '生成中…' : 'Drafting…')
                : (locale==='zh' ? '✨ AI 生成简历草稿' : '✨ AI Draft Resume') }}</span>
              <span class="btn-shine"></span>
            </button>

            <div v-if="!canDraft && dPhase==='idle'" class="req-note">
              {{ locale === 'zh' ? '请先粘贴 JD 并描述你的背景（各≥20 字）' : 'Paste a JD and describe your background (20+ chars each)' }}
            </div>

            <transition name="pill-in">
              <div v-if="dPhase==='loading'" class="status-pill">
                <span class="spin-ring"></span> {{ dStatus }}
              </div>
            </transition>

            <transition name="res-in">
              <div v-if="dResult" class="result-card" v-html="md(dResult)" />
            </transition>

            <button v-if="dPhase==='done'" class="ghost-btn" @click="resetDraft">
              {{ locale === 'zh' ? '↺ 重新生成' : '↺ Draft Again' }}
            </button>
          </template>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import DOMPurify from 'dompurify'

defineEmits(['close'])

const API_BASE = 'https://offer-catcher-api.onrender.com'
const { locale } = useI18n()

// ── refs ──────────────────────────────────────────────────────
const root       = ref(null)
const canvas     = ref(null)
const cursorGlow = ref(null)
const panelL     = ref(null)
const panelR     = ref(null)

// ── shared state ──────────────────────────────────────────────
const tab      = ref('match')
const jdText   = ref('')
const jdFocus  = ref(false)
const err      = ref('')

// ── match tab state ───────────────────────────────────────────
const mFile    = ref(null)
const mPhase   = ref('idle')   // idle | loading | streaming | done
const mStatus  = ref('')
const mResult  = ref('')

// ── draft tab state ───────────────────────────────────────────
const bgText   = ref('')
const bgFocus  = ref(false)
const dPhase   = ref('idle')
const dStatus  = ref('')
const dResult  = ref('')

const canMatch = computed(() => jdText.value.trim().length >= 20 && mFile.value)
const canDraft = computed(() => jdText.value.trim().length >= 20 && bgText.value.trim().length >= 20)

// ── file picker ───────────────────────────────────────────────
const ALLOWED = new Set(['pdf','docx','doc','xlsx','xls','md','txt','jpg','jpeg','png'])
function pickFile(e) {
  const f = e.target.files?.[0]
  if (!f) return
  const ext = f.name.split('.').pop().toLowerCase()
  if (ALLOWED.has(ext)) { mFile.value = f; err.value = '' }
  else err.value = locale.value === 'zh' ? '不支持的文件格式' : 'Unsupported file format'
}

// ── SSE stream helper ─────────────────────────────────────────
async function streamSSE(url, body, onStatus, onChunk, onDone) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Accept-Language': locale.value === 'zh' ? 'zh-CN' : 'en-US' },
    body,
  })
  if (!resp.ok) {
    const e = await resp.json().catch(() => ({}))
    throw new Error(e.detail || `HTTP ${resp.status}`)
  }
  const reader = resp.body.getReader()
  const dec = new TextDecoder()
  let buf = ''
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buf += dec.decode(value, { stream: true })
    const lines = buf.split('\n'); buf = lines.pop() || ''
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      const obj = JSON.parse(line.slice(6))
      if (obj.type === 'status') onStatus(obj.text)
      else if (obj.type === 'chunk') onChunk(obj.text)
      else if (obj.type === 'error') throw new Error(obj.message)
      else if (obj.type === 'done') onDone()
    }
  }
  onDone()
}

// ── run match ─────────────────────────────────────────────────
async function runMatch() {
  if (!canMatch.value) return
  err.value = ''; mResult.value = ''; mPhase.value = 'loading'
  mStatus.value = locale.value === 'zh' ? '正在深度分析匹配度…' : 'Analyzing fit…'
  try {
    const fd = new FormData()
    fd.append('file', mFile.value)
    fd.append('jd_text', jdText.value.slice(0, 3000))
    await streamSSE(
      `${API_BASE}/api/analyze-jd`, fd,
      t => { mStatus.value = t; mPhase.value = 'loading' },
      t => { mResult.value += t; mPhase.value = 'streaming' },
      () => { mPhase.value = 'done' },
    )
  } catch (e) {
    err.value = e.message; mPhase.value = 'idle'
  }
}

function resetMatch() {
  mFile.value = null; mResult.value = ''; mPhase.value = 'idle'; err.value = ''
}

// ── run draft ─────────────────────────────────────────────────
async function runDraft() {
  if (!canDraft.value) return
  err.value = ''; dResult.value = ''; dPhase.value = 'loading'
  dStatus.value = locale.value === 'zh' ? '正在为你定制简历草稿…' : 'Drafting your tailored resume…'
  try {
    const fd = new FormData()
    fd.append('jd_text', jdText.value.slice(0, 3000))
    fd.append('background', bgText.value.slice(0, 1500))
    await streamSSE(
      `${API_BASE}/api/draft-resume`, fd,
      t => { dStatus.value = t; dPhase.value = 'loading' },
      t => { dResult.value += t; dPhase.value = 'streaming' },
      () => { dPhase.value = 'done' },
    )
  } catch (e) {
    err.value = e.message; dPhase.value = 'idle'
  }
}

function resetDraft() {
  dResult.value = ''; dPhase.value = 'idle'; err.value = ''
}

// ── Markdown renderer ─────────────────────────────────────────
function md(raw) {
  const lines = raw.split('\n')
  let html = '', ul = false, tbuf = []
  const inl = s => s
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
  const flushTable = () => {
    if (tbuf.length < 2) { tbuf.forEach(l => { html += '<p>' + inl(l) + '</p>' }); tbuf = []; return }
    const cells = row => row.split('|').slice(1, -1).map(c => c.trim())
    html += '<div class="tbl-wrap"><table class="md-tbl"><thead><tr>'
    cells(tbuf[0]).forEach(h => { html += `<th>${inl(h)}</th>` })
    html += '</tr></thead><tbody>'
    tbuf.slice(2).forEach(row => { html += '<tr>'; cells(row).forEach(c => { html += `<td>${inl(c)}</td>` }); html += '</tr>' })
    html += '</tbody></table></div>'; tbuf = []
  }
  for (const raw of lines) {
    const t = raw.trim()
    if (t.startsWith('|')) { if (ul) { html += '</ul>'; ul = false } tbuf.push(t); continue }
    if (tbuf.length) flushTable()
    if (!t) { if (ul) { html += '</ul>'; ul = false } continue }
    if (t.startsWith('### ')) { if (ul) { html += '</ul>'; ul = false } html += '<h3>' + inl(t.slice(4)) + '</h3>'; continue }
    if (t.startsWith('## '))  { if (ul) { html += '</ul>'; ul = false } html += '<h2>' + inl(t.slice(3)) + '</h2>'; continue }
    if (t.startsWith('> '))   { if (ul) { html += '</ul>'; ul = false } html += '<blockquote>' + inl(t.slice(2)) + '</blockquote>'; continue }
    if (t.startsWith('- '))   { if (!ul) { html += '<ul>'; ul = true } html += '<li>' + inl(t.slice(2)) + '</li>'; continue }
    const m = t.match(/^(\d+)\.\s(.*)/)
    if (m) { if (ul) { html += '</ul>'; ul = false } html += '<p><strong>' + m[1] + '.</strong> ' + inl(m[2]) + '</p>'; continue }
    if (ul) { html += '</ul>'; ul = false }
    html += '<p>' + inl(t) + '</p>'
  }
  if (tbuf.length) flushTable()
  if (ul) html += '</ul>'
  return DOMPurify.sanitize(html, { USE_PROFILES: { html: true } })
}
const mdResult = computed(() => md)

// ── cursor glow ───────────────────────────────────────────────
let mx = 0, my = 0, cgx = 0, cgy = 0, rafCursor = 0
function onMouse(e) { mx = e.clientX; my = e.clientY }
function animCursor() {
  cgx += (mx - cgx) * 0.09
  cgy += (my - cgy) * 0.09
  if (cursorGlow.value)
    cursorGlow.value.style.transform = `translate(${cgx - 200}px,${cgy - 200}px)`
  rafCursor = requestAnimationFrame(animCursor)
}

// ── 3D tilt ───────────────────────────────────────────────────
function tilt(e, elRef) {
  const el = elRef?.value ?? elRef
  if (!el) return
  const r = el.getBoundingClientRect()
  const x = (e.clientX - r.left) / r.width  - 0.5
  const y = (e.clientY - r.top)  / r.height - 0.5
  el.style.transform = `perspective(800px) rotateX(${-y * 7}deg) rotateY(${x * 7}deg) scale(1.02) translateZ(6px)`
  el.style.transition = 'transform .08s linear'
}
function resetTilt(elRef) {
  const el = elRef?.value ?? elRef
  if (!el) return
  el.style.transform = ''
  el.style.transition = 'transform .55s cubic-bezier(0.22,1,0.36,1)'
}

// ── canvas particles ──────────────────────────────────────────
let ctx2d, pts = [], rafCanvas = 0
const N = 65, MAX_D = 130

function initCanvas() {
  const c = canvas.value
  if (!c) return
  c.width = window.innerWidth; c.height = window.innerHeight
  ctx2d = c.getContext('2d')
  pts = Array.from({ length: N }, () => ({
    x: Math.random() * c.width, y: Math.random() * c.height,
    vx: (Math.random() - 0.5) * 0.38, vy: (Math.random() - 0.5) * 0.38,
    r: Math.random() * 1.4 + 0.5,
  }))
}

function drawCanvas() {
  const c = canvas.value
  if (!c || !ctx2d) return
  ctx2d.clearRect(0, 0, c.width, c.height)
  for (const p of pts) {
    p.x += p.vx; p.y += p.vy
    if (p.x < 0 || p.x > c.width)  p.vx *= -1
    if (p.y < 0 || p.y > c.height) p.vy *= -1
    ctx2d.beginPath()
    ctx2d.arc(p.x, p.y, p.r, 0, Math.PI * 2)
    ctx2d.fillStyle = 'rgba(129,140,248,.65)'
    ctx2d.fill()
  }
  for (let i = 0; i < pts.length; i++) {
    for (let j = i + 1; j < pts.length; j++) {
      const dx = pts[i].x - pts[j].x, dy = pts[i].y - pts[j].y
      const d = Math.sqrt(dx * dx + dy * dy)
      if (d < MAX_D) {
        ctx2d.beginPath()
        ctx2d.moveTo(pts[i].x, pts[i].y)
        ctx2d.lineTo(pts[j].x, pts[j].y)
        ctx2d.strokeStyle = `rgba(129,140,248,${.11 * (1 - d / MAX_D)})`
        ctx2d.lineWidth = 0.75
        ctx2d.stroke()
      }
    }
  }
  rafCanvas = requestAnimationFrame(drawCanvas)
}

function onResize() {
  if (canvas.value) {
    canvas.value.width = window.innerWidth
    canvas.value.height = window.innerHeight
  }
}

onMounted(() => {
  initCanvas(); drawCanvas(); animCursor()
  window.addEventListener('resize', onResize)
})
onUnmounted(() => {
  cancelAnimationFrame(rafCanvas)
  cancelAnimationFrame(rafCursor)
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
/* ── Root: full-page dark overlay ────────────────────────────── */
.jdm {
  position: fixed; inset: 0; z-index: 50;
  background: #050510;
  color: #e2e8f0;
  font-family: -apple-system, 'SF Pro Text', 'Inter', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  overflow-y: auto;
  overflow-x: hidden;
}

/* ── Fixed BG layer ── */
.bg-canvas { position: fixed; inset: 0; z-index: 0; pointer-events: none; }

.aurora { position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
.ab { position: absolute; border-radius: 50%; filter: blur(88px); opacity: .12; animation: ab-float 9s ease-in-out infinite; }
.ab1 { width: 680px; height: 680px; background: #6366f1; top: -220px; left: -160px; }
.ab2 { width: 520px; height: 520px; background: #8b5cf6; top: 40%; right: -180px; animation-delay: -3.5s; }
.ab3 { width: 440px; height: 440px; background: #06b6d4; bottom: 8%; left: 18%; animation-delay: -6s; }
@keyframes ab-float {
  0%, 100% { transform: translateY(0) scale(1); }
  50%       { transform: translateY(-36px) scale(1.04); }
}

.cursor-glow {
  position: fixed; top: 0; left: 0; width: 400px; height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99,102,241,.17) 0%, transparent 70%);
  pointer-events: none; z-index: 1; will-change: transform;
}

/* ── Nav ── */
.jdm-nav {
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 28px; height: 56px;
  background: rgba(5,5,16,.75);
  backdrop-filter: saturate(180%) blur(24px);
  -webkit-backdrop-filter: saturate(180%) blur(24px);
  border-bottom: 1px solid rgba(255,255,255,.06);
}
.back-btn {
  display: flex; align-items: center; gap: 7px;
  background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.1);
  color: #94a3b8; border-radius: 980px; padding: 6px 16px;
  font-size: .8rem; font-weight: 600; cursor: pointer;
  transition: all .4s cubic-bezier(0.22,1,0.36,1);
}
.back-btn:hover { background: rgba(255,255,255,.11); color: #f1f5f9; transform: translateX(-2px); }
.back-ico { transition: transform .35s cubic-bezier(0.22,1,0.36,1); }
.back-btn:hover .back-ico { transform: translateX(-3px); }
.nav-brand { display: flex; align-items: center; gap: 8px; }
.brand-ico { font-size: 1rem; }
.brand-word { font-weight: 700; font-size: .9rem; color: #f1f5f9; letter-spacing: -.01em; }

/* ── Scrollable content wrapper ── */
.jdm-body {
  position: relative; z-index: 10;
  max-width: 1140px; margin: 0 auto;
  padding: 64px 24px 100px;
}

/* ── Hero ── */
.jdm-hero { text-align: center; margin-bottom: 44px; }

.hero-tag {
  display: inline-flex; align-items: center; gap: 8px;
  font-size: .72rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase;
  color: #818cf8;
  background: rgba(99,102,241,.1); border: 1px solid rgba(99,102,241,.25);
  padding: 5px 15px; border-radius: 20px; margin-bottom: 24px;
}
.tag-dot {
  width: 6px; height: 6px; border-radius: 50%; background: #818cf8;
  animation: dot-pulse 2s ease-in-out infinite;
}
@keyframes dot-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: .4; transform: scale(.75); }
}

.jdm-h1 {
  font-size: clamp(2rem, 5.5vw, 3.8rem);
  font-weight: 800; line-height: 1.1; letter-spacing: -.04em;
  margin: 0 0 18px;
}
.h1-plain { color: #f1f5f9; }
.h1-grad {
  display: inline-block;
  background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #67e8f9 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  animation: grad-anim 6s ease-in-out infinite alternate; background-size: 200% 200%;
}
.h1-grad2 {
  display: inline-block;
  background: linear-gradient(135deg, #34d399 0%, #06b6d4 50%, #818cf8 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  animation: grad-anim 6s ease-in-out infinite alternate; background-size: 200% 200%;
}
@keyframes grad-anim {
  from { background-position: 0% 50%; }
  to   { background-position: 100% 50%; }
}

.jdm-sub {
  font-size: clamp(.85rem, 2vw, 1rem);
  color: #94a3b8; max-width: 560px; margin: 0 auto; line-height: 1.7;
}

/* ── Tab bar ── */
.tabs {
  display: flex; gap: 10px; justify-content: center;
  margin-bottom: 36px;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.07);
  padding: 6px; border-radius: 16px;
  max-width: 380px; margin-left: auto; margin-right: auto; margin-bottom: 36px;
}
.tab-btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 7px;
  padding: 10px 18px; border-radius: 12px; border: none; cursor: pointer;
  font-size: .84rem; font-weight: 600; letter-spacing: -.01em;
  color: #64748b; background: transparent;
  transition: all .4s cubic-bezier(0.22,1,0.36,1);
}
.tab-btn.active {
  background: rgba(99,102,241,.25);
  color: #c7d2fe;
  box-shadow: 0 0 0 1px rgba(99,102,241,.35), 0 4px 16px rgba(99,102,241,.2);
}
.tab-btn:not(.active):hover { color: #94a3b8; background: rgba(255,255,255,.05); }
.tab-ico { font-size: .9rem; }

/* ── Error ── */
.err-box {
  max-width: 860px; margin: 0 auto 20px;
  background: rgba(254,202,202,.08); border: 1px solid rgba(252,165,165,.25);
  border-radius: 14px; padding: 12px 18px; color: #fca5a5; font-size: .85rem;
}
.err-fade-enter-active, .err-fade-leave-active { transition: opacity .35s, transform .35s cubic-bezier(0.22,1,0.36,1); }
.err-fade-enter-from, .err-fade-leave-to { opacity: 0; transform: translateY(-8px); }

/* ── Panels grid ── */
.panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22px;
  align-items: start;
}
@media (max-width: 700px) { .panels { grid-template-columns: 1fr; } }

/* ── Panel card ── */
.panel {
  position: relative;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 22px;
  padding: 24px 22px 20px;
  overflow: hidden;
  transition: transform .55s cubic-bezier(0.22,1,0.36,1), box-shadow .55s cubic-bezier(0.22,1,0.36,1);
  will-change: transform;
}
.panel:hover { box-shadow: 0 16px 48px rgba(99,102,241,.16), 0 0 0 1px rgba(99,102,241,.22); }
.panel-glow {
  position: absolute; inset: -1px; border-radius: 23px; z-index: 0;
  background: linear-gradient(135deg, rgba(99,102,241,0), rgba(139,92,246,0), rgba(6,182,212,0));
  transition: background .45s;
  pointer-events: none;
}
.panel:hover .panel-glow {
  background: linear-gradient(135deg, rgba(99,102,241,.3), rgba(139,92,246,.18), rgba(6,182,212,.22));
}

.panel-hd {
  display: flex; align-items: flex-start; gap: 12px;
  margin-bottom: 16px; position: relative; z-index: 1;
}
.panel-ico {
  font-size: 1.4rem; margin-top: 2px;
  background: rgba(99,102,241,.15); border: 1px solid rgba(99,102,241,.25);
  width: 40px; height: 40px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.panel-title { font-size: .9rem; font-weight: 700; color: #f1f5f9; letter-spacing: -.01em; }
.panel-hint  { font-size: .72rem; color: #64748b; margin-top: 2px; }

/* ── Textarea ── */
.ta-wrap {
  border: 1.5px solid rgba(255,255,255,.08);
  border-radius: 16px;
  overflow: hidden;     /* clips child if somehow it still overflows */
  max-height: 340px;    /* parent cap — top boundary can never rise above JD panel */
  transition: border-color .35s cubic-bezier(0.22,1,0.36,1), box-shadow .35s cubic-bezier(0.22,1,0.36,1);
  position: relative; z-index: 1;
}
.ta-wrap.focused {
  border-color: rgba(99,102,241,.5);
  box-shadow: 0 0 0 3px rgba(99,102,241,.12);
}
.glass-ta {
  display: block; width: 100%;
  height: 280px;        /* fixed height — prevents infinite vertical growth */
  min-height: 120px;    /* graceful floor on very small viewports */
  max-height: 320px;    /* hard ceiling */
  overflow-y: auto;     /* scroll inside instead of expanding the panel */
  background: rgba(255,255,255,.03); color: #e2e8f0;
  border: none; outline: none; resize: none;
  padding: 15px 16px;
  font-size: .86rem; line-height: 1.75; font-family: inherit;
}
.bg-ta { height: 220px; max-height: 260px; }
.glass-ta::placeholder { color: #334155; }

.ta-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 7px 14px;
  border-top: 1px solid rgba(255,255,255,.05);
  background: rgba(255,255,255,.02);
  position: relative; z-index: 1;
}
.char-cnt { font-size: .68rem; color: #475569; font-variant-numeric: tabular-nums; }
.char-cnt.warn { color: #f87171; }
.clear-btn {
  font-size: .7rem; font-weight: 600; color: #475569;
  background: none; border: none; cursor: pointer; padding: 2px 8px;
  border-radius: 8px; transition: background .25s, color .25s;
}
.clear-btn:hover { background: rgba(255,255,255,.08); color: #94a3b8; }

/* ── Drop zone ── */
.drop-zone {
  display: block;
  border: 1.5px dashed rgba(99,102,241,.3);
  border-radius: 18px;
  background: rgba(99,102,241,.04);
  padding: 32px 24px; text-align: center;
  cursor: pointer;
  transition: all .45s cubic-bezier(0.22,1,0.36,1);
  position: relative; z-index: 1;
}
.drop-zone:hover {
  border-color: rgba(99,102,241,.6);
  background: rgba(99,102,241,.1);
  transform: scale(1.015) translateY(-2px);
}
.drop-zone.has-file {
  border-style: solid; border-color: rgba(52,211,153,.4);
  background: rgba(52,211,153,.06);
}
.dz-cloud { display: block; font-size: 2rem; margin-bottom: 8px; color: #818cf8; opacity: .7; }
.dz-check { display: block; font-size: 2rem; margin-bottom: 8px; color: #34d399; }
.dz-main  { display: block; font-size: .88rem; font-weight: 600; color: #cbd5e1; }
.dz-sub   { display: block; font-size: .72rem; color: #475569; margin-top: 5px; }
.dz-name  { display: block; font-size: .84rem; font-weight: 600; color: #34d399; word-break: break-all; }

/* ── CTA button ── */
.cta-btn {
  position: relative; overflow: hidden;
  display: block; width: 100%; margin-top: 16px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border: none; border-radius: 14px;
  padding: 13px 24px;
  font-size: .9rem; font-weight: 700; color: #fff; letter-spacing: -.01em;
  cursor: pointer;
  box-shadow: 0 4px 22px rgba(99,102,241,.38);
  transition: transform .45s cubic-bezier(0.22,1,0.36,1), box-shadow .45s cubic-bezier(0.22,1,0.36,1);
  will-change: transform; z-index: 1;
}
.cta-btn:disabled {
  opacity: .45; cursor: not-allowed; transform: none !important; box-shadow: none !important;
}
.cta-btn:not(:disabled):hover {
  transform: scale(1.03) translateY(-2px);
  box-shadow: 0 8px 32px rgba(99,102,241,.52), 0 0 0 3px rgba(99,102,241,.18);
}
.cta-btn:not(:disabled):active { transform: scale(.97); transition-duration: .1s; }
.btn-shine {
  position: absolute; inset: 0;
  background: linear-gradient(110deg, transparent 30%, rgba(255,255,255,.2) 50%, transparent 70%);
  transform: translateX(-100%); transition: transform 0s;
}
.cta-btn:not(:disabled):hover .btn-shine { transform: translateX(100%); transition: transform .5s ease; }

/* ── Hint text ── */
.req-note {
  font-size: .73rem; color: #475569; text-align: center;
  margin-top: 10px; position: relative; z-index: 1;
}

/* ── Status pill ── */
.status-pill {
  display: flex; align-items: center; gap: 10px;
  margin-top: 16px; padding: 11px 16px;
  background: rgba(99,102,241,.1); border: 1px solid rgba(99,102,241,.2);
  border-radius: 12px; font-size: .84rem; color: #a5b4fc;
  position: relative; z-index: 1;
}
.spin-ring {
  display: inline-block; width: 14px; height: 14px; flex-shrink: 0;
  border: 2px solid rgba(165,180,252,.3); border-top-color: #818cf8;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.pill-in-enter-active { transition: opacity .35s, transform .35s cubic-bezier(0.22,1,0.36,1); }
.pill-in-enter-from   { opacity: 0; transform: translateY(8px); }

/* ── Result card ── */
.result-card {
  margin-top: 18px; padding: 20px 18px;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.07);
  border-radius: 16px;
  position: relative; z-index: 1;
}
.res-in-enter-active { transition: opacity .55s cubic-bezier(0.22,1,0.36,1), transform .55s cubic-bezier(0.22,1,0.36,1); }
.res-in-enter-from   { opacity: 0; transform: translateY(14px); }

:deep(.result-card h2) {
  font-size: .88rem; font-weight: 800; color: #c7d2fe;
  margin: 20px 0 8px;
  padding-bottom: 6px; border-bottom: 1px solid rgba(99,102,241,.2);
  letter-spacing: -.01em;
}
:deep(.result-card h2:first-child) { margin-top: 0; }
:deep(.result-card h3) { font-size: .84rem; font-weight: 700; color: #a5b4fc; margin: 12px 0 5px; }
:deep(.result-card p), :deep(.result-card li) { font-size: .83rem; color: #cbd5e1; line-height: 1.78; }
:deep(.result-card ul) { padding-left: 20px; }
:deep(.result-card li) { margin-bottom: 4px; }
:deep(.result-card strong) { color: #e2e8f0; font-weight: 700; }
:deep(.result-card blockquote) {
  border-left: 3px solid #6366f1; margin: 8px 0;
  padding: 6px 14px; background: rgba(99,102,241,.08); border-radius: 0 10px 10px 0;
  font-size: .82rem; color: #94a3b8;
}
:deep(.result-card .tbl-wrap) { overflow-x: auto; }
:deep(.result-card .md-tbl) { width: 100%; border-collapse: collapse; font-size: .8rem; }
:deep(.result-card .md-tbl th) { background: rgba(99,102,241,.15); color: #c7d2fe; padding: 7px 10px; text-align: left; }
:deep(.result-card .md-tbl td) { padding: 6px 10px; color: #94a3b8; border-bottom: 1px solid rgba(255,255,255,.05); }

/* ── Ghost / reset button ── */
.ghost-btn {
  display: block; width: 100%; margin-top: 14px;
  background: transparent; border: 1px solid rgba(255,255,255,.1);
  border-radius: 12px; padding: 10px;
  font-size: .83rem; font-weight: 600; color: #64748b; cursor: pointer;
  transition: all .4s cubic-bezier(0.22,1,0.36,1);
  position: relative; z-index: 1;
}
.ghost-btn:hover { border-color: rgba(255,255,255,.22); color: #94a3b8; background: rgba(255,255,255,.04); }

/* ── Entrance animation ── */
.ai-in {
  opacity: 0;
  transform: translateY(26px);
  animation: fadeUp .9s cubic-bezier(0.22,1,0.36,1) both;
  animation-delay: var(--d, 0s);
}
@keyframes fadeUp { to { opacity: 1; transform: translateY(0); } }
</style>
