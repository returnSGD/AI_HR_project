<template>
  <header class="hdr">
    <div class="logo"><span class="lb">🎯</span> Offer-Catcher <span class="pill">{{ t('badge') }}</span></div>
    <div class="hr">
      <button v-if="phase === 'done'" class="btn-g" @click="reset">{{ t('nav.new') }}</button>
      <button class="prof" @click="showProfile = true" :title="t('nav.profile')">👤</button>
    </div>
  </header>

  <main class="main">
    <div v-if="err" class="err">⚠️ {{ err }}</div>

    <!-- IDLE -->
    <template v-if="phase === 'idle'">
      <h1 v-if="locale === 'zh'" class="h1">{{ t('hero.l1') }}<br><span class="ac">{{ t('hero.accent') }}</span></h1>
      <h1 v-else class="h1">{{ t('hero.l1') }} <span class="ac">{{ t('hero.accent') }}</span><br>{{ t('hero.l2') }}</h1>
      <p class="sub">{{ t('hero.sub') }}</p>

      <label class="upload">
        <input type="file" accept=".pdf" @change="pick" hidden>
        <span v-if="!file">📋 {{ t('upload.drag') }}</span>
        <span v-else>📄 {{ file.name }}</span>
      </label>
      <div class="center">
        <button class="btn" :disabled="!file" @click="run">{{ t('btn.run') }}</button>
      </div>
    </template>

    <!-- WORKING / RESULTS -->
    <template v-else>
      <div v-if="phase === 'loading'" class="status">⏳ {{ statusText }}</div>

      <div v-if="jobs.length">
        <div class="slabel">{{ t('section.jobs', { n: jobs.length }) }}</div>
        <div v-for="(j, i) in jobs" :key="j.id" :class="['job', i === 0 && 'top']">
          <div class="job-top">
            <div>
              <div class="co">{{ j.company }}</div>
              <div class="ti">{{ j.title }}</div>
            </div>
            <div class="score">{{ j.score }}%<span>{{ t('job.match') }}</span></div>
          </div>
          <div class="tags"><span v-for="tg in j.tags" :key="tg">{{ tg }}</span></div>
        </div>
      </div>

      <div v-if="report" class="slabel">
        {{ t('section.report') }}
        <span class="bdg">{{ phase === 'done' ? t('section.complete') : t('section.generating') }}</span>
      </div>
      <div v-if="report" class="rbox" v-html="reportHtml"></div>

      <div v-if="phase === 'done'" class="center">
        <button class="btn" @click="reset">{{ t('btn.again') }}</button>
      </div>
    </template>

    <div class="footer">{{ t('footer') }}</div>
  </main>

  <MyProfile v-model="showProfile" />
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import MyProfile from './components/MyProfile.vue'

const API = 'http://localhost:8000/api/match'
const { t, locale } = useI18n()

const phase = ref('idle')        // idle | loading | streaming | done
const file = ref(null)
const jobs = ref([])
const report = ref('')
const err = ref('')
const statusText = ref('')
const showProfile = ref(false)

const reportHtml = computed(() => renderMarkdown(report.value))

function renderMarkdown(md) {
  const lines = md.split('\n'); let html = '', ul = false
  const inl = s => s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  for (const raw of lines) {
    const t = raw.trim()
    if (!t) { if (ul) { html += '</ul>'; ul = false } continue }
    if (t.startsWith('## ')) { if (ul) { html += '</ul>'; ul = false } html += '<h2>' + inl(t.slice(3)) + '</h2>'; continue }
    if (t.startsWith('- ')) { if (!ul) { html += '<ul>'; ul = true } html += '<li>' + inl(t.slice(2)) + '</li>'; continue }
    const m = t.match(/^(\d+)\.\s(.*)/)
    if (m) { if (ul) { html += '</ul>'; ul = false } html += '<p><strong>' + m[1] + '.</strong> ' + inl(m[2]) + '</p>'; continue }
    if (ul) { html += '</ul>'; ul = false }
    html += '<p>' + inl(t) + '</p>'
  }
  if (ul) html += '</ul>'
  return html
}

function pick(e) {
  const f = e.target.files?.[0]
  if (f?.type === 'application/pdf') { file.value = f; err.value = '' }
  else if (f) err.value = t('error.pdf')
}

async function run() {
  if (!file.value) return
  err.value = ''; jobs.value = []; report.value = ''
  phase.value = 'loading'; statusText.value = t('status.read')
  try {
    const fd = new FormData()
    fd.append('file', file.value)
    const resp = await fetch(API, {
      method: 'POST',
      headers: { 'Accept-Language': locale.value === 'zh' ? 'zh-CN' : 'en-US' },
      body: fd
    })
    if (!resp.ok) {
      const e = await resp.json().catch(() => ({}))
      throw new Error(e.detail || ('HTTP ' + resp.status))
    }
    statusText.value = t('status.match')
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
        if (obj.type === 'jobs') { jobs.value = obj.jobs; phase.value = 'streaming' }
        else if (obj.type === 'chunk') { report.value += obj.text }
        else if (obj.type === 'error') { throw new Error(obj.message) }
        else if (obj.type === 'done') { phase.value = 'done' }
      }
    }
    phase.value = 'done'
  } catch (e) {
    err.value = e.message || t('error.api')
    phase.value = 'idle'
  }
}

function reset() {
  phase.value = 'idle'; file.value = null; jobs.value = []
  report.value = ''; err.value = ''
}
</script>

<style>
:root { --y: #FFD700; --yh: #F0C800; --dk: #0F172A; --g5: #64748B; --g2: #E2E8F0; }
* { box-sizing: border-box; margin: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #F8FAFC; color: var(--dk); }
.hdr { background: #fff; border-bottom: 1px solid var(--g2); height: 58px; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; }
.logo { font-weight: 800; }
.lb { background: var(--y); border-radius: 8px; padding: 4px 6px; }
.pill { font-size: .65rem; font-weight: 700; background: #FFFBEB; border: 1px solid #FDE68A; color: #92400E; padding: 2px 8px; border-radius: 20px; }
.hr { display: flex; align-items: center; gap: 8px; }
.prof { width: 34px; height: 34px; border-radius: 50%; border: 1.5px solid var(--g2); background: #fff; cursor: pointer; }
.prof:hover { border-color: var(--y); background: #FFFBEB; }
.main { max-width: 760px; margin: 0 auto; padding: 40px 20px 80px; }
.h1 { font-size: clamp(1.8rem, 5vw, 2.6rem); font-weight: 900; text-align: center; line-height: 1.15; }
.ac { color: var(--yh); }
.sub { text-align: center; color: var(--g5); margin: 14px auto 28px; max-width: 480px; }
.upload { display: block; border: 2px dashed var(--g2); border-radius: 14px; background: #fff; padding: 48px; text-align: center; cursor: pointer; font-weight: 600; }
.upload:hover { border-color: var(--y); background: #FFFBEB; }
.center { text-align: center; margin-top: 20px; }
.btn { background: var(--y); border: none; border-radius: 8px; padding: 13px 32px; font-weight: 700; cursor: pointer; box-shadow: 0 2px 10px rgba(255,215,0,.35); }
.btn:hover:not([disabled]) { background: var(--yh); }
.btn[disabled] { opacity: .55; cursor: not-allowed; }
.btn-g { background: #fff; border: 1px solid var(--g2); border-radius: 8px; padding: 8px 16px; font-weight: 600; cursor: pointer; }
.status { background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px; padding: 12px 18px; color: #78350F; margin-bottom: 20px; }
.err { background: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; padding: 14px 18px; color: #991B1B; margin-bottom: 20px; }
.slabel { font-weight: 700; margin: 22px 0 14px; display: flex; align-items: center; gap: 8px; }
.bdg { font-size: .68rem; font-weight: 700; background: #FFFBEB; border: 1px solid #FDE68A; color: #92400E; padding: 2px 8px; border-radius: 20px; }
.job { background: #fff; border: 1px solid var(--g2); border-radius: 14px; padding: 18px; margin-bottom: 12px; }
.job.top { border-top: 3px solid var(--y); }
.job-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 10px; }
.co { font-size: .78rem; color: var(--g5); }
.ti { font-weight: 700; }
.score { font-size: 1.3rem; font-weight: 900; text-align: right; }
.score span { display: block; font-size: .62rem; font-weight: 600; color: var(--g5); text-transform: uppercase; }
.tags { display: flex; flex-wrap: wrap; gap: 5px; }
.tags span { background: #F8FAFC; border-radius: 5px; padding: 3px 9px; font-size: .76rem; }
.rbox { background: #fff; border: 1px solid var(--g2); border-radius: 14px; padding: 24px; line-height: 1.8; }
.rbox h2 { font-size: .95rem; margin: 20px 0 8px; padding-bottom: 6px; border-bottom: 2px solid #FFFBEB; }
.rbox h2:first-child { margin-top: 0; }
.rbox ul { padding-left: 22px; }
.footer { text-align: center; color: #94A3B8; font-size: .78rem; margin-top: 48px; }
</style>
